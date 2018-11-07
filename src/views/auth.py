# -*- coding: utf8 -*-
#
# SwarmOps views for auth
#

import datetime, SpliceURL
from flask import Blueprint, request, g, redirect, make_response, url_for
from urllib import urlencode
from config import SSO, GLOBAL
from utils.public import logger, md5

auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.route('/login/')
def login():
    if g.auth:
        return redirect(url_for("index"))
    else:
        query = {"sso": True,
           "sso_r": SpliceURL.Modify(request.url_root, "/sso/").geturl,
           "sso_p": SSO["SSO.PROJECT"],
           "sso_t": md5("%s:%s" %(SSO["SSO.PROJECT"], SpliceURL.Modify(request.url_root, "/sso/").geturl))
        }
        SSOLoginURL = SpliceURL.Modify(url=SSO["SSO.URL"], path="/login/", query=query).geturl
        logger.info("User request login to SSO: %s" %SSOLoginURL)
        return redirect(SSOLoginURL)

@auth_blueprint.route('/logout/')
def logout():
    if GLOBAL["Authentication"] == "sso":
        SSOLogoutURL = SSO.get("SSO.URL") + "/sso/?nextUrl=" + request.url_root.strip("/")
    else:
        SSOLogoutURL = url_for("ui.index")
    resp = make_response(redirect(SSOLogoutURL))
    resp.set_cookie(key='logged_in', value='', expires=0)
    resp.set_cookie(key='username',  value='', expires=0)
    resp.set_cookie(key='sessionId',  value='', expires=0)
    resp.set_cookie(key='time',  value='', expires=0)
    resp.set_cookie(key='Azone',  value='', expires=0)
    return resp

@auth_blueprint.route('/sso/')
def sso():
    ticket = request.args.get("ticket")
    if not ticket:
        logger.info("sso ticket get failed")
        return """<html><head><title>正在跳转中……</title><meta http-equiv="Content-Language" content="zh-CN"><meta HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=utf8"><meta http-equiv="refresh" content="1.0;url={}"></head><body></b>用户未授权, 返回登录, 请重新认证!<b></body></html>""".format(url_for("auth.logout"))
    logger.info("ticket: %s" %ticket)
    username, expires, sessionId = ticket.split('.')
    if username and username not in SSO["SSO.AllowedUserList"]:
        logger.info("SwarmOps is not allowed to login with {}.".format(username))
        return redirect(url_for("auth.sso"))
    if expires == 'None':
        UnixExpires = None
    else:
        UnixExpires = datetime.datetime.strptime(expires,"%Y-%m-%d")
    resp = make_response(redirect(url_for("index")))
    resp.set_cookie(key='logged_in', value="yes", expires=UnixExpires)
    resp.set_cookie(key='username',  value=username, expires=UnixExpires)
    resp.set_cookie(key='sessionId', value=sessionId, expires=UnixExpires)
    resp.set_cookie(key='time', value=expires, expires=UnixExpires)
    resp.set_cookie(key='Azone', value="sso", expires=UnixExpires)
    return resp