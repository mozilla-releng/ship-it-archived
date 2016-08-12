#!/bin/bash

set -e

commit=$(git rev-parse HEAD)
version=$(cat version.txt)
source=$(cat contribute.json | python -c 'import json, sys; a = json.load(sys.stdin); print a["repository"]["url"]')

# TODO: Add link to CI job that produced the docker image
echo "{
    \"commit\": \"${commit}\",
    \"version\": \"${version}\",
    \"source\": \"${source}\"
}" > version.json
