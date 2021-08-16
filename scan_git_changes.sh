#!/bin/bash

function scan_git_changes {
    find . -maxdepth 2 -type d ! -name "*.git" | while read line; do
        abs_path="`readlink -e $line`"
        check "$abs_path"
    done
}

function check {
    if [ ! -z "$1" ]
    then
        (
        cd "$1"
        if [ -d ".git" ] 
        then
            status=`git status`
            changes=`echo $status | grep 'Changes not staged'`
            if [ ! -z "$changes" ] && [ "$changes" != "" ]            
            then
                echo "Found uncommited changes in $1"
            fi

            commits=`echo $status | grep 'Your branch is ahead of'`
            if [ ! -z "$commits" ] && [ "$commits" != "" ]            
            then
                echo "Found commits not yet pushed in $1"
            fi
        fi
        )
    fi

}

scan_git_changes
