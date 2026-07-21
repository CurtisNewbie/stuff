#!/bin/bash

(
    cd $GIT_PATH/moon-monorepo/frontend/moon

    remote="alphaboi@curtisnewbie.com"
    remote_path="/home/alphaboi/services/nginx/html/bolobao/"

    NODE_OPTIONS=--openssl-legacy-provider ng build --prod

    # Package dist as single archive (faster than scp -r of many files)
    COPYFILE_DISABLE=1 tar czf dist.tar.gz -C dist/moon .
    scp dist.tar.gz "${remote}:${remote_path}"
    ssh "${remote}" "cd ${remote_path} && tar xzf dist.tar.gz 2>/tmp/tar_stderr.\$\$ && rm dist.tar.gz; grep -v 'LIBARCHIVE.xattr' /tmp/tar_stderr.\$\$ >&2; rm -f /tmp/tar_stderr.\$\$"
    rm dist.tar.gz
)