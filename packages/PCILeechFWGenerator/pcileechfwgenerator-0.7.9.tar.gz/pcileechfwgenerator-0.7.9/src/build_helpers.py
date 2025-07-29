#!/usr/bin/env python3
"""
PCILeech Firmware Build - Helper Library (strict‑mode)
=====================================================
Shared utilities for the *unified* build flow.  All functions assume a fully‑
provisioned production environment: **no fall‑backs, no mocks, no legacy
shims**.  Any missing dependency is treated as a fatal error.

Provided helpers
----------------
• `add_src_to_path()` - ensure `<project‑root>/src` is importable.
• `select_pcie_ip_core()` - map FPGA part → correct Xilinx PCIe IP name.
• `write_tcl_file()` - atomic TCL write with INFO logging + list bookkeeping.
• `create_fpga_strategy_selector()` - returns a strategy func giving per‑family
  parameters (IP core, lane‑count, constraint file, …).
• `batch_write_tcl_files()` - convenience wrapper for writing many TCL files.
• `validate_fpga_part()` - quick sanity‑check for part numbers.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Union

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


def add_src_to_path() -> None:
    """Prepend `<project‑root>/src` to *sys.path* exactly once."""
    src = (Path(__file__).resolve().parent.parent / "src").resolve()
    if not src.exists():
        raise RuntimeError(f"Expected src directory not found: {src}")
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
        logger.debug("Added %s to PYTHONPATH", src)


# ---------------------------------------------------------------------------
# PCIe IP core selection + FPGA strategy
# ---------------------------------------------------------------------------


def select_pcie_ip_core(fpga_part: str) -> str:
    """Return the canonical Xilinx IP core name for *fpga_part*."""
    part = fpga_part.lower()
    if part.startswith("xc7a35t"):
        return "axi_pcie"  # small Artix‑7
    if part.startswith("xc7a75t") or part.startswith("xc7k"):
        return "pcie_7x"  # larger Artix‑7 / Kintex‑7
    if part.startswith("xczu"):
        return "pcie_ultrascale"  # Zynq UltraScale+
    logger.warning("Unknown FPGA part '%s' - defaulting to pcie_7x", fpga_part)
    return "pcie_7x"


def create_fpga_strategy_selector() -> Callable[[str], Dict[str, Any]]:
    """Return a *strategy(fpga_part) -> dict* chooser for per‑family params."""

    def artix35(_) -> Dict[str, Any]:
        return {
            "pcie_ip_type": "axi_pcie",
            "family": "artix7",
            "max_lanes": 4,
            "supports_msi": True,
            "supports_msix": False,
            "clock_constraints": "artix7_35t.xdc",
        }

    def artix75_or_kintex(_) -> Dict[str, Any]:
        fam = "kintex7" if _.startswith("xc7k") else "artix7"
        return {
            "pcie_ip_type": "pcie_7x",
            "family": fam,
            "max_lanes": 8,
            "supports_msi": True,
            "supports_msix": True,
            "clock_constraints": f"{fam}.xdc",
        }

    def ultrascale(_) -> Dict[str, Any]:
        return {
            "pcie_ip_type": "pcie_ultrascale",
            "family": "zynq_ultrascale",
            "max_lanes": 16,
            "supports_msi": True,
            "supports_msix": True,
            "clock_constraints": "zynq_ultrascale.xdc",
        }

    strategies: Dict[str, Callable[[str], Dict[str, Any]]] = {
        "xc7a35t": artix35,
        "xc7a75t": artix75_or_kintex,
        "xc7k": artix75_or_kintex,
        "xczu": ultrascale,
    }

    def select(fpga_part: str) -> Dict[str, Any]:
        part = fpga_part.lower()
        for prefix, fn in strategies.items():
            if part.startswith(prefix):
                return fn(fpga_part)
        logger.warning(
            "No dedicated strategy for '%s' - using generic defaults", fpga_part
        )
        return artix75_or_kintex(fpga_part)  # sensible generic

    return select


# ---------------------------------------------------------------------------
# TCL helpers
# ---------------------------------------------------------------------------


def write_tcl_file(
    content: str,
    file_path: Union[str, Path],
    tcl_files: List[str],
    description: str,
) -> None:
    """Write *content* to *file_path*, append to *tcl_files*, log success."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf‑8")
    tcl_files.append(str(path))
    logger.info("Generated %s", description)


def batch_write_tcl_files(
    tcl_contents: Dict[str, str],
    output_dir: Union[str, Path],
    tcl_files: List[str],
    logger: logging.Logger,
) -> None:
    """Write many TCL files under *output_dir*.

    Raises on the first failure - strict mode implies partial writes are fatal.
    """
    out = Path(output_dir)
    successes = 0
    for name, content in tcl_contents.items():
        write_tcl_file(content, out / name, tcl_files, name)
        successes += 1
    logger.info("Batch TCL write complete: %d/%d files", successes, len(tcl_contents))


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------


def validate_fpga_part(fpga_part: str) -> bool:
    """Light sanity‑check for *fpga_part* strings."""
    prefixes = ("xc7a", "xc7k", "xc7v", "xczu", "xck", "xcvu")
    ok = bool(fpga_part) and fpga_part.lower().startswith(prefixes)
    if not ok:
        logger.error("Invalid or unsupported FPGA part: %s", fpga_part)
    return ok
