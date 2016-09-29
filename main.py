# -*- coding:utf-8 -*-

import os
import sys
import time
import json
import config
import utils.public
import libs.swarm.swarm_multi
import libs.swarm.swarm_engine
import libs.swarm.swarm_cluster
from flask import Flask, request, g, jsonify
from flask_restful import Api, Resource
from utils.public import logger
from apis.misc import misc_blueprint
from apis.core import core_blueprint

__author__  = 'Mr.tao'
__email__   = 'taochengwei@emar.com'
__doc__     = 'Manage swarm clusters to provide a more concise and compact intermediate layer web application'
__version__ = '0.2.1-rc3'
__process__ = config.GLOBAL.get("ProcessName", "SwarmOpsApi")
__product__ = True if config.PRODUCT.get("IsProduction") in ('true', 'True', True) else False

app   = Flask(__name__)
api   = Api(app)
swarm = libs.swarm.swarm_multi.MultiSwarmManager(default=config.SWARM, method=config.GLOBAL.get("SwarmStorageMode"), IsProduction=__product__, **config.ETCD)


#每个URL请求之前，定义初始化时间、requestId、用户验证结果等相关信息并绑定到g.
@app.before_request
def before_request():
    logger.info("Start Once Access")
    g.startTime = time.time()
    g.requestId = utils.public.gen_requestId()
    g.username  = request.cookies.get("username", request.args.get("username", ""))
    g.sessionid = request.cookies.get("Esessionid", request.args.get("Esessionid", ""))
    g.auth      = True
    g.swarm     = swarm
    g.swarm_node    = libs.swarm.swarm_engine.SWARM_NODE_API(swarm.getActive.get("manager")) if swarm.getActive.get("type") == "engine" else ''
    g.swarm_service = libs.swarm.swarm_engine.SWARM_SERVICE_API(swarm.getActive.get("manager")) if swarm.getActive.get("type") == "engine" else ''
    logger.info("And this requestId is %s, auth(%s), username(%s), sessionid(%s)" %(g.requestId, g.auth, g.username, g.sessionid))

#每次返回数据中，带上响应头，包含本次请求的requestId，以及允许所有域跨域访问API, 记录访问日志.
@app.after_request
def add_header(response):
    response.headers["X-Emar-Request-Id"]   = g.requestId
    response.headers["Access-Control-Allow-Origin"] = "*"
    logger.info(json.dumps({
        "AccessLog": {
            "status_code": response.status_code,
            "method": request.method,
            "ip": request.headers.get('X-Real-Ip', request.remote_addr),
            "url": request.url,
            "referer": request.headers.get('Referer'),
            "agent": request.headers.get("User-Agent"),
            "requestId": g.requestId,
            "OneTimeInterval": "%0.2fs" %float(time.time() - g.startTime)
            }
        }
    ))
    return response

#首页
@app.route("/")
def index():
    return jsonify({__process__: "ok"})

#系统信息页
@app.route("/info/")
def info():
    if g.auth:
        Application={
                        "Host": utils.public.get_wanip(),
                        "Port": config.GLOBAL.get('Port'),
                        "Name": __process__,
                        "Author": "%s(%s)" %(__author__, __email__),
                        "Loglevel": config.GLOBAL.get("LogLevel"),
                        "Production": __product__
                    }
        Version  =  {
                        "ApiVersion": __version__,
                        "PythonVersion": sys.version,
                        "SystemVersion": os.uname() if hasattr(os, 'uname') else 'Windows'
                    }

        return jsonify({"Application": Application, "Launch": config.PRODUCT.get('ProductType') if __product__ else None, "Version": Version})
    else:
        res = {"msg": "Authentication failed, permission denied.", "code": 403}
        logger.warn(res)
        return jsonify(res), 403

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

#自定义错误显示信息，500错误
@app.errorhandler(500)
def server_error(error=None):
    message = {
        'code': 500,
        'msg': 'Server error, please contact taochengwei@emar.com'
    }
    resp = jsonify(message)
    resp.status_code = 500
    return resp


#路由规则，除却首页和信息页，其他路由均为蓝图注册，获取路由列表，使用app.url_map
app.register_blueprint(misc_blueprint, url_prefix="/misc")
app.register_blueprint(core_blueprint)


if __name__ == '__main__':
    Host  = config.GLOBAL.get('Host')
    Port  = config.GLOBAL.get('Port')
    Debug = config.GLOBAL.get('Debug', True)
    app.run(host=Host, port=int(Port), debug=Debug)
