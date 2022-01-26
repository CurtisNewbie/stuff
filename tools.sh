#!/bin/bash

function echo_red() {
    echo $'\e[0;31m'"$1"$'\e[0m'
}

function echo_green() {
    echo $'\e[0;32m'"$1"$'\e[0m'
}

function mcompile() {
    if [ ! -z $1 ]
    then
        if [ ! -f "$1/pom.xml" ]; then
            echo_red ">>> $1/pom.xml is not found, aborted"
        else
            mvn clean compile -f $1 
        fi
    else
        if [ ! -f "pom.xml" ]; then

            echo_red ">>> pom.xml is not found, aborted"
        else
            mvn clean compile 
        fi  
    fi
}

function minstall() {
    if [ ! -z $1 ]
    then
        if [ ! -f "$1/pom.xml" ]; then
            echo_red ">>> $1/pom.xml is not found, aborted"
        else
            mvn clean install -f $1 
        fi
    else
        if [ ! -f "pom.xml" ]; then
            echo_red ">>> pom.xml is not found, aborted"
        else
            mvn clean install 
        fi
    fi
}

function mtest() {
    if [ ! -z $1 ]
    then
        if [ ! -f "$1/pom.xml" ]; then
            echo_red ">>> $1/pom.xml is not found, aborted"
        else
            mvn clean test -f $1 
        fi
    else
        if [ ! -f "pom.xml" ]; then
            echo_red ">>> pom.xml is not found, aborted"
        else
            mvn clean test  
        fi
    fi
}

function cmtrecklessly() {
    git add .

    #Set the field separator to new line
    IFS=$'\n'

    msg=`git diff --staged --raw`
    lines=""

    for line in $msg; do
        t="${line:31:1}"
        s_line="${line:33}"$'\n'
        t_name=""

        if [ $t == 'M' ]; then
            t_name="Modified" 
        elif [ $t == 'A' ]; then
            t_name="Added"
        else 
            t="${line:31:4}"
            if [ $t == "R092" ]; then
                t_name="Renamed"
                s_line="${line:36}"$'\n'
            fi
        fi

        lines+="$t_name: $s_line"
    done

    git commit -m "$lines"
    if [ $? -eq 0 ]; then
        echo_green ">>> you recklessly committed a change"
    fi
}

function reloadrc() {
    source ~/.bashrc
    echo_green ">>> reloaded bashrc :D"
}

# check whether $1 is in master branch, return 1-true, 0-false
function is_master(){

    if [ -z "$1" ]; then 
        echo 0 
        return 0
    fi

    status=`git status | grep "On branch master"`
    if [ ! -z "$status" ] && [ "$status" != "" ]; then
        echo 1 
    else 
        echo 0
    fi
    return 0 
}

function check(){
    debug=0
    fetch=0
    pull=0

    if [ ! -z "$2" ]; then
        if [ "$2" == "--debug" ]; then
            debug=1
            # echo_green "--debug mode turned on"
        elif [ "$2" == "--fetch" ]; then
            fetch=1
            # echo_green "--fetch mode turned on"
        elif [ "$2" == "--pull" ]; then
            pull=1
            # echo_green "--pull mode turned pn"
        fi
    fi

    if [ ! -z "$1" ]; then
        (
            cd "$1"

            if [ $debug -eq 1 ]; then 
                echo_green "debug: cd $1"
            fi

            # not a git repo
            if [ ! -d ".git" ]; then
                return 0
            fi

            if [ $fetch -eq 1 ]; then
                # always fetch first, but we don't print the result
                git fetch &> /dev/null            

                exit_if_failed $? "failed to fetch from remote"

                if [ $debug -eq 1 ]; then 
                    echo_green "debug: git fetch in $1"
                fi

            fi

            status=`git status`

            if [ $debug -eq 1 ]; then 
                echo_green "called git status in $1"
            fi

            # check whether repo is up-to-date
            utd=`echo $status | grep "Your branch is up to date"`
            if [ -z "$utd" ] || [ "$utd" == "" ]; then
                echo_red "found changes from upstream repository in $1"
                master=`is_master $1`

                if [ $pull -eq 1 ] && [ $master -eq 1 ] ; then
                    echo_green "pulling changes from upstream"
                    git pull
                fi
            fi        
            
            # find uncommited changes
            tbc=`echo $status | grep 'Changes to be committed'`
            if [ ! -z "$tbc" ] && [ "$tbc" != "" ]; then
                echo_red "found uncommited changes in $1"
            fi  
            
            # find untracked files 
            utf=`echo $status | grep 'Untracked files'`
            if [ ! -z "$utf" ] && [ "$utf" != "" ]; then
                echo_red "found untracked files in $1"
            fi
 
            # find changes not staged
            changes=`echo $status | grep 'Changes not staged'`
            if [ ! -z "$changes" ] && [ "$changes" != "" ]; then            
                echo_red "found uncommited changes in $1"
            fi

            # find commits not pushed
            commits=`echo $status | grep 'Your branch is ahead of'`
            if [ ! -z "$commits" ] && [ "$commits" != "" ]; then            
                echo_red "found commits not yet pushed in $1"
            fi

            if [ $debug -eq 1 ]; then 
                echo_green "debug: finished checking $1"
            fi
        )
    fi

}

# scan repo for uncommited changes, use --fetch to fetch each repo
function repocheck () {
    find . -maxdepth 2 -type d ! -name "*.git" | while read line; do
        abs_path="$(pwd)/${line:2}"

        # non-hidden directories
        if [ "${line:0}" != "." ]; then
            if [ ! -z $1 ]; then
                check "$abs_path" "$1"
            else
                check "$abs_path"
            fi
        fi
    done
} 

# fetch and pull
function gfp () {
    echo_green "Fetching..."
    git fetch;
    echo_green "Pulling..."
    git pull;
}

# [0]: process exit value, [1]: error message
function exit_if_failed() {
    if [ ! $1 -eq 0 ]; then
        echo_red $2
        return 1;
    fi
}

function reset_one() {
    read -p "sure you want to reset one commit? [y] "
    ans=$REPLY

    if [ -z $ans ] || [ $ans != 'y' ] || [ ! $ans != 'Y' ]; then
        echo_green "aborting ..."
        return 1
    fi

    git reset --soft HEAD~1
    git restore --staged .
    echo_green "git resetted one commit"
    git status 
}

function ps_grep(){
    ps -ef | grep $1 | grep -v grep
}



