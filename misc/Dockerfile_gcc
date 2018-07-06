FROM alpine:latest

MAINTAINER taochengwei <staugur@saintic.com>

ADD localtime /etc/localtime

ENV PS1 "\[\033[01;31m\]\u\[\033[00m\]@\[\033[01;32m\]\W\[\033[00m\] "

RUN apk add --no-cache gcc g++ python python-dev py-pip 

RUN echo 'ls -alh --color=auto $@' > /bin/l && chmod +x /bin/l

ENTRYPOINT ["/bin/sh"]
