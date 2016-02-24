FROM rail/python-test-runner

MAINTAINER callek@mozilla.com

RUN apt-get -q update && \
    apt-get -q --yes install \
        sqlite3 \
        phantomjs \
        npm \
    && apt-get clean

RUN ln -s /usr/bin/nodejs /usr/bin/node
