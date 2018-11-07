# -*- coding: utf-8 -*-
"""
    SwarmOps.utils.tool
    ~~~~~~~~~~~~~~

    Common function.

    :copyright: (c) 2018 by staugur.
    :license: MIT, see LICENSE for more details.
"""

import re, hashlib, datetime, time, random, hmac
from uuid import uuid4
from log import Logger
from base64 import b32encode
from config import SYSTEM

ip_pat          = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
mail_pat        = re.compile(r"([0-9a-zA-Z\_*\.*\-*]+)@([a-zA-Z0-9\-*\_*\.*]+)\.([a-zA-Z]+$)")
chinese_pat     = re.compile(u"[\u4e00-\u9fa5]+")
Universal_pat   = re.compile(r"[a-zA-Z\_][0-9a-zA-Z\_]*")
comma_pat       = re.compile(r"\s*,\s*")
logger          = Logger("sys").getLogger
err_logger      = Logger("error").getLogger
plugin_logger   = Logger("plugin").getLogger
access_logger   = Logger("access").getLogger
md5             = lambda pwd:hashlib.md5(pwd).hexdigest()
hmac_sha256     = lambda message: hmac.new(key=SYSTEM["HMAC_SHA256_KEY"], msg=message, digestmod=hashlib.sha256).hexdigest()
gen_token       = lambda n=32:b32encode(uuid4().hex)[:n]
gen_requestId   = lambda :str(uuid4())
gen_fingerprint = lambda n=16,s=2: ":".join([ "".join(random.sample("0123456789abcdef",s)) for i in range(0, n) ])


def ip_check(ip):
    if isinstance(ip, (str, unicode)):
        return ip_pat.match(ip)

def url_check(addr):
    """检测UrlAddr是否为有效格式，例如
    http://ip:port
    https://abc.com
    """
    regex = re.compile(
        r'^(?:http)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if addr and isinstance(addr, (str, unicode)):
        if regex.match(addr):
            return True
    return False

def get_current_timestamp():
    """ 获取本地当前时间戳(10位): Unix timestamp：是从1970年1月1日（UTC/GMT的午夜）开始所经过的秒数，不考虑闰秒 """
    return int(time.time())

def timestamp_after_timestamp(timestamp=None, seconds=0, minutes=0, hours=0, days=0):
    """ 给定时间戳(10位),计算该时间戳之后多少秒、分钟、小时、天的时间戳(本地时间) """
    # 1. 默认时间戳为当前时间
    timestamp = get_current_timestamp() if timestamp is None else timestamp
    # 2. 先转换为datetime
    d1 = datetime.datetime.fromtimestamp(timestamp)
    # 3. 根据相关时间得到datetime对象并相加给定时间戳的时间
    d2 = d1 + datetime.timedelta(seconds=int(seconds), minutes=int(minutes), hours=int(hours), days=int(days))
    # 4. 返回某时间后的时间戳
    return int(time.mktime(d2.timetuple()))

def timestamp_to_timestring(timestamp, format='%Y-%m-%d %H:%M:%S'):
    """ 将时间戳(10位)转换为可读性的时间 """
    # timestamp为传入的值为时间戳(10位整数)，如：1332888820
    timestamp = time.localtime(timestamp)
    # 经过localtime转换后变成
    ## time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=0)
    # 最后再经过strftime函数转换为正常日期格式。
    return time.strftime(format, timestamp)

def timestring_to_timestamp(timestring, format="%Y-%m-%d %H:%M:%S"):
    """ 将普通时间格式转换为时间戳(10位), 形如 '2016-05-05 20:28:54'，由format指定 """
    try:
        # 转换成时间数组
        timeArray = time.strptime(timestring, format)
    except Exception:
        raise
    else:
        # 转换成10位时间戳
        return int(time.mktime(timeArray))

class DO(dict):
    """A dict that allows for object-like property access syntax."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

def ParseMySQL(mysql, callback="dict"):
    """解析MYSQL配置段"""
    if not mysql:
        return None
    protocol, dburl = mysql.split("://")
    if "?" in mysql:
        dbinfo, dbargs = dburl.split("?")
    else:
        dbinfo, dbargs = dburl, "charset=utf8&timezone=+8:00"
    host, port, user, password, database = dbinfo.split(":")
    charset, timezone = dbargs.split("&")[0].split("charset=")[-1] or "utf8", dbargs.split("&")[-1].split("timezone=")[-1] or "+8:00"
    if callback in ("list", "tuple"):
        return protocol, host, port, user, password, database, charset, timezone
    else:
        return {"Protocol": protocol, "Host": host, "Port": port, "Database": database, "User": user, "Password": password, "Charset": charset, "Timezone": timezone}

def create_redis_engine():
    """ 创建redis连接 """
    from redis import from_url
    from config import REDIS as REDIS_URL
    return from_url(REDIS_URL)

def create_mysql_engine(mysql_url=None):
    """ 创建mysql连接 """
    from torndb import Connection
    from config import MYSQL as MYSQL_URL
    protocol, host, port, user, password, database, charset, timezone = ParseMySQL(mysql_url or MYSQL_URL, callback="tuple")
    return Connection(host="{}:{}".format(host, port), database=database, user=user, password=password, time_zone=timezone, charset=charset)
