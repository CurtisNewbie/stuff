#!/bin/bash

export HOMEBREW_NO_AUTO_UPDATE=1

# colours https://www.shellhacks.com/bash-colors/
# bash coloring https://gist.github.com/vratiu/9780109
colourreset=$'\e[0m'
red=$'\e[1;31m'
green=$'\e[1;32m'
yellow=$'\e[1;33m'
blue=$'\e[1;34m'
purple=$'\e[1;35m'
cyan=$'\e[1;36m'
white=$'\e[1;37m'
trash_can="$HOME/trash"

export PYTHONPATH="$PYTHONPATH:$STUFF"
export LANG=en_US.UTF-8

alias mk="minikube"
alias kb="kubectl"
alias bc="bc -l"
alias gs="git status"
alias gf="git fetch"
alias gfp="git fetch pull"
alias gp="git pull"
alias gl="git log"
alias gds="git diff --staged"
alias gd="git diff"
alias gshow="git show"
alias gpush="git push"
alias gad="git add"
alias mclean="mvn clean"
alias grest="git restore --staged"
alias grep="grep --color"
alias gcmt="git commit"
alias ag="ag -i -A 3 -B 3"
alias idea.="idea ."
alias code.="code ."
alias gck="git checkout"

# for debugging
# set -eE -o functrace

# complete -W "-r" gbranch
# complete -F _gbranch_completion gbranch
# complete -F _reset_one_completion reset_one

# trap error
function traperr(){
    trap 'print_failure ${LINENO} "$BASH_COMMAND" "$@"' ERR
}

function print_failure() {
  local lineno=$1
  local msg=$2
  echo "Failed at $lineno: $msg, extra: $3"
}

function pprint() {
    printf ' %-35s %-40s %-35s\n' "$green${1}"  "$yellow${2}$colourreset" "${cyan}${3}$colourreset"
}

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

gcld1() {
    repo="$1"
    git clone --depth 1 "$repo"
    if [ $? -eq 0 ]; then
        e="${repo##*/}"
        cd "${e%%.git}"
    fi
}

gcl() {
    repo="$1"
    git clone "$repo"
    if [ $? -eq 0 ]; then
        e="${repo##*/}"
        cd "${e%%.git}"
    fi
}

gamd() { git commit --amend; }
gdt() { git difftool "$@"; }
glike() { git branch | grep "$1"; }
gstashshow() { git stash show -p; }

function lfind() { ls -alh | grep "$1" -i; }

function brief_lfind() { ls -a | grep "$1" -i; }

function cdlfind() { cd $(brief_lfind "$1"); }

function dfind() {
    if [ $# -gt 1 ]; then
        find "$1" -type d -name "*$2*"
    else
        find . -type d -name "*$1*"
    fi
}

function ffind() {
    find . -type f -iname "*$1*" \
        -not \( -path "**/target/*" -prune \) \
        -not \( -path "**/.*/*" -prune \) \
        -not \( -path "**/node_modules/*" -prune \) \
        -not \( -path "**/dist/*" -prune \) \
        -not \( -path "**/logs/*" -prune \) \
        -not \( -path "**/log/*" -prune \) \
        -not \( -path "**/__MACOSX/*" -prune \)
}

function rfind() {
    if [ $(uname) == 'Darwin' ]; then
        find -E . -type f -regex "$1"
    else
        find -regextype posix-extended . -type f -regex "$1"
    fi
}

function trashsize() {
    if [ ! -d "$trash_can" ]; then
        echocyan "Trash can is not found"
        return 0
    fi

    size=$(cd $trash_can; du -h -d 1 . | tail -n 1)
    echocyan "$size"
}

# dump file to trash can
function trsh() {
    if [ -z $1 ]; then
        return 0
    fi

    # trash_can_p=$(readlink -e "$trash_can")
    trash_can_p="$trash_can"

    if [ ! -d $trash_can_p ]; then
        mkdir $trash_can_p
    fi
    # echo "Using trash: $trash_can_p"

    if [ -d "$1" ]; then
        cp -rf "$1" "$trash_can_p"
        rm -rf "$1"
    else
        mv "$1" "$trash_can_p"
    fi
    echogreen ">>> Trashed '$1' to '$trash_can_p'"
}


function mpackage() {
    pom=$(python3 $STUFF/findpom.py $@)
    if [ $? -ne 0 ] || [ ! -f "$pom" ]; then
        echored ">>> pom.xml is not found, aborted"
    else
        echogreen ">>> found $pom"
        mvn clean package -f $pom -Dmaven.test.skip=true -DadditionalJOption=-Xdoclint:none
    fi
}

function gpr() {
    branch=$(git status)
    if [ $? -ne 0 ]; then
        return 1
    fi

    branch=$(echo "$branch" | cut -d $'\n' -f 1)
    branch=${branch:10}
    branch=${branch%%$'\n'*}

    read -p "Creating remote branch '$branch'. To cancel: [n/N] "
    ans=$REPLY

    if [[ $ans =~ [Nn] ]]; then
      return 0
    fi

    git push -u origin "$branch"
}

function prevbranch() {
    echocyan "Previous branch was: $GSWITCH_BACK"
}

function gcb() {
    if [ -z $1 ]; then
        echored "please enter branch name"
        return 1;
    fi

    branch=$(git status)
    if [ $? -ne 0 ]; then
        return 1
    fi

    branch=$(echo "$branch" | cut -d $'\n' -f 1)
    branch=${branch:10}
    branch=${branch%%$'\n'*}

    git checkout -b $1

    if [ $? -eq 0 ]; then
        GSWITCH_BACK="$branch"
        echocyan "Previous was: $GSWITCH_BACK"
    fi
}

function guntrack() { git rm --cache "$@"; }

mresolve() {
    pom=$(python3 $STUFF/findpom.py $@)
    if [ $? -ne 0 ] || [ ! -f "$pom" ]; then
        echored ">>> pom.xml is not found, aborted"
    else
        echogreen ">>> found $pom"
        mvn dependency:resolve -f "$pom" -U
    fi
}

mresolve_src() {
    pom=$(python3 $STUFF/findpom.py)
    if [ $? -ne 0 ] || [ ! -f "$pom" ]; then
        echored ">>> pom.xml is not found, aborted"
    else
        echogreen ">>> found $pom"
        if [ $# -gt 0 ]; then
            echogreen ">>> resolving sources for '$1'"
            mvn dependency:sources -f "$pom" -DincludeArtifactIds="$1"
            mvn dependency:resolve -f "$pom" -Dclassifier=javadoc -DincludeArtifactIds="$1"
        else
            echogreen ">>> resolving sources for all dependencies"
            mvn dependency:sources -f "pom"
            mvn dependency:resolve -f "$pom" -Dclassifier=javadoc
        fi
    fi
}

function curr_branch() {
    # On branch xxx
    branch=$(git status)
    if [ $? -ne 0 ]; then
        return 1
    fi

    branch=$(echo "$branch" | cut -d $'\n' -f 1)
    branch=${branch:10}
    branch=${branch%%$'\n'*}
    echo "$branch"
}
export -f curr_branch

function gsw() {
    # On branch xxx
    branch=$(git status)
    if [ $? -ne 0 ]; then
        return 1
    fi

    git switch "$1"
    if [ $? -eq 0 ]; then
        branch=$(echo "$branch" | cut -d $'\n' -f 1)
        branch=${branch:10}
        branch=${branch%%$'\n'*}

        GSWITCH_BACK="$branch"
        echocyan "Previous was: $GSWITCH_BACK"
        return 0
    fi
    return 1
}
export -f gsw

function gswb() {
    if [ ! -z $GSWITCH_BACK ]; then
        gsw $GSWITCH_BACK
    else
        echored "No branch to switch back"
    fi
}

function installall(){
    find . -maxdepth 2 -type d | while read dir; do
    if [ -f "$dir/pom.xml" ]; then
        mvn clean install -f "$dir/pom.xml"
    fi
    done
}

function diskusage() { du -d 1 -h; }

function echored() { echo $red"$1"$colourreset; }
export -f echored

function echogreen() { echo $green"$1"$colourreset; }
export -f echogreen

function echoyellow() { echo $yellow"$1"$colourreset; }
export -f echoyellow

function echocyan() { echo $cyan"$1"$colourreset; }
export -f echocyan

# mvn test-compile
function mcpt() {
    pom=$(python3 $STUFF/findpom.py $@)
    if [ $? -ne 0 ] || [ ! -f "$pom" ]; then
        echored ">>> pom.xml is not found, aborted"
    else
        echogreen ">>> found $pom"
        mvn -f "$pom" -T 0.5C -o -Dmaven.test.skip=true -DadditionalJOption=-Xdoclint:none test-compile
    fi
}

function mcp() {
    pom=$(python3 $STUFF/findpom.py $@)
    if [ $? -ne 0 ] || [ ! -f "$pom" ]; then
        echored ">>> pom.xml is not found, aborted"
    else
        echogreen ">>> found $pom"
        mvn compile -T 0.5C -o -Dmaven.test.skip=true -f $pom  -DadditionalJOption=-Xdoclint:none
    fi
}

function mdeploy() {
    if [ $# -gt 0 ]; then
        mvn -T 0.5C deploy -Dmaven.test.skip=true -DadditionalJOption=-Xdoclint:none -pl "$@"
    else
        mvn -T 0.5C deploy -Dmaven.test.skip=true -DadditionalJOption=-Xdoclint:none
    fi
}

function minst() {
    if [ $# -gt 0 ]; then
        mvn install -N && mvn clean install -T 0.5C -o -Dmaven.test.skip=true -DadditionalJOption=-Xdoclint:none -pl "$@"
    else
        mvn clean install -T 0.5C -o -Dmaven.test.skip=true -DadditionalJOption=-Xdoclint:none
    fi
}

function mtest() {
    pom=$(python3 $STUFF/findpom.py $@)
    if [ $? -ne 0 ] || [ ! -f "$pom" ]; then
        echored ">>> pom.xml is not found, aborted"
    else
        echogreen ">>> found $pom"
        mvn test -T 0.5C -f $pom
    fi
}

function gencmtmsg() { python3 $STUFF/gencmtmsg.py; }
export -f gencmtmsg

function rkcmt() {
    git add .

    # #Set the field separator to new line
    # IFS=$'\n'

    # msg=`git diff --staged --raw`
    # lines=""

    # for line in $msg; do
    #     t="${line:31:1}"
    #     s_line="${line:33}"$'\n'
    #     t_name=""

    #     if [ $t == 'M' ]; then
    #         t_name="Modified"
    #     elif [ $t == 'A' ]; then
    #         t_name="Added"
    #     elif [ $t == 'D' ]; then
    #         t_name="Deleted"
    #     else
    #         t="${line:31:4}"
    #         if [ $t == "R092" ]; then
    #             t_name="Renamed"
    #             s_line="${line:36}"$'\n'
    #         fi
    #     fi

    #     lines+="$t_name: $s_line"
    # done
    lines=`gencmtmsg`
    git commit -m "$lines"
    if [ $? -eq 0 ]; then
        echogreen ">>> you recklessly committed a change"
    fi
}

function rbash() { source ~/.bashrc; }
function rtmux() { tmux source-file ~/.tmux.conf; }

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
        status=`git status | grep "On branch main"`
        if [ ! -z "$status" ] && [ "$status" != "" ]; then
            echo 1
        else
            echo 0
        fi
    fi
}
export -f is_master

function gcheck() {
    # set -eE -o functrace
    # traperr

    debug=0
    fetch=0
    pull=0

    if [ ! -z "$2" ]; then
        if [ "$2" == "--debug" ]; then
            debug=1
            # echogreen "--debug mode turned on"
        elif [ "$2" == "--fetch" ]; then
            fetch=1 # echogreen "--fetch mode turned on"
        elif [ "$2" == "--pull" ]; then
            pull=1
            # echogreen "--pull mode turned pn"
        fi
    fi

    if [ ! -z "$1" ]; then
        (
            cd "$1"

            #echocyan "debug: $1, 1"

            if [ "$debug" -eq 1 ]; then
                echogreen "debug: cd $1"
            fi

            #echocyan "debug: $1, 2"

            # not a git repo
            gitdir="$(pwd)/.git"

            #echocyan "debug: $1, 3, $gitdir"

            if [ ! -d "$gitdir" ]; then
                return 0
            fi

            #echocyan "debug: $1, 4"

            if [ $fetch -eq 1 ]; then
                # always fetch first, but we don't print the result
                git fetch &> /dev/null
                if [ ! $? -eq 0 ]; then
                    echored "failed to fetch from remote"
                    return 0
                fi

                if [ $debug -eq 1 ]; then
                    echogreen ">>> debug: git fetch in $1"
                fi

            fi

            status=`git status`

            if [ $debug -eq 1 ]; then
                echogreen ">>> called git status in $1"
            fi

            # check whether repo is up-to-date
            utd=`echo "$status" | grep "Your branch is up to date"`
            if [ $? -eq 0 ] && [ -z "$utd" ] || [ "$utd" == "" ]; then
                echored "found changes from upstream repository in $1"
                master=`is_master "$1"`

                if [ "$pull" -eq 1 ] && [ "$master" -eq 1 ] ; then
                    echogreen ">>> pulling changes from upstream"
                    git pull
                fi
            fi

            # find uncommited changes
            tbc=`echo "$status" | grep 'Changes to be committed'`
            if [ $? -eq 0 ] && [ ! -z "$tbc" ] && [ "$tbc" != "" ]; then
                echored "found uncommited changes in $1"
                return 0
            fi

            # find untracked files
            utf=`echo "$status" | grep 'Untracked files'`
            if [ $? -eq 0 ] && [ ! -z "$utf" ] && [ "$utf" != "" ]; then
                echored "found untracked files in $1"
                return 0
            fi

            # find changes not staged
            changes=`echo "$status" | grep 'Changes not staged'`
            if [ $? -eq 0 ] && [ ! -z "$changes" ] && [ "$changes" != "" ]; then
                echored "found uncommited changes in $1"
                return 0
            fi

            # find commits not pushed
            commits=`echo "$status" | grep 'Your branch is ahead of'`
            if [ $? -eq 0 ] && [ ! -z "$commits" ] && [ "$commits" != "" ]; then
                echored "found commits not yet pushed in $1"
                return 0
            fi

            # if [ "$debug" -eq 1 ]; then
            # fi
            # echogreen "finished checking $1"
        )
    fi

}

# scan repo for uncommited changes, use --fetch to fetch each repo
function repocheck () {
    find . -maxdepth 2 -type d ! -name "*.git" | while read line; do
        abs_path="$(pwd)/${line:2}"

        # non-hidden directories
        if [ "${line:0}" != "." ]; then
            if [ ! -z "$1" ]; then
                gcheck "$abs_path" "$1"
            else
                gcheck "$abs_path"
            fi
        fi
    done
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
        echored "please specify base path first..."
        return 1;
    fi

    base=$1
    num=`last_weekly_report $base`
    target=$base/week-$num.md

    if [ -f $target ]; then
        echored "file: '$target' exists, aborting..."
        return 1;
    fi

    touch $target
    echogreen ">>> touched file: '$target', initializing content"

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

    echogreen ">>> '$target' content initialized, finished"

    # open file using vscode
    code $target
}

# reset one git commit, '--stage' to keep files in stage area, '--y' or '--Y' to reset without confirmation
function resetone() {

    # do we need to restre --staged
    unstage=1

    # do we need confirmation, 'no' by default
    need_confirm=0

    for arg in "$@"; do
        if [ $arg == '--stage' ]; then
            unstage=0
        # elif [[ $arg =~ --[yY] ]]; then
        #     need_confirm=0
        fi
    done

    if [ $need_confirm -eq 1 ]; then
        read -p "Sure you want to reset one commit? [y/Y] "
        ans=$REPLY

        if [ -z $ans ] || [[ $ans =~ [^yY] ]]; then
            echogreen ">>> Aborting ..."
            return 1
        fi
    fi

    git reset --soft HEAD~1

    if [ $unstage -eq 1 ]; then
        git restore --staged .
    fi

    echogreen ">>>> resetted one git commit"
    git status
}

function psgrep() {
    if [ -z "$1" ]; then
        return 0
    fi
    ps -ef | head -1
    ps -ef | grep "$1" | grep -v grep
}

function pom_ver() {
    if [ -z $1 ] || [ $1 == "." ] ; then
        root=`pwd`
    else
        root="$1"
    fi

    name="$root/pom.xml"
    if [ ! -f $name ]; then
        echored "Unable to find $name"
        return 1
    fi

    # get project.version
    ver=$(mvn -q \
    -Dexec.executable=echo \
    -Dexec.args='${project.version}' \
    --non-recursive \
    exec:exec)

    echo "'$name' Project.Version: $cyan $ver $colourreset"
}

function set_git_user() {
  if [ ! -d ".git" ]; then
    # echo "$(pwd) not a git repository, skipped ..."
    exit 0;
  fi

  git config user.name "$1"
  git config user.email "$2"
  if [ $? -eq 0 ]; then
    echo "Configured git.user in $(pwd)"
  fi
}

function all_set_git_user() {
  echo "Configuring all git repo under $(pwd) to use user.name: $1, user.email: $2"
  for d in *
  do
    if [ -d "$d" ]; then
      (cd "$d"; set_git_user "$1" "$2")
    fi
  done
}

function set_append_target(){
    APPEND_TARGET="$1"
}

function append() {
    if [ -z "$1" ]; then
        cnt=""
    else
        cnt="$1"
    fi
    echo "$cnt" >> "$APPEND_TARGET"
}

function rmlogs() {
    find . -name "*.log" | while read f; do
        echo "removed $f"
        rm $f
    done
}

function rmtarget() {
    find . -type d -name "target" | while read f; do
        echo "found $f"
    done

    read -p "confirm ? [Y/y] "
    ans=$REPLY
    if [ $ans = "Y" ] || [ $ans = 'y' ]; then
        find . -type d -name "target" | while read f; do
            echo "removed $f"
            rm -r $f
        done
    fi

}

function fdcount() {
    if [ -z "$1" ]; then
        echored "Please enter PID"
        return 1
    fi
    sudo ls -l /proc/$1/fd/ | wc -l
}

function threadcount() {
    if [ -z "$1" ]; then
        echored "Please enter PID"
        return 1
    fi
    sudo ls /proc/$1/task | wc -l
}

function mem() {
    free -mh
}

function lcount() {
    ll | wc -l
}

function apiver() {
    readpom -t 'project.properties.api.version'
}

function projver() {
    readpom -t 'project.version'
}

function cc() {
    echo "$@" | bc -l
}

function codediff() {
    /usr/local/bin/code --diff "$1" "$2"
}

# check if current OS is MAC, return 1 is true, else 0
function ismac() {
    if [ $(uname) == 'Darwin' ]; then
        echo "1"
    else
        echo "0"
    fi
}

function clipboard() {
    read c
    # echo "clipboard: $c"
    if [ "$(ismac)" == "1" ]; then
        echo "$c" | tr -d '\n' | pbcopy
    else
        # apt install xclip
        echo "$c" | tr -d '\n' | xclip -selection clipboard
    fi
    echogreen ">>> copied to clipboard..."
}
export -f clipboard

# readlink -e with 'copied to clipboard'
function rl() { p=$(readlink -e "$1"); echo "$p"; echo "$p" | clipboard; }

# Extract git history
function gxpatch() {
    if [ -z "$2" ]; then
        echored "please specify where the generated patch will be"
        return 1
    fi

    if [ -z "$1" ]; then
        echored "please specify where the git history will be extracted"
        return 1
    fi

    git log --pretty=email --patch-with-stat --reverse --full-index --binary -- "$1" > "$2"
}

function gapplypatch(){
    if [ -z "$1" ]; then
        echored "please specify where the generated patch is"
        return 1
    fi

    if [ ! -f "$1" ]; then
        echored "file $1 not found"
        return 1
    fi

    git am < "$1"
}

function attachcli(){
    docker exec -it "$1" /bin/sh
}

function docker-compose-rebuild(){
    if [ -z $1 ]; then
        echo "Must specify service name"
        return 1;
    fi
    docker-compose up -d --no-deps --build $1
    # docker-compose up -d --build $1
}

function docker-compose-up() { docker-compose up -d --build --remove-orphans; }
function docker-compose-down() { docker-compose down; }
function docker-compose-re-up() { docker-compose-down; docker-compose-up; }
function encrypt() { python3 "$STUFF/aes.py" -m encrypt; }
function decrypt() { python3 "$STUFF/aes.py" -m decrypt; }
function split() { res=$(python3 "$STUFF/split.py" $@); echo $res; echo $res | clipboard; }
function jsonarray() { res=$(python3 "$STUFF/json_array.py" $@); echo $res; echo $res | clipboard; }
function strlen() { python3 "$STUFF/strlen.py" "$@"; }

function readpom() {
  if [ ! -z "$2" ]; then
    pom_p="$2"
  else
    pom_p="./pom.xml"
  fi
  python3 "$STUFF/readpom.py" "$1" "$pom_p"
}
export -f readpom

function monday() {	python3 "$STUFF/monday.py"; }
export -f monday

function rands() { python3 "$STUFF/rands.py" "$@"; }
export -f rands

function dectobin() { python3 "$STUFF/dec_to_bin.py" "$1"; }
export -f dectobin

function bintodec() { python3 "$STUFF/bin_to_dec.py" "$1"; }
export -f bintodec

function dectohex() { python3 "$STUFF/dec_to_hex.py" "$1"; }
export -f dectohex

function hextodec() { python3 "$STUFF/hex_to_dec.py" "$1"; }
export -f hextodec

function hextobin() { python3 "$STUFF/hex_to_bin.py" "$1"; }
export -f hextobin

function tzone() { python3 "$STUFF/tzone.py" $@; }
export -f tzone

function lbranch() { python3 $STUFF/lbranch.py; }
export -f lbranch

function findpom() { python3 $STUFF/findpom.py $@; }
export -f findpom

function pyhash() { python3 $STUFF/hash.py $@; }
export -f pyhash

function insertgen() { python3 $STUFF/insertgenpy/insertgenpd.py $@; }
export -f insertgen

function updategen() { python3 $STUFF/updategenpy/updategenpd.py $@; }
export -f updategen

function cleandir() {
  if [ -z "$1" ]; then
    return 0
  fi

  if [ -f "$1" ]; then
    read -p "Sure you want to remove '$1'? To cancel: [n/N] "
  else
    read -p "Sure you want to remove all in '$1'? To cancel: [n/N] "
  fi
  ans=$REPLY

  if [[ $ans =~ [Nn] ]]; then
    return 0
  fi

  echogreen "Removing (rm -rvf) $1"
  time rm -rvf "$1"
  mkdir "$1"
}

function rmr() {
  if [ -z "$1" ]; then
    return 0
  fi

  if [ -f "$1" ]; then
    read -p "Sure you want to remove '$1'? To cancel: [n/N] "
  else
    read -p "Sure you want to remove all in '$1'? To cancel: [n/N] "
  fi
  ans=$REPLY

  if [[ $ans =~ [Nn] ]]; then
    return 0
  fi

  echogreen "Removing (rm -rvf) $1"
  time rm -rvf "$1"
}

function grepcode() {
  if [ -z "$1" ];then
    return 0
  fi

  grep -i -R "$1" . \
  -C 1 \
  --exclude-dir "target" \
  --exclude-dir ".git" \
  --exclude-dir ".vscode" \
  --exclude-dir "node_modules" \
  --exclude-dir "dist" \
  --exclude-dir "logs" \
  --exclude-dir "log" \
  --exclude-dir ".idea" \
  --exclude "*.dmg" \
  --exclude "*.jar" \
  --exclude "*.zip" \
  --exclude "*.gzip" \
  --exclude "*.tar" \
  --exclude "*.mp4" \
  --exclude "*.mov" \
  --exclude "*.jpg" \
  --exclude "*.jpeg" \
  --exclude "*.png"
  # -l
}

function tips_tdump() {
    echo
    echocyan " sudo tcpdump -nnAS -s 0 -i any $@"
    echo
    pprint "-n" "not dns resolution stuff"
    pprint "-X" "similar to -A, prints out all header, content"
    pprint "-S" "absolute seq num"
    pprint "-s" "size, 0 means all"
    pprint "-w" "\$somefile.pcap"
    pprint "src" "\$host"
    pprint "dst" "\$host"
    pprint "port" "\$port"
    pprint "i" "interface, tcpdump -D"
}

function tdump() {
    # -n not dns resolution stuff
    # -X similar to -A, prints out all header, content
    # -S absolute seq num
    # -s size, 0 means all
    # -w $somefile.pcap
    # src $host
    # dst $host
    # port $port
    # i interface, tcpdump -D
    sudo tcpdump -nnAS -s 0 -i any $@
}
export -f tdump

function fxname() { python3 $STUFF/fixfname.py "$@"; }
function conflict() { time ag "=======|>>>>|<<<<"; }

# alternative to npm install, without writing package.json :D
function npmci() { npm ci; }

function ghead() { out=$(git rev-parse HEAD); echo "$out"; echo "$out" | clipboard; }

# $1: username, $2: database, $3: table, $4: where
function dumpinsert() {
    if [ "${#@}" -lt 5 ]; then
        echored "Please provide arguments: \$1:host \$2:username, \$3:password, \$4:database, \$5:table, \$6:where"
        return 1
    fi

    mysqldump -c -t -h "$1" -u "$2" --password="$3" "$4" "$5" --complete-insert --skip-add-locks --skip-lock-tables --where="$6"
}
export -f dumpinsert

function ttables() { python3 $STUFF/ttables.py $@; }
export -f ttables

function quotejoin() { out=$(python3 $STUFF/quotejoin.py $@); echo "$out"; echo "$out" | clipboard; }
export -f quotejoin

function unquote() { out=$(python3 $STUFF/unquote.py $@); echo "$out"; echo "$out" | clipboard; }
export -f unquote

function today() { out=$(date +'%Y-%m-%d'); echo "$out"; echo "$out" | clipboard; }
export -f today

function pport() { lsof -i ":$1"; }

function certinfo() { openssl x509 -noout -text -inform pem -in "$1"; }

function certfingerprint() {
    openssl x509 -noout -fingerprint -sha256 -inform pem -in "$1";
    openssl x509 -noout -fingerprint -sha1 -inform pem -in "$1";
}

function fetchcert() { openssl s_client -servername "$1" -connect "$1":443 </dev/null 2>/dev/null | openssl x509 -text; }

function use_vimdiff_for_git() {
    git config --global diff.tool vimdiff
    git config --global merge.tool vimdiff
}

function decompressall_gzip() { find . -name '*.gz' -type f -exec gzip -d {} \; ; }

function decompressall_tar() { find . -name '*.(tar|tar.gz)' -type f -exec tar -xf {} \; ; }

function substr() { python3 $STUFF/sub.py "$1" "$2" "$3"; }

function unquotejoin() { python3 $STUFF/unquotejoin.py $@; }

function mac_javahome() { /usr/libexec/java_home -V; }

function camelcase() { out=$(python3 $STUFF/camelcase.py $@); echo $out; echo "$out" | clipboard; }

function hmac() { python3 $STUFF/phmac.py $@; }

function gobuildall() { go build ./...;  }

function buondua() { python3 $STUFF/buondua.py $@; }

function gpick() { git cherry-pick $@ ; }

function peek_journal() {
    journalctl -xe -u '$1'
}

settermproxy() {
	# for shadowsocks
  export HTTP_PROXY="http://127.0.0.1:1087"
  export HTTPS_PROXY="http://127.0.0.1:1087"
  export ALL_PROXY="http://127.0.0.1:1086"
}

unsettermproxy() {
  unset HTTP_PROXY
  unset HTTPS_PROXY
  unset ALL_PROXY
}

test_github_ssh() {
  ssh -Tv git@github.com
  # ssh -Tv git@github.com -vvv
}

compress_mp4() {
    # https://unix.stackexchange.com/questions/28803/how-can-i-reduce-a-videos-size-with-ffmpeg
    # the higher the crf is, the worst the quality will be, 0 is lossless
    ffmpeg -i "$1"  -vcodec libx264 -crf 32 -preset faster "$2"
}

go_build_analyse() {
    go build -gcflags '-m' ./... 2>  "analyze.log"
}

function mergeto() {
    echo "Merging current branch to $1"

    gsw "$1"
    if [ $? -ne 0 ]; then
        return 1
    fi

    git merge "$GSWITCH_BACK"
    if [ $? -ne 0 ]; then
        git merge --abort
        gswb
        return 1
    fi
}

function springbootrun() {

    app="$1"
    if [ -z "$app" ]; then
        mvn spring-boot:run -Dspring-boot.run.jvmArguments="-Xmx400m"
        return 0
    fi

    echo "Running $app"
    mvn install -N -q \
	&& mvn install -T 0.5C -Dmaven.test.skip=true -q \
        && ( \
            cd "$app" && echo "cd into $app" \
                && mvn spring-boot:run -Dspring-boot.run.jvmArguments="-Xmx400m" -q \
        )
}

function archivell() {
    d=365
    if [ ! -z "$1" ]; then
        d="$1"
    fi
    echo "Finding files modified before $d days ago"
    find . -maxdepth 1 -mtime +$d -ls
}

function archivels() {
    d=365
    if [ ! -z "$1" ]; then
        d="$1"
    fi
    find . -maxdepth 1 -mtime +$d
}

function move_archive_to() {
    to="$1"
    if [ -z $to ]; then
        echored "Where these files are moved to?"
        return 0
    fi

    archivels | xargs -I {} mv "{}" "$to/{}"
}

function prefix_file() {
    if [ -z "$1" ]; then
        echored "Enter prefix"
        return 0
    fi

    ls | xargs -I {} mv "{}" "$1{}"
}


function myddl() {
    echo "CREATE TABLE IF NOT EXISTS _ ("
    echo "    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT COMMENT 'primary key',"
    echo ""
    echo "    ctime TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',"
    echo "    cby VARCHAR(255) NOT NULL DEFAULT '' comment 'created by',"
    echo "    utime TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',"
    echo "    uby VARCHAR(255) NOT NULL DEFAULT '' comment 'updated by',"
    echo "    del CHAR(1) NOT NULL DEFAULT 'N' comment 'is record deleted: Y/N'"
    echo ") ENGINE=INNODB COMMENT '';"
}

function copymyddl() {
    if [ "$(ismac)" == "1" ]; then
        myddl | tr -d '' | pbcopy
    else
        myddl | tr -d '' | xclip -selection clipboard
    fi
}

function basic_auth() {
    username="$1"
    password="$2"
    auth="$1:$2"
    encoded="$(echo -n $auth | base64)"
    echo ""
    echo "Authorization:Basic $encoded"
}

function fmt() {
    go fmt ./...
}

function build() {
    go build ./...
}

function initwork() {
    go work init
    if [ $? -ne 0 ]; then
        return 1
    fi 
    echo "" >> go.work
    echo "use ." >> go.work
    ls -l
}

function cleanwork(){
    if [ -f go.work ]; then
        echogreen 'removed go.work'
        rm go.work
    fi
    if [ -f go.work.sum ]; then
        echogreen 'removed go.work.sum'
        rm go.work.sum
    fi
}
