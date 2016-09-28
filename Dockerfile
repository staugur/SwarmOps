FROM alpine:gcc

MAINTAINER taochengwei <taochengwei@emar.com>

ADD . /SwarmOpsApi

ADD misc/supervisord.conf /etc/supervisord.conf

WORKDIR /SwarmOpsApi

RUN apk add --no-cache libffi-dev openssl-dev

RUN pip install supervisor Flask Flask-RESTful tornado gevent setproctitle requests SpliceURL docker-py paramiko && \
    chmod +x Product.py ControlDSMRun.sh

ENTRYPOINT ["supervisord"]