#!/bin/bash

function help() {
    echo "args[0] - target directory"
    echo "args[1] - project name"
    echo "args[2] - project description (optional)"
}

curr=$MVN_INIT_BASE_PATH
if [ -z "$curr" ]; then
    curr="./"
fi
echo "base path: $curr"

target="$1"
project="$2"
description="$3"

# echo "Args: $@"

if [ -z "$target" ]; then
    echo "Please specify target"
    help
    exit 1;
fi

if [ ! -d "$target" ]; then
    mkdir "$target"
fi
echo "Target directory: $target"


if [ -z "$project" ]; then
    echo "Please specify project name"
    help
    exit 1;
fi
echo "Project name: $project"

if [ -f "$target/$project" ]; then
    echo "Project already existed"
    exit 1;
fi

if [ -z "$description" ]; then
    description=$project
fi

tzip="$target/template.zip"
if [ -f "$tzip" ]; then
    rm "$tzip" 
fi

zipd="$target/template"
if [ -d "$zipd" ]; then
    rm -rvf "$zipd"
fi

projd="$target/$project"
if [ -d "$projd" ]; then
    echo "Please remove '$projd' first"
    exit 1
fi

cp "$curr/template.zip" "$target"
cp "$curr/.gitignore" "$target"
(
cd $target  
unzip "./template.zip"
rm "./template.zip"
mv "template" "$project"
)

pom_path="$target/$project/pom.xml"
echo "starting to reconfigure project pom: $pom_path"
$curr/reconfigure.py "$pom_path" "$project" "$description"

echo "finished..."

