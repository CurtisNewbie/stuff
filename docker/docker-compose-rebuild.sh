#!/bin/bash

function rebuild () {
    if [ -z $1 ]; then
        echo "Must specify service name"
        return 1;
    fi
    # docker-compose up -d --no-deps --build $1
    docker-compose up -d --build $1 
} 

rebuild $1
