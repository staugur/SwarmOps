# -*- coding: utf8 -*-


import re
import uuid
import datetime
import requests
import hashlib
from redis import Redis
from config import STORAGE
from functools import wraps
from flask import g, request, redirect, url_for, abort


md5             = lambda pwd:hashlib.md5(pwd).hexdigest()
ip_pat          = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
comma_Pat       = re.compile(r"\s*,\s*")
Ot2Bool         = lambda string:string.lower() in ("desc",) #将字符串desc转化为True
gen_requestId   = lambda :str(uuid.uuid4())
ParseRedis      = STORAGE["Connection"].split("redis://")[-1].split(":")
RedisConnection = Redis(host=ParseRedis[0], port=ParseRedis[1], password=ParseRedis[2] if len(ParseRedis) >= 3 else None, db=0, socket_timeout=5, socket_connect_timeout=5)


def timeChange(timestring):
    """ 将形如2017-01-19T02:05:58.129161072Z转化为可读性高的字符串 """

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


def string2dict(string):
    """ 把规律性字符串转化为字典 """
    if string:
        data = {}
        for _ in re.split(comma_Pat, string):
            k, v = _.split("=")
            data.update({k:v})
    else:
        data = {}
    logger.info("change string2dict, return {}".format(data))
    return data

