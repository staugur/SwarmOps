# -*- coding:utf8 -*-


import re
import uuid
import datetime
from redis import Redis
from config import REDIS
from .syslog import Syslog


ip_pat          = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
commaPat        = re.compile(r"\s*,\s*")
commaConvert    = lambda string:[ l for l in re.split(commaPat, string) if l ]
logger          = Syslog.getLogger()
Ot2Bool         = lambda string:string.lower() in ("desc",) #将字符串desc转化为True
gen_requestId   = lambda :str(uuid.uuid4())
ParseRedis      = lambda string: string.split("redis://")[-1].split(":")
RedisConnection = Redis(host=ParseRedis(REDIS["Connection"])[0], port=ParseRedis(REDIS["Connection"])[1], password=ParseRedis(REDIS["Connection"])[2], db=0, socket_timeout=5, socket_connect_timeout=5)


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
