# -*- coding:utf-8 -*-

import time
from flask import Flask, request, g, jsonify
from config import GLOBAL, PRODUCT
from utils.public import logger, gen_requestId
from apis.core import core_blueprint
from swarm.Swarm import MultiSwarmManager


__author__  = 'Mr.tao'
__email__   = 'taochengwei@emar.com'
__doc__     = 'Manage swarm clusters to provide a more concise and compact intermediate layer web application'
__version__ = '0.0.1'

app = Flask(__name__)
app.register_blueprint(core_blueprint)

#swarm = libs.swarm.swarm_multi.MultiSwarmManager(default=config.SWARM, method=config.GLOBAL.get("SwarmStorageMode"), **config.ETCD)
swarm = MultiSwarmManager()

#每个URL请求之前，定义初始化时间、requestId、用户验证结果等相关信息并绑定到g.
@app.before_request
def before_request():
    g.startTime = time.time()
    g.requestId = gen_requestId()
    g.username  = request.cookies.get("username", request.args.get("username", ""))
    g.sessionid = request.cookies.get("Esessionid", request.args.get("Esessionid", ""))
    g.auth      = True
    g.swarm     = swarm
    logger.info("Start Once Access, and this requestId is %s, auth(%s), username(%s), sessionid(%s)" %(g.requestId, g.auth, g.username, g.sessionid))
    logger.debug(app.url_map)

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

#首页
@app.route("/")
def index():
    return jsonify({PRODUCT["ProcessName"]: "ok"})

#自定义错误显示信息，404错误
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
