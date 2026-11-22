#!/bin/bash

# Builds the linux binary and deploys it as a container, like the other services:
# the binary and its Dockerfile go to ~/services/homeproxy/build/, then the
# compose project in ~/services rebuilds and restarts the service.
#
# The config is NOT copied or created here. It belongs on the server at the path
# below and is mounted into the container read-only; this script only reminds you
# where that is.

# --------- remote
remote="alphaboi@curtisnewbie.com"
service="homeproxy"
remote_build_path="~/services/${service}/build/"
remote_config_path="~/services/${service}/config/conf.yml"
os="linux"
arch="amd64"
build="${service}_build"
dockerfile="./Dockerfile"
# ---------

(
    n=$(date "+%Y-%m-%d %H:%M:%S")
    echo "--- Building $service $n"

    cd "$GIT_PATH/homeproxy"
    if [ ! $? -eq 0 ]; then
        echo "cannot cd to \$GIT_PATH/homeproxy"
        exit -1
    fi

    echo "Building Go app for platform $os/$arch to binary '$build'"
    CGO_ENABLED=0 GOOS="$os" GOARCH="$arch" go build -o "$build" .
    if [ ! $? -eq 0 ]; then
        exit -1
    fi

    ssh "$remote" "mkdir -p ${remote_build_path} && rm -rf ${remote_build_path}*"
    if [ ! $? -eq 0 ]; then
        exit -1
    fi

    rsync -av -e ssh "./$build" "${remote}:${remote_build_path}"
    if [ ! $? -eq 0 ]; then
        exit -1
    fi

    rsync -av -e ssh "$dockerfile" "${remote}:${remote_build_path}Dockerfile"
    if [ ! $? -eq 0 ]; then
        exit -1
    fi

    # Read-only check, no write: it only tells you whether the mount point exists.
    if ! ssh "$remote" "test -f ${remote_config_path}"; then
        echo "--- WARNING: ${remote_config_path} does not exist"
        echo "--- Put your conf.yml there; it is mounted at /usr/src/config/conf.yml"
    fi

    ssh "$remote" "cd services; docker-compose up -d --build ${service}"
    if [ ! $? -eq 0 ]; then
        echo "compose rebuild failed: cd ~/services && docker-compose up -d --build ${service}"
        exit -1
    fi

    echo "--- Config in use: ${remote_config_path}"

    # cleanup
    if [ -f "$build" ]; then
        rm "$build"
    fi
)