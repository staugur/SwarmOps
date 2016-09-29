# -*- coding:utf8 -*-

import re
import uuid
import json
import datetime
import requests
from time import sleep
from SpliceURL import Splice
from .syslog import Syslog


logger         = Syslog.getLogger()
Ot2Bool        = lambda string:string.lower() in ("desc",) #将字符串desc转化为True
gen_requestId  = lambda :str(uuid.uuid4())

#Regular expressions and functions that depend on it.
ip_pat       = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
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
                logger.info("Register the etcd returned(status_code: %d)" %(req_key.status_code))
            except Exception,e:
                logger.error(e, exc_info=True)
        else:
            logger.error("WanIp invaild, continue.")
            WanIp = get_wanip()
            continue
        sleep(10)