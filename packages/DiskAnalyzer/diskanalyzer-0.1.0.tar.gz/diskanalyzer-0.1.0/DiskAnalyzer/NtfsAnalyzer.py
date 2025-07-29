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

'''
This package implements multiples libraries and tools to parse, analyze
and extract informations from disk on the live system.
'''

__version__ = "0.1.0"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = '''
This package implements multiples libraries and tools to parse, analyze
and extract informations from disk on the live system.
'''
__url__ = "https://github.com/mauricelambert/DiskAnalyzer"

__all__ = ["NTFS_VBR", "ntfs_parse"]

__license__ = "GPL-3.0 License"
__copyright__ = '''
DiskAnalyzer  Copyright (C) 2025  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
'''
copyright = __copyright__
license = __license__

from ctypes import LittleEndianStructure, c_uint8, c_uint32, c_char, c_uint64, c_ubyte, c_uint16, c_int8

if __package__:
    from .DiskAnalyzer import get_main_partition, SECTOR_SIZE
else:
    from DiskAnalyzer import get_main_partition, SECTOR_SIZE

from _io import BufferedReader
from sys import exit, stderr
from typing import Tuple

class NTFS_VBR(LittleEndianStructure):
    """
    This class defines the NTFS VBR structure.
    """

    _pack_ = 1
    _fields_ = [
        ('jump', c_ubyte * 3),                 # 0x00                     x86 JMP and NOP instructions to skip past the data structure and execute the bootstrap code
        ('oem_id', c_char * 8),                # 0x03                     NTFS partition name
        ('bytes_per_sector', c_uint16),        # 0x0B                     Number of bytes in a sector (commonly 512)
        ('sectors_per_cluster', c_uint8),      # 0x0D                     Number of sectors in a cluster (cluster size = bytes per sector × sectors per cluster)
        ('reserved_sectors', c_uint16),        # 0x0E                     Always 0 for NTFS; reserved for legacy use
        ('zero1', c_ubyte * 3),                # 0x10                     Not used by NTFS; always 0
        ('unused1', c_uint16),                 # 0x13                     Not used by NTFS; always 0
        ('media_descriptor', c_uint8),         # 0x15                     Media type (0xF8 for hard disk)
        ('zero2', c_uint16),                   # 0x16                     Not used by NTFS; always 0
        ('sectors_per_track', c_uint16),       # 0x18                     Number of sectors per track (BIOS geometry, may be dummy value)
        ('number_of_heads', c_uint16),         # 0x1A                     Number of heads (BIOS geometry, may be dummy value)
        ('hidden_sectors', c_uint32),          # 0x1C                     Number of sectors preceding the partition (from MBR/GPT to partition start)
        ('unused2', c_uint32),                 # 0x20                     Not used by NTFS; always 0
        ('unused3', c_uint32),                 # 0x24                     Not used by NTFS; always 0
        ('total_sectors', c_uint64),           # 0x28                     Total number of sectors in the NTFS partition
        ('mft_lcn', c_uint64),                 # 0x30                     Cluster number of the Master File Table (MFT) start
        ('mftmirr_lcn', c_uint64),             # 0x38                     Cluster number of the MFT mirror (backup)
        ('clusters_per_mft_record', c_int8),   # 0x40                     If positive, clusters per file record segment; if negative, size in bytes is 2^abs(value)
        ('reserved0', c_ubyte * 3),            # padding                  Not used by NTFS; always 0
        ('clusters_per_index_record', c_int8), # 0x44                     If positive, clusters per index buffer; if negative, size in bytes is 2^abs(value)
        ('reserved1', c_ubyte * 3),            # padding                  Not used by NTFS; always 0
        ('volume_serial_number', c_uint64),    # 0x48                     Unique identifier for the NTFS volume
        ('checksum', c_uint32),                # 0x50                     Not used by NTFS
        ('bootstrap_code', c_ubyte * 426),     # 0x54 to 0x1FD            Code to load the operating system
        ('signature', c_uint16),               # 0x1FE (should be 0xAA55) Always 0xAA55, marks a valid boot sector
    ]

def parse_vbr(vbr_data: bytes) -> NTFS_VBR:
    """
    This function parses the VBR data.
    """

    return NTFS_VBR.from_buffer_copy(vbr_data)

def ntfs_parse() -> Tuple[BufferedReader, NTFS_VBR, int]:
    """
    This function parses the disk, find the NTFS partition
    and parses the VBR to return it.
    """

    partition, file = get_main_partition(True)
    ntfs_offset = partition.start_sector * SECTOR_SIZE
    file.seek(ntfs_offset)
    return file, parse_vbr(file.read(SECTOR_SIZE)), ntfs_offset

def print_vbr(vbr: NTFS_VBR) -> None:
    """
    This function prints VBR values.
    """

    print("[+] VBR Detected")
    print(f"  Jump:                      {bytes(vbr.jump).hex()}")
    print(f"  OEM ID:                    {vbr.oem_id.decode().strip()}")
    print(f"  Bytes per sector:          {vbr.bytes_per_sector}")
    print(f"  Sectors per cluster:       {vbr.sectors_per_cluster}")
    print(f"  Reserved sectors:          {vbr.reserved_sectors}")
    print(f"  Zero:                      {bytes(vbr.zero1).hex()}")
    print(f"  Unused:                    {vbr.unused1}")
    print(f"  Media type:                {hex(vbr.media_descriptor)}")
    print(f"  Zero:                      {vbr.zero2}")
    print(f"  Sectors per track:         {vbr.sectors_per_track}")
    print(f"  Number of heads:           {vbr.number_of_heads}")
    print(f"  Total sectors:             {vbr.total_sectors}")
    print(f"  MFT LCN:                   {vbr.mft_lcn}")
    print(f"  MFTMirr LCN:               {vbr.mftmirr_lcn}")
    print(f"  Clusters per mft record:   {vbr.clusters_per_mft_record}")
    print(f"  Reserved:                  {bytes(vbr.reserved0).hex()}")
    print(f"  Clusters per index record: {vbr.clusters_per_index_record}")
    print(f"  Reserved:                  {bytes(vbr.reserved1).hex()}")
    print(f"  Volume Serial Number:      {hex(vbr.volume_serial_number)}")
    print(f"  Checksum:                  {hex(vbr.checksum)}")

    line_length = 40
    bootstrap_code = memoryview(bytes(vbr.bootstrap_code))
    print("  Bootstrap code:")
    for index in range(0, len(bootstrap_code), line_length):
        print("   ", bootstrap_code[index:index + line_length].hex())

    print(f"  Signature:                 {hex(vbr.signature)}")

def main() -> int:
    """
    The main function to starts the script from the command line.
    """

    print(copyright)
    file, vbr, offset = ntfs_parse()

    if vbr.signature != 0xAA55:
        print("Warning: Invalid NTFS boot sector signature.", file=stderr)
        return 1

    print_vbr(vbr)
    return 0

if __name__ == "__main__":
    exit(main())
