# -*- coding:utf-8 -*-

import time, json, datetime, SpliceURL
from urllib import urlencode
from flask import Flask, request, g, jsonify, redirect, make_response, url_for
from config import GLOBAL, PRODUCT, SSO
from utils.public import logger, gen_requestId, isLogged_in, md5
from ui.ui import ui_blueprint
from apis.core import core_blueprint
from apis.misc import misc_blueprint
from libs.Swarm import MultiSwarmManager


__author__  = 'Mr.tao'
__email__   = 'staugur@saintic.com'
__doc__     = 'Manage swarm clusters to provide a more concise and compact intermediate layer web application with ui'
__version__ = '0.0.1'

app = Flask(__name__)
app.register_blueprint(ui_blueprint, url_prefix="/ui")
app.register_blueprint(core_blueprint, url_prefix="/api")
app.register_blueprint(misc_blueprint, url_prefix="/misc")

swarm = MultiSwarmManager()
logger.debug(dir(swarm))

#每个URL请求之前，定义初始化时间、requestId、用户验证结果等相关信息并绑定到g.
@app.before_request
def before_request():
    g.startTime = time.time()
    g.requestId = gen_requestId()
    g.sessionId = request.cookies.get("sessionId", "")
    g.username  = request.cookies.get("username", "")
    g.expires   = request.cookies.get("time", "")
    g.auth      = True#isLogged_in('.'.join([ g.username, g.expires, g.sessionId ]))
    g.swarm     = swarm
    logger.info("Start Once Access, and this requestId is %s, auth(%s)" %(g.requestId, g.auth))
    app.logger.debug(app.url_map)

#每次返回数据中，带上响应头，包含本次请求的requestId，以及允许所有域跨域访问API, 记录访问日志.
@app.after_request
def add_header(response):
    response.headers["X-Emar-Request-Id"]   = g.requestId
    response.headers["Access-Control-Allow-Origin"] = "*"
    logger.info({
            "AccessLog": True,
            "status_code": response.status_code,
            "method": request.method,
            "ip": request.headers.get('X-Real-Ip', request.remote_addr),
            "url": request.url,
            "referer": request.headers.get('Referer'),
            "agent": request.headers.get("User-Agent"),
            "requestId": g.requestId,
            "OneTimeInterval": "%0.2fs" %float(time.time() - g.startTime)
    })
    return response

@app.route("/")
def index():
    return redirect(url_for("ui.index"))

@app.route("/home/")
def home():
    return redirect(GLOBAL["Interest.blog.Url"])

@app.route('/login/')
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

@app.route('/logout/')
def logout():
    SSOLogoutURL = SSO.get("SSO.URL") + "/sso/?nextUrl=" + request.url_root.strip("/")
    resp = make_response(redirect(SSOLogoutURL))
    resp.set_cookie(key='logged_in', value='', expires=0)
    resp.set_cookie(key='username',  value='', expires=0)
    resp.set_cookie(key='sessionId',  value='', expires=0)
    resp.set_cookie(key='time',  value='', expires=0)
    resp.set_cookie(key='Azone',  value='', expires=0)
    return resp

@app.route('/sso/')
def sso():
    ticket = request.args.get("ticket")
    logger.info("ticket: %s" %ticket)
    username, expires, sessionId = ticket.split('.')
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

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'code': 404,
        'msg': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp


if __name__ == '__main__':
    Host  = GLOBAL.get('Host')
    Port  = GLOBAL.get('Port')
    Debug = GLOBAL.get('Debug', True)
    app.run(host=Host, port=int(Port), debug=Debug)
