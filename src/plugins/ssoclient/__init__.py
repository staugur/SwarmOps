# -*- coding: utf-8 -*-
"""
    plugins.ssoclient
    ~~~~~~~~~~~~~~~~~

    SSO Client

    :copyright: (c) 2018 by staugur.
    :license: MIT, see LICENSE for more details.
"""

#: Importing these two modules is the first and must be done.
#: 首先导入这两个必须模块
from __future__ import absolute_import
from libs.base import PluginBase
#: Import the other modules here, and if it's your own module, use the relative Import. eg: from .lib import Lib
#: 在这里导入其他模块, 如果有自定义包目录, 使用相对导入, 如: from .lib import Lib
import requests, json, hmac, hashlib, re
from flask import Blueprint, request, jsonify, g, redirect, url_for, make_response
from flask_pluginkit import string_types
from config import SSO, SYSTEM
from utils.web import login_required, anonymous_required, set_ssoparam, set_sessionId, get_redirect_url, get_referrer_url, set_userinfo, logger

#：Your plugin name
#：你的插件名称
__plugin_name__ = "ssoclient"
#: Plugin describes information
#: 插件描述信息
__description__ = "SSO Client"
#: Plugin Author
#: 插件作者
__author__      = "Mr.tao <staugur@saintic.com>"
#: Plugin Version
#: 插件版本
__version__     = "0.1.0" 
#: Plugin Url
#: 插件主页
__url__         = "https://www.saintic.com"
#: Plugin License
#: 插件许可证
__license__     = "MIT"
#: Plugin License File
#: 插件许可证文件
__license_file__= "LICENSE"
#: Plugin Readme File
#: 插件自述文件
__readme_file__ = "README"
#: Plugin state, enabled or disabled, default: enabled
#: 插件状态, enabled、disabled, 默认enabled
__state__       = "enabled"

# 定义解析以逗号分隔的字符串为列表
comma_pat = re.compile(r"\s*,\s*")

def sso_request(url, params=None, data=None, timeout=5, num_retries=1):
    """定义请求函数
    @params dict: 请求查询参数
    @data dict: 提交表单数据
    @timeout int: 超时时间，单位秒
    @num_retries int: 超时重试次数
    """
    headers = {"User-Agent": "Mozilla/5.0 (X11; CentOS; Linux i686; rv:7.0.1406) Gecko/20100101 PassportClient/{}".format(__version__)}
    try:
        resp = requests.post(url, params=params, headers=headers, timeout=timeout, data=data).json()
    except requests.exceptions.Timeout,e:
        if num_retries > 0:
            return sso_request(url, params=params, data=data, timeout=timeout, num_retries=num_retries-1)
    else:
        return resp

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

def allow_uids():
    """解析允许登录的uid列表"""
    if SSO["sso_allow"] and isinstance(SSO["sso_allow"], string_types):
        uids = [ uid for uid in comma_pat.split(SSO["sso_allow"]) if uid ]
        return uids

def deny_uids():
    """解析拒绝登录的uid列表"""
    if SSO["sso_deny"] and isinstance(SSO["sso_deny"], string_types):
        uids = [ uid for uid in comma_pat.split(SSO["sso_deny"]) if uid and isinstance(uid, string_types) ]
        return uids
    return []

def is_allowUid(uid):
    """判断uid是否允许登录，规则(按数字顺序判断，每一步返回True即刻中止并return False拒绝后续登录):
    1. uid在拒绝列表中
    2. 允许列表为True时，uid不在允许列表；允许列表为False时。
    :returns:bool:True允许登录，False拒绝登录
    """
    if uid and isinstance(uid, string_types):
        allowUids = allow_uids()
        denyUids = deny_uids()
        if uid in denyUids:
            return False
        if allowUids:
            return uid in allowUids
        else:
            return True

def hmac_sha256(message):
    """HMAC SHA256 Signature"""
    return hmac.new(key=SYSTEM["HMAC_SHA256_KEY"], msg=message, digestmod=hashlib.sha256).hexdigest()

# 定义sso server地址并删除SSO多余参数
sso_server = SSO.get("sso_server").strip("/")
if not url_check(sso_server):
    raise

# 定义蓝图
sso_blueprint = Blueprint("sso", "sso")
@sso_blueprint.route("/Login")
@anonymous_required
def Login():
    """ Client登录地址，需要跳转到SSO Server上 """
    ReturnUrl = request.args.get("ReturnUrl") or get_referrer_url() or url_for("front.index", _external=True)
    if url_check(sso_server):
        NextUrl = "{}/sso/?sso={}".format(sso_server, set_ssoparam(ReturnUrl))
        return redirect(NextUrl)
    else:
        return "Invalid Configuration"

@sso_blueprint.route("/Logout")
@login_required
def Logout():
    """ Client注销地址，需要跳转到SSO Server上 """
    ReturnUrl = request.args.get("ReturnUrl") or get_referrer_url() or url_for("front.index", _external=True)
    NextUrl = "{}/signOut?ReturnUrl={}".format(sso_server, ReturnUrl)
    return redirect(NextUrl)

@sso_blueprint.route("/authorized", methods=["GET", "POST"])
def authorized():
    """ Client SSO 单点登录、注销入口, 根据`Action`参数判断是`ssoLogin`还是`ssoLogout` """
    Action = request.args.get("Action")
    if Action == "ssoLogin":
        # 单点登录
        ticket = request.args.get("ticket")
        if request.method == "GET" and ticket and g.signin == False:
            resp = sso_request("{}/sso/validate".format(sso_server), dict(Action="validate_ticket"), dict(ticket=ticket, app_name=SSO["app_name"], get_userinfo=True, get_userbind=False))
            logger.debug("SSO check ticket resp: {}".format(resp))
            if resp and isinstance(resp, dict) and "success" in resp and "uid" in resp:
                if resp["success"] is True:
                    uid = resp["uid"]
                    sid = resp["sid"]
                    expire = int(resp["expire"])
                    # 判断是否允许登录
                    if is_allowUid(uid) is True:
                        # 获取用户信息，若不需要，可将get_userinfo=True改为False，并注释下两行
                        g.userinfo = resp["userinfo"].get("data") or dict()
                        set_userinfo(uid, g.userinfo, expire)
                        logger.debug(g.userinfo)
                        # 授权令牌验证通过，设置局部会话，允许登录
                        sessionId = set_sessionId(uid=uid, seconds=expire, sid=sid)
                        response = make_response(redirect(get_redirect_url("front.index")))
                        response.set_cookie(key="sessionId", value=sessionId, max_age=expire, httponly=True, secure=False if request.url_root.split("://")[0] == "http" else True)
                        return response
    elif Action == "ssoLogout":
        # 单点注销
        ReturnUrl = request.args.get("ReturnUrl") or get_referrer_url() or url_for("front.index", _external=True)
        NextUrl   = "{}/signOut?ReturnUrl={}".format(sso_server, ReturnUrl)
        app_name  = request.args.get("app_name")
        if request.method == "GET" and NextUrl and app_name and g.signin == True and app_name == SSO["app_name"]:
            response = make_response(redirect(NextUrl))
            response.set_cookie(key="sessionId", value="", expires=0)
            return response
    elif Action == "ssoConSync":
        # 数据同步：参数中必须包含大写的hmac_sha256(app_name:app_id:app_secret)的signature值
        signature = request.args.get("signature")
        if request.method == "POST" and signature and signature == hmac_sha256("{}:{}:{}".format(SSO["app_name"], SSO["app_id"], SSO["app_secret"])).upper():
            try:
                data = json.loads(request.form.get("data"))
                ct = data["CallbackType"]
                cd = data["CallbackData"]
                uid = data["uid"]
                token = data["token"]
            except Exception,e:
                logger.warning(e)
            else:
                logger.info("ssoConSync with uid: {} -> {}: {}".format(uid, ct, cd))
                resp = sso_request("{}/sso/validate".format(sso_server), dict(Action="validate_sync"), dict(token=token, uid=uid))
                if resp and isinstance(resp, dict) and resp.get("success") is True:
                    # 之后根据不同类型的ct处理cd
                    logger.debug("ssoConSync is ok")
                    if ct == "user_profile":
                        g.userinfo.update(cd)
                    elif ct == "user_avatar":
                        g.userinfo["avatar"] = cd
                    return jsonify(msg="Synchronization completed", success=set_userinfo(uid, g.userinfo), app_name=SSO["app_name"])
    return "Invalid Authorized"

#: 返回插件主类
def getPluginClass():
    return SSOClientMain

#: 插件主类, 不强制要求名称与插件名一致, 保证getPluginClass准确返回此类
class SSOClientMain(PluginBase):

    def register_bep(self):
        """注册蓝图入口, 返回蓝图路由前缀及蓝图名称"""
        bep = {"prefix": "/sso", "blueprint": sso_blueprint}
        return bep
