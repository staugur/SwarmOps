# -*- coding: utf-8 -*-
"""
    SwarmOps.utils.web
    ~~~~~~~~~~~~~~

    Common function for web.

    :copyright: (c) 2018 by staugur.
    :license: MIT, see LICENSE for more details.
"""

import json
from .tool import logger
from .jwt import JWTUtil, JWTException
from .aes_cbc import CBC
from libs.base import CacheBase
from config import SSO
from functools import wraps
from flask import g, request, redirect, url_for, abort

jwt = JWTUtil()
cbc = CBC()


def get_referrer_url():
    """获取上一页地址"""
    if request.referrer and request.referrer.startswith(request.host_url) and request.endpoint and not "api." in request.endpoint:
        url = request.referrer
    else:
        url = None
    return url


def get_redirect_url(endpoint="front.index"):
    """获取重定向地址
    NextUrl: 引导重定向下一步地址
    ReturnUrl: 最终重定向地址
    以上两个不存在时，如果定义了非默认endpoint，则首先返回；否则返回referrer地址，不存在时返回endpoint默认主页
    """
    url = request.args.get('NextUrl') or request.args.get('ReturnUrl')
    if not url:
        if endpoint != "front.index":
            url = url_for(endpoint)
        else:
            url = get_referrer_url() or url_for(endpoint)
    return url


def set_ssoparam(ReturnUrl="/"):
    """生成sso请求参数，5min过期"""
    app_name = SSO.get("app_name")
    app_id = SSO.get("app_id")
    app_secret = SSO.get("app_secret")
    return cbc.encrypt(jwt.createJWT(payload=dict(app_name=app_name, app_id=app_id, app_secret=app_secret, ReturnUrl=ReturnUrl), expiredSeconds=300))


def set_sessionId(uid, seconds=43200, sid=None):
    """设置cookie"""
    payload = dict(uid=uid, sid=sid) if sid else dict(uid=uid)
    sessionId = jwt.createJWT(payload=payload, expiredSeconds=seconds)
    return cbc.encrypt(sessionId)


def verify_sessionId(cookie):
    """验证cookie"""
    if cookie:
        try:
            sessionId = cbc.decrypt(cookie)
        except Exception, e:
            logger.debug(e)
        else:
            try:
                success = jwt.verifyJWT(sessionId)
            except JWTException, e:
                logger.debug(e)
            else:
                # 验证token无误即设置登录态，所以确保解密、验证两处key切不可丢失，否则随意伪造！
                return success
    return False


def analysis_sessionId(cookie, ReturnType="dict"):
    """分析获取cookie中payload数据"""
    data = dict()
    if cookie:
        try:
            sessionId = cbc.decrypt(cookie)
        except Exception, e:
            logger.debug(e)
        else:
            try:
                success = jwt.verifyJWT(sessionId)
            except JWTException, e:
                logger.debug(e)
            else:
                if success:
                    # 验证token无误即设置登录态，所以确保解密、验证两处key切不可丢失，否则随意伪造！
                    data = jwt.analysisJWT(sessionId)["payload"]
    if ReturnType == "dict":
        return data
    else:
        return data.get("sid"), data.get("uid")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.signin:
            return redirect(url_for('sso.Login'))
        return f(*args, **kwargs)
    return decorated_function


def anonymous_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.signin:
            return redirect(get_redirect_url())
        return f(*args, **kwargs)
    return decorated_function


def set_userinfo(uid, userinfo, expire=None):
    """ 缓存uid用户信息5min """
    if uid and isinstance(userinfo, dict):
        key = "PublicCache:userinfo:{}".format(uid)
        source = get_userinfo(uid)
        source.update(userinfo)
        if source:
            cache = CacheBase()
            try:
                cache.set(key, json.dumps(source), expire)
            except Exception,e:
                logger.warn(e)
            else:
                return True
    return False


def get_userinfo(uid):
    """ 查看缓存中uid对应的用户信息 """
    if uid:
        key = "PublicCache:userinfo:{}".format(uid)
        cache = CacheBase()
        try:
            data = json.loads(cache.get(key))
        except:
            pass
        else:
            return data
    return dict()

