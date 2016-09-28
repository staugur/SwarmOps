# -*- coding:utf8 -*-

import os
import re
import uuid
import json
import time
import datetime
import docker
import requests
from libs.syslog import Syslog
from SpliceURL import Splice
from random import choice


logger         = Syslog.getLogger()
gen_requestId  = lambda :str(uuid.uuid4())
docker_connect = lambda conn:docker.Client(base_url=conn, timeout=5, version="auto")
ip_pat         = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
Ot2Bool        = lambda string:string.lower() in ("desc",) #将字符串desc转化为True

#Regular expressions and functions that depend on it.
commaPat     = re.compile(r"\s*,\s*")
commaConvert = lambda string:[ l for l in re.split(commaPat, string) if l ]


def timeChange(timestring):
    logger.debug("Change time, source time is %s" %timestring)
    startedat = timestring.replace('T', ' ')[:19]
    try:
        dt  = datetime.datetime.strptime(startedat, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)
        res = dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception, e:
        logger.warn(e, exc_info=True)
    else:
        logger.debug("Change time, result time is %s" %res)
        return res


def ip_check(ip):
    logger.info("the function ip_check param is %s" %ip)
    if isinstance(ip, (str, unicode)):
        return ip_pat.match(ip)


def get_ip(getLanIp=False):
    import commands
    _WanIpCmd = "/sbin/ifconfig | grep -o '\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}' | grep -vE '192.168.|172.1[0-9]|172.2[0-9]|172.3[0-1]|10.[0-9]|255|127.0.0.1|0.0.0.0'"
    _WanIp    = commands.getoutput(_WanIpCmd).replace("\n", ",")
    if _WanIp:
        logger.info("First get ip success, WanIp is %s with cmd(%s), enter LanIp." %(_WanIp, _WanIpCmd))
    else:
        _WanIp = requests.get("http://members.3322.org/dyndns/getip", timeout=3).text.strip()
        if ip_check(_WanIp):
            logger.info("Second get ip success, WanIp is %s with requests, enter LanIp." %_WanIp)
        else:
            logger.error("get_ip fail")
            return ('', '')
    if getLanIp == True:
        _LanIpCmd = "/sbin/ifconfig | grep '192.168.' | grep -o '\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}' | grep -v 255 | sort -n -k 3 -t .| head -n1"
        _LanIp    = commands.getoutput(_LanIpCmd).replace("\n", ",") or 'Unknown'
        logger.info("Get ip success, LanIp is %s with cmd(%s), over IP." %(_LanIp, _LanIpCmd))
        Ips = (_WanIp, _LanIp)
    else:
        Ips = (_WanIp,)
    return Ips

def get_wanip():
    ip = requests.get("http://members.3322.org/dyndns/getip", timeout=3).text.strip()
    if ip_check(ip):
        logger.info("Second get ip success, WanIp is %s with requests, enter LanIp." %ip)
    else:
        logger.error("get_ip fail")
    return ip

def putEtcd(name="SwarmOpsApi", port=10030, etcd={}, misc={}):
    if not isinstance(etcd, dict): raise TypeError("etcd not a dict.")
    if not isinstance(misc, dict): raise TypeError("misc not a dict.")
    WanIp = get_wanip()
    etcdUrl = Splice(scheme=etcd.get("ETCD_SCHEME"), domain=etcd.get("ETCD_HOST"), port=etcd.get("ETCD_PORT"), path=etcd.get("ETCD_VERSION") + "/keys").geturl
    etcdKey = etcdUrl + "/%s/%s/%s:%d" %(name, "sys", WanIp, port)
    while True:
        if ip_check(WanIp):
            logger.info("You want to start creating the key URL etcd is %s, begin" %etcdKey)
            try:
                value = {"service.name": name, "service.address": WanIp, "service.port": port, "service.tag": misc.get("version")}
                req_key = requests.put(etcdKey, data={"value": json.dumps(value), "ttl": 30}, timeout=10)
                logger.info("And the key returned(status_code: %d): %s" %(req_key.status_code, req_key.json()))
            except Exception,e:
                logger.error(e)
        else:
            logger.error("WanIp invaild, continue.")
            WanIp = get_wanip()
            continue
        time.sleep(10)