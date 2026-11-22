#!/bin/bash

# Builds the linux binary and copies it to the server. No Dockerfile, no
# container rebuild, no systemd calls: the unit is expected to exist and the
# restart is left to the operator.
#
# conf.yml is seeded from conf-prod.yml only when the server has none, so an
# edited copy on the server is never overwritten.

# --------- remote
remote="alphaboi@curtisnewbie.com"
service="homeproxy"
os="linux"
arch="amd64"
build="${service}_build"
# ---------

(
    n=$(date "+%Y-%m-%d %H:%M:%S")
    echo "--- Building $service $n"

    remote_home=$(ssh "$remote" 'echo $HOME')
    if [ -z "$remote_home" ]; then
        echo "cannot resolve the remote home directory"
        exit -1
    fi
    remote_path="${remote_home}/services/${service}/"

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

    ssh "$remote" "mkdir -p ${remote_path}"
    rsync -av -e ssh "./$build" "${remote}:${remote_path}"
    if [ ! $? -eq 0 ]; then
        exit -1
    fi

    # conf.yml: seed it once, never overwrite an edited copy
    if ! ssh "$remote" "test -f ${remote_path}conf.yml"; then
        echo "--- Seeding ${remote_path}conf.yml from conf-prod.yml"
        rsync -av -e ssh ./conf-prod.yml "${remote}:${remote_path}conf.yml"
        if [ ! $? -eq 0 ]; then
            exit -1
        fi
        echo "--- Edit ${remote_path}conf.yml on the server (credentials, trusted-clients, pac.*)"
    fi

    echo "--- Binary deployed to ${remote}:${remote_path}${build}"

    # cleanup
    if [ -f "$build" ]; then
        rm "$build"
    fi
)