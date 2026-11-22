#!/bin/bash

# Builds the linux binary, copies it to the server, installs the systemd unit
# the first time, and restarts the service. No Dockerfile, no container rebuild.
#
# First run: creates ~/services/homeproxy/, installs conf.yml from conf-prod.yml
# (only when the server has none), writes /etc/systemd/system/homeproxy.service
# and enables it. Later runs: replaces the binary and restarts the unit. A unit
# or conf.yml that already exists on the server is never overwritten.

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
    remote_user="${remote%@*}"
    unit_path="/etc/systemd/system/${service}.service"

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

    # systemd unit: install once, leave an existing one alone
    if ! ssh "$remote" "test -f ${unit_path}"; then
        echo "--- Installing ${unit_path}"
        ssh "$remote" "sudo tee ${unit_path} >/dev/null" <<EOF
[Unit]
Description=${service} forward HTTP proxy
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${remote_user}
WorkingDirectory=${remote_path}
ExecStart=${remote_path}${build} configFile=${remote_path}conf.yml
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
        if [ ! $? -eq 0 ]; then
            echo "cannot write ${unit_path}"
            exit -1
        fi
        ssh "$remote" "sudo systemctl daemon-reload && sudo systemctl enable ${service}"
        if [ ! $? -eq 0 ]; then
            exit -1
        fi
    fi

    ssh "$remote" "sudo systemctl restart ${service}"
    if [ ! $? -eq 0 ]; then
        echo "restart failed: sudo systemctl status ${service}"
        exit -1
    fi

    ssh "$remote" "sudo systemctl --no-pager --lines=5 status ${service}"

    # cleanup
    if [ -f "$build" ]; then
        rm "$build"
    fi
)