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

__all__ = [
    "ACEHeader",
    "ACL",
    "AttributeHeader",
    "AttributeHeaderNonResident",
    "AttributeHeaderResident",
    "AttributeList",
    "FileName",
    "MFTEntryHeader",
    "NonResidentAttribute",
    "ResidentAttribute",
    "SecurityDescriptor",
    "StandardInformation",
    "StandardInformationLess2K",
    "get_mft_content",
    "parse_mft",
]

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
    Structure,
    c_ubyte,
    c_uint8,
    c_uint32,
    c_char,
    c_uint64,
    c_uint16,
    sizeof,
)
from typing import List, Tuple, Iterable, Union
from datetime import timedelta, datetime

if __package__:
    from .NtfsAnalyzer import ntfs_parse
else:
    from NtfsAnalyzer import ntfs_parse

from _io import BufferedReader
from sys import exit

ATTRIBUTE_TYPES = {
    0x10: '$STANDARD_INFORMATION',           # [resident] Contains file system metadata: creation time, modification time, access time, file flags (readonly, hidden, system), etc
    0x20: '$ATTRIBUTE_LIST',                 # Used when a file has too many attributes to fit in one MFT record
    0x30: '$FILE_NAME',                      # Contains the file name, its parent directory reference, name namespace and userland modifiable timestamps
    0x40: '$OBJECT_ID',                      # Contains a 128-bit Object ID (GUID)
    0x50: '$SECURITY_DESCRIPTOR',            # Stores security metadata: owner SID, ACLs, DACLs
    0x60: '$VOLUME_NAME',                    # Contains the volume name of the NTFS partition
    0x70: '$VOLUME_INFORMATION',             # Flags and version info for the volume: dirty bit, NTFS version
    0x80: '$DATA',                           # Holds actual file content. Can be resident (for small files) or non-resident (with data runs)
    0x90: '$INDEX_ROOT',                     # Holds the root of the B-tree index for filenames in a folder
    0xA0: '$INDEX_ALLOCATION',               # Contains non-resident blocks of the B-tree
    0xB0: '$BITMAP',                         # Bitmap that tracks allocation of MFT entries or index blocks (contains information about: block free/used)
    0xC0: '$REPARSE_POINT',                  # Contains reparse tag and associated data (symbolic links, mount points and OneDrive placeholders)
    0xD0: '$EA_INFORMATION',                 # [legacy] Extended Attributes header
    0xE0: '$EA',                             # [obsolete] Extended Attributes
    0x100: '$LOGGED_UTILITY_STREAM',         # Internal NTFS metadata used for integrity streams
    0xFFFFFFFF: 'END',                       # Sentinel value marking the end of attributes in an MFT record
}

FILE_INFORMATION_ATTRIBUTE_FLAGS = {
    0x0001: "ReadOnly",
    0x0002: "Hidden",
    0x0004: "System",
    0x0020: "Archive",
    0x0040: "Device",
    0x0080: "Normal",
    0x0100: "Temporary",
    0x0200: "Sparse File",
    0x0400: "Reparse Point",
    0x0800: "Compressed",
    0x1000: "Offline",
    0x2000: "Not Content Indexed",
    0x4000: "Encrypted",
}

FILE_NAME_ATTRIBUTE_FLAGS = {
    0x0001: "Read-Only",
    0x0002: "Hidden",
    0x0004: "System",
    0x0020: "Archive",
    0x0040: "Device",
    0x0080: "Normal",
    0x0100: "Temporary",
    0x0200: "Sparse File",
    0x0400: "Reparse Point",
    0x0800: "Compressed",
    0x1000: "Offline",
    0x2000: "Not Content Indexed",
    0x4000: "Encrypted",
    0x10000000: "Directory",
    0x20000000: "Index View",
}

ACE_TYPE_MAP = {
    0x00: "Access Allowed",
    0x01: "Access Denied",
    0x02: "System Audit",
}

ACE_FLAG_MAP = {
    0x01: "Object Inherit",
    0x02: "Container Inherit",
    0x04: "No Propagate Inherit",
    0x08: "Inherit Only",
    0x40: "Audit Success",
    0x80: "Audit Failure",
}

ACCESS_MASK_FLAGS = {
    0x00000001: "ReadData / ListDirectory",
    0x00000002: "WriteData / AddFile",
    0x00000004: "AppendData / AddSubdirectory",
    0x00000008: "ReadExtendedAttributes",
    0x00000010: "WriteExtendedAttributes",
    0x00000020: "Execute / Traverse",
    0x00000040: "DeleteChild",
    0x00000080: "ReadAttributes",
    0x00000100: "WriteAttributes",
    0x00010000: "Delete",
    0x00020000: "ReadPermissions",
    0x00040000: "WriteDACL",
    0x00080000: "WriteOwner",
    0x00100000: "Synchronize",
    0x01000000: "AccessSystemSecurity",
    0x10000000: "GenericAll",
    0x20000000: "GenericExecute",
    0x40000000: "GenericWrite",
    0x80000000: "GenericRead",
}

SECURITY_DESCRIPTOR_CONTROL_FLAGS = {
    0x0001: "Owner Defaulted",
    0x0002: "Group Defaulted",
    0x0004: "DACL Present",
    0x0008: "DACL Defaulted",
    0x0010: "SACL Present",
    0x0020: "SACL Defaulted",
    0x0100: "DACL Auto Inherit Req",
    0x0200: "SACL Auto Inherit Req",
    0x0400: "DACL Auto Inherited",
    0x0800: "SACL Auto Inherited",
    0x1000: "DACL Protected",
    0x2000: "SACL Protected",
    0x4000: "RM Control Valid",
    0x8000: "Self Relative",
}


class MFTEntryHeader(LittleEndianStructure):
    """
    This class defines the MFT entry structure.
    """

    _pack_ = 1
    _fields_ = [
        ("signature", c_char * 4),  # "FILE"
        ("fixup_offset", c_uint16),
        ("fixup_entries", c_uint16),
        ("log_seq_number", c_uint64),
        ("sequence_number", c_uint16),
        ("hard_link_count", c_uint16),
        ("first_attr_offset", c_uint16),
        ("flags", c_uint16),  # 0x01 = in-use, 0x02 = directory
        ("used_entry_size", c_uint32),
        ("allocated_entry_size", c_uint32),
        ("base_file_record", c_uint64),
        ("next_attr_id", c_uint16),
        ("align", c_uint16),
        ("mft_record_number", c_uint32),
    ]


class AttributeHeader(LittleEndianStructure):
    """
    This class defines the MFT attribute headers.
    """

    _pack_ = 1
    _fields_ = [
        ("type_id", c_uint32),
        ("length", c_uint32),
        ("non_resident", c_uint8),
        ("name_length", c_uint8),
        ("name_offset", c_uint16),
        ("flags", c_uint16),
        ("attribute_id", c_uint16),
    ]


class AttributeHeaderResident(LittleEndianStructure):
    """
    This class defines the full MFT resident
    attribute headers (value inside the MFT,
    small value - ~700 bytes).
    """

    _pack_ = 1
    _fields_ = [
        ("type_id", c_uint32),
        ("length", c_uint32),
        ("non_resident", c_uint8),  # 0 = resident, 1 = non-resident
        ("name_length", c_uint8),
        ("name_offset", c_uint16),
        ("flags", c_uint16),
        ("attribute_id", c_uint16),
        ("attr_length", c_uint32),
        ("attr_offset", c_uint16),
        ("indexed_flag", c_uint8),
        ("padding", c_uint8),
    ]


class ResidentAttribute(LittleEndianStructure):
    """
    This class defines the MFT resident attribute
    specific fields (value inside the MFT,
    small value - ~700 bytes).
    """

    _pack_ = 1
    _fields_ = [
        ("value_length", c_uint32),
        ("value_offset", c_uint16),
        ("flags", c_uint8),
        ("reserved", c_uint8),
    ]


class AttributeHeaderNonResident(LittleEndianStructure):
    """
    This class defines the full MFT non resident
    attribute headers (value outside the MFT,
    value > ~700 bytes).
    """

    _pack_ = 1
    _fields_ = [
        ("type_id", c_uint32),
        ("length", c_uint32),
        ("non_resident", c_uint8),  # 0 = resident, 1 = non-resident
        ("name_length", c_uint8),
        ("name_offset", c_uint16),
        ("flags", c_uint16),
        ("attribute_id", c_uint16),
        ("starting_vcn", c_uint64),
        ("last_vcn", c_uint64),
        ("data_run_offset", c_uint16),
        ("compression_unit_size", c_uint16),
        ("reserved", c_uint32),
        ("allocated_size", c_uint64),
        ("real_size", c_uint64),
        ("initialized_size", c_uint64),
    ]

    def parse_data_runs(self, cluster_size: int) -> List[Tuple[int, int]]:
        """
        This method parses data runs (data: length, offset).
        """

        i = 0
        lcn = 0
        self.data_runs = []
        self.size = 0

        while i < len(self.data_runs_data):
            header = self.data_runs_data[i]
            i += 1
            if header == 0x00:
                break

            len_size = header & 0x0F
            off_size = (header >> 4) & 0x0F

            length_bytes = self.data_runs_data[i : i + len_size]
            i += len_size
            offset_bytes = self.data_runs_data[i : i + off_size]
            i += off_size

            length = int.from_bytes(length_bytes, "little")

            if off_size > 0:
                offset = int.from_bytes(
                    offset_bytes
                    + (b"\x00" if offset_bytes[-1] < 0x80 else b"\xFF")
                    * (8 - off_size),
                    "little",
                    signed=True,
                )
                lcn += offset

            size = length * cluster_size
            self.size += size
            self.data_runs.append((lcn * cluster_size, size))

        return self.data_runs

    def read_data_runs(
        self, file: BufferedReader, ntfs_offset: int
    ) -> Iterable[bytes]:
        """
        This generator yields content block by content block.
        """

        for offset, size in self.data_runs:
            file.seek(ntfs_offset + offset)
            yield file.read(size)

    def read_content(
        self, file: BufferedReader, ntfs_offset: int
    ) -> bytearray:
        """
        This method returns content as bytearray.
        """

        content = bytearray()
        for block in self.read_data_runs(file, ntfs_offset):
            content.extend(block)
        return content


class NonResidentAttribute(LittleEndianStructure):
    """
    This class defines the MFT non resident attribute
    specific fields (value outside the MFT,
    value > ~700 bytes).
    """

    _pack_ = 1
    _fields_ = [
        ("starting_vcn", c_uint64),
        ("last_vcn", c_uint64),
        ("data_run_offset", c_uint16),
        ("compression_unit_size", c_uint16),
        ("reserved", c_uint32),
        ("allocated_size", c_uint64),
        ("real_size", c_uint64),
        ("initialized_size", c_uint64),
    ]


class StandardInformationLess2K(LittleEndianStructure):
    """
    This class defines the $STANDARD_INFORMATION MFT attribute.
    """

    _pack_ = 1
    _fields_ = [
        ("CreationTime", c_uint64),        # 0x00
        ("ModificationTime", c_uint64),    # 0x08
        ("MFTChangeTime", c_uint64),       # 0x10
        ("AccessTime", c_uint64),          # 0x18
        ("FileAttributes", c_uint32),      # 0x20
        ("MaxVersions", c_uint32),         # 0x24
        ("VersionNumber", c_uint32),       # 0x28
        ("ClassId", c_uint32),             # 0x2C
    ]

    def __str__(self):
        return (
            "[+] $STANDARD_INFORMATION detected\n"
            f"  Creation time:          {self.creation_time}\n"
            f"  Modification time:      {self.modification_time}\n"
            f"  MFT change time:        {self.mft_modification_time}\n"
            f"  Access time:            {self.access_time}\n"
            f"  File attributes:        {self.FileAttributes}\n"
            + (
                (
                    "    "
                    + ", ".join(
                        parse_standard_information_flags(self.FileAttributes)
                    )
                    + "\n"
                )
                if self.FileAttributes
                else ""
            )
            + f"  Max versions:           {self.MaxVersions}\n"
            f"  Version number:         {self.VersionNumber}\n"
            f"  Class ID:               {self.ClassId}\n"
        )


class StandardInformation(LittleEndianStructure):
    """
    This class defines the $STANDARD_INFORMATION MFT attribute.
    """

    _pack_ = 1
    _fields_ = [
        ("CreationTime", c_uint64),        # 0x00
        ("ModificationTime", c_uint64),    # 0x08
        ("MFTChangeTime", c_uint64),       # 0x10
        ("AccessTime", c_uint64),          # 0x18
        ("FileAttributes", c_uint32),      # 0x20
        ("MaxVersions", c_uint32),         # 0x24
        ("VersionNumber", c_uint32),       # 0x28
        ("ClassId", c_uint32),             # 0x2C
        ("OwnerId", c_uint32),             # 0x30 (2K+)
        ("SecurityId", c_uint32),          # 0x34 (2K+)
        ("QuotaCharged", c_uint64),        # 0x38 (2K+)
        ("USN", c_uint64),                 # 0x40 (2K+)
    ]

    def __str__(self):
        return (
            "[+] $STANDARD_INFORMATION detected\n"
            f"  Creation time:          {self.creation_time}\n"
            f"  Modification time:      {self.modification_time}\n"
            f"  MFT change time:        {self.mft_modification_time}\n"
            f"  Access time:            {self.access_time}\n"
            f"  File attributes:        {self.FileAttributes}\n"
            + (
                (
                    "    "
                    + ", ".join(
                        parse_standard_information_flags(self.FileAttributes)
                    )
                    + "\n"
                )
                if self.FileAttributes
                else ""
            )
            + f"  Max versions:           {self.MaxVersions}\n"
            f"  Version number:         {self.VersionNumber}\n"
            f"  Class ID:               {self.ClassId}\n"
            f"  Owner ID:               {self.OwnerId}\n"
            f"  Security ID:            {self.SecurityId}\n"
            f"  Quota charged:          {self.QuotaCharged}\n"
            f"  Update Sequence Number: {self.USN}\n"
        )


class AttributeList(LittleEndianStructure):
    """
    This class defines the $ATTRIBUTE_LIST MFT attribute.
    """

    _pack_ = 1
    _fields_ = [
        ("Type", c_uint32),              # 4 bytes: Type of the attribute list (typically 0x00)
        ("RecordLength", c_uint16),      # 2 bytes: Record length
        ("NameLength", c_ubyte),         # 1 byte:  Name length
        ("OffsetToName", c_ubyte),       # 1 byte:  Offset to the name
        ("StartingVCN", c_uint64),       # 8 bytes: Starting VCN (Virtual Cluster Number)
        ("BaseFileReference", c_uint64), # 8 bytes: Base file reference
        ("AttributeId", c_uint16),       # 2 bytes: Attribute ID
    ]

    def __str__(self):
        return (
            "[+] $ATTRIBUTE_LIST detected\n"
            f"  Type:                         {self.Type}\n"
            f"  Record length:                {self.RecordLength}\n"
            f"  Name length:                  {self.NameLength}\n"
            f"  Name offset:                  {self.OffsetToName}\n"
            f"  Virtual Cluster Number start: {self.StartingVCN}\n"
            f"  Base file reference:          {self.BaseFileReference}\n"
            f"  Attribute ID:                 {self.AttributeId}\n"
            f"  Name:                         {self.name}\n"
        )


class FileName(LittleEndianStructure):
    """
    This class defines the $FILE_NAME MFT attribute.
    """

    _pack_ = 1
    _fields_ = [
        ("ParentDirectory", c_uint64),    # 0x00: 8 bytes: File reference to the parent directory
        ("CreationTime", c_uint64),       # 0x08: 8 bytes: File creation time
        ("ModificationTime", c_uint64),   # 0x10: 8 bytes: Last write (modified) time
        ("MFTChangeTime", c_uint64),      # 0x18: 8 bytes: Last change to MFT entry (not file content)
        ("AccessTime", c_uint64),         # 0x20: 8 bytes: Last access time
        ("AllocatedSize", c_uint64),      # 0x28: 8 bytes: Allocated size of the file
        ("RealSize", c_uint64),           # 0x30: 8 bytes: Actual file size
        ("Flags", c_uint32),              # 0x38: 4 bytes: Flags (e.g., Directory, compressed, hidden)
        ("Reserved", c_uint32),           # 0x3C: 4 bytes: Reserved for future use (Extended Attributes, Reparse)
        ("FileNameLength", c_ubyte),      # 0x40: 1 byte:  Filename length in characters
        ("FileNameNamespace", c_ubyte),   # 0x41: 1 byte:  Filename namespace (e.g., Win32, DOS)
                                          # 0x42: X wchar: Filename content
    ]

    def __str__(self):
        return (
            "[+] $FILE_NAME detected\n"
            f"  Creation time:          {self.creation_time}\n"
            f"  Modification time:      {self.modification_time}\n"
            f"  MFT change time:        {self.mft_modification_time}\n"
            f"  Access time:            {self.access_time}\n"
            f"  Allocated size:         {self.AllocatedSize}\n"
            f"  Real size:              {self.RealSize}\n"
            f"  Flags:                  {self.Flags}\n"
            + (
                ("    " + ", ".join(parse_file_name_flags(self.Flags)) + "\n")
                if self.Flags
                else ""
            )
            + f"  Reserved:               {self.Reserved}\n"
            f"  Filename length:        {self.FileNameLength}\n"
            f"  Filename Namespace:     {self.FileNameNamespace}\n"
            f"  Name:                   {self.name}\n"
        )


class SecurityDescriptor(LittleEndianStructure):
    """
    This class defines the $SECURITY_DESCRIPTOR MFT attribute.
    """

    _pack_ = 1
    _fields_ = [
        ("Revision", c_uint8),
        ("Padding1", c_uint8),
        ("ControlFlags", c_uint16),
        ("OffsetOwner", c_uint32),
        ("OffsetGroup", c_uint32),
        ("OffsetSACL", c_uint32),
        ("OffsetDACL", c_uint32),
    ]

    def __str__(self):
        if self.sacl:
            sacl_indent = "\n  " + str(self.sacl).replace("\n", "\n  ")
        if self.dacl:
            dacl_indent = "\n  " + str(self.dacl).replace("\n", "\n  ")
        return (
            "[+] $SECURITY_DESCRIPTOR detected\n"
            f"  Revision:  {self.Revision}\n"
            f"  Padding:   {self.Padding1}\n"
            f"  Control flags:      {self.ControlFlags}\n"
            + (
                (
                    "    "
                    + ", ".join(parse_control_flags(self.ControlFlags))
                    + "\n"
                )
                if self.ControlFlags
                else ""
            )
            + f"  Offset owner: {self.OffsetOwner}"
            + (f" ({self.owner_sid})" if self.owner_sid else "")
            + "\n"
            f"  Offset group: {self.OffsetGroup}"
            + (f" ({self.group_sid})" if self.group_sid else "")
            + "\n"
            + (f"  SACL: {sacl_indent}\n" if self.sacl else "")
            + (f"  DACL: {dacl_indent}" if self.dacl else "")
        )


class ACL(LittleEndianStructure):
    """
    This class defines the MFT Access Control List structure.
    """

    _pack_ = 1
    _fields_ = [
        ("AclRevision", c_uint8),
        ("Padding1", c_uint8),
        ("AclSize", c_uint16),
        ("AceCount", c_uint16),
        ("Padding2", c_uint16),
    ]

    def __str__(self):
        ace_indent = "\n    " + "\n".join(str(x) for x in self.ace).replace(
            "\n", "\n    "
        )
        return (
            "[+] ACL detected\n"
            f"  Revision:  {self.AclRevision}\n"
            f"  Padding:   {self.Padding1}\n"
            f"  Size:      {self.AclSize}\n"
            f"  Ace count: {self.AceCount}\n"
            f"  ACE: {ace_indent}"
        )


class ACEHeader(LittleEndianStructure):
    """
    This class defines the MFT ACE header structure.
    """

    _pack_ = 1
    _fields_ = [
        ("AceType", c_uint8),
        ("AceFlags", c_uint8),
        ("AceSize", c_uint16),
        ("AccessMask", c_uint32),
        # SID follows dynamically
    ]

    def __str__(self):
        return (
            "[+] ACE Header detected\n"
            f"  Type:        {ACE_TYPE_MAP.get(self.AceType, f'Unknown ({self.AceType})')} ({self.AceType})\n"
            f"  Flags:       {self.AceFlags}\n"
            + (
                ("    " + ", ".join(parse_ace_flags(self.AceFlags)) + "\n")
                if self.AceFlags
                else ""
            )
            + f"  Size:        {self.AceSize}\n"
            f"  Access mask: {self.AccessMask}\n"
            + (
                ("    " + ", ".join(parse_access_mask(self.AccessMask)) + "\n")
                if self.AccessMask
                else ""
            )
            + f"  SID:         {self.sid}"
        )


def parse_sid(data: bytes) -> Tuple[str, int]:
    """
    This function converts SID data to human readable format.
    """

    revision = data[0]
    subauth_count = data[1]
    id_auth = int.from_bytes(data[2:8], "big")
    sid_parts = [
        int.from_bytes(data[8 + i * 4 : 12 + i * 4], "little")
        for i in range(subauth_count)
    ]
    sid = f"S-{revision}-{id_auth}" + "".join(f"-{x}" for x in sid_parts)
    sid_length = 8 + subauth_count * 4
    return sid, sid_length


def parse_acl(data: bytes) -> ACL:
    """
    This function parses ACL and ACEs.
    """

    acl = ACL.from_buffer_copy(data)
    entries = []
    acl_size = sizeof(ACL)

    for _ in range(acl.AceCount):
        ace_hdr = ACEHeader.from_buffer_copy(data[acl_size:])
        sid, sid_len = parse_sid(data[acl_size + 8 :])
        ace_hdr.sid = sid
        entries.append(ace_hdr)
        acl_size += ace_hdr.AceSize

    acl.ace = entries
    return acl


def parse_security_descriptor(
    attribute_header: Union[
        AttributeHeaderResident, AttributeHeaderNonResident
    ],
    file: BufferedReader,
    ntfs_offset: int,
) -> SecurityDescriptor:
    """
    This function parses the $SECURITY_DESCRIPTOR MFT attribute.
    """

    data = get_attribute_data(attribute_header, file, ntfs_offset)
    security_descriptor = SecurityDescriptor.from_buffer_copy(data[:20])
    security_descriptor.owner_sid = security_descriptor.group_sid = (
        security_descriptor.sacl
    ) = security_descriptor.dacl = None

    if security_descriptor.OffsetOwner:
        sid, _ = parse_sid(data[security_descriptor.OffsetOwner :])
        security_descriptor.owner_sid = sid

    if security_descriptor.OffsetGroup:
        sid, _ = parse_sid(data[security_descriptor.OffsetGroup :])
        security_descriptor.group_sid = sid

    if security_descriptor.OffsetSACL:
        security_descriptor.sacl = parse_acl(
            data[security_descriptor.OffsetSACL :],
        )

    if security_descriptor.OffsetDACL:
        security_descriptor.dacl = parse_acl(
            data[security_descriptor.OffsetDACL :]
        )

    attribute_header.parsing = security_descriptor
    return security_descriptor


def get_attribute_data(
    attribute_header: Union[
        AttributeHeaderResident, AttributeHeaderNonResident
    ],
    file: BufferedReader,
    ntfs_offset: int,
) -> bytes:
    """
    This function returns attribute data from resident and non resident attribute.
    """

    if attribute_header.non_resident:
        return attribute_header.read_content(file, ntfs_offset)
    else:
        return attribute_header.data


def parse_attribute_list(
    attribute_header: Union[
        AttributeHeaderResident, AttributeHeaderNonResident
    ],
    file: BufferedReader,
    ntfs_offset: int,
) -> List[AttributeList]:
    """
    This function parses a $ATTRIBUTE_LIST MFT attribute.
    """

    offset = 0
    entries = []
    data = get_attribute_data(attribute_header, file, ntfs_offset)

    while offset < len(data):
        attribute_list = AttributeList.from_buffer_copy(data)

        if attribute_list.RecordLength == 0:
            break

        entry_data = data[offset : offset + attribute_list.RecordLength]

        name = ""
        if attribute_list.NameLength > 0:
            name_offset = attribute_list.OffsetToName
            name_end = name_offset + attribute_list.NameLength * 2
            try:
                name = entry_data[name_offset:name_end].decode("utf-16-le")
            except UnicodeDecodeError:
                name = repr(entry_data[name_offset:name_end].decode("latin1"))

        attribute_list.name = name
        entries.append(attribute_list)
        offset += attribute_list.RecordLength

    attribute_header.parsing = entries
    return entries


def filetime_to_datetime(filetime: int) -> datetime:
    """
    This function converts windows filetime to python datetime.
    """

    if filetime == 0:
        return None
    return datetime(1601, 1, 1) + timedelta(microseconds=filetime / 10)


def parse_standard_information(
    attribute_header: Union[
        AttributeHeaderResident, AttributeHeaderNonResident
    ],
    file: BufferedReader,
    ntfs_offset: int,
) -> None:
    """
    This function parses the $STANDARD_INFORMATION MFT attribute.
    """

    data = get_attribute_data(attribute_header, file, ntfs_offset)

    if len(data) == 48:
        standard_information = StandardInformationLess2K.from_buffer_copy(data)
    else:
        standard_information = StandardInformation.from_buffer_copy(data)
    standard_information.creation_time = filetime_to_datetime(
        standard_information.CreationTime
    )
    standard_information.modification_time = filetime_to_datetime(
        standard_information.ModificationTime
    )
    standard_information.mft_modification_time = filetime_to_datetime(
        standard_information.MFTChangeTime
    )
    standard_information.access_time = filetime_to_datetime(
        standard_information.AccessTime
    )
    attribute_header.parsing = standard_information


def parse_file_name(
    attribute_header: Union[
        AttributeHeaderResident, AttributeHeaderNonResident
    ],
    file: BufferedReader,
    ntfs_offset: int,
) -> None:
    """
    This function parses the $FILE_NAME MFT attribute.
    """

    data = get_attribute_data(attribute_header, file, ntfs_offset)

    filename = FileName.from_buffer_copy(data)
    filename.creation_time = filetime_to_datetime(filename.CreationTime)
    filename.modification_time = filetime_to_datetime(
        filename.ModificationTime
    )
    filename.mft_modification_time = filetime_to_datetime(
        filename.MFTChangeTime
    )
    filename.access_time = filetime_to_datetime(filename.AccessTime)
    attribute_header.parsing = filename

    name = ""
    if filename.FileNameLength > 0:
        offset = sizeof(FileName)
        try:
            name = data[offset : offset + filename.FileNameLength * 2].decode(
                "utf-16-le"
            )
        except UnicodeDecodeError:
            name = repr(
                data[offset : offset + filename.FileNameLength * 2].decode(
                    "latin1"
                )
            )

    filename.name = name


def parse_standard_information_flags(flags: int) -> List[str]:
    """
    This function returns the string values for MFT entry flags.
    """

    return [
        name
        for bit, name in FILE_INFORMATION_ATTRIBUTE_FLAGS.items()
        if flags & bit
    ]


def parse_file_name_flags(flags: int) -> List[str]:
    """
    This function returns the string values for MFT entry flags.
    """

    return [
        name for bit, name in FILE_NAME_ATTRIBUTE_FLAGS.items() if flags & bit
    ]


def parse_control_flags(flags: int) -> List[str]:
    """
    This function returns human readable control flags from flags value.
    """

    return [
        desc
        for bit, desc in SECURITY_DESCRIPTOR_CONTROL_FLAGS.items()
        if flags & bit
    ]


def parse_ace_flags(flags: int) -> List[str]:
    """
    This function returns human readable ACE flags from flags value.
    """

    return [name for bit, name in ACE_FLAG_MAP.items() if flags & bit]


def parse_access_mask(mask: int) -> List[str]:
    """
    This function returns human readable access flags from flags value.
    """

    return [name for bit, name in ACCESS_MASK_FLAGS.items() if mask & bit]


def parse_mft_flags(flags: int) -> List[str]:
    """
    This function returns the string values for MFT entry flags.
    """

    FLAG_MAP = {
        0x0001: "IN_USE",
        0x0002: "DIRECTORY",
        0x0004: "SYSTEM",
        0x0008: "NOT_INDEXED",
    }
    return [name for bit, name in FLAG_MAP.items() if flags & bit]


def parse_attribute_flags(flags: int) -> List[str]:
    """
    This function returns the string values for MFT attribute flags.
    """

    ATTR_FLAGS = {
        0x0001: "COMPRESSED",
        0x4000: "ENCRYPTED",
        0x8000: "SPARSE",
    }
    return [name for bit, name in ATTR_FLAGS.items() if flags & bit]


def get_mft_entry_size(value: int, cluster_size: int) -> int:
    """
    This function returns the MFT entry size.
    """

    if value < 0:
        return 2 ** abs(value)
    else:
        return value * cluster_size


def walk_attributes(
    data: bytes,
    mft_entry: MFTEntryHeader,
    entry_offset: int,
    cluster_size: int,
    file: BufferedReader,
    ntfs_offset: int,
) -> None:
    """
    This function loops over one entry attributes.
    """

    offset = entry_offset
    attribute_header = AttributeHeader.from_buffer_copy(
        data[offset : offset + sizeof(AttributeHeader)]
    )

    while attribute_header.type_id != 0xFFFFFFFF:
        if attribute_header.non_resident == 0:
            # resident = ResidentAttribute.from_buffer_copy(data[offset + sizeof(AttributeHeader):])
            attribute_header = AttributeHeaderResident.from_buffer_copy(
                data[offset : offset + sizeof(AttributeHeaderResident)]
            )
            # value_offset = offset + resident.value_offset
            attribute_header.value_offset = (
                offset + attribute_header.attr_offset
            )
            attribute_header.data = data[
                attribute_header.value_offset : attribute_header.value_offset
                + attribute_header.attr_length
            ]
        else:
            # nonresident = NonResidentAttribute.from_buffer_copy(data[offset + sizeof(AttributeHeader):])
            attribute_header = AttributeHeaderNonResident.from_buffer_copy(
                data[offset : offset + sizeof(AttributeHeaderNonResident)]
            )
            attribute_header.value_offset = (
                offset + attribute_header.data_run_offset
            )
            attribute_header.data_runs_data = data[
                attribute_header.value_offset :
            ]
            attribute_header.parse_data_runs(cluster_size)

        if attribute_header.type_id == 0x10:
            parse_standard_information(attribute_header, file, ntfs_offset)
        elif attribute_header.type_id == 0x20:
            parse_attribute_list(attribute_header, file, ntfs_offset)
        elif attribute_header.type_id == 0x30:
            parse_file_name(attribute_header, file, ntfs_offset)
        elif attribute_header.type_id == 0x50:
            parse_security_descriptor(attribute_header, file, ntfs_offset)

        attribute_header.offset = offset
        attribute_header.name = ATTRIBUTE_TYPES.get(
            attribute_header.type_id, hex(attribute_header.type_id)
        )
        mft_entry.attributes.append(attribute_header)
        offset += attribute_header.length

        if data[offset : offset + 4] == b"\xff\xff\xff\xff":
            break

        attribute_header = AttributeHeader.from_buffer_copy(
            data[offset : offset + sizeof(AttributeHeader)]
        )


def parse_mft() -> Tuple[BufferedReader, MFTEntryHeader, int]:
    """
    This function parses the MFT from the disk, using NTFS
    partition and VBR (first sector).
    """

    file, vbr, ntfs_offset = ntfs_parse()
    cluster_size = vbr.bytes_per_sector * vbr.sectors_per_cluster
    mft_offset_bytes = ntfs_offset + (vbr.mft_lcn * cluster_size)
    mft_entry_size = get_mft_entry_size(
        vbr.clusters_per_mft_record, cluster_size
    )

    file.seek(mft_offset_bytes)
    data = file.read(mft_entry_size)

    mft_entry = MFTEntryHeader.from_buffer_copy(data)
    mft_entry.attributes = []
    walk_attributes(
        data,
        mft_entry,
        mft_entry.first_attr_offset,
        cluster_size,
        file,
        ntfs_offset,
    )

    return file, mft_entry, ntfs_offset


def get_mft_content(
    file: BufferedReader, mft_entry: MFTEntryHeader, ntfs_offset: int
) -> bytearray:
    """
    This generator yields MFT content blocks.
    """

    for attribute in mft_entry.attributes:
        if attribute.type_id == 0x80 and attribute.non_resident:
            yield from attribute.read_data_runs(file, ntfs_offset)


def print_mft(mft: MFTEntryHeader) -> None:
    """
    This function prints the MFT values.
    """

    print("[+] MFT Entry Detected")
    print(f"  Signature:              {bytes(mft_entry.signature).decode()}")
    print(f"  Fixup offset:           {mft_entry.fixup_offset}")
    print(f"  Fixup entries:          {mft_entry.fixup_entries}")
    print(f"  Log sequence number:    {mft_entry.log_seq_number}")
    print(f"  Sequence #:             {mft_entry.sequence_number}")
    print(f"  Hard Links:             {mft_entry.hard_link_count}")
    print(f"  First attribute offset: {mft_entry.first_attr_offset}")
    print(f"  Flags:                  {hex(mft_entry.flags)}")
    if mft_entry.flags:
        print("     ", ", ".join(parse_mft_flags(mft_entry.flags)))
    print(f"  Used entry size:        {mft_entry.used_entry_size}")
    print(f"  Allocated entry size:   {mft_entry.allocated_entry_size}")
    print(f"  Next attribute ID:      {mft_entry.next_attr_id}")
    print(f"  MFT Record #:           {mft_entry.mft_record_number}")

    for attribute in mft_entry.attributes:
        non_resident = bool(attribute.non_resident)
        print(f"\n[+] Attribute detected: {attribute.name} at offset {attribute.offset}")
        print(f"  Type ID:                      {attribute.type_id}")
        print(f"  Length:                       {attribute.length}")
        print(f"  Non-resident:                 {non_resident}")
        print(f"  Name length:                  {attribute.name_length}")
        print(f"  Name offset:                  {attribute.name_offset}")
        print(f"  Flags:                        {hex(attribute.flags)}")
        if attribute.flags:
            print("     ", ", ".join(parse_attribute_flags(attribute.flags)))
        print(f"  Attribute ID:                 {hex(attribute.attribute_id)}")

        if non_resident:
            print(f"  Starting VCN:                 {attribute.starting_vcn}")
            print(f"  Last VCN:                     {attribute.last_vcn}")
            print(f"  Non-resident DATA run offset: {attribute.data_run_offset}")
            print(f"  Compression unit size:        {attribute.compression_unit_size}")
            print(f"  Reserved:                     {attribute.reserved}")
            print(f"  Allocated size:               {attribute.allocated_size}")
            print(f"  Real size:                    {attribute.real_size}")
            print(f"  Initialized size:             {attribute.initialized_size}")
            print(f"  Size:                         {attribute.size}")
        else:
            print(f"  Resident value length:        {attribute.attr_length}")
            print(f"  Value offset:                 {attribute.attr_offset}")
            print(f"  Indexed flag:                 {bool(attribute.indexed_flag)} (fast lookup: map $FILE_NAME in the $I30 index to the MFT entry for big directory)")
            print(f"  Padding:                      {attribute.padding}")
            print(f"  Value (hex):                  {attribute.data.hex()}")

        if getattr(attribute, "parsing", None):
            if isinstance(attribute.parsing, list):
                parsing_indent = "\n    " + "\n".join(
                    (str(x) for x in attribute.parsing)
                ).replace("\n", "\n    ")
            else:
                parsing_indent = "\n  " + str(attribute.parsing).replace(
                    "\n", "\n  "
                )
            print(f"  Value parsed: {parsing_indent}")


def mft_extract(
    file: BufferedReader, mft_entry: MFTEntryHeader, ntfs_offset: int
) -> None:
    """
    This function extracts the full MFT file content.
    """

    with open("$MFT", "wb") as mft_extract:
        for block in get_mft_content(file, mft_entry, ntfs_offset):
            mft_extract.write(block)


def main() -> int:
    """
    The main function to starts the script from the command line.
    """

    print(copyright)

    file, mft_entry, ntfs_offset = parse_mft()

    if mft_entry.signature != b"FILE":
        print("Invalid MFT entry signature.")
        return 1

    print_mft(mft_entry)
    mft_extract(file, mft_entry, ntfs_offset)

    return 0


if __name__ == "__main__":
    exit(main())
