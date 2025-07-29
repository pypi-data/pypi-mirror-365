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

__version__ = "0.1.0"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This package implements multiples libraries and tools to parse, analyze
and extract informations from disk on the live system.
"""
__url__ = "https://github.com/mauricelambert/DiskAnalyzer"

__all__ = ["GPTHeader", "GPTPartitionEntry", "MBRHeader", "MBRPartitionEntry", "Partition", "disk_parsing", "get_main_partition"]

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
    c_uint8,
    c_uint32,
    c_char,
    c_uint64,
    c_ubyte,
    c_wchar,
)
from typing import Tuple, List, Union
from dataclasses import dataclass
from _io import BufferedReader
from enum import Enum
from sys import exit

SECTOR_SIZE = 512
DRIVE_PATH = r"\\.\PhysicalDrive0"


class PartitionStatus(Enum):
    """
    Enum for disk partitions status (bootable or not bootable).
    """

    ACTIVE = 0x80
    INACTIVE = 0x00


class MbrPartitionType(Enum):
    """
    Enum for disk partitions type.
    """

    EMPTY = 0x00
    FAT12 = 0x01
    FAT16 = 0x04
    FAT32 = 0x0B
    FAT32_LBA = 0x0C
    NTFS = 0x07
    LINUX_SWAP = 0x82
    EXT2 = 0x83
    EXT3 = 0x83
    EXT4 = 0x83
    LINUX_LVM = 0x8E
    WINDOWS_RE = 0x27
    GPT_PROTECTIVE = 0xEE


class GptPartitionType(Enum):
    """
    Enum for disk partitions type.
    """

    EMPTY = "00000000-0000-0000-0000-000000000000"
    PARTITION_SYSTEM_GUID = "C12A7328-F81F-11D2-BA4B-00A0C93EC93B"
    LEGACY_MBR_PARTITION_GUID = "024DEE41-33E7-11D3-9D69-0008C781F39F"
    PARTITION_MSFT_RESERVED_GUID = "E3C9E316-0B5C-4DB8-817D-F92DF00215AE"
    PARTITION_BASIC_DATA_GUID = "EBD0A0A2-B9E5-4433-87C0-68B6B72699C7"
    PARTITION_LINUX_FILE_SYSTEM_DATA_GUID = (
        "0FC63DAF-8483-4772-8E79-3D69D8477DE4"
    )
    PARTITION_LINUX_RAID_GUID = "A19D880F-05FC-4D3B-A006-743F0F84911E"
    PARTITION_LINUX_SWAP_GUID = "0657FD6D-A4AB-43C4-84E5-0933C84B4F4F"
    PARTITION_LINUX_LVM_GUID = "E6D6D379-F507-44C2-A23C-238F2A3DF928"
    PARTITION_U_BOOT_ENVIRONMENT = "3DE21764-95BD-54BD-A5C3-4ABE786F38A8"
    WINDOWS_RECOVERY_TOOLS = "DE94BBA4-06D1-4D40-A16A-BFD50179D6AC"


status_dict = {status.value: status.name for status in PartitionStatus}
mbr_type_dict = {
    part_type.value: part_type.name for part_type in MbrPartitionType
}
gpt_type_dict = {
    part_type.value: part_type.name for part_type in GptPartitionType
}

gpt_attributes = {
    0x0000000000000001: "Platform required",
    0x0000000000000002: "EFI firmware ignore partition",
    0x0000000000000004: "Legacy BIOS bootable",
    0x0000000000000008: "Reserved for future use",
    0x0100000000000000: "Successful boot flag",
    0x0010000000000000: "Tries remaining",
    0x0020000000000000: "Tries remaining",
    0x0040000000000000: "Tries remaining",
    0x0001000000000000: "Priority low",
    0x0002000000000000: "Priority medium",
    0x0004000000000000: "Priority high",
    0x0008000000000000: "Priority highest",
    0x0100000000000000: "Successful boot flag",
    0x1000000000000000: "Read-only",
    0x2000000000000000: "Shadow copy",
    0x4000000000000000: "Hidden",
    0x8000000000000000: "No drive letter",
}


@dataclass
class Partition:
    start_sector: int
    end_sector: int
    size: int  # In sectors


class MBRPartitionEntry(LittleEndianStructure):
    """
    This class defines the MBR partition structure.
    """

    _pack_ = 1
    _fields_ = [
        ("status", c_uint8),
        ("chs_first", c_uint8 * 3),
        ("type", c_uint8),
        ("chs_last", c_uint8 * 3),
        ("lba_start", c_uint32),
        ("total_sectors", c_uint32),
    ]


class MBRHeader(LittleEndianStructure):
    """
    This class defines the MBR structure.
    """

    _pack_ = 1
    _fields_ = [
        ("bootloader", c_ubyte * 446),
        ("partitions", MBRPartitionEntry * 4),
        ("signature", c_ubyte * 2),
    ]

    def to_partition(self) -> Union[Partition, None]:
        """
        This function makes partition from MBR.
        """

        for entry in self.partitions:
            if (
                entry.type != 0x00
                and entry.type != 0x05
                and entry.type != 0x0F
            ):
                start = entry.lba_start
                size = entry.total_sectors
                end = start + size - 1
                if size > 2097152:
                    return Partition(
                        start_sector=start, end_sector=end, size=size
                    )
        return None


class GPTHeader(LittleEndianStructure):
    """
    This class defines the GPT structure.
    """

    _pack_ = 1
    _fields_ = [
        ("signature", c_char * 8),
        ("revision", c_uint32),
        ("header_size", c_uint32),
        ("header_crc32", c_uint32),
        ("reserved", c_uint32),
        ("current_lba", c_uint64),
        ("backup_lba", c_uint64),
        ("first_usable_lba", c_uint64),
        ("last_usable_lba", c_uint64),
        ("disk_guid", c_ubyte * 16),
        ("partition_entry_lba", c_uint64),
        ("num_part_entries", c_uint32),
        ("part_entry_size", c_uint32),
        ("part_array_crc32", c_uint32),
    ]

    def to_partition(self) -> Union[Partition, None]:
        """
        This function makes partition from GPT.
        """

        for entry in self.partitions:
            guid_type = format_guid(entry.part_type_guid).upper()
            if (
                guid_type == "EBD0A0A2-B9E5-4433-87C0-68B6B72699C7"
                or guid_type == "0FC63DAF-8483-4772-8E79-3D69D8477DE4"
            ):
                start = entry.start_lba
                end = entry.end_lba
                size = end - start + 1
                return Partition(start_sector=start, end_sector=end, size=size)
        return None


class GPTPartitionEntry(LittleEndianStructure):
    """
    This class defines the GPT partition structure.
    """

    _pack_ = 1
    _fields_ = [
        ("part_type_guid", c_ubyte * 16),
        ("unique_part_guid", c_ubyte * 16),
        ("start_lba", c_uint64),
        ("end_lba", c_uint64),
        ("attributes", c_uint64),
        ("part_name", c_wchar * 36),  # 72 bytes, UTF-16 encoded
    ]


data_type = type(c_ubyte * 16)


def format_guid(guid_bytes: data_type) -> str:
    """
    This function returns a GUID string from data.
    """

    data = bytes(guid_bytes)
    return (
        f"{int.from_bytes(data[0:4], 'little'):08X}-"
        f"{int.from_bytes(data[4:6], 'little'):04X}-"
        f"{int.from_bytes(data[6:8], 'little'):04X}-"
        f"{data[8:10].hex()}-{data[10:].hex()}"
    )


def is_gpt_signature(mbr: MBRHeader, sector_data: bytes) -> bool:
    """
    This function checks the GPT magic bytes
    to detect the start sector structure.
    """

    return any(
        entry.type == 0xEE for entry in mbr.partitions
    ) and sector_data.startswith(b"EFI PART")


def parse_mbr(mbr_data: bytes) -> MBRHeader:
    """
    This function parses the MBR data.
    """

    return MBRHeader.from_buffer_copy(mbr_data)


def print_mbr_analysis(mbr: MBRHeader) -> None:
    """
    This function prints informations about MBR.
    """

    if bytes(mbr.signature) != b"\x55\xaa":
        print("[-] Invalid MBR signature")
        return None

    print("[+] MBR Detected")

    line_length = 40
    bootloader = memoryview(bytes(mbr.bootloader))

    print("  Bootloader")
    for index in range(0, len(bootloader), line_length):
        print("   ", bootloader[index : index + line_length].hex())

    for index, entry in enumerate(mbr.partitions):
        if entry.type != 0:
            print(f"  Partition {index + 1}:")
            print(f"    Status       : 0x{entry.status:02X} ({status_dict[entry.status]})")
            print(f"    Type         : 0x{entry.type:02X} ({mbr_type_dict[entry.type]})")
            print(f"    Start LBA    : {entry.lba_start}")
            print(f"    Total Sectors: {entry.total_sectors} ({(entry.total_sectors * 512) / (1024 ** 2):.2f} MB)")

    print("  Boot Signature")
    print("   ", bytes(mbr.signature).hex())


def gpt_partitions_size(partition: GPTPartitionEntry) -> float:
    """
    This function returns the size in MB for a GPT partition
    """

    return (
        (partition.end_lba - partition.start_lba) * SECTOR_SIZE / (1024 * 1024)
    )


def parse_gpt(file: BufferedReader, gpt_data: bytes) -> GPTHeader:
    """
    This function parses the GPT data.
    """

    gpt_header = GPTHeader.from_buffer_copy(gpt_data)

    gpt_header.partitions = []
    file.seek(gpt_header.partition_entry_lba * SECTOR_SIZE)
    for _ in range(gpt_header.num_part_entries):
        entry_data = file.read(128)
        if len(entry_data) == 128 and entry_data != b"\0" * 128:
            entry = GPTPartitionEntry.from_buffer_copy(entry_data)
            gpt_header.partitions.append(entry)
            entry.flags = [
                attr
                for value, attr in gpt_attributes.items()
                if entry.attributes & value
            ]

    return gpt_header


def print_gpt_analysis(gpt_header: GPTHeader) -> None:
    """
    This function prints informations about GPT headers and partitions.
    """

    if gpt_header.signature != b"EFI PART":
        print("[-] Invalid GPT signature")
        return None

    print("[+] GPT Detected")
    print(f"  GPT Signature       : {gpt_header.signature.decode()}")
    print(f"  GPT Disk GUID       : {format_guid(gpt_header.disk_guid)}")
    print(f"  Partition Count     : {gpt_header.num_part_entries}")
    print(f"  Partition Entry Size: {gpt_header.part_entry_size}")
    print(f"  Partition Table LBA : {gpt_header.partition_entry_lba}")

    print("\n[+] Partition Entries:")
    for index, entry in enumerate(gpt_header.partitions):
        part_name = entry.part_name.strip() if entry.part_name else "No Name"
        part_guid = format_guid(entry.unique_part_guid)
        type_guid = format_guid(entry.part_type_guid).upper()
        print(f"  Partition {index+1}:")
        print(f"    Type GUID    : {type_guid} ({gpt_type_dict[type_guid]})")
        print(f"    Unique GUID  : {part_guid}")
        print(f"    Start LBA    : {entry.start_lba}")
        print(f"    End LBA      : {entry.end_lba}")
        print(f"    Size in MB   : {gpt_partitions_size(entry):.2f} MB")
        print(f"    Attributes   : {hex(entry.attributes)} ({entry.attributes})")
        if entry.attributes:
            print(f"        {', '.join(entry.flags)}")
        print(f"    Partition Name: {part_name}")


def disk_parsing(
    keep_open: bool = False,
) -> Union[
    Tuple[
        Union[PermissionError, Exception, MBRHeader, GPTHeader], BufferedReader
    ],
    PermissionError,
    Exception,
    MBRHeader,
    GPTHeader,
]:
    """
    This function returns the parsed structure or error and opened file if keep_open is True.
    """

    try:
        file = open(DRIVE_PATH, "rb")
    except PermissionError:
        print("[-] Permission denied. Run as Administrator.")
        return 1
    except Exception as e:
        print(f"[-] Error: {e}")
        return 127

    first_sector = file.read(SECTOR_SIZE)
    second_sector = file.read(SECTOR_SIZE)

    mbr = parse_mbr(first_sector)

    if is_gpt_signature(mbr, second_sector):
        return_value = parse_gpt(file, second_sector)
    else:
        return_value = parse_mbr(mbr)

    if keep_open:
        return return_value, file

    file.close()
    return return_value


def get_main_partition(
    *args, **kwargs
) -> Tuple[Partition, Union[None, BufferedReader]]:
    """
    This function returns the main partition.
    """

    file = None
    data = disk_parsing(*args, **kwargs)

    if isinstance(data, tuple) and isinstance(data[1], BufferedReader):
        file = data[1]
        data = data[0]

    return data.to_partition(), file


def main() -> int:
    """
    The main function to starts the script from the command line.
    """

    print(copyright)
    value = disk_parsing()

    if isinstance(value, PermissionError):
        print("[-] Permission denied. Run as Administrator.")
        return 1
    elif isinstance(value, Exception):
        print(f"[-] Error: {value}")
        return 127
    elif isinstance(value, GPTHeader):
        print_gpt_analysis(value)
    elif isinstance(value, MBRHeader):
        print_mbr_analysis(value)
    else:
        return 127

    return 0


if __name__ == "__main__":
    exit(main())
