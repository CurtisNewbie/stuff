# Trust self-signed certificate on Linux

ref: https://unix.stackexchange.com/questions/90450/adding-a-self-signed-certificate-to-the-trusted-list

```sh
sudo cp my.crt /usr/share/ca-certificates/
sudo update-ca-certificates
```
