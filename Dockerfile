FROM registry.saintic.com/python

MAINTAINER Mr.tao <staugur@saintic.com>

ADD .src /SwarmOpsApi

ADD misc/supervisord.conf /etc/supervisord.conf

ADD requirements.txt /tmp

WORKDIR /SwarmOpsApi

#RUN apk add --no-cache libffi-dev openssl-dev

RUN pip install --timeout 30 --index https://pypi.douban.com/simple/ -r /tmp/requirements.txt

ENTRYPOINT ["supervisord"]