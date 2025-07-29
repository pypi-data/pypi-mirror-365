#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package implements multiples libraries and tools to parse, analyze
#    and extract informations from disk on the live system.
#    Copyright (C) 2025  DiskAnalyzer

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
This package implements multiples libraries and tools to parse, analyze
and extract informations from disk on the live system.
"""

__version__ = "0.0.1"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This package implements multiples libraries and tools to parse, analyze
and extract informations from disk on the live system.
"""
__url__ = "https://github.com/mauricelambert/DiskAnalyzer"

__all__ = ["ExFATBootSector", "exfat_parse"]

__license__ = "GPL-3.0 License"
__copyright__ = """
DiskAnalyzer  Copyright (C) 2025  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
copyright = __copyright__
license = __license__

from ctypes import (
    LittleEndianStructure,
    c_char,
    c_uint64,
    c_uint32,
    c_uint16,
    c_uint8,
)

if __package__:
    from .DiskAnalyzer import get_main_partition, SECTOR_SIZE
else:
    from DiskAnalyzer import get_main_partition, SECTOR_SIZE

from _io import BufferedReader
from sys import exit, stderr
from typing import Tuple


class ExFATBootSector(LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("JumpBoot", c_uint8 * 3),                  # 0x00
        ("FileSystemName", c_char * 8),             # 0x03
        ("MustBeZero", c_uint8 * 53),               # 0x0B
        ("PartitionOffset", c_uint64),              # 0x40
        ("VolumeLength", c_uint64),                 # 0x48
        ("FatOffset", c_uint32),                    # 0x50
        ("FatLength", c_uint32),                    # 0x54
        ("ClusterHeapOffset", c_uint32),            # 0x58
        ("ClusterCount", c_uint32),                 # 0x5C
        ("FirstClusterOfRootDirectory", c_uint32),  # 0x60
        ("VolumeSerialNumber", c_uint32),           # 0x64
        ("FileSystemRevision", c_uint16),           # 0x68
        ("VolumeFlags", c_uint16),                  # 0x6A
        ("BytesPerSectorShift", c_uint8),           # 0x6C
        ("SectorsPerClusterShift", c_uint8),        # 0x6D
        ("NumberOfFats", c_uint8),                  # 0x6E
        ("DriveSelect", c_uint8),                   # 0x6F
        ("PercentInUse", c_uint8),                  # 0x70
        ("Reserved2", c_uint8 * 7),                 # 0x71
        ("BootCode", c_uint8 * 390),                # 0x78
        ("BootSignature", c_uint16),                # 0x1FE
    ]


def parse_bootsector(bootsector_data: bytes) -> ExFATBootSector:
    """
    This function parses the Boot Sector data.
    """

    return ExFATBootSector.from_buffer_copy(bootsector_data)


def exfat_parse() -> Tuple[BufferedReader, ExFATBootSector, int]:
    """
    This function parses the disk, find the ExFAT partition
    and parses the Boot Sector to return it.
    """

    partition, file = get_main_partition(True)
    exfat_offset = partition.start_sector * SECTOR_SIZE
    file.seek(exfat_offset)
    return file, parse_bootsector(file.read(SECTOR_SIZE)), exfat_offset


def print_bootsector(bootsector: ExFATBootSector) -> None:
    """
    This function prints ExFAT value.
    """

    print("[+] exFAT Boot Sector Detected")
    print(f"  Jump Boot:                 {bytes(bootsector.JumpBoot).hex()}")
    print(f"  File System Name:          {bootsector.FileSystemName.decode(errors='ignore').strip()}")
    print(f"  MustBeZero:                {bytes(bootsector.MustBeZero).hex()}")
    print(f"  Partition Offset:          {bootsector.PartitionOffset} (LBA)")
    print(f"  Volume Length:             {bootsector.VolumeLength} sectors")
    print(f"  FAT Offset:                {bootsector.FatOffset} (LBA)")
    print(f"  FAT Length:                {bootsector.FatLength} sectors")
    print(f"  Cluster Heap Offset:       {bootsector.ClusterHeapOffset} (LBA)")
    print(f"  Cluster Count:             {bootsector.ClusterCount}")
    print(f"  Root Dir First Cluster:    {bootsector.FirstClusterOfRootDirectory}")
    print(f"  Volume Serial Number:      {hex(bootsector.VolumeSerialNumber)}")
    print(f"  File System Revision:      {bootsector.FileSystemRevision >> 8}.{bootsector.FileSystemRevision & 0xFF}")
    print(f"  Volume Flags:              {bin(bootsector.VolumeFlags)}")
    print(f"  Bytes Per Sector Shift:    {bootsector.BytesPerSectorShift} (=> {1 << bootsector.BytesPerSectorShift} bytes)")
    print(f"  Sectors Per Cluster Shift: {bootsector.SectorsPerClusterShift} (=> {1 << bootsector.SectorsPerClusterShift} sectors)")
    print(f"  Number of FATs:            {bootsector.NumberOfFats}")
    print(f"  Drive Select:              {hex(bootsector.DriveSelect)}")
    print(f"  Percent In Use:            {bootsector.PercentInUse if bootsector.PercentInUse != 0xFF else 'N/A'}")
    print(f"  Reserved2:                 {bytes(bootsector.Reserved2).hex()}")

    line_length = 40
    boot_code = memoryview(bytes(bootsector.BootCode))
    print("  Boot code:")
    for index in range(0, len(boot_code), line_length):
        print("   ", boot_code[index : index + line_length].hex())

    print(f"  Boot Signature:            {hex(bootsector.BootSignature)}")


def main() -> int:
    """
    The main function to starts the script from the command line.
    """

    print(copyright)

    file, bootsector, offset = exfat_parse()

    if bootsector.BootSignature != 0xAA55:
        print(
            "Invalid Boot Signature:",
            bootsector.BootSignature,
            "(0xAA55)",
            file=stderr,
        )
        return 1

    print_bootsector(bootsector)
    return 0


if __name__ == "__main__":
    exit(main())
