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

__license__ = "GPL-3.0 License"
__copyright__ = """
DiskAnalyzer  Copyright (C) 2025  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
copyright = __copyright__
license = __license__

print(copyright)

if __package__:
    from .DiskAnalyzer import (
        GPTHeader,
        GPTPartitionEntry,
        MBRHeader,
        MBRPartitionEntry,
        Partition,
        disk_parsing,
        get_main_partition,
        SECTOR_SIZE,
    )
    from .NtfsAnalyzer import NTFS_VBR, ntfs_parse
    from .MftAnalyzer import (
        ACEHeader,
        ACL,
        AttributeHeader,
        AttributeHeaderNonResident,
        AttributeHeaderResident,
        AttributeList,
        FileName,
        MFTEntryHeader,
        NonResidentAttribute,
        ResidentAttribute,
        SecurityDescriptor,
        StandardInformation,
        StandardInformationLess2K,
        get_mft_content,
        parse_mft,
    )
    from .MbrRepair import (
        check_boot_sector,
        carve_boot_sectors,
        check_mbr,
        parse_boot_sector,
        write_mbr,
    )
else:
    from DiskAnalyzer import (
        GPTHeader,
        GPTPartitionEntry,
        MBRHeader,
        MBRPartitionEntry,
        Partition,
        disk_parsing,
        get_main_partition,
        SECTOR_SIZE,
    )
    from NtfsAnalyzer import NTFS_VBR, ntfs_parse
    from MftAnalyzer import (
        ACEHeader,
        ACL,
        AttributeHeader,
        AttributeHeaderNonResident,
        AttributeHeaderResident,
        AttributeList,
        FileName,
        MFTEntryHeader,
        NonResidentAttribute,
        ResidentAttribute,
        SecurityDescriptor,
        StandardInformation,
        StandardInformationLess2K,
        get_mft_content,
        parse_mft,
    )
    from MbrRepair import (
        check_boot_sector,
        carve_boot_sectors,
        check_mbr,
        parse_boot_sector,
        write_mbr,
    )
