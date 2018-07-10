# Release Kick-off
## CI Build Status

[![Build Status](https://travis-ci.org/mozilla-releng/ship-it.svg?branch=master)](https://travis-ci.org/mozilla-releng/ship-it)
[![Coverage Status](https://coveralls.io/repos/github/mozilla-releng/ship-it/badge.svg?branch=master)](https://coveralls.io/github/mozilla-releng/ship-it?branch=master)


[Product-details JSON sync status](https://github.com/mozilla/product-details-json): [![Build Status](https://ci.us-west.moz.works/job/product-details-json-watch/badge/icon)](https://ci.us-west.moz.works/job/product-details-json-watch/)


## About
Release kick-off (ship-it) is a Mozilla "internal" tool used to start the release of
Firefox Desktop, Android and Thunderbird.
This tool is specific to Mozilla workflows and tools.

### Python Deps
Dependencies are listed in requirements/*.txt.

* compiled+prod are required to run in production
* compiled+prod+dev are required to run the standalone server/tests

## Running Locally
To get the list of options:

$ ```python kickoff-web.py --help```

To run release-kickoff using mysql with docker:

* ```docker-compose build```
* ```docker-compose up```

To run release-kickoff using a sqlite database

* ```python kickoff-web.py -d sqlite://///var/www/update.db --username=admin --password=password```

Or with MySQL:

* ```python kickoff-web.py -d mysql://root@localhost/ship_it --username=admin --password=password```

Open your Firefox on: **http://127.0.0.1:5000/**

If you're on Mac or Windows, you'll need Docker for Mac or Docker for Windows v1.12.0 or higher. Or if you're
running Docker in a VM for another reason, you'll need to replace 127.0.0.1 with the IP of your VM.

To have the auto completion in the various forms there needs to be some releases in the database. A
snapshot of data is included in the repo. You can reset the db by removing the .cache/mysql directory
and run `docker-compose up`.

## Testing

To run python and JS tests with docker:

* ```docker build -t shipit-test-runner -f Dockerfile-tests ./```
* ```docker run --rm -v $(pwd):/src -ti shipit-test-runner /src/scripts/run_tests.sh```

## Deployment
After a PR is merged to master, it is automatically deployed to https://ship-it-dev.allizom.org/ and https://ship-it.allizom.org/. In order to deploy to production, the `master` branch should be pushed to the `production` branch:

```git push origin origin/master:production```
