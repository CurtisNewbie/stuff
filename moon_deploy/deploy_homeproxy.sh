#!/bin/bash

# Builds the linux binary and deploys it as a container, like the other services:
# the binary and its Dockerfile go to ~/services/homeproxy/build/, conf.yml to
# ~/services/homeproxy/config/, then the compose project in ~/services rebuilds
# and restarts the service.
#
# conf.yml is seeded from conf-prod.yml only when the server has none, so an
# edited copy on the server is never overwritten.

# --------- remote
remote="alphaboi@curtisnewbie.com"
service="homeproxy"
remote_build_path="~/services/${service}/build/"
remote_config_path="~/services/${service}/config/"
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

    ssh "$remote" "mkdir -p ${remote_build_path} ${remote_config_path} && rm -rf ${remote_build_path}*"
    if [ ! $? -eq 0 ]; then
        exit -1
    fi

    # conf.yml: seed it once, never overwrite an edited copy
    if ! ssh "$remote" "test -f ${remote_config_path}conf.yml"; then
        echo "--- Seeding ${remote_config_path}conf.yml from conf-prod.yml"
        rsync -av -e ssh ./conf-prod.yml "${remote}:${remote_config_path}conf.yml"
        if [ ! $? -eq 0 ]; then
            exit -1
        fi
        echo "--- Edit ${remote_config_path}conf.yml on the server (trusted-clients, users, pac.*)"
    fi

    rsync -av -e ssh "./$build" "${remote}:${remote_build_path}"
    if [ ! $? -eq 0 ]; then
        exit -1
    fi

    rsync -av -e ssh "$dockerfile" "${remote}:${remote_build_path}Dockerfile"
    if [ ! $? -eq 0 ]; then
        exit -1
    fi

    ssh "$remote" "cd services; docker-compose up -d --build ${service}"
    if [ ! $? -eq 0 ]; then
        echo "compose rebuild failed: cd ~/services && docker-compose up -d --build ${service}"
        exit -1
    fi

    # cleanup
    if [ -f "$build" ]; then
        rm "$build"
    fi
)