# mc-downloader

This is a python package design to download Minecraft servers files from Mojang servers.

The downloader verify integrity from mojang servers after download.

If the files have already been downloaded, they are rechecked, and if necessary they are re-downloaded.

## Installation

You need to install the package from pypi repository.

```bash
pip install mc-downloader
```

## Utilisation example

```python
import os
import mcdwld

def main():
    """Download all servers."""
    downloads_directory = os.getcwd() + '/downloads/'
    versions = mcdwld.get_versions(mcdwld.MOJANG_MANIFEST_URL)
    mcdwld.download_versions(versions, downloads_directory)

if __name__ == '__main__':
    main()
```
