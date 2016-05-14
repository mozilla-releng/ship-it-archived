#!bin/bash

set -e

if [ ! -f /.dockerenv ]; then
    echo "We expect to run from docker, see the README for more info"
    exit 1
fi

# Don't write python bytecode, docker writes out files as root.
export PYTHONDONTWRITEBYTECODE=1

cd /src
npm install
tox
./node_modules/.bin/grunt --verbose
