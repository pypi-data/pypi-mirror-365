![DiskAnalyzer Logo](https://mauricelambert.github.io/info/python/security/DiskAnalyzer/DiskAnalyzer_small.png "DiskAnalyzer logo")

# DiskAnalyzer

## Description

This package implements multiples libraries and tools to parse, analyze
and extract informations from disk on the live system.

 - Pure python package
 - Running on live Windows system
 - Analyze MBR (Master Boot Record) and GPT (GUID Partition Table)
 - List partitions
 - Analyze VBR (Volume Boot Record) for NTFS partition (New Technology File System)
 - Analyze MFT file and attribute (Master File Table)
 - Extract MFT file
 - Analyze ExFAT Boot Sector
 - Repair MBR for non bootable disk and MFT/ExFAT partitions (using disk carving)

## Requirements

This package require:
 - python3
 - python3 Standard Library

## Installation

### Pip

```bash
python3 -m pip install DiskAnalyzer
```

### Git

```bash
git clone "https://github.com/mauricelambert/DiskAnalyzer.git"
cd "DiskAnalyzer"
python3 -m pip install .
```

### Wget

```bash
wget https://github.com/mauricelambert/DiskAnalyzer/archive/refs/heads/main.zip
unzip main.zip
cd DiskAnalyzer-main
python3 -m pip install .
```

### cURL

```bash
curl -O https://github.com/mauricelambert/DiskAnalyzer/archive/refs/heads/main.zip
unzip main.zip
cd DiskAnalyzer-main
python3 -m pip install .
```

## Usages

### Command line

```bash
DiskAnalyzer              # Using CLI package executable
python3 -m DiskAnalyzer   # Using python module
python3 DiskAnalyzer.pyz  # Using python executable
DiskAnalyzer.exe          # Using python Windows executable

NtfsAnalyzer              # Using CLI package executable
python3 -m NtfsAnalyzer   # Using python module
python3 NtfsAnalyzer.pyz  # Using python executable
NtfsAnalyzer.exe          # Using python Windows executable

MftAnalyzer               # Using CLI package executable
python3 -m MftAnalyzer    # Using python module
python3 MftAnalyzer.pyz   # Using python executable
MftAnalyzer.exe           # Using python Windows executable
```

### Python script

```python
from DiskAnalyzer import *

print(disk_parsing().to_partition())

file, vbr, ntfs_offset = ntfs_parse()
file.close()

with open("$MFT", "rb") as file:
    for data in get_mft_content():
        file.write(data)
```

## Links

 - [Pypi](https://pypi.org/project/DiskAnalyzer)
 - [Github](https://github.com/mauricelambert/DiskAnalyzer)
 - [DiskAnalyzer - Documentation](https://mauricelambert.github.io/info/python/security/DiskAnalyzer/DiskAnalyzer.html)
 - [DiskAnalyzer - Python executable](https://mauricelambert.github.io/info/python/security/DiskAnalyzer/DiskAnalyzer.pyz)
 - [DiskAnalyzer - Python Windows executable](https://mauricelambert.github.io/info/python/security/DiskAnalyzer/DiskAnalyzer.exe)
 - [NtfsAnalyzer - Documentation](https://mauricelambert.github.io/info/python/security/DiskAnalyzer/NtfsAnalyzer.html)
 - [NtfsAnalyzer - Python executable](https://mauricelambert.github.io/info/python/security/DiskAnalyzer/NtfsAnalyzer.pyz)
 - [NtfsAnalyzer - Python Windows executable](https://mauricelambert.github.io/info/python/security/DiskAnalyzer/NtfsAnalyzer.exe)
 - [MftAnalyzer - Documentation](https://mauricelambert.github.io/info/python/security/DiskAnalyzer/MftAnalyzer.html)
 - [MftAnalyzer - Python executable](https://mauricelambert.github.io/info/python/security/DiskAnalyzer/MftAnalyzer.pyz)
 - [MftAnalyzer - Python Windows executable](https://mauricelambert.github.io/info/python/security/DiskAnalyzer/MftAnalyzer.exe)

## License

Licensed under the [GPL, version 3](https://www.gnu.org/licenses/).
