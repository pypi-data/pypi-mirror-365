"""
PCILeech FPGA Firmware Builder Main Script
Usage:
    python3 build.py \
            --bdf 0000:03:00.0 \
            --board pcileech_35t325_x4 \
            [--vivado] \
            [--preload-msix]
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple, Union

# Import board functions from the correct module
from src.device_clone.board_config import (
    get_board_info,
    get_pcileech_board_config,
    validate_board,
)

# Import msix_capability at the module level to avoid late imports
from src.device_clone.msix_capability import parse_msix_capability
from src.exceptions import PlatformCompatibilityError
from src.log_config import get_logger, setup_logging
from src.string_utils import safe_format

# ──────────────────────────────────────────────────────────────────────────────
# Constants - Extracted magic numbers
# ──────────────────────────────────────────────────────────────────────────────
BUFFER_SIZE = 1024 * 1024  # 1MB buffer for file operations
CONFIG_SPACE_PATH_TEMPLATE = "/sys/bus/pci/devices/{}/config"
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_PROFILE_DURATION = 30  # seconds
MAX_PARALLEL_FILE_WRITES = 4  # Maximum concurrent file write operations
FILE_WRITE_TIMEOUT = 30  # seconds

# Required modules for production
REQUIRED_MODULES = [
    "src.device_clone.pcileech_generator",
    "src.device_clone.behavior_profiler",
    "src.templating.tcl_builder",
]

# File extension mappings
SPECIAL_FILE_EXTENSIONS = {".coe", ".hex"}
SYSTEMVERILOG_EXTENSION = ".sv"


# ──────────────────────────────────────────────────────────────────────────────
# Custom Exceptions
# ──────────────────────────────────────────────────────────────────────────────
class PCILeechBuildError(Exception):
    """Base exception for PCILeech build errors."""

    pass


class ModuleImportError(PCILeechBuildError):
    """Raised when required modules cannot be imported."""

    pass


class MSIXPreloadError(PCILeechBuildError):
    """Raised when MSI-X data preloading fails."""

    pass


class FileOperationError(PCILeechBuildError):
    """Raised when file operations fail."""

    pass


class VivadoIntegrationError(PCILeechBuildError):
    """Raised when Vivado integration fails."""

    pass


class ConfigurationError(PCILeechBuildError):
    """Raised when configuration is invalid."""

    pass


# ──────────────────────────────────────────────────────────────────────────────
# Type Definitions and Protocols
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class BuildConfiguration:
    """Configuration for the firmware build process."""

    bdf: str
    board: str
    output_dir: Path
    enable_profiling: bool = True
    preload_msix: bool = True
    profile_duration: int = DEFAULT_PROFILE_DURATION
    parallel_writes: bool = True
    max_workers: int = MAX_PARALLEL_FILE_WRITES
    output_template: Optional[str] = None
    donor_template: Optional[str] = None


@dataclass
class MSIXData:
    """Container for MSI-X capability data."""

    preloaded: bool
    msix_info: Optional[Dict[str, Any]] = None
    config_space_hex: Optional[str] = None
    config_space_bytes: Optional[bytes] = None


@dataclass
class DeviceConfiguration:
    """Device configuration extracted from the build process."""

    vendor_id: int
    device_id: int
    revision_id: int
    class_code: int
    requires_msix: bool
    pcie_lanes: int


class FileWriter(Protocol):
    """Protocol for file writing implementations."""

    def write_file(self, path: Path, content: str) -> None:
        """Write content to a file."""
        ...


# ──────────────────────────────────────────────────────────────────────────────
# Module Import Checker
# ──────────────────────────────────────────────────────────────────────────────
class ModuleChecker:
    """Handles checking and validation of required modules."""

    def __init__(self, required_modules: List[str]):
        """
        Initialize the module checker.

        Args:
            required_modules: List of module names that must be available
        """
        self.required_modules = required_modules
        self.logger = get_logger(self.__class__.__name__)

    def check_all(self) -> None:
        """
        Check that all required modules are available.

        Raises:
            ModuleImportError: If any required module cannot be imported
        """
        for module in self.required_modules:
            self._check_module(module)

    def _check_module(self, module: str) -> None:
        """
        Check a single module for availability.

        Args:
            module: Module name to check

        Raises:
            ModuleImportError: If the module cannot be imported
        """
        try:
            __import__(module)
        except ImportError as err:
            self._handle_import_error(module, err)

    def _handle_import_error(self, module: str, error: ImportError) -> None:
        """
        Handle import error with detailed diagnostics.

        Args:
            module: Module that failed to import
            error: The import error

        Raises:
            ModuleImportError: Always raises with diagnostic information
        """
        diagnostics = self._gather_diagnostics(module)
        error_msg = (
            f"Required module `{module}` is missing. "
            "Ensure the production container/image is built correctly.\n"
            f"{diagnostics}"
        )
        raise ModuleImportError(error_msg) from error

    def _gather_diagnostics(self, module: str) -> str:
        """
        Gather diagnostic information for import failure.

        Args:
            module: Module that failed to import

        Returns:
            Formatted diagnostic information
        """
        lines = [
            "\n[DIAGNOSTICS] Python module import failure",
            f"Python version: {sys.version}",
            f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}",
            f"Current directory: {os.getcwd()}",
        ]

        # Check module file existence
        module_parts = module.split(".")
        module_path = os.path.join(*module_parts) + ".py"
        # Handle case where module_parts[1:] is empty
        alt_module_path = (
            os.path.join(*module_parts[1:]) + ".py" if len(module_parts) > 1 else ""
        )

        lines.extend(
            [
                f"Looking for module file at: {module_path}",
                (
                    f"✓ File exists at {module_path}"
                    if os.path.exists(module_path)
                    else f"✗ File not found at {module_path}"
                ),
            ]
        )

        # Only check alternative path if it exists
        if alt_module_path:
            lines.extend(
                [
                    f"Looking for module file at: {alt_module_path}",
                    (
                        f"✓ File exists at {alt_module_path}"
                        if os.path.exists(alt_module_path)
                        else f"✗ File not found at {alt_module_path}"
                    ),
                ]
            )

        # Check for __init__.py files
        module_dir = os.path.dirname(module_path)
        lines.append(f"Checking for __init__.py files in path: {module_dir}")

        current_dir = ""
        for part in module_dir.split(os.path.sep):
            if not part:
                continue
            current_dir = os.path.join(current_dir, part)
            init_path = os.path.join(current_dir, "__init__.py")
            status = "✓" if os.path.exists(init_path) else "✗"
            lines.append(f"{status} __init__.py in {current_dir}")

        # List sys.path
        lines.append("\nPython module search path:")
        lines.extend(f"  - {path}" for path in sys.path)

        return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# MSI-X Manager
# ──────────────────────────────────────────────────────────────────────────────
class MSIXManager:
    """Manages MSI-X capability data preloading and injection."""

    def __init__(self, bdf: str, logger: Optional[logging.Logger] = None):
        """
        Initialize the MSI-X manager.

        Args:
            bdf: PCI Bus/Device/Function address
            logger: Optional logger instance
        """
        self.bdf = bdf
        self.logger = logger or get_logger(self.__class__.__name__)

    def preload_data(self) -> MSIXData:
        """
        Preload MSI-X data before VFIO binding.

        Returns:
            MSIXData object containing preloaded information

        Note:
            Returns empty MSIXData on any failure (non-critical operation)
        """
        try:
            self.logger.info("➤ Preloading MSI-X data before VFIO binding")

            config_space_path = CONFIG_SPACE_PATH_TEMPLATE.format(self.bdf)
            if not os.path.exists(config_space_path):
                self.logger.warning(
                    "Config space not accessible via sysfs, skipping MSI-X preload"
                )
                return MSIXData(preloaded=False)

            config_space_bytes = self._read_config_space(config_space_path)
            config_space_hex = config_space_bytes.hex()
            msix_info = parse_msix_capability(config_space_hex)

            if msix_info["table_size"] > 0:
                self.logger.info(
                    "  • Found MSI-X capability: %d vectors", msix_info["table_size"]
                )
                return MSIXData(
                    preloaded=True,
                    msix_info=msix_info,
                    config_space_hex=config_space_hex,
                    config_space_bytes=config_space_bytes,
                )
            else:
                self.logger.info("  • No MSI-X capability found")
                return MSIXData(preloaded=True, msix_info=None)

        except Exception as e:
            self.logger.warning("MSI-X preload failed: %s", str(e))
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug("MSI-X preload exception details:", exc_info=True)
            return MSIXData(preloaded=False)

    def inject_data(self, result: Dict[str, Any], msix_data: MSIXData) -> None:
        """
        Inject preloaded MSI-X data into the generation result.

        Args:
            result: The generation result dictionary to update
            msix_data: The preloaded MSI-X data
        """
        if not self._should_inject(msix_data):
            return

        self.logger.info("  • Using preloaded MSI-X data")

        # msix_info is guaranteed to be non-None by _should_inject
        if msix_data.msix_info is not None:
            if "msix_data" not in result or not result["msix_data"]:
                result["msix_data"] = self._create_msix_result(msix_data.msix_info)

            # Update template context if present
            if (
                "template_context" in result
                and "msix_config" in result["template_context"]
            ):
                result["template_context"]["msix_config"].update(
                    {
                        "is_supported": True,
                        "num_vectors": msix_data.msix_info["table_size"],
                    }
                )

    def _read_config_space(self, path: str) -> bytes:
        """
        Read PCI config space from sysfs.

        Args:
            path: Path to config space file

        Returns:
            Config space bytes

        Raises:
            IOError: If reading fails
        """
        with open(path, "rb") as f:
            return f.read()

    def _should_inject(self, msix_data: MSIXData) -> bool:
        """
        Check if MSI-X data should be injected.

        Args:
            msix_data: The MSI-X data to check

        Returns:
            True if data should be injected
        """
        return (
            msix_data.preloaded
            and msix_data.msix_info is not None
            and msix_data.msix_info.get("table_size", 0) > 0
        )

    def _create_msix_result(self, msix_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create MSI-X result dictionary from capability info.

        Args:
            msix_info: MSI-X capability information

        Returns:
            Formatted MSI-X result dictionary
        """
        return {
            "capability_info": msix_info,
            "table_size": msix_info["table_size"],
            "table_bir": msix_info["table_bir"],
            "table_offset": msix_info["table_offset"],
            "pba_bir": msix_info["pba_bir"],
            "pba_offset": msix_info["pba_offset"],
            "enabled": msix_info["enabled"],
            "function_mask": msix_info["function_mask"],
            "is_valid": True,
            "validation_errors": [],
        }


# ──────────────────────────────────────────────────────────────────────────────
# File Operations Manager
# ──────────────────────────────────────────────────────────────────────────────
class FileOperationsManager:
    """Manages file operations with optional parallel processing."""

    def __init__(
        self,
        output_dir: Path,
        parallel: bool = True,
        max_workers: int = MAX_PARALLEL_FILE_WRITES,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the file operations manager.

        Args:
            output_dir: Base output directory
            parallel: Enable parallel file writes
            max_workers: Maximum number of parallel workers
            logger: Optional logger instance
        """
        self.output_dir = output_dir
        self.parallel = parallel
        self.max_workers = max_workers
        self.logger = logger or get_logger(self.__class__.__name__)
        self._ensure_output_dir()

    def write_systemverilog_modules(
        self, modules: Dict[str, str]
    ) -> Tuple[List[str], List[str]]:
        """
        Write SystemVerilog modules to disk with proper file extensions.
        COE files are excluded from this method to prevent duplication.

        Args:
            modules: Dictionary of module names to content

        Returns:
            Tuple of (sv_files, special_files) lists

        Raises:
            FileOperationError: If writing fails
        """
        sv_dir = self.output_dir / "src"
        sv_dir.mkdir(exist_ok=True)

        # Prepare file write tasks
        write_tasks = []
        sv_files = []
        special_files = []

        for name, content in modules.items():
            # Skip COE files to prevent duplication
            # COE files are handled separately and saved to systemverilog directory
            if name.endswith(".coe"):
                continue

            file_path, category = self._determine_file_path(name, sv_dir)

            if category == "sv":
                sv_files.append(file_path.name)
            else:
                special_files.append(file_path.name)

            write_tasks.append((file_path, content))

        # Execute writes
        if self.parallel and len(write_tasks) > 1:
            self._parallel_write(write_tasks)
        else:
            self._sequential_write(write_tasks)

        return sv_files, special_files

    def write_json(self, filename: str, data: Any, indent: int = 2) -> None:
        """
        Write JSON data to a file.

        Args:
            filename: Name of the file (relative to output_dir)
            data: Data to serialize to JSON
            indent: JSON indentation level

        Raises:
            FileOperationError: If writing fails
        """
        file_path = self.output_dir / filename
        try:
            with open(file_path, "w", buffering=BUFFER_SIZE) as f:
                json.dump(data, f, indent=indent, default=self._json_serialize_default)
        except Exception as e:
            raise FileOperationError(
                f"Failed to write JSON file {filename}: {e}"
            ) from e

    def write_text(self, filename: str, content: str) -> None:
        """
        Write text content to a file.

        Args:
            filename: Name of the file (relative to output_dir)
            content: Text content to write

        Raises:
            FileOperationError: If writing fails
        """
        file_path = self.output_dir / filename
        try:
            with open(file_path, "w", buffering=BUFFER_SIZE) as f:
                f.write(content)
        except Exception as e:
            raise FileOperationError(
                f"Failed to write text file {filename}: {e}"
            ) from e

    def list_artifacts(self) -> List[str]:
        """
        List all file artifacts in the output directory.

        Returns:
            List of relative file paths
        """
        return [
            str(p.relative_to(self.output_dir))
            for p in self.output_dir.rglob("*")
            if p.is_file()
        ]

    def _ensure_output_dir(self) -> None:
        """Ensure the output directory exists."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _determine_file_path(self, name: str, base_dir: Path) -> Tuple[Path, str]:
        """
        Determine the file path and category for a module.

        Args:
            name: Module name
            base_dir: Base directory for the file

        Returns:
            Tuple of (file_path, category_label)
        """
        # Check if it's a special file type
        if any(name.endswith(ext) for ext in SPECIAL_FILE_EXTENSIONS):
            return base_dir / name, "special"

        # SystemVerilog files
        if name.endswith(SYSTEMVERILOG_EXTENSION):
            return base_dir / name, "sv"
        else:
            return base_dir / f"{name}{SYSTEMVERILOG_EXTENSION}", "sv"

    def _parallel_write(self, write_tasks: List[Tuple[Path, str]]) -> None:
        """
        Write files in parallel.

        Args:
            write_tasks: List of (path, content) tuples

        Raises:
            FileOperationError: If any write fails
        """
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._write_single_file, path, content): path
                for path, content in write_tasks
            }

            for future in as_completed(futures, timeout=FILE_WRITE_TIMEOUT):
                path = futures[future]
                try:
                    future.result()
                except Exception as e:
                    raise FileOperationError(f"Failed to write file {path}: {e}") from e

    def _sequential_write(self, write_tasks: List[Tuple[Path, str]]) -> None:
        """
        Write files sequentially.

        Args:
            write_tasks: List of (path, content) tuples

        Raises:
            FileOperationError: If any write fails
        """
        for path, content in write_tasks:
            try:
                self._write_single_file(path, content)
            except Exception as e:
                raise FileOperationError(f"Failed to write file {path}: {e}") from e

    def _write_single_file(self, path: Path, content: str) -> None:
        """
        Write a single file.

        Args:
            path: File path
            content: File content
        """
        with open(path, "w", buffering=BUFFER_SIZE) as f:
            f.write(content)

    def _json_serialize_default(self, obj: Any) -> str:
        """Default JSON serialization function for complex objects."""
        return obj.__dict__ if hasattr(obj, "__dict__") else str(obj)


# ──────────────────────────────────────────────────────────────────────────────
# Configuration Manager
# ──────────────────────────────────────────────────────────────────────────────
class ConfigurationManager:
    """Manages build configuration and validation."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the configuration manager.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or get_logger(self.__class__.__name__)

    def create_from_args(self, args: argparse.Namespace) -> BuildConfiguration:
        """
        Create build configuration from command line arguments.

        Args:
            args: Parsed command line arguments

        Returns:
            BuildConfiguration instance

        Raises:
            ConfigurationError: If configuration is invalid
        """
        self._validate_args(args)

        return BuildConfiguration(
            bdf=args.bdf,
            board=args.board,
            output_dir=Path(args.output).resolve(),
            enable_profiling=args.profile > 0,
            preload_msix=getattr(args, "preload_msix", True),
            profile_duration=args.profile,
            output_template=getattr(args, "output_template", None),
            donor_template=getattr(args, "donor_template", None),
        )

    def extract_device_config(
        self, template_context: Dict[str, Any], msix_data: Dict[str, Any]
    ) -> DeviceConfiguration:
        """
        Extract device configuration from build results.

        Args:
            template_context: Template context from generation
            msix_data: MSI-X data from generation

        Returns:
            DeviceConfiguration instance
        """
        device_config = template_context["device_config"]
        pcie_config = template_context.get("pcie_config", {})

        return DeviceConfiguration(
            vendor_id=device_config["vendor_id"],
            device_id=device_config["device_id"],
            revision_id=device_config["revision_id"],
            class_code=device_config["class_code"],
            requires_msix=bool(msix_data.get("is_valid", False)),
            pcie_lanes=pcie_config.get("max_lanes", 1),
        )

    def _validate_args(self, args: argparse.Namespace) -> None:
        """
        Validate command line arguments.

        Args:
            args: Arguments to validate

        Raises:
            ConfigurationError: If validation fails
        """
        # Validate BDF format
        if not self._is_valid_bdf(args.bdf):
            raise ConfigurationError(
                f"Invalid BDF format: {args.bdf}. "
                "Expected format: XXXX:XX:XX.X (e.g., 0000:03:00.0)"
            )

        # Validate profile duration
        if args.profile < 0:
            raise ConfigurationError(
                f"Invalid profile duration: {args.profile}. Must be >= 0"
            )

    def _is_valid_bdf(self, bdf: str) -> bool:
        """
        Check if BDF string is valid.

        Args:
            bdf: BDF string to validate

        Returns:
            True if valid
        """
        pattern = r"^[0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-9a-fA-F]$"
        return bool(re.match(pattern, bdf))


# ──────────────────────────────────────────────────────────────────────────────
# Main Firmware Builder (Refactored)
# ──────────────────────────────────────────────────────────────────────────────
class FirmwareBuilder:
    """
    Refactored firmware builder with modular architecture.

    This class orchestrates the firmware generation process using
    dedicated manager classes for different responsibilities.
    """

    def __init__(
        self,
        config: BuildConfiguration,
        msix_manager: Optional[MSIXManager] = None,
        file_manager: Optional[FileOperationsManager] = None,
        config_manager: Optional[ConfigurationManager] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the firmware builder with dependency injection.

        Args:
            config: Build configuration
            msix_manager: Optional MSI-X manager (creates default if None)
            file_manager: Optional file operations manager (creates default if None)
            config_manager: Optional configuration manager (creates default if None)
            logger: Optional logger instance
        """
        self.config = config
        self.logger = logger or get_logger(self.__class__.__name__)

        # Initialize managers (dependency injection with defaults)
        self.msix_manager = msix_manager or MSIXManager(config.bdf, self.logger)
        self.file_manager = file_manager or FileOperationsManager(
            config.output_dir,
            parallel=config.parallel_writes,
            max_workers=config.max_workers,
            logger=self.logger,
        )
        self.config_manager = config_manager or ConfigurationManager(self.logger)

        # Initialize generator and other components
        self._init_components()

        # Store device configuration for later use
        self._device_config: Optional[DeviceConfiguration] = None

    def build(self) -> List[str]:
        """
        Run the full firmware generation flow.

        Returns:
            List of generated artifact paths (relative to output directory)

        Raises:
            PCILeechBuildError: If build fails
        """
        try:
            # Step 1: Load donor template if provided
            donor_template = self._load_donor_template()

            # Step 2: Preload MSI-X data if requested
            msix_data = self._preload_msix()

            # Step 3: Generate PCILeech firmware
            self.logger.info("➤ Generating PCILeech firmware …")
            generation_result = self._generate_firmware(donor_template)

            # Step 3: Inject preloaded MSI-X data if available
            self._inject_msix(generation_result, msix_data)

            # Step 4: Write SystemVerilog modules
            self._write_modules(generation_result)

            # Step 5: Generate behavior profile if requested
            self._generate_profile()

            # Step 6: Generate TCL scripts
            self._generate_tcl_scripts(generation_result)

            # Step 7: Save device information
            self._save_device_info(generation_result)

            # Step 8: Store device configuration
            self._store_device_config(generation_result)

            # Step 9: Generate donor template if requested
            if self.config.output_template:
                self._generate_donor_template(generation_result)

            # Return list of artifacts
            return self.file_manager.list_artifacts()

        except PlatformCompatibilityError:
            # For platform compatibility issues, don't log additional error messages
            # The original detailed error was already logged
            raise
        except Exception as e:
            self.logger.error("Build failed: %s", str(e))
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug("Full traceback:", exc_info=True)
            raise

    def run_vivado(self) -> None:
        """
        Hand-off to Vivado in batch mode using the generated scripts.

        Raises:
            VivadoIntegrationError: If Vivado integration fails
        """
        try:
            from src.vivado_handling import (
                find_vivado_installation,
                integrate_pcileech_build,
                run_vivado_with_error_reporting,
            )
        except ImportError as e:
            raise VivadoIntegrationError("Vivado handling modules not available") from e

        vivado = find_vivado_installation()
        if not vivado:
            raise VivadoIntegrationError("Vivado not found in PATH")

        try:
            # Use integrated build if available
            build_script = integrate_pcileech_build(
                self.config.board,
                self.config.output_dir,
                device_config=(
                    self._device_config.__dict__ if self._device_config else None
                ),
            )
            self.logger.info(f"Using integrated build script: {build_script}")
            build_tcl = build_script
        except Exception as e:
            self.logger.warning(
                f"Failed to use integrated build, falling back to generated scripts: {e}"
            )
            build_tcl = self.config.output_dir / "vivado_build.tcl"

        rc, rpt = run_vivado_with_error_reporting(
            build_tcl, self.config.output_dir, vivado["executable"]
        )
        if rc:
            raise VivadoIntegrationError(f"Vivado failed - see {rpt}")

        self.logger.info("Vivado implementation finished successfully ✓")

    # ────────────────────────────────────────────────────────────────────────
    # Private methods - initialization
    # ────────────────────────────────────────────────────────────────────────
    def _init_components(self) -> None:
        """Initialize PCILeech generator and other components."""
        from src.device_clone.behavior_profiler import BehaviorProfiler
        from src.device_clone.board_config import get_pcileech_board_config
        from src.device_clone.pcileech_generator import (
            PCILeechGenerationConfig,
            PCILeechGenerator,
        )
        from src.templating.tcl_builder import BuildContext, TCLBuilder

        self.gen = PCILeechGenerator(
            PCILeechGenerationConfig(
                device_bdf=self.config.bdf,
                template_dir=None,
                output_dir=self.config.output_dir,
                enable_behavior_profiling=self.config.enable_profiling,
            )
        )

        self.tcl = TCLBuilder(output_dir=self.config.output_dir)
        self.profiler = BehaviorProfiler(bdf=self.config.bdf)

    # ────────────────────────────────────────────────────────────────────────
    # Private methods - build steps
    # ────────────────────────────────────────────────────────────────────────
    def _load_donor_template(self) -> Optional[Dict[str, Any]]:
        """Load donor template if provided."""
        if self.config.donor_template:
            from src.device_clone.donor_info_template import DonorInfoTemplateGenerator

            self.logger.info(
                f"Loading donor template from: {self.config.donor_template}"
            )
            try:
                template = DonorInfoTemplateGenerator.load_template(
                    self.config.donor_template
                )
                self.logger.info("✓ Donor template loaded successfully")
                return template
            except Exception as e:
                self.logger.error(f"Failed to load donor template: {e}")
                raise PCILeechBuildError(f"Failed to load donor template: {e}")
        return None

    def _preload_msix(self) -> MSIXData:
        """Preload MSI-X data if configured."""
        if self.config.preload_msix:
            return self.msix_manager.preload_data()
        return MSIXData(preloaded=False)

    def _generate_firmware(
        self, donor_template: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate PCILeech firmware with optional donor template."""
        if donor_template:
            # Pass the donor template to the generator config
            self.gen.config.donor_template = donor_template
        return self.gen.generate_pcileech_firmware()

    def _inject_msix(self, result: Dict[str, Any], msix_data: MSIXData) -> None:
        """Inject MSI-X data into generation result."""
        self.msix_manager.inject_data(result, msix_data)

    def _write_modules(self, result: Dict[str, Any]) -> None:
        """Write SystemVerilog modules to disk."""
        sv_files, special_files = self.file_manager.write_systemverilog_modules(
            result["systemverilog_modules"]
        )

        self.logger.info(
            "  • Wrote %d SystemVerilog modules: %s", len(sv_files), ", ".join(sv_files)
        )
        if special_files:
            self.logger.info(
                "  • Wrote %d special files: %s",
                len(special_files),
                ", ".join(special_files),
            )

    def _generate_profile(self) -> None:
        """Generate behavior profile if configured."""
        if self.config.profile_duration > 0:
            profile = self.profiler.capture_behavior_profile(
                duration=self.config.profile_duration
            )
            self.file_manager.write_json("behavior_profile.json", profile)
            self.logger.info("  • Saved behavior profile → behavior_profile.json")

    def _generate_tcl_scripts(self, result: Dict[str, Any]) -> None:
        """Generate TCL scripts for Vivado."""
        ctx = result["template_context"]
        device_config = ctx["device_config"]

        # Extract subsystem IDs from template context
        subsys_vendor_id = device_config.get("subsystem_vendor_id")
        subsys_device_id = device_config.get("subsystem_device_id")

        # Convert hex strings to integers if needed
        if isinstance(subsys_vendor_id, str) and subsys_vendor_id.startswith("0x"):
            subsys_vendor_id = int(subsys_vendor_id, 16)
        elif isinstance(subsys_vendor_id, str):
            subsys_vendor_id = int(subsys_vendor_id, 16)

        if isinstance(subsys_device_id, str) and subsys_device_id.startswith("0x"):
            subsys_device_id = int(subsys_device_id, 16)
        elif isinstance(subsys_device_id, str):
            subsys_device_id = int(subsys_device_id, 16)

        self.tcl.build_all_tcl_scripts(
            board=self.config.board,
            device_id=device_config["device_id"],
            class_code=device_config["class_code"],
            revision_id=device_config["revision_id"],
            vendor_id=device_config["vendor_id"],
            subsys_vendor_id=subsys_vendor_id,
            subsys_device_id=subsys_device_id,
        )

        self.logger.info(
            "  • Emitted Vivado scripts → vivado_project.tcl, vivado_build.tcl"
        )

    def _save_device_info(self, result: Dict[str, Any]) -> None:
        """Save device information for auditing."""
        device_info = result["config_space_data"].get("device_info", {})
        self.file_manager.write_json("device_info.json", device_info)

    def _store_device_config(self, result: Dict[str, Any]) -> None:
        """Store device configuration for Vivado integration."""
        ctx = result["template_context"]
        msix_data = result.get("msix_data", {})

        self._device_config = self.config_manager.extract_device_config(ctx, msix_data)

    def _generate_donor_template(self, result: Dict[str, Any]) -> None:
        """Generate and save donor info template if requested."""
        from src.device_clone.donor_info_template import DonorInfoTemplateGenerator

        # Get device info from the result
        device_info = result.get("config_space_data", {}).get("device_info", {})
        template_context = result.get("template_context", {})
        device_config = template_context.get("device_config", {})

        # Create a pre-filled template
        generator = DonorInfoTemplateGenerator()
        template = generator.generate_blank_template()

        # Pre-fill with available device information
        if device_config:
            ident = template["device_info"]["identification"]
            ident["vendor_id"] = device_config.get("vendor_id")
            ident["device_id"] = device_config.get("device_id")
            ident["subsystem_vendor_id"] = device_config.get("subsystem_vendor_id")
            ident["subsystem_device_id"] = device_config.get("subsystem_device_id")
            ident["class_code"] = device_config.get("class_code")
            ident["revision_id"] = device_config.get("revision_id")

        # Add BDF if available
        template["metadata"]["device_bdf"] = self.config.bdf

        # Save the template
        if self.config.output_template:
            output_path = Path(self.config.output_template)
            if not output_path.is_absolute():
                output_path = self.config.output_dir / output_path

            generator.save_template_dict(template, output_path, pretty=True)
            self.logger.info(f"  • Generated donor info template → {output_path.name}")


# ──────────────────────────────────────────────────────────────────────────────
# CLI Functions
# ──────────────────────────────────────────────────────────────────────────────
def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command line arguments.

    Args:
        argv: Command line arguments (uses sys.argv if None)

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="PCILeech FPGA Firmware Builder - Improved Modular Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic build
  %(prog)s --bdf 0000:03:00.0 --board pcileech_35t325_x4
  
  # Build with Vivado integration
  %(prog)s --bdf 0000:03:00.0 --board pcileech_35t325_x4 --vivado
  
  # Build with behavior profiling
  %(prog)s --bdf 0000:03:00.0 --board pcileech_35t325_x4 --profile 60
  
  # Build without MSI-X preloading
  %(prog)s --bdf 0000:03:00.0 --board pcileech_35t325_x4 --no-preload-msix
        """,
    )

    parser.add_argument(
        "--bdf",
        required=True,
        help="PCI Bus/Device/Function address (e.g., 0000:03:00.0)",
    )
    parser.add_argument(
        "--board",
        required=True,
        help="Target FPGA board key (e.g., pcileech_35t325_x4)",
    )
    parser.add_argument(
        "--profile",
        type=int,
        default=DEFAULT_PROFILE_DURATION,
        metavar="SECONDS",
        help=f"Capture behavior profile for N seconds (default: {DEFAULT_PROFILE_DURATION}, 0 to disable)",
    )
    parser.add_argument(
        "--vivado", action="store_true", help="Run Vivado build after generation"
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--no-preload-msix",
        action="store_false",
        dest="preload_msix",
        default=True,
        help="Disable preloading of MSI-X data before VFIO binding",
    )
    parser.add_argument(
        "--output-template",
        help="Output donor info JSON template alongside build artifacts",
    )
    parser.add_argument(
        "--donor-template",
        help="Use donor info JSON template to override discovered values",
    )

    return parser.parse_args(argv)


# ──────────────────────────────────────────────────────────────────────────────
# Main Entry Point
# ──────────────────────────────────────────────────────────────────────────────
def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for the PCILeech firmware builder.

    This function orchestrates the entire build process:
    1. Validates required modules
    2. Parses command line arguments
    3. Creates build configuration
    4. Runs the firmware build
    5. Optionally runs Vivado

    Args:
        argv: Command line arguments (uses sys.argv if None)

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Setup logging if not already configured
    if not logging.getLogger().handlers:
        setup_logging(level=logging.INFO)

    logger = get_logger("pcileech_builder")

    try:
        # Check required modules
        module_checker = ModuleChecker(REQUIRED_MODULES)
        module_checker.check_all()

        # Parse arguments
        args = parse_args(argv)

        # Create configuration
        config_manager = ConfigurationManager(logger)
        config = config_manager.create_from_args(args)

        # Time the build
        start_time = time.perf_counter()

        # Create and run builder
        builder = FirmwareBuilder(config, logger=logger)
        artifacts = builder.build()

        # Calculate elapsed time
        elapsed_time = time.perf_counter() - start_time
        logger.info("Build finished in %.1f s ✓", elapsed_time)

        # Run Vivado if requested
        if args.vivado:
            builder.run_vivado()

        # Display summary
        _display_summary(artifacts, config.output_dir)

        return 0

    except ModuleImportError as e:
        # Module import errors are fatal and should show diagnostics
        print(f"[FATAL] {e}", file=sys.stderr)
        return 2

    except PlatformCompatibilityError as e:
        # Platform compatibility errors - log once at info level since details were already logged
        logger.info("Build skipped due to platform compatibility: %s", e)
        return 1

    except ConfigurationError as e:
        # Configuration errors indicate user error
        logger.error("Configuration error: %s", e)
        return 1

    except PCILeechBuildError as e:
        # Known build errors
        logger.error("Build failed: %s", e)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Full traceback:", exc_info=True)
        return 1

    except KeyboardInterrupt:
        # User interrupted
        logger.warning("Build interrupted by user")
        return 130

    except Exception as e:
        # Check if this is a platform compatibility error
        error_str = str(e)
        if (
            "requires Linux" in error_str
            or "platform incompatibility" in error_str
            or "only available on Linux" in error_str
        ):
            # Platform compatibility errors were already logged in detail
            logger.info(
                "Build skipped due to platform compatibility (see details above)"
            )
        else:
            # Unexpected errors
            logger.error("Unexpected error: %s", e)
            logger.debug("Full traceback:", exc_info=True)
        return 1


def _display_summary(artifacts: List[str], output_dir: Path) -> None:
    """
    Display a summary of generated artifacts.

    Args:
        artifacts: List of artifact paths
        output_dir: Output directory path
    """
    print(f"\nGenerated artifacts in {output_dir}:")

    # Group artifacts by type
    sv_files = [a for a in artifacts if a.endswith(".sv")]
    tcl_files = [a for a in artifacts if a.endswith(".tcl")]
    json_files = [a for a in artifacts if a.endswith(".json")]
    other_files = [a for a in artifacts if a not in sv_files + tcl_files + json_files]

    if sv_files:
        print(f"\n  SystemVerilog modules ({len(sv_files)}):")
        for f in sorted(sv_files):
            print(f"    - {f}")

    if tcl_files:
        print(f"\n  TCL scripts ({len(tcl_files)}):")
        for f in sorted(tcl_files):
            print(f"    - {f}")

    if json_files:
        print(f"\n  JSON files ({len(json_files)}):")
        for f in sorted(json_files):
            print(f"    - {f}")

    if other_files:
        print(f"\n  Other files ({len(other_files)}):")
        for f in sorted(other_files):
            print(f"    - {f}")

    print(f"\nTotal: {len(artifacts)} files")


# ──────────────────────────────────────────────────────────────────────────────
# Script Entry Point
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sys.exit(main())
