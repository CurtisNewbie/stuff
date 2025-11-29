#!/bin/bash

# mirrors for brew
export HOMEBREW_API_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles/api"
export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles"
export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git"
export HOMEBREW_CORE_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git"
export HOMEBREW_PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"

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

if ! cat ~/.bashrc | grep -q "stuff/workspace.sh"; then
    f="$(pwd)/workspace.sh"
    echo -e "# Automatically inserted by workspace.sh\nsource $f\n$(cat ~/.bashrc)" > ~/.bashrc
fi

function echored() {
    echo $red"$1"$colourreset;
}
export -f echored

function echogreen() {
    echo $green"$1"$colourreset;
}
export -f echogreen

function echoyellow() {
    echo $yellow"$1"$colourreset;
}
export -f echoyellow

function echocyan() {
    echo $cyan"$1"$colourreset;
}
export -f echocyan

function readenv() {
  env="$1"
  renv="echo \$$env"
  eval $renv
}
export -f readenv

function ismac() {
    if [ $(uname) == 'Darwin' ]; then
        return 0
    else
        return 1
    fi
}
export -f ismac

# --------------- command check ---------------

if ismac; then
    cmds="brew git mvn java go ag"
    for c in $cmds; do
        if ! command -v "brew" 2&> /dev/null ; then
            echored "$c is not found"
        fi
    done
fi

gitps1=0
if [ -f "/Library/Developer/CommandLineTools/usr/share/git-core/git-prompt.sh" ]; then
    source "/Library/Developer/CommandLineTools/usr/share/git-core/git-prompt.sh"
    gitps1=1
fi
if [ $gitps1 -ne 1 ] && [ -d "/usr/local/etc/bash_completion.d" ]; then
    source /usr/local/etc/bash_completion.d/git-prompt.sh
    source /usr/local/etc/bash_completion.d/git-completion.bash
    gitps1=1
fi

if [ $gitps1 -eq 1 ]; then
    PS1="\[\e[1;34m\]\u@\h\[\e[0m\] \w\[\e[1;31m\]\$(__git_ps1)\[\e[0m\]\$ "
fi

if ismac; then
    if ! command -v "greadlink" 2&> /dev/null; then
        echo "missing greadlink"
        if command -v "brew" 2&> /dev/null ; then
            echo "installing coreutils for greadlink"
            brew install coreutils
        fi
    fi
    alias readlink="greadlink"
fi

# -------------------- env -------------------------

export HOMEBREW_NO_AUTO_UPDATE=1
export MAVEN_OPTS="-Xmx1000m -XX:+TieredCompilation -XX:TieredStopAtLevel=1"
export CGO_ENABLED=1
export LANG=en_US.UTF-8

# for brew's executables
[ -d "/usr/local/opt/ruby/bin" ] && export PATH="/usr/local/opt/ruby/bin:$PATH"

# stuff repo location
script_source=${BASH_SOURCE[0]}
script_dir="$( cd -- "$( dirname -- "$script_source" )" &> /dev/null && pwd )"
[ -z "$STUFF" ] && STUFF="$script_dir"

if ismac; then
    if [ -d "$STUFF/vscode_snippet" ] && [ -d "$HOME/Library/Application Support/Code/User/snippets/" ]; then
        l=$(ls $STUFF/vscode_snippet)
        for f in "$l" ; do
            if [ ! -f "$HOME/Library/Application Support/Code/User/snippets/$f" ]; then
                cp "$STUFF/vscode_snippet/$f" "$HOME/Library/Application Support/Code/User/snippets/"
                echo "Copied $STUFF/vscode_snippet/$f to $HOME/Library/Application Support/Code/User/snippets/"
            fi
        done
    fi
fi

# default trash can location: ~/trash
trash_can="$HOME/trash"

# link to python files in current directory
export PYTHONPATH="$PYTHONPATH:$STUFF"

# local executable bin directory
export LOC_BIN="/usr/local/bin"

# not directly executable files
export USER_EXEC=~/exec

# upgrade miso version
miso_ver="v0.3.9"

# github repo path: GIT_PATH
# work repo path: WORK_REPO_PATH
expected_env="GIT_PATH WORK_REPO_PATH"
for env in $expected_env; do
  if [ -z "$env" ]; then
    echored "Missing $env environment variable, please export $env=... in ~/.bashrc"
  fi
done

export SYNC_REPOS="stuff,vfm,mini-fstore,user-vault,event-pump,gatekeeper,logbot,miso,grapher,chill,moon,pocket,acct,tamper_script,smash,cvlet,moon-monorepo"

# ---------------------------------------------------------------

# alias rm="rm -i"
alias reset_alarm="sfltool resetbtm"
alias mk="minikube"
alias kb="kubectl"
alias bc="bc -l"
alias gs="git status"
alias gf="while ! git fetch; do sleep 0.3; done;"
alias gp="git pull"
# alias gm="git merge"
alias gl="git log"
alias gds="git diff -p --staged --stat"
alias gd="git diff -p --stat"
# alias gbranch="git for-each-ref --count=10 --sort=-committerdate refs/heads/ --format='%(HEAD) %(align:80)%(color:yellow)%(refname:short)%(color:reset)%(end) - %(align:60)%(contents:subject)%(end) - %(authorname) (%(color:green)%(committerdate:relative)%(color:reset))'"
alias gbranch="printf '\n' && git for-each-ref --count=10 --sort=-committerdate refs/heads/ --format='%(HEAD) %(align:35)%(color:yellow)%(refname:short)%(color:reset)%(end) - %(align:60)%(contents:subject)%(end) - %(color:green)%(authorname) %(committerdate:relative)%(color:reset)' && printf '\n' && git for-each-ref --count=10 --sort=-committerdate refs/remotes/ --format='%(HEAD) %(align:35)%(color:yellow)%(refname:short)%(color:reset)%(end) - %(align:60)%(contents:subject)%(end) - %(color:green)%(authorname) %(committerdate:relative)%(color:reset)' && printf '\n'"
alias gshow="git show -p --stat"
alias gpush="while ! git push; do sleep 0.3; done"
alias gad="git add"
alias gad.="git add ."
alias mclean="mvn clean"
alias grest="git restore --staged"
alias grep="grep --color"
alias ag="ag -i -A 3 -B 3"
alias idea.="idea ."
alias code.="code ."
alias gck="git checkout"
alias ex='exit'
alias l="ll"
alias ll="ls -lth"
alias tmux="tmux -2"
alias less="less -nR"
alias bc="bc -l"
alias jd="(cd ~; java -jar $STUFF/jd-gui-1.6.6.jar)"
alias leetcode="cp $STUFF/leetcode/Solution.java . && code Solution.java"
alias diff="diff -bur"

if [ -f "$USER_EXEC/arthas-boot.jar" ]; then
    alias arthas="java -jar $USER_EXEC/arthas-boot.jar"
fi

function cgit() {
  repo="$1"
  if [ ! -z "$repo" ]; then
    repo="/$repo"
  fi
  cd "$GIT_PATH$repo"
}

function cstuff() {
  cd "$STUFF"
}

function cwork() {
  repo="$1"
  if [ ! -z "$repo" ]; then
    repo="/$repo"
  fi
  cd "$WORK_REPO_PATH$repo"
}

function pprint() {
  printf ' %-35s %-40s %-35s\n' "$green${1}"  "$yellow${2}$colourreset" "${cyan}${3}$colourreset"
}

function gcl() {
  repo="$1"
  rest="${@:2}" # e.g., --depth=1 -b 2.4 git@....
  # echo "$rest"
  git clone $rest "$repo"
  if [ $? -eq 0 ]; then
      e="${repo##*/}"
      cd "${e%%.git}"
  fi
}

function gcl_shallow() {
  # gcl "repo_url" "tag/branch"
  # e.g.,
  # gcl_shallow git@github.com:elastic/go-elasticsearch.git 5.x

  repo="$1"
  tag="$2"

  if [ ! -z "$tag" ]; then
      gcl "$repo" --depth=1 -b "$tag"
  else
      gcl "$repo" --depth=1
  fi
}

function gamd() {
    git commit --amend;
}

function gdt() {
    git difftool "$@";
}

function glike() {
    git branch | grep "$1";
}

function gstashshow() {
    git stash show -p;
}

function lfind() {
    ls -alh | grep "$1" -i;
}

function brief_lfind() {
    ls -a | grep "$1" -i;
}

function cdlfind() {
    cd $(brief_lfind "$1");
}

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
        -not \( -path "**/__MACOSX/*" -prune \) -exec sh -c 'file="$1"; echo "$(ls -l "$file") | $(stat -f %SB "$file")"' _ {} \; | sort -k5,5nr
}

function ffind_log(){
    ffind $1 > $1.txt
}

function pdffind() {
    find . -type f -iname "*.pdf" \
        -not \( -path "**/target/*" -prune \) \
        -not \( -path "**/.*/*" -prune \) \
        -not \( -path "**/node_modules/*" -prune \) \
        -not \( -path "**/dist/*" -prune \) \
        -not \( -path "**/logs/*" -prune \) \
        -not \( -path "**/log/*" -prune \) \
        -not \( -path "**/__MACOSX/*" -prune \) -exec sh -c 'file="$1"; pdfgrep -n -i "$2" "$file" && printf "____  $file\n\n"' _ {} $1 \;
}

function rfind() {
    if [ $(uname) == 'Darwin' ]; then
        find -E . -type f -regex "$1"
    else
        find -regextype posix-extended . -type f -regex "$1"
    fi
}

function trash_size() {
    if [ ! -d "$trash_can" ]; then
        echocyan "Trash can is not found"
        return 0
    fi

    size=$(cd $trash_can; du -h -d 1 . | tail -n 1)
    echocyan "$size"
}

function trash_ls() {
    if [ ! -d "$trash_can" ]; then
        echocyan "Trash can is not found"
        return 0
    fi
    ls "$trash_can"
}

# dump file to trash can
function trash() {
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

function release() {
  python3 $STUFF/release.py $@
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

function guntrack() {
    git rm --cache "$@";
}

function mresolve() {
    pom=$(python3 $STUFF/findpom.py $@)
    if [ $? -ne 0 ] || [ ! -f "$pom" ]; then
        echored ">>> pom.xml is not found, aborted"
    else
        echogreen ">>> found $pom"
        mvn dependency:resolve -f "$pom" -U
    fi
}

function force_mresolve() {
    pom=$(python3 $STUFF/findpom.py $@)
    if [ $? -ne 0 ] || [ ! -f "$pom" ]; then
        echored ">>> pom.xml is not found, aborted"
    else
        echogreen ">>> found $pom"
        mvn dependency:purge-local-repository -f "$pom" && mvn dependency:resolve -f "$pom" -U
    fi
}

function mresolve_src() {
    pom=$(python3 $STUFF/findpom.py)
    if [ $? -ne 0 ] || [ ! -f "$pom" ]; then
        echored ">>> pom.xml is not found, aborted"
    else
        echogreen ">>> found $pom"
        if [ $# -gt 0 ]; then
            echogreen ">>> resolving sources for '$1'"
            mvn dependency:resolve -f "$pom" -Dclassifier=javadoc -DincludeArtifactIds="$1"
        else
            echogreen ">>> resolving sources for all dependencies"
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

function diskusage() {
    du -d 1 -h;
}

# mvn test-compile
function mcpt() {
    pom=$(python3 $STUFF/findpom.py $@)
    if [ $? -ne 0 ] || [ ! -f "$pom" ]; then
        echored ">>> pom.xml is not found, aborted"
    else
        echogreen ">>> found $pom"
        mvn -f "$pom" -T 1C -o -Dmaven.test.skip=true -Dmaven.javadoc.skip=true -DadditionalJOption=-Xdoclint:none test-compile -DskipTests
    fi
}

function mcp() {
    pom=$(python3 $STUFF/findpom.py $@)
    if [ $? -ne 0 ] || [ ! -f "$pom" ]; then
        echored ">>> pom.xml is not found, aborted"
    else
        echogreen ">>> found $pom"
        mvn compile -T 1C -o -Dmaven.javadoc.skip=true -Dmaven.test.skip=true -f $pom -DadditionalJOption=-Xdoclint:none -DskipTests
    fi
}

function mdeploy() {
    if [ $# -gt 0 ]; then
        mvn -T 1C deploy -Dmaven.test.skip=true -DadditionalJOption=-Xdoclint:none -DskipTests -pl "$@"
    else
        mvn -T 1C deploy -Dmaven.test.skip=true -DadditionalJOption=-Xdoclint:none -DskipTests
    fi
}

function minst() {
    if [ $# -gt 0 ]; then
        mvn install -N && mvn clean install -T 1C -o -Dmaven.test.skip=true -DadditionalJOption=-Xdoclint:none -DskipTests -pl "$@"
    else
        mvn clean install -T 1C -o -Dmaven.test.skip=true -DadditionalJOption=-Xdoclint:none -DskipTests
    fi
}

function mtest() {
    pom=$(python3 $STUFF/findpom.py $@)
    if [ $? -ne 0 ] || [ ! -f "$pom" ]; then
        echored ">>> pom.xml is not found, aborted"
    else
        echogreen ">>> found $pom"
        mvn test -T 1C -f $pom -DskipTests
    fi
}

function gencmtmsg() {
    python3 $STUFF/gencmtmsg.py;
}
export -f gencmtmsg

function rkcmt() {
    git add .
    lines=`gencmtmsg`
    git commit -m "Polishing"
    if [ $? -eq 0 ]; then
        echogreen ">>> you recklessly committed a change"
        echogreen "$lines"
    fi
}

function rbash() {
    source ~/.bashrc;
}
function rtmux() {
    tmux source-file ~/.tmux.conf;
}

# check whether $1 is in master branch, return 1-true, 0-false
function is_master() {
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

function last_weekly_report() {

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

function clipboard() {
    read c
    # echo "clipboard: $c"
    if [ ismac ]; then
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

# Extract git history for commit
function gxpatch_commit() {
    out="commit.patch"
    if [ -z "$1" ]; then
        echored "please specify where the git history will be extracted"
        return 1
    fi

    git format-patch -1 "$1" --stdout > "$out"
}

function gitgrep() {
    pat="$1"
    path=""
    if [ ! -z "$2" ]; then
        path="$1"
        pat="$2"
    fi
    if [ ! -z "$path" ]; then
        git log -p -S "$pat" $path
    else
        git log -p -S "$pat"
    fi
}

function gapplypatch() {
    if [ -z "$1" ]; then
        echored "please specify where the generated patch is"
        return 1
    fi

    if [ ! -f "$1" ]; then
        echored "file $1 not found"
        return 1
    fi

    if [ ! -z "$2" ]; then
        git am -C1 --3way --ignore-space-change --ignore-whitespace --empty keep --directory "$2" "$1"
    else
        git am -C1 --3way --ignore-space-change --ignore-whitespace --empty keep "$1"
    fi
}

function attachcli() {
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

function docker-compose-up() {
    docker-compose up -d --build --remove-orphans;
}

function docker-compose-down() {
    docker-compose down;
}

function docker-compose-re-up() {
    docker-compose-down; docker-compose-up;
}

function encrypt() {
    python3 "$STUFF/aes.py" -m encrypt;
}

function decrypt() {
    python3 "$STUFF/aes.py" -m decrypt;
}

function split() {
    res=$(python3 "$STUFF/split.py" $@); echo $res; echo $res | clipboard;
}

function jsonarray() {
    res=$(python3 "$STUFF/json_array.py" $@); echo $res; echo $res | clipboard;
}

function strlen() {
    python3 "$STUFF/strlen.py" "$@";
}

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

  if [[ $ans =~ [Yy] ]]; then
      echogreen "Removing (rm -rf) $1"
      time rm -rf "$1"
      echogreen "Done"
  else
      echocyan "Aborted ..."
  fi
}

function grepcode() {
  if [ -z "$1" ];then
    echo "What are you searching for?"
    return 0
  fi

#   grep -i -R "$1" . \
#     -C 1 \
#     --exclude-dir "target" \
#     --exclude-dir ".git" \
#     --exclude-dir ".vscode" \
#     --exclude-dir "node_modules" \
#     --exclude-dir "dist" \
#     --exclude-dir "logs" \
#     --exclude-dir "log" \
#     --exclude-dir ".idea" \
#     --exclude "*.dmg" \
#     --exclude "*.jar" \
#     --exclude "*.zip" \
#     --exclude "*.gzip" \
#     --exclude "*.tar" \
#     --exclude "*.mp4" \
#     --exclude "*.mov" \
#     --exclude "*.jpg" \
#     --exclude "*.jpeg" \
#     --exclude "*.png"
  # -l

    # --ignore "*.sql" \

  ag -i -r "$1" . \
    -C 1 \
    --ignore-dir "target" \
    --ignore-dir ".git" \
    --ignore-dir ".vscode" \
    --ignore-dir "node_modules" \
    --ignore-dir "dist" \
    --ignore-dir "logs" \
    --ignore-dir "log" \
    --ignore-dir ".idea" \
    --ignore "*.dmg" \
    --ignore "*.jar" \
    --ignore "*.zip" \
    --ignore "*.gzip" \
    --ignore "*.tar" \
    --ignore "*.mp4" \
    --ignore "*.mov" \
    --ignore "*.jpg" \
    --ignore "*.jpeg" \
    --ignore "*.png" \
    --ignore "*.excalidraw" \
    --ignore "go.sum" \
    --ignore "*.svg" \
    --ignore "*.md"
    # -l
}

function tips_tdump() {
    echo
    echocyan " sudo tcpdump -nAS -s 0 -i any $@"
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
    tips_tdump
    echo ""
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

function pid_ports() {
    lsof -aPi -p $1
}

function certinfo() { openssl x509 -noout -text -in "$1"; }

function certfingerprint() {
    openssl x509 -noout -fingerprint -sha256 -in "$1";
    openssl x509 -noout -fingerprint -sha1 -in "$1";
}

function fetchcert() { openssl s_client -servername "$1" -connect "$1":443 </dev/null 2>/dev/null | openssl x509 -text; }

function root_cert() {
    openssl s_client -showcerts -verify 10 -connect $1:443 > /dev/null
}

function scrape_all_cert() {
    openssl s_client -showcerts -verify 10 -connect $1:443 < /dev/null |
    awk '/BEGIN CERTIFICATE/,/END CERTIFICATE/{ if(/BEGIN CERTIFICATE/){a++}; out="cert"a".pem"; print >out}'
    i=0
    echo ""
    for cert in *.pem; do
            newname=$(openssl x509 -noout -subject -in $cert | sed -nE 's/.*CN ?= ?(.*)/\1/; s/[ ,.*]/_/g; s/__/_/g; s/_-_/-/; s/^_//g;p' | tr '[:upper:]' '[:lower:]').pem
            echo "- ${i} /tmp/${newname}"
            mv "$cert" "/tmp/${newname}"
            i=$((i+1))
    done
}

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

function gobuildlinux() { CGO_ENABLED=0 GOOS="linux" GOARCH="amd64" go build -o $1 ;  }

function buondua() { python3 $STUFF/buondua.py $@; }

function gpick() { git cherry-pick $@ ; }

function peek_journal() {
    journalctl -xe -u '$1'
}

function settermproxy() {
    port="7890"
    ismac && port="1087"

    # for shadowsocks
    export HTTP_PROXY="http://127.0.0.1:$port"
    export HTTPS_PROXY="http://127.0.0.1:$port"
    export ALL_PROXY="http://127.0.0.1:$port"
    printf "set to proxy: %s\n" $HTTP_PROXY
}

function unsettermproxy() {
    unset HTTP_PROXY
    unset HTTPS_PROXY
    unset ALL_PROXY
    printf "unset proxy\n"
}

function test_github_ssh() {
    ssh -Tv git@github.com
    # ssh -Tv git@github.com -vvv
}

function cvt_mp4_codec() {
    # https://unix.stackexchange.com/questions/28803/how-can-i-reduce-a-videos-size-with-ffmpeg
    # the higher the crf is, the worst the quality will be, 0 is lossless
    # -ss 00:03:00 -t 00:00:20.0
    ffmpeg -i "$1" -vcodec libx264 -crf 32 -preset faster "$2"
}

function cvt_mp4() {
    ffmpeg -i "$1" -crf 32 -preset faster "$2"
}

function cvt_mp4_cut() {
    # -ss 00:03:00 -t 00:00:20.0 (-t is duration)
    if [ "${#@}" -gt 3 ]; then
        ffmpeg -i "$1" -ss "$2" -t "$3" "$4"
    else
        ffmpeg -i "$1" -ss "$2" "$3"
    fi
}

function ffmpeg_loop() {
    ffmpeg -stream_loop $3 -i "$1" "$2"
}

function ffmpeg_hls_download() {
    # $1 - https://****.m3u8
    out="output.mp4"
    if [ ! -z "$2" ]; then
        out="$2"
    fi
    ffmpeg -loglevel debug -f hls \
        -user_agent "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36" \
        -i "$1" \
        -c copy "$out"
}

function analyze() {
    go build -gcflags='-m -l' ./... 2>&1 | grep -v 'does not escape' | grep escape > "analyze.log"
}

function mergeto() {
    echo "Merging current branch to $1"

    gsw "$1"
    if [ $? -ne 0 ]; then
        return 1
    fi

    git merge --no-ff "$GSWITCH_BACK"
    if [ $? -ne 0 ]; then
        git merge --abort
        gswb
        return 1
    fi
}

function springbootrun() {
    app="$1"
    if [ -z "$app" ]; then
        echo "Running mvn spring-boot:run at ./"
        mvn spring-boot:run -Dspring-boot.run.jvmArguments="-Xmx400m"
        return 0
    fi

    mvn install -N -q && echo "Installed root pom" \
    && mvn install -T 1C -DskipTests -Dmaven.test.skip=true -q && echo "Installed modules" \
        && ( \
            cd "$app" && echo "Running mvn spring-boot:run at $app" \
                && mvn spring-boot:run -Dspring-boot.run.jvmArguments="-Xmx400m" \
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
    echo ""
    text="CREATE TABLE \`$1\` (
    \`id\` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT 'primary key',

    \`trace_id\` varchar(32) NOT NULL DEFAULT '' COMMENT 'trace_id',
    \`created_at\` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'created at',
    \`created_by\` varchar(255) NOT NULL DEFAULT '' COMMENT 'created by',
    \`updated_at\` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'updated at',
    \`updated_by\` varchar(255) NOT NULL DEFAULT '' COMMENT 'updated by',
    \`deleted\` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'record deleted',
    PRIMARY KEY (\`id\`)
) ENGINE=InnoDB DEFAULT CHARSET="utf8mb4" COMMENT='$2';
    "
    echo "$text"
}

function copymyddl() {
    if ismac; then
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
    if [ -f "go.mod" ]; then
        go fmt ./...
        echo "Formatted $(pwd)"
    fi
    for d in $(ls);
    do
        if [ -f "$d/go.mod" ]; then
            (cd $d && go fmt ./... && echo "Formatted $d")
        fi
    done
}

function build() {
    go build -o /dev/null ./...
}

function initwork() {
    go work init
    if [ $? -ne 0 ]; then
        return 1
    fi
    # echo "go 1.22" >> go.work
    # echo "" >> go.work
    echo "use ." >> go.work
    echo "" >> go.work
    echo "replace github.com/curtisnewbie/miso => $GIT_PATH/miso" >> go.work;
    echo "" >> go.work
    ls -l
}
export -f initwork

function clean_local_work(){
    if [ -f go.work ]; then
        echogreen 'removed go.work'
        rm go.work
    fi
    if [ -f go.work.sum ]; then
        echogreen 'removed go.work.sum'
        rm go.work.sum
    fi
}

function persudo_ver() {
    python3 $STUFF/go_persudo_ver/persudover.py
}
export -f persudo_ver

function curr_dirname() {
    printf '%q\n' "${PWD##*/}"
}
export -f curr_dirname

function gcmt() {
    msg="$1"
    if [ ! -z "$msg" ]; then
        git commit -am "$msg"
    else
        git add . && git commit
    fi
}
export -f gcmt

function jmapdump() {
    pid="$1"
    dir="$2"

    if [ -z "$pid" ]; then
        echored "\$1 - Pid"
        return -1
    fi
    if [ -z "$dir" ]; then
        dir="$(pwd)"
    fi

    out="$dir/dump_$(date +"%y%m%d_%H%M%S").hprof"
    jmap -dump:format=b,file=$out $pid
    echo
    echogreen "Dump $pid heap to $out"
    echo
}

function jcmdprofile() {
    pid="$1"
    out="$2"

    if [ -z "$pid" ]; then
        echored "\$1 - Pid"
        return -1
    fi
    if [ -z "$out" ]; then
        echored "\$2 - Output JFR file"
        return -1
    fi

    jcmd $pid VM.unlock_commercial_features
    jcmd $pid JFR.start name=sampling settings=profile  delay=20s duration=10m filename="$out"
}

function jcmdcheck() {
    pid="$1"
    if [ -z "$pid" ]; then
        echored "\$1 - Pid"
        return -1
    fi
    jcmd $pid JFR.check
}

function tcp_echo() {
    port="$1"
    if [ -z "$port" ]; then
        port="8080"
    fi

    echo "Echo tcp on port: $port"
    nc -kl $port
}

function upgrade_commit() {
    project="miso"
    commit="$1"
    if [ $# -ge 2 ]; then
        project="$1"
        commit="$2"
    fi

    if [ -f go.work ]; then rm go.work && echo "removed go.work"; fi
    if [ -f go.work.sum ]; then rm go.work.sum && echo "removed go.work.sum"; fi

    moddir=""
    modf="go.mod"
    if [ ! -f "$modf" ]; then
        for di in ./* ; do
            if [ ! -d "$di" ]; then
                continue
            fi
            submod="$di/go.mod"
            if [ -f "$submod" ]; then
                modf="$submod"
                moddir="$di"
            else
                break
            fi
        done
    fi

    wd=$(pwd)
    echo "Mod file found: $modf"

    if [ "$moddir" != "" ]; then
        cd "$moddir"
    fi

    [ ! -z "$commit" ] && miso_ver="$commit"

    echo "Upgrading $project to $miso_ver"

    go get "github.com/curtisnewbie/$project@$miso_ver" \
        && go mod tidy \
        && go fmt ./... \
        && go build -o /dev/null ./... \
        && git commit -am "Upgrade $project to $miso_ver"

    cd "$wd"
    return 0
}
export -f upgrade_commit

function upgrade() {
    project="miso"
    commit="$1"
    if [ $# -ge 2 ]; then
        project="$1"
        commit="$2"
    fi

    if [ -f go.work ]; then rm go.work && echo "removed go.work"; fi
    if [ -f go.work.sum ]; then rm go.work.sum && echo "removed go.work.sum"; fi

    moddir=""
    modf="go.mod"
    if [ ! -f "$modf" ]; then
        for di in ./* ; do
            if [ ! -d "$di" ]; then
                continue
            fi
            submod="$di/go.mod"
            if [ -f "$submod" ]; then
                modf="$submod"
                moddir="$di"
            else
                break
            fi
        done
    fi

    wd=$(pwd)
    echo "Mod file found: $modf"

    if [ "$moddir" != "" ]; then
        cd "$moddir"
    fi

    [ ! -z "$commit" ] && miso_ver="$commit"

    echo "Upgrading $project to $miso_ver"

    go get "github.com/curtisnewbie/$project@$miso_ver" \
        && go mod tidy \
        && go fmt ./... \
        && go build -o /dev/null ./... \
        && echo "git commit -am \"Upgrade $project to $miso_ver\""

    cd "$wd"
    return 0
}
export -f upgrade

function upgrade_all() {
    # l="vfm mini-fstore user-vault event-pump gatekeeper hammer doc-indexer postbox logbot"
    l="vfm mini-fstore user-vault gatekeeper logbot acct"
    for r in $l;
    do
        echogreen ">>> $r"
        (cd ./$r; upgrade "$@")
        printf "\n"
    done
}

function status_all() {
    gitpath="${GIT_PATH}"
    if [ -z $gitpath ]; then
        echo "GIT_PATH is empty"
        return 1
    fi

    l="vfm mini-fstore user-vault event-pump gatekeeper logbot miso grapher chill moon pocket acct"
    for r in $l;
    do
        echogreen ">>> $r"
        (cd $GIT_PATH/$r; git status)
        printf "\n"
    done
}

function pushtag() {
    git tag $1 && git push && git push origin $1
}

function startcluster() {
    l="event-pump vfm mini-fstore gatekeeper acct logbot user-vault drone"
    for r in $l;
    do
        startapp "$r"
    done
}

function stopcluster() {
    l="event-pump vfm mini-fstore gatekeeper acct logbot user-vault"
    for r in $l;
    do
        stopapp "$r"
    done
}

function stopfront() {
    pids=$(ps -ef | grep "ng serve" | grep -v grep | awk '{ print $2}')
    for p in $pids
    do
        kill -15 "$p"
        echo "killed $p"
    done
}

function findapp() {
    app="$1"
    ps -ef | grep $app | grep -v grep
}

function stopapp() {
    app="$1"
    pids=`ps -ef | grep $app | grep -v grep | awk '{ print $2 }'`
    if [ -z "$pids" ]; then
        return 0
    fi
    echo "killing $pids"
    kill -15 $pids
}
export -f stopapp

function restartapp() {
    app="$1"
    stopapp $app
    startapp $app
}

function startapp() {
    app="$1"
    echo "Building $app"
    if [ "$app" = "event-pump" ]; then
        (
            cd "$GIT_PATH/event-pump"
            go run main.go "logging.rolling.file=./logs/event-pump.log" 'consul.enabled=true' 'logging.file.max-backups=1' 'logging.file.max-size=30' > /dev/null 2>&1 &
        )
    elif [ "$app" = "drone" ]; then
        (
            cd "$GIT_PATH/drone"
            go run main.go "logging.rolling.file=./logs/drone.log" 'consul.enabled=true' 'logging.file.max-backups=1' 'logging.file.max-size=30' > /dev/null 2>&1 &
        )
    else
        (
            cd "$GIT_PATH/moon-monorepo/backend/$app"
            logfile="./logs/$app.log"
            if [ -f "$logfile" ]; then
                > "$logfile"
            fi

            if [ -f "main.go" ]; then
                go run main.go "logging.rolling.file=./logs/$app.log" 'consul.enabled=true' 'logging.file.max-backups=1' 'logging.file.max-size=30' > /dev/null 2>&1 &
            else
                go run cmd/main.go "logging.rolling.file=./logs/$app.log" 'consul.enabled=true' 'logging.file.max-backups=1' 'logging.file.max-size=30' > /dev/null 2>&1 &
            fi
        )
    fi
}

function pprof_heap() {
    host_port="$1"
    go tool pprof -http=: http://$host_port/debug/pprof/heap?seconds=30
}

function pprof_profile() {
    host_port="$1"
    go tool pprof -http=: http://$host_port/debug/pprof/profile?seconds=30
}

function benchmark_pprof() {
    # $1 - test name, %2 - path to pkg
    # e.g., benchmark_pprof BenchmarkError ./miso/
    go test -bench $1 -run $1 $2 -v -count=1 -memprofile profile.out && go tool pprof -http=: profile.out
}

function gen_graph() {
    out="out.svg"
    dot -Tsvg $1 > "$out"
    echo "graph generated"
    # readlink -e $out
}

function installbin() {
    mv $1 $LOC_BIN && echo "Moved $1 to $LOC_BIN/$1"
}
export -f installbin

function par() {
    # par 10 echo "!"
    conc="$1"
    cmd="${@:2}"
    # echo "concurrency: $conc, '$cmd'"
    for i in $(seq 1 1 $conc); do
        eval "$cmd" &
        pids[${i}]=$!
    done

    for pid in ${pids[*]}; do
        # echo "Waiting $pid"
        wait $pid &> /dev/null
    done

    echo ""
    echo "par finished, parallel: $1"
    echo ""
}

function restore_tmux() {
    prev=`tmux ls | awk '{ print $1 }' | cut -b 1-1`
    if [ -z "$prev" ]; then
        tmux
        return 0
    fi
    tmux attach-session -t "$prev"
}

function kill_scim() {
    kill -9 $(pgrep SCIM)
}

function newng() {
  ng new "$1" --no-standalone --routing --ssr=false
}

function urldecode() {
    python3 "$STUFF/urlencode.py" -decode -value "$1"
}
export -f urldecode

function urlencode() {
    python3 "$STUFF/urlencode.py" -value "$1"
}
export -f urlencode

function ocr() {
    # brew install tesseract
    # brew install tesseract-lang
    tesseract "$1" - -l "chi_sim+eng" --oem 3 --psm 3 quiet
}
export -f ocr

export BREW_SERVICES="consul mysql@5.7 redis rabbitmq"
function stopservices() {
  for s in $BREW_SERVICES; do
    brew services stop $s
  done
}

function startservices() {
  for s in $BREW_SERVICES; do
    brew services start $s
  done
}

function redis_del_keys() {
    host="$1"
    password="$2"
    pattern="$3"
    if [ -z "$pattern" ]; then
        echo "Please specify key pattern"
        return 0
    fi
    redis-cli -h "$host" -a "$password" keys "$pattern" | xargs -I {} bash -c "echo 'Deleting key {}' && devredis del {}"
}

function unload_corplink() {
  # sudo launchctl list | grep corplink
  sudo launchctl unload -w /Library/LaunchDaemons/com.volcengine.corplink.service.plist
  sudo launchctl unload -w /Library/LaunchDaemons/com.volcengine.corplink.systemextension.plist
  sudo launchctl unload -w ~/Library/LaunchAgents/CorpLink.plist
}

function load_corplink() {
  sudo launchctl load -w /Library/LaunchDaemons/com.volcengine.corplink.service.plist
  sudo launchctl load -w /Library/LaunchDaemons/com.volcengine.corplink.systemextension.plist
  sudo launchctl load -w ~/Library/LaunchAgents/CorpLink.plist
}

function sqlclone() {
  ip="$1"
  user="$2"
  password="$3"
  sql="$4"
  echo ""
  python3 "$STUFF/dbinsert.py" -host "$ip" -user "$user" -password "$password" -sql "$sql"
  python3 "$STUFF/dbupdate.py" -host "$ip" -user "$user" -password "$password" -sql "$sql"
}

function xrq_start() {
  caffe_pid="$(ps -ef | grep caffeinate | grep -v grep | awk '{ print $2 }')"
  if [ "$caffe_pid" == "" ]; then
    caffeinate -s & &> /dev/null \
      && echogreen "caffeinate started in background with pid: $(ps -ef | grep caffeinate | grep -v grep | awk '{ print $2 }')"
  else
    echogreen "caffeinate already running with pid: $caffe_pid"
  fi

  slc_pid="$(ps -ef | grep MacOS/SunloginClient | grep -v grep | grep -v "mod=service" | awk '{ print $2 }')"
  if [ "$slc_pid" == "" ]; then
    open /Applications/SunloginClient.app \
      && echogreen "sunloginclient started with pid: $(ps -ef | grep MacOS/SunloginClient | grep -v grep | grep -v "mod=service" | awk '{ print $2 }')"
  else
    echogreen "sunloginclient already running with pid: $slc_pid"
  fi
}

function xrq_stop() {
  caffe_pid="$(ps -ef | grep caffeinate | grep -v grep | awk '{ print $2 }')"
  if [ "$caffe_pid" != "" ]; then
    kill -15 "$caffe_pid" && echored "stopped $caffe_pid"
  fi

  slc_pid="$(ps -ef | grep MacOS/SunloginClient | grep -v grep | grep -v "mod=service" | awk '{ print $2 }')"
  if [ "$slc_pid" != "" ]; then
    kill -15 "$slc_pid" && echored "stopped $slc_pid"
  fi
}

function download_arthas() {
    curl -O https://arthas.aliyun.com/arthas-boot.jar \
        && mv arthas-boot.jar "$USER_EXEC/" \
        && echogreen "arthas-boot.jar moved to $USER_EXEC"
}

function download_jmc() {
    brew install --cask jdk-mission-control
}

function sync_monorepo() {
    rsync -av --exclude .git $GIT_PATH/event-pump/* $GIT_PATH/moon-monorepo/backend/event-pump/
    # rsync -av --exclude .git $GIT_PATH/moon-monorepo/backend/vfm/* $GIT_PATH/vfm/
    # rsync -av --exclude .git --exclude trash/ --exclude storage/ $GIT_PATH/moon-monorepo/backend/mini-fstore/* $GIT_PATH/mini-fstore/
    # rsync -av --exclude .git $GIT_PATH/moon-monorepo/backend/user-vault/* $GIT_PATH/user-vault/
    # rsync -av --exclude .git $GIT_PATH/moon-monorepo/backend/logbot/* $GIT_PATH/logbot/
    # rsync -av --exclude .git $GIT_PATH/moon-monorepo/backend/gatekeeper/* $GIT_PATH/gatekeeper/
    # rsync -av --exclude node_modules/ --exclude .git --exclude dist/ $GIT_PATH/moon-monorepo/frontend/moon/* $GIT_PATH/moon/
}

function deploy_moon_all() {
    (
        cd $STUFF/moon_deploy
        ./deploy_moon_all.sh
    )
}

function deploy_moon_backend() {
    (
        cd $STUFF/moon_deploy
        ./deploy_moon_backend.sh
    )
}

function applog() {
    if [ -z "$1" ]; then
        less -nR "$GIT_PATH/moon-monorepo/backend/logbot/logs/merged.log"
    else
        if [ "$1" = "event-pump" ]; then
            less -nR "$GIT_PATH/event-pump/logs/$1.log"
        elif [ "$1" = "drone" ]; then
            less -nR "$GIT_PATH/drone/logs/$1.log"
        else
            less -nR "$GIT_PATH/moon-monorepo/backend/$1/logs/$1.log"
        fi
    fi
}

function jekyll_new_post() {
    if [ ! -d "_posts" ]; then
        echored "./_posts not found"
        return 1
    fi
    name="$1"
    fname=$(echo "$name" | awk '{print tolower($0)}')
    fname="${fname// /-}"
    today=$(date +'%Y-%m-%d')
    fn="./_posts/${today}-${fname}.md"
    touch "$fn" \
        && echo "created $fn" \
        && echo "---"  >> "$fn" \
        && echo "layout: post"  >> "$fn" \
        && echo "title: \"${name}\""  >> "$fn" \
        && echo "date: ${today} 09:00:00 +0800"  >> "$fn" \
        && echo "categories: Learning"  >> "$fn" \
        && echo "hidden: 1"  >> "$fn" \
        && echo "---"  >> "$fn"
}

function link_title() {
    python3.11 $STUFF/link_title.py -f $1
}

function deploy() {
    app="$1"
    if [ -z "$app" ]; then
        echo "Which app"
        return 0
    fi
    $STUFF/moon_deploy/deploy_$app.sh
}

function activate() {
    if [ -f "./bin/activate" ]; then
        source ./bin/activate
    else
        echored "bin/activate not found"
        return 1
    fi
}

function mac_hide_desktop() {
    # https://www.reddit.com/r/mac/comments/1axg037/hide_all_files_and_folders_on_desktop/
    defaults write com.apple.finder CreateDesktop FALSE; killall Finder

    # to restore
    # defaults write com.apple.finder CreateDesktop TRUE; killall Finder
}

function upgrade_go() {
    if [ -z "$1" ]; then
        echored "specify golang version, e.g., 1.24.1, 1.24.3"
        return -1
    fi
    ver="$1"
    exec="go$ver"
    go install golang.org/dl/go$ver@latest \
        && $exec download \
        && $exec version \
        && root=$($exec env GOROOT) \
        && echo "Installed at: $root" \
        && echo "Removing previous golang version at /usr/local/go" \
        && sudo rm -rf /usr/local/go \
        && sudo mv $root /usr/local/go \
        && echo "Finished"
}

function list_branch_author() {
   git for-each-ref --format=' %(authorname) %09 %(refname)' --sort=authorname
}

function remove_prefix() {
    v="${1#"$2"}"
    echo $v
}

function remove_suffix() {
    v="${1%"$2"}"
    echo $v
}

function sshkeygen() {
    ssh-keygen -t rsa -b 4096
}

function rsakeygen() {
    priv_loc="keypair_private_pkcs8.pem"
    priv_loc_tmp="${priv_loc}_tmp"
    pub_loc="keypair_public_x509.key"

    # https://blog.ndpar.com/2017/04/17/p1-p8/
    # pkcs1: publick/private key format
    # pkcs8: private key format
    # x.509: public key format
    # If priv_loc is somehow pkcs1, use following command to convert to pkcs8 if necessary
    #   openssl pkcs8 -in $priv_loc -topk8 -out $priv_loc -nocrypt
    openssl genrsa -out $priv_loc 4096 && echo "Generated private key: $priv_loc"
    openssl rsa -in $priv_loc -pubout -out $pub_loc && echo "Extracted public key: $priv_loc"
    # if grep -q "BEGIN RSA PRIVATE KEY" $priv_loc; then
        openssl pkcs8 -in $priv_loc -topk8 -out $priv_loc_tmp -nocrypt && mv $priv_loc_tmp $priv_loc
    # fi
}

function ggrep() {
    git grep $1 $(git rev-list --all)
}

function git_rm_tail_tags() {
    tags=$(git tag | tail);
    printf "Removing tags:\n$tags\n\n"
    for t in $tags;
        do git tag -d $t && git push -d origin $t;
    done
}

function gm() {
    while ! git fetch; do sleep 0.3; done;
    git merge
}

function mvlast() {
    last=$(ls -t $1 | head -n 1)
    to="$2"
    if [ -z $to ]; then
        to="."
    fi
    mv "$1/$last" $to
}

function cplast() {
    last=$(ls -t $1 | head -n 1)
    to="$2"
    if [ -z $to ]; then
        to="."
    fi
    cp "$1/$last" $to
}

#function miso_patch() {
#    gopatch -p $GIT_PATH/miso/patch/$1.patch ./...
#}
#

function llm() {
    query="$1"
    model="qwen3:1.7b"
    curl http://localhost:11434/api/chat -s -d "{
        \"model\": \"$model\",
        \"stream\": false,
        \"think\": false,
        \"messages\": [
            { \"role\": \"user\", \"content\": \"$query\" }
        ]
    }" | jq -r .message.content
}
