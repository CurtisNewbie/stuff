# Windows install

## Steps

1. Download windows iso, e.g., from https://massgrave.dev/windows_10_links
2. Install https://github.com/TechUnRestricted/WinDiskWriter (for macos)
3. Prepare a USB stick, and use WinDiskWriter to create the boot image
4. Insert the USB stick, turn on the computer and install whichever version we want
5. Execute script from [MAS](https://github.com/massgravel/Microsoft-Activation-Scripts), which is essentially:
    ```
    irm https://get.activated.win | iex

    # with proxy
    irm -Proxy http://xxxx:1087 https://get.activated.win | iex
    ```
6. Good to go

## Sources

- https://github.com/massgravel/Microsoft-Activation-Scripts
- https://massgrave.dev/
- https://github.com/TechUnRestricted/WinDiskWriter
- https://gist.github.com/hungneox/1831e86982f7d8ee430f4b594fa4f223