#!/bin/bash
# colours https://www.shellhacks.com/bash-colors/

colour_reset=$'\e[0m'
red=$'\e[1;31m'
green=$'\e[1;32m'
yellow=$'\e[1;33m'
cyan=$'\e[1;36m'
trash_can="$HOME/tmp"

# complete -W "-r" gbranch 
complete -F _gbranch_completion gbranch 
complete -F _reset_one_completion reset_one 


_gbranch_completion()
{
    if [ ${#COMP_WORDS[@]} -gt 2 ]; then
        return
    fi

    COMPREPLY=("-r")
}

_reset_one_completion()
{
    if [ ${#COMP_WORDS[@]} -gt 2 ]; then
        return
    fi

    COMPREPLY=("--y")
}

function trm() {
    if [ -z $1 ]; then
        echo_red "please specify file to remove"
    fi

    trash_can_p=$(readlink -e "$trash_can")
    echo "Trash can path: $trash_can_p"

    if [ ! -d $trash_can_p ]; then
        mkdir $trash_can_p 
    fi

    mv $1 $trash_can_p 
    echo_green "Moved $1 to $trash_can_p"
}

function gstashpop() {
    git stash pop
}

function mpackage() {
    mvn package 
}

function gcb() {
    if [ -z $1 ]; then
        echo_red "please enter branch name" 
        return 1;
    fi

    git checkout -b $1
}

function gp() {
    git pull
}

function gshow() {
    git show "$@"
}

function gmerge() {
    git merge "$@"
}

function guntrack() {
    git rm --cache "$@"
}

function mclean() {
    mvn clean
}

function mresolve() {
    mvn dependency:resolve
}

function gadd() {

    if [ ! -z "$1" ]; then
        git add "$@"
    else 
        git add .
    fi
}
    
function grestore() {
    git restore --staged "$@"
}

function gclone() {
    git clone $1
}

function gstash() {
    git add .
    git stash
}

function gf() {
    git fetch
}

function gpush() {
    git push "$@"
}

function glike() {
    git branch -l | grep "$@"
    git branch -r | grep "$@"
}

function gbranch() {
    extra="-l"
    if [ $# -gt 0 ]; then
        extra="$@"
    fi

    git branch $extra
}

function gamd() {
    git commit --amend 
}

function gswitch() {
    git switch "$1"
}

function gcmt() {

    msg="$1"

    git add .

    if [ -z "$msg" ]; then
        git commit
    else
        git commit -m "$msg"
    fi
}

function gl() {

    extra=""
    if [ $# -gt 0 ]; then
        extra="$@"
    fi

    git log $extra
}

function gs() {
    git status
}

function gd() {
    extra=""
    if [ $# -gt 0 ]; then
        extra="$@"
    fi

    git diff $extra
}

function gds() {
    git diff --staged
}

function installall(){
    find . -maxdepth 2 -type d | while read dir; do 
    if [ -f "$dir/pom.xml" ]; then 
        mvn clean install -f "$dir/pom.xml" 
    fi
    done
}

function diskusage() {
    du -d 1 -h
}

function echo_red() {
    echo $red"$1"$colour_reset
}

function echo_green() {
    echo $green"$1"$colour_reset
}

function echo_yellow() {
    echo $yellow"$1"$colour_reset

}

function echo_cyan() {
    echo $cyan"$1"$colour_reset
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
            mvn clean install -f $1 -Dmaven.test.skip=true -DadditionalJOption=-Xdoclint:none
        fi
    else
        if [ ! -f "pom.xml" ]; then
            echo_red ">>> pom.xml is not found, aborted"
        else
            mvn clean install -Dmaven.test.skip=true -DadditionalJOption=-Xdoclint:none
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

function rkcmt() {
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
        elif [ $t == 'D' ]; then
            t_name="Deleted"
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

function check() {
    debug=0
    fetch=0
    pull=0

    if [ ! -z "$2" ]; then
        if [ "$2" == "--debug" ]; then
            debug=1
            # echo_green "--debug mode turned on"
        elif [ "$2" == "--fetch" ]; then
            fetch=1 # echo_green "--fetch mode turned on"
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
    msg=`git fetch 2>&1`

    if [ $? -ne 0 ]; then 
        echo_red "$msg"
        return 1
    fi

    echo_green "Pulling..."
    git pull;
}

# [0]: command return value ($?), [1]: error message
function exit_if_failed() {
    if [ $1 -ne 0 ]; then
        if [ ! -z $2 ]; then
            echo_red $2
        fi
        return 1;
    fi
}

function last_weekly_report(){

    (cd $1

    # echo "pwd:" `pwd`

    #Set the field separator to new line
    IFS=$'\n'

    arr=($(for fname in `ls`; do
        suffix="${fname#*-}"
        echo "${suffix%*.md}"
    done | sort -n))

    # echo "arr: ${arr[@]}"

    len=${#arr[@]}
    if [ $len -eq 0 ]; then
        echo 0
        return 0
    fi

    last_idx=`expr $len - 1`
    # echo "last_idx: " $last_idx

    last_num=${arr[$last_idx]}
    echo `expr $last_num + 1`
    )
}

# generate a new weekly report
function gen_weekly_report(){
    if [ -z $1 ]; then
        echo_red "please specify base path first..."
        return 1;
    fi

    base=$1
    num=`last_weekly_report $base`
    target=$base/week-$num.md

    if [ -f $target ]; then
        echo_red "file: '$target' exists, aborting..."
        return 1;
    fi

    touch $target
    echo_green "touched file: '$target', initializing content"

    # initialize content
    echo "# Week-$num" >> $target
    echo >> $target
    echo "## 本周完成工作" >> $target
    echo >> $target
    echo "## 本周工作总结" >> $target
    echo >> $target
    echo "## 下周工作计划" >> $target
    echo >> $target
    echo "## 需协助与帮助" >> $target
    echo >> $target
    echo "暂无" >> $target
    echo >> $target
    echo "## 备注" >> $target
    echo >> $target
    echo "暂无" >> $target
    echo >> $target
            
    echo_green "'$target' content initialized, finished" 

    # open file using vscode
    code $target  
}

# reset one git commit, '--stage' to keep files in stage area, '--y' or '--Y' to reset without confirmation
function reset_one() {

    # do we need to restre --staged
    unstage=1

    # do we need confirmation
    need_confirm=1

    for arg in "$@"; do
        if [ $arg == '--stage' ]; then  
            unstage=0
        elif [[ $arg =~ --[yY] ]]; then  
            need_confirm=0
        fi 
    done 

    if [ $need_confirm -eq 1 ]; then
        read -p "Sure you want to reset one commit? [y/Y] "
        ans=$REPLY

        if [ -z $ans ] || [[ $ans =~ [^yY] ]]; then
            echo_green "Aborting ..."
            return 1
        fi
    fi

    git reset --soft HEAD~1

    if [ $unstage -eq 1 ]; then 
        git restore --staged .
    fi

    echo_green "Resetted one git commit"
    git status 
}

function ps_grep() {
    ps -ef | grep $1 | grep -v grep
}

function pom_ver() {
    if [ -z $1 ] || [ $1 == "." ] ; then
        root=`pwd`
    else 
        root="$1"
    fi
 
    name="$root/pom.xml"
    if [ ! -f $name ]; then
        echo_red "Unable to find $name"
        return 1
    fi

    # get project.version
    ver=$(mvn -q \
    -Dexec.executable=echo \
    -Dexec.args='${project.version}' \
    --non-recursive \
    exec:exec)

    echo "'$name' Project.Version: $cyan $ver $colour_reset"
}




