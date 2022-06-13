#!/bin/bash

go env -w GO111MODULE=on

# go env -w  GOPROXY=https://goproxy.cn,direct
# go env -w  GOPROXY=https://goproxy.io,direct

go env -w GOPROXY=https://mirrors.aliyun.com/goproxy/,direct

# finished
go env | grep GOPROXY

### ---- unset
# go env -u GO111MODULE
# go env -u GOPROXY
### ---------
