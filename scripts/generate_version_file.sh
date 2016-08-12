#!/bin/bash

set -e

commit=$(git rev-parse HEAD)
version='latest'

# TODO: Add link to CI job that produced the docker image
# TODO: Fetch source repo from contribute.json
echo "{
    \"commit\": \"${commit}\",
    \"version\": \"${version}\",
    \"source\": \"https://github.com/mozilla-releng/ship-it\"
}" > version.json
