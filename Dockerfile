FROM alpine:gcc

MAINTAINER Mr.tao <staugur@saintic.com>

ADD src /SwarmOps

ADD misc/supervisord.conf /etc/supervisord.conf

ADD requirements.txt /tmp

WORKDIR /SwarmOps

RUN pip install --timeout 30 --index https://pypi.douban.com/simple/ -r /tmp/requirements.txt

EXPOSE 10130

ENTRYPOINT ["supervisord"]