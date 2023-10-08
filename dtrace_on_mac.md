# dtrace on mac

Seems like this doesn't work?

- src: https://stackoverflow.com/questions/33476432/is-there-a-workaround-for-dtrace-cannot-control-executables-signed-with-restri

```
1. Boot your Mac into Recovery Mode: reboot it and hold cmd+R until a progress bar appears.
2. Go to Utilities menu. Choose Terminal there.

$ csrutil clear # restore the default configuration first
$ csrutil enable --without dtrace # disable dtrace restrictions *only*
```


