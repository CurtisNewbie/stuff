# Mount to an Iphone on Linux

Install packagse

```sh
sudo apt install libimobiledevice6 libimobiledevice-utils ifuse
```

Pair Iphone (May require extra confirm on the phone)

```sh
sudo idevicepair pair
```

Mount to a local dir (should be created beforehand)

```sh
ifuse ~/iphonemnt 
```

Unmount the directory

```sh
fusermount -u ~/iphonemnt
```

Unpair Iphone

```sh
idevicepair unpair
```
