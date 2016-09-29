FROM docker.emarbox.com/sys/alpine-python:gcc
MAINTAINER taochengwei <taochengwei@emar.com>
ADD . /SwarmOpsApi
ADD misc/supervisord.conf /etc/supervisord.conf
WORKDIR /SwarmOpsApi
RUN apk add --no-cache libffi-dev openssl-dev
RUN pip install supervisor Flask==0.11.1 Flask-RESTful==0.3.5 SpliceURL>=0.5 tornado gevent setproctitle docker-py requests paramiko
ENTRYPOINT ["supervisord"]