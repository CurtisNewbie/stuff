#!/bin/bash

# --------- remote
remote="alphaboi@curtisnewbie.com"
service="event-pump"
remote_build_path="~/services/${service}/build/"
remote_config_path="~/services/${service}/config/"
os="linux"
arch="amd64"
build="${service}_build"
dockerfile="./Dockerfile_local"
# ---------

set -e

(
    cd $GIT_PATH/event-pump

    # dashboard frontend
    ( cd front/dashboard && ./build_moon.sh )

    echo "Building Go app for platform $os/$arch to binary '$build'"
    CGO_ENABLED=0 GOOS="$os" GOARCH="$arch" go build -o "$build"

    ssh  "alphaboi@curtisnewbie.com" "rm -rv ${remote_build_path}*"

    rsync -av -e ssh ./conf-prod.yml "${remote}:${remote_config_path}/conf.yml"
    if [ ! $? -eq 0 ]; then
        exit -1
    fi

    rsync -av -e ssh "./$build" "${remote}:${remote_build_path}"
    if [ ! $? -eq 0 ]; then
        exit -1
    fi

    rsync -av -e ssh "./$dockerfile" "${remote}:${remote_build_path}/Dockerfile"
    if [ ! $? -eq 0 ]; then
        exit -1
    fi

    ssh  "alphaboi@curtisnewbie.com" "cd services; docker-compose up -d --build ${service}"

    # cleanup
    if [ -f "$build" ]; then
        rm "$build"
    fi

)