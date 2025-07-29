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

__all__ = ["carve_boot_sectors"]

__license__ = "GPL-3.0 License"
__copyright__ = """
DiskAnalyzer  Copyright (C) 2025  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
copyright = __copyright__
license = __license__

if __package__:
    from .DiskAnalyzer import parse_mbr, SECTOR_SIZE, DRIVE_PATH
    from .ExFatBootSector import ExFATBootSector
    from .NtfsAnalyzer import NTFS_VBR
else:
    from DiskAnalyzer import parse_mbr, SECTOR_SIZE, DRIVE_PATH
    from ExFatBootSector import ExFATBootSector
    from NtfsAnalyzer import NTFS_VBR

from typing import Tuple, Union, Iterable, List
from dataclasses import dataclass
from _io import BufferedReader
from sys import exit, stderr

SIGNATURE = b"\x55\xaa"
NTFS_ID = b"\xEB\x52\x90NTFS    "
EXFAT_ID = b"\xEB\x76\x90EXFAT   "


@dataclass
class Partition:
    start_sector: int
    sectors: int


def check_boot_sector(
    file: BufferedReader,
) -> Union[Tuple[bytes, str], None, False]:
    """
    This function implements the disk boot sector.
    """

    try:
        sector = file.read(SECTOR_SIZE)
    except OSError as error:
        if error.errno == 22 or error.errno == 13:
            print("Error: probably End Of File", file=stderr)
            return None

    if len(sector) < SECTOR_SIZE:
        print("End Of File", file=stderr)
        return None

    if sector[510:512] == SIGNATURE:
        if sector.startswith(NTFS_ID):
            return sector, "NTFS"
        elif sector.startswith(EXFAT_ID):
            return sector, "ExFAT"

    return False


def carve_boot_sectors(
    file: BufferedReader,
) -> Iterable[Tuple[int, Tuple[bytes, str]]]:
    """
    This function implements the disk carving to
    found the first sector for the partition.
    """

    sector_num = 1

    while True:
        check = check_boot_sector(file)
        if check is None:
            print("Last sector", sector_num, file=stderr)
            break

        if check:
            yield sector_num, check

        sector_num = int(file.tell() / 512)


def check_mbr(file: BufferedReader) -> bool:
    """
    This function checks for valid MBR.
    """

    mbr = parse_mbr(file.read(SECTOR_SIZE))
    if bytes(mbr.signature) == SIGNATURE:
        print("Warning: Invalid MBR signature.", file=stderr)
        return False

    partition = mbr.to_partition()
    if partition is None:
        print("Warning: No partition found", file=stderr)
        return False

    file.seek(partition.start_sector * SECTOR_SIZE)
    boot_sector = check_boot_sector(file)
    file.seek(SECTOR_SIZE)

    if not boot_sector:
        print("Warning: Invalid partition start found", file=stderr)
        return False

    if not parse_boot_sector(boot_sector).sectors == partition.size:
        print("Warning: Invalid partition size found", file=stderr)
        return False

    return True


def parse_boot_sector(
    sector: Tuple[bytes, str], offset: int = None
) -> Partition:
    """
    This function parses sector into partition.
    """

    if sector[1] == "NTFS":
        partition = NTFS_VBR.from_buffer_copy(sector[0])
        return Partition(offset, partition.total_sectors)
    elif sector[1] == "ExFAT":
        partition = ExFATBootSector.from_buffer_copy(sector[0])
        if offset and offset != partition.PartitionOffset:
            print(
                "Warning: Invalid offset",
                offset,
                "!=",
                partition.PartitionOffset,
                file=stderr,
            )
        return Partition(partition.PartitionOffset, partition.VolumeLength)


def write_mbr(file: BufferedReader, partitions: List[Partition]) -> None:
    """
    This function writes the MBR.
    """

    if not partitions or len(partitions) > 4:
        return None

    mbr = bytearray(512)

    partitions_bytes = bytearray()
    for partition in partitions:
        partitions_bytes.extend(
            b"\0\0\0\0\7\xFF\xFF\xFF"
            + partition.start_sector.to_bytes(4, "little")
            + partition.sectors.to_bytes(4, "little")
        )

    mbr[446 : 446 + len(partitions_bytes)] = partitions_bytes
    mbr[0:446] = b"\xEB\xFE" + b"\xFF" * (446 - 2)
    mbr[510] = 0x55
    mbr[511] = 0xAA

    file.seek(0)
    file.write(mbr)
    file.flush()


def main() -> int:
    """
    The main function to starts the script from the command line.
    """

    print(copyright)

    with open(DRIVE_PATH, "rb") as file:
        if check_mbr(file):
            print("[+] MBR is good")
            return 0

        input("[?] <enter> to search partitions, Ctrl+C to stop...")

        partitions = []
        for offset, sector in carve_boot_sectors(file):
            partition = parse_boot_sector(sector, offset)
            partitions.append(partition)
            end = (offset + partition.sectors) * SECTOR_SIZE
            print(
                "[!] Found a new",
                sector[1],
                "partition at",
                offset,
                "with",
                partition.sectors,
                "sectors (end:",
                end,
                "B)",
            )
            file.seek(end)

        input("[?] <enter> to write a new unbootable MBR, Ctrl+C to stop...")
        write_mbr(file, partitions)

    return 1


if __name__ == "__main__":
    exit(main())
