#!/bin/bash

(
    cd $GIT_PATH/moon-monorepo/frontend/moon

    remote="alphaboi@curtisnewbie.com"
    remote_path="/home/alphaboi/services/nginx/html/bolobao/"

    NODE_OPTIONS=--openssl-legacy-provider ng build --prod;
    scp -r ./dist/moon/* "${remote}:${remote_path}"
)