#!/usr/bin/env python3
"""
PCILeech Overlay RAM Mapper

This module automatically detects which PCI configuration space registers need
overlay RAM entries and generates the OVERLAY_MAP for the cfg_shadow.sv template.

Overlay RAM is used for registers that have special write behavior:
- Partially writable registers (some bits RW, others RO)
- Write-1-to-clear (RW1C) bits
- Registers with complex write masks
"""

import logging
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Dict, List, Optional, Set, Tuple

from ..pci_capability.constants import (
    EXTENDED_CAPABILITY_NAMES,
    PCI_CAPABILITIES_POINTER,
    PCI_DEVICE_ID_OFFSET,
    PCI_STATUS_REGISTER,
    PCI_VENDOR_ID_OFFSET,
    STANDARD_CAPABILITY_NAMES,
)

logger = logging.getLogger(__name__)


class RegisterType(IntEnum):
    """Types of register write behavior."""

    READ_ONLY = 0  # All bits read-only
    READ_WRITE = 1  # All bits read-write
    MIXED = 2  # Some bits RW, others RO
    RW1C = 3  # Write-1-to-clear bits
    SPECIAL = 4  # Special handling required


@dataclass
class OverlayEntry:
    """Represents an overlay RAM entry."""

    offset: int  # Register offset in config space
    mask: int  # Write mask (1 = writable, 0 = read-only)
    description: str  # Human-readable description
    register_type: RegisterType


class PCIeRegisterDefinitions:
    """PCIe register definitions based on PCIe specifications."""

    # Standard PCI Configuration Space Registers (0x00-0x3F)
    STANDARD_REGISTERS = {
        0x00: OverlayEntry(
            0x00, 0x00000000, "Vendor ID / Device ID", RegisterType.READ_ONLY
        ),
        0x04: OverlayEntry(0x04, 0x0000FBF9, "Command / Status", RegisterType.MIXED),
        0x08: OverlayEntry(
            0x08, 0x00000000, "Revision ID / Class Code", RegisterType.READ_ONLY
        ),
        0x0C: OverlayEntry(
            0x0C, 0x0000FF00, "Cache Line / Latency / Header / BIST", RegisterType.MIXED
        ),
        0x10: OverlayEntry(
            0x10, 0xFFFFFFFF, "BAR0", RegisterType.SPECIAL
        ),  # Size detection
        0x14: OverlayEntry(0x14, 0xFFFFFFFF, "BAR1", RegisterType.SPECIAL),
        0x18: OverlayEntry(0x18, 0xFFFFFFFF, "BAR2", RegisterType.SPECIAL),
        0x1C: OverlayEntry(0x1C, 0xFFFFFFFF, "BAR3", RegisterType.SPECIAL),
        0x20: OverlayEntry(0x20, 0xFFFFFFFF, "BAR4", RegisterType.SPECIAL),
        0x24: OverlayEntry(0x24, 0xFFFFFFFF, "BAR5", RegisterType.SPECIAL),
        0x28: OverlayEntry(
            0x28, 0x00000000, "Cardbus CIS Pointer", RegisterType.READ_ONLY
        ),
        0x2C: OverlayEntry(
            0x2C,
            0x00000000,
            "Subsystem Vendor ID / Subsystem ID",
            RegisterType.READ_ONLY,
        ),
        0x30: OverlayEntry(
            0x30, 0xFFFFF800, "Expansion ROM Base Address", RegisterType.MIXED
        ),
        0x34: OverlayEntry(
            0x34, 0x00000000, "Capabilities Pointer", RegisterType.READ_ONLY
        ),
        0x38: OverlayEntry(0x38, 0x00000000, "Reserved", RegisterType.READ_ONLY),
        0x3C: OverlayEntry(
            0x3C,
            0x000000FF,
            "Interrupt Line / Pin / Min Grant / Max Latency",
            RegisterType.MIXED,
        ),
    }

    # Command Register (0x04) bit definitions
    COMMAND_REGISTER_BITS = {
        0: ("IO Space Enable", True),
        1: ("Memory Space Enable", True),
        2: ("Bus Master Enable", True),
        3: ("Special Cycles", False),
        4: ("Memory Write and Invalidate", True),
        5: ("VGA Palette Snoop", False),
        6: ("Parity Error Response", True),
        7: ("Reserved", False),
        8: ("SERR# Enable", True),
        9: ("Fast Back-to-Back Enable", False),
        10: ("Interrupt Disable", True),
        # Bits 11-15 are reserved
    }

    # Status Register (0x06) bit definitions - many are RW1C
    STATUS_REGISTER_BITS = {
        0: ("Reserved", False, False),
        1: ("Reserved", False, False),
        2: ("Reserved", False, False),
        3: ("Interrupt Status", False, False),  # RO
        4: ("Capabilities List", False, False),  # RO
        5: ("66 MHz Capable", False, False),  # RO
        6: ("Reserved", False, False),
        7: ("Fast Back-to-Back Capable", False, False),  # RO
        8: ("Master Data Parity Error", True, True),  # RW1C
        9: ("DEVSEL Timing", False, False),  # RO
        10: ("DEVSEL Timing", False, False),  # RO
        11: ("Signaled Target Abort", True, True),  # RW1C
        12: ("Received Target Abort", True, True),  # RW1C
        13: ("Received Master Abort", True, True),  # RW1C
        14: ("Signaled System Error", True, True),  # RW1C
        15: ("Detected Parity Error", True, True),  # RW1C
    }

    # Generate Status register mask from bit definitions
    @classmethod
    def get_status_mask(cls) -> int:
        """Generate status register mask from bit definitions."""
        mask = 0
        for bit, (_, writable, rw1c) in cls.STATUS_REGISTER_BITS.items():
            if (writable or rw1c) and bit < 16:
                mask |= 1 << bit
        return mask

    # Power Management Capability Registers
    PM_CAPABILITY_REGISTERS = {
        0x00: OverlayEntry(
            0x00,
            0x00000000,
            "PM Cap ID / Next Ptr / PM Capabilities",
            RegisterType.READ_ONLY,
        ),
        0x04: OverlayEntry(
            0x04, 0x0000FF03, "PMCSR / PMCSR_BSE / Data", RegisterType.MIXED
        ),
    }

    # MSI Capability Registers
    MSI_CAPABILITY_REGISTERS = {
        0x00: OverlayEntry(
            0x00,
            0x00710000,
            "MSI Cap ID / Next Ptr / Message Control",
            RegisterType.MIXED,
        ),
        0x04: OverlayEntry(0x04, 0xFFFFFFFC, "Message Address Low", RegisterType.MIXED),
        0x08: OverlayEntry(
            0x08, 0xFFFFFFFF, "Message Address High (64-bit)", RegisterType.READ_WRITE
        ),
        0x0C: OverlayEntry(0x0C, 0x0000FFFF, "Message Data", RegisterType.READ_WRITE),
    }

    # MSI-X Capability Registers
    MSIX_CAPABILITY_REGISTERS = {
        0x00: OverlayEntry(
            0x00,
            0xC0000000,
            "MSI-X Cap ID / Next Ptr / Message Control",
            RegisterType.MIXED,
        ),
        0x04: OverlayEntry(
            0x04, 0x00000000, "Table Offset / BIR", RegisterType.READ_ONLY
        ),
        0x08: OverlayEntry(
            0x08, 0x00000000, "PBA Offset / BIR", RegisterType.READ_ONLY
        ),
    }

    # PCIe Capability Registers (partial list of key registers)
    PCIE_CAPABILITY_REGISTERS = {
        0x00: OverlayEntry(
            0x00,
            0x00000000,
            "PCIe Cap ID / Next Ptr / PCIe Capabilities",
            RegisterType.READ_ONLY,
        ),
        0x04: OverlayEntry(
            0x04, 0x00000000, "Device Capabilities", RegisterType.READ_ONLY
        ),
        0x08: OverlayEntry(
            0x08, 0x00002FEF, "Device Control / Device Status", RegisterType.MIXED
        ),
        0x0C: OverlayEntry(
            0x0C, 0x00000000, "Link Capabilities", RegisterType.READ_ONLY
        ),
        0x10: OverlayEntry(
            0x10, 0x0000F41F, "Link Control / Link Status", RegisterType.MIXED
        ),
        0x14: OverlayEntry(
            0x14, 0x00000000, "Slot Capabilities", RegisterType.READ_ONLY
        ),
        0x18: OverlayEntry(
            0x18, 0x000007FF, "Slot Control / Slot Status", RegisterType.MIXED
        ),
        0x1C: OverlayEntry(
            0x1C, 0x00000000, "Root Capabilities", RegisterType.READ_ONLY
        ),
        0x20: OverlayEntry(
            0x20, 0x0000001F, "Root Control / Root Status", RegisterType.MIXED
        ),
        0x24: OverlayEntry(
            0x24, 0x00000000, "Device Capabilities 2", RegisterType.READ_ONLY
        ),
        0x28: OverlayEntry(
            0x28, 0x0000741F, "Device Control 2 / Device Status 2", RegisterType.MIXED
        ),
    }

    # AER Extended Capability Registers
    AER_CAPABILITY_REGISTERS = {
        0x00: OverlayEntry(0x00, 0x00000000, "AER Cap Header", RegisterType.READ_ONLY),
        0x04: OverlayEntry(
            0x04, 0xFFFFFFFF, "Uncorrectable Error Status", RegisterType.RW1C
        ),
        0x08: OverlayEntry(
            0x08, 0x00462030, "Uncorrectable Error Mask", RegisterType.READ_WRITE
        ),
        0x0C: OverlayEntry(
            0x0C, 0x00462030, "Uncorrectable Error Severity", RegisterType.READ_WRITE
        ),
        0x10: OverlayEntry(
            0x10, 0xFFFFFFFF, "Correctable Error Status", RegisterType.RW1C
        ),
        0x14: OverlayEntry(
            0x14, 0x00003F01, "Correctable Error Mask", RegisterType.READ_WRITE
        ),
        0x18: OverlayEntry(
            0x18, 0x00000060, "AER Capabilities and Control", RegisterType.MIXED
        ),
        0x1C: OverlayEntry(0x1C, 0x00000000, "Header Log 1", RegisterType.READ_ONLY),
        0x20: OverlayEntry(0x20, 0x00000000, "Header Log 2", RegisterType.READ_ONLY),
        0x24: OverlayEntry(0x24, 0x00000000, "Header Log 3", RegisterType.READ_ONLY),
        0x28: OverlayEntry(0x28, 0x00000000, "Header Log 4", RegisterType.READ_ONLY),
    }


class OverlayMapper:
    """Generates overlay RAM mappings for PCIe configuration space."""

    def __init__(self):
        """Initialize the overlay mapper."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.definitions = PCIeRegisterDefinitions()

    def detect_overlay_registers(
        self, config_space: Dict[int, int], capabilities: Dict[str, int]
    ) -> List[Tuple[int, int]]:
        """
        Automatically detect which registers need overlay entries.

        Args:
            config_space: Configuration space dword map
            capabilities: Dictionary mapping capability ID to offset

        Returns:
            List of (offset, mask) tuples for OVERLAY_MAP
        """
        overlay_map = []
        processed_offsets = set()

        # Process standard PCI configuration space registers
        for offset, entry in self.definitions.STANDARD_REGISTERS.items():
            if entry.register_type in (
                RegisterType.MIXED,
                RegisterType.RW1C,
                RegisterType.SPECIAL,
            ):
                if offset not in processed_offsets:
                    # Special handling for BARs
                    if (
                        0x10 <= offset <= 0x24
                        and entry.register_type == RegisterType.SPECIAL
                    ):
                        mask = self._calculate_bar_mask(config_space, offset)
                    else:
                        mask = entry.mask

                    if (
                        mask != 0x00000000 and mask != 0xFFFFFFFF
                    ):  # Only add if partially writable
                        overlay_map.append((offset, mask))
                        processed_offsets.add(offset)
                        self.logger.debug(
                            f"Added overlay for {entry.description} at 0x{offset:03X} with mask 0x{mask:08X}"
                        )

        # Process capability-specific registers
        for cap_id, cap_offset in capabilities.items():
            overlay_entries = self._get_capability_overlay_entries(cap_id, cap_offset)
            for offset, mask, description in overlay_entries:
                if (
                    offset not in processed_offsets
                    and mask != 0x00000000
                    and mask != 0xFFFFFFFF
                ):
                    overlay_map.append((offset, mask))
                    processed_offsets.add(offset)
                    self.logger.debug(
                        f"Added overlay for {description} at 0x{offset:03X} with mask 0x{mask:08X}"
                    )

        # Sort by offset for consistent ordering
        overlay_map.sort(key=lambda x: x[0])

        return overlay_map

    def _calculate_bar_mask(self, config_space: Dict[int, int], offset: int) -> int:
        """
        Calculate the write mask for a BAR based on its size.

        Args:
            config_space: Configuration space dword map
            offset: BAR offset

        Returns:
            Write mask for the BAR
        """
        dword_idx = offset // 4
        bar_value = config_space.get(dword_idx, 0)

        # Check if this is an I/O BAR
        if bar_value & 0x1:
            # I/O BAR - bits [31:2] are address, bits [1:0] are flags
            return 0xFFFFFFFC
        else:
            # Memory BAR
            # Check if 64-bit BAR
            is_64bit = (bar_value & 0x6) == 0x4
            is_prefetchable = bool(bar_value & 0x8)

            # For memory BARs, the size bits are read-only
            # We need to determine the size to know which bits are writable
            # This is typically done by writing all 1s and reading back
            # For now, we'll use a conservative approach

            # Lower bits are read-only (size indication)
            # Upper bits are writable (base address)
            # Bits [3:0] are always read-only for memory BARs
            return 0xFFFFFFF0

    def _get_capability_overlay_entries(
        self, cap_id: str, cap_offset: int
    ) -> List[Tuple[int, int, str]]:
        """
        Get overlay entries for a specific capability.

        Args:
            cap_id: Capability ID (hex string)
            cap_offset: Offset of the capability in config space

        Returns:
            List of (offset, mask, description) tuples
        """
        entries = []

        # Convert cap_id to integer
        try:
            cap_id_int = int(cap_id, 16)
        except ValueError:
            return entries

        # Power Management
        if cap_id_int == 0x01:
            for rel_offset, entry in self.definitions.PM_CAPABILITY_REGISTERS.items():
                if entry.register_type in (RegisterType.MIXED, RegisterType.RW1C):
                    entries.append(
                        (cap_offset + rel_offset, entry.mask, entry.description)
                    )

        # MSI
        elif cap_id_int == 0x05:
            for rel_offset, entry in self.definitions.MSI_CAPABILITY_REGISTERS.items():
                if entry.register_type in (RegisterType.MIXED, RegisterType.RW1C):
                    entries.append(
                        (cap_offset + rel_offset, entry.mask, entry.description)
                    )

        # MSI-X
        elif cap_id_int == 0x11:
            for rel_offset, entry in self.definitions.MSIX_CAPABILITY_REGISTERS.items():
                if entry.register_type in (RegisterType.MIXED, RegisterType.RW1C):
                    entries.append(
                        (cap_offset + rel_offset, entry.mask, entry.description)
                    )

        # PCIe
        elif cap_id_int == 0x10:
            for rel_offset, entry in self.definitions.PCIE_CAPABILITY_REGISTERS.items():
                if entry.register_type in (RegisterType.MIXED, RegisterType.RW1C):
                    entries.append(
                        (cap_offset + rel_offset, entry.mask, entry.description)
                    )

        # AER (Extended capability)
        elif cap_id == "0x0001":
            for rel_offset, entry in self.definitions.AER_CAPABILITY_REGISTERS.items():
                if entry.register_type in (RegisterType.MIXED, RegisterType.RW1C):
                    entries.append(
                        (cap_offset + rel_offset, entry.mask, entry.description)
                    )

        return entries

    def generate_overlay_map(
        self, config_space: Dict[int, int], capabilities: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Generate the complete overlay mapping for the template.

        Args:
            config_space: Configuration space dword map
            capabilities: Dictionary mapping capability ID to offset

        Returns:
            Dictionary with OVERLAY_MAP and OVERLAY_ENTRIES for template
        """
        overlay_map = self.detect_overlay_registers(config_space, capabilities)

        # Convert to format expected by template
        template_overlay_map = []
        for offset, mask in overlay_map:
            # Template expects offset as register number (offset / 4)
            reg_num = offset // 4
            template_overlay_map.append((reg_num, mask))

        return {
            "OVERLAY_MAP": template_overlay_map,
            "OVERLAY_ENTRIES": len(template_overlay_map),
        }

    def get_overlay_info(self, offset: int) -> Optional[OverlayEntry]:
        """
        Get overlay information for a specific register offset.

        Args:
            offset: Register offset

        Returns:
            OverlayEntry if register needs overlay, None otherwise
        """
        # Check standard registers
        if offset in self.definitions.STANDARD_REGISTERS:
            entry = self.definitions.STANDARD_REGISTERS[offset]
            if entry.register_type in (
                RegisterType.MIXED,
                RegisterType.RW1C,
                RegisterType.SPECIAL,
            ):
                return entry

        return None
