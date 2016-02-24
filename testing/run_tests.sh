#!bin/bash

set -e

echo "Expect to run from docker, in callek/shipit-test-runner"
echo "  docker run --rm -v `pwd`:/src -ti callek/shipit-test-runner /src/testing/run_tests.sh"
cd /src
npm install
tox
./node_modules/.bin/grunt --verbose
