# -*- coding:utf-8 -*-

import os
import sys
import time
import json
import config
import libs.public
import libs.authentication
import libs.swarm.swarm_multi
import libs.swarm.swarm_engine
import libs.swarm.swarm_cluster
from libs.public import logger
from flask import Flask, request, g, jsonify
from flask_restful import Api, Resource

__author__  = 'Mr.tao'
__email__   = 'taochengwei@emar.com'
__doc__     = 'SwarmOpsApi'
__version__ = '0.2.1-rc2'
__process__ = config.GLOBAL.get("ProcessName", "SwarmOpsApi")
__product__ = True if config.PRODUCT.get("IsProduction") in ('true', 'True', True) else False

app   = Flask(__name__)
api   = Api(app)
swarm = libs.swarm.swarm_multi.MultiSwarmManager(default=config.SWARM, method=config.GLOBAL.get("SwarmStorageMode"), IsProduction=__product__, **config.ETCD)

#记录下启动的配置信息
logger.info(config.GLOBAL)
logger.info(config.PRODUCT)
logger.info(config.SWARM)
logger.info(config.ETCD)


#每个URL请求之前，定义初始化时间、requestId、用户验证结果等相关信息并绑定到g.
@app.before_request
def before_request():
    logger.info("Start Once Access")
    g.startTime = time.time()
    g.requestId = libs.public.gen_requestId()
    g.username  = request.cookies.get("username", request.args.get("username", ""))
    g.sessionid = request.cookies.get("Esessionid", request.args.get("Esessionid", ""))
    g.auth      = libs.authentication.auth(config.GLOBAL.get("AuthSysUrl"), g.username, g.sessionid)
    g.swarm_node    = libs.swarm.swarm_engine.SWARM_NODE_API(swarm.getActive.get("manager")) if swarm.getActive.get("type") == "engine" else ''
    g.swarm_service = libs.swarm.swarm_engine.SWARM_SERVICE_API(swarm.getActive.get("manager")) if swarm.getActive.get("type") == "engine" else ''
    logger.info("And this requestId is %s, auth(%s), username(%s), sessionid(%s)" %(g.requestId, g.auth, g.username, g.sessionid))


#每次返回数据中，带上响应头，包含API版本和本次请求的requestId，以及允许所有域跨域访问API, 记录访问日志.
@app.after_request
def add_header(response):
    response.headers["X-Emar-Name"]         = __process__
    response.headers["X-Emar-Version"]      = __version__
    response.headers["X-Emar-Request-Id"]   = g.requestId
    response.headers["X-Emar-Cluster-Mode"] = swarm.getActive.get("type")
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


class Index(Resource):

    def get(self):
        return {__process__: "ok"}


class Swarm(Resource):

    @classmethod
    def get(self):
        """ Query cluster information """

        get   = request.args.get("get")
        state = True if request.args.get("state", True) in ('true', 'True', True) else False

        if g.auth:
            return swarm.GET(get, state)
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res

    @classmethod
    def post(self):
        """ The api for adding a swarm cluster, post data """

        swarmname = request.form.get("name")
        swarmtype = request.form.get("type")
        swarmip   = request.form.get("manager", request.form.get("ip"))

        if g.auth:    
            return swarm.POST(name=swarmname, type=swarmtype, ip=swarmip)
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res 

    @classmethod
    def put(self):
        """ Update swarm info or set active swarm """

        setActive = True if request.args.get("setActive", request.form.get("setActive")) in ("true", "True", True) else False
        swarmname = request.args.get("name", request.form.get("name"))

        if g.auth:    
            return swarm.PUT(setActive=setActive, name=swarmname)
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res 

    @classmethod
    def delete(self):
        """ Delete a swarm cluster """

        swarmname = request.args.get("name", request.form.get("name"))

        if g.auth:    
            return swarm.DELETE(name=swarmname)
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res 


class Service(Resource):

    @classmethod
    def get(self):
        """ get swarm all service """

        core    = True if request.args.get("core", False) in ("True", "true", True) else False
        service = request.args.get("id", request.args.get("name", None))
        convert = True if request.args.get("convert", True) in ("True", "true", True) else False

        if g.auth:
            return g.swarm_service.Retrieve(
                       service=service,
                       core=core,
                       conversion=convert,
                   )
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res

    @classmethod
    def post(self):
        """ create a service """

        #get query, optional only is "name, env, mount, publish, replicas", required "image".
        image     = request.form.get("image")
        name      = request.form.get("name")
        env       = request.form.get("env")
        mount     = request.form.get("mount")        
        publish   = request.form.get("publish")
        replicas  = request.form.get("replicas", 1)
        if g.auth:
            return g.swarm_service.Create(image=image,name=name,env=env,mount=mount,publish=publish,replicas=replicas)
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res

    @classmethod
    def put(self):
        """put, update service"""

        flag        = request.form.get("flag", request.form.get("serviceId", request.form.get("serviceName")))
        #In fact, the official currently only supports the ID form of the update operation.
        image       = request.form.get("image")
        name        = request.form.get("name")
        env         = request.form.get("env")
        mount       = request.form.get("mount")    
        publish     = request.form.get("publish")
        replicas    = request.form.get("replicas")
        delay       = request.form.get("delay")
        parallelism = request.form.get("parallelism")

        if g.auth:
            return g.swarm_service.Update(serviceFlag=flag, image=image, name=name, env=env, mount=mount, publish=publish, replicas=replicas, delay=delay, parallelism=parallelism)
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res

    @classmethod
    def delete(self):
        """delete a service"""

        flag = request.form.get("flag", request.form.get("serviceId", request.form.get("serviceName", request.form.get("id", request.form.get("name")))))

        if g.auth:
            return g.swarm_service.Delete(serviceFlag=flag)
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res 


class Node(Resource):

    @classmethod
    def get(self):
        """ get swarm node """

        #Initialize Request Query Parameters
        if g.auth:
            return g.swarm_node.NodeQuery(
                start      = request.args.get("start", 0),
                length     = request.args.get("length", 10),
                search     = request.args.get("search[value]", request.args.get("search", '')),
                orderindex = request.args.get("order[0][column]", 0),
                ordertype  = request.args.get("order[0][dir]", 'asc')
            )
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res

    @classmethod
    def post(self):
        """create a node into swarm cluster"""

        Ip   = request.form.get("ip")
        Role = request.form.get("role", "worker")
        if g.auth:
            return g.swarm_node.add(Ip, Role, swarm.getActive.get("managerToken"), swarm.getActive.get("workerToken"))
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res

    @classmethod
    def delete(self):
        """Remove a node to swarm cluster"""

        nodeip   = request.form.get("ip")
        nodeflag = request.form.get("flag")
        force    = True if request.form.get("force") in ("true", "True", True) else False
        if g.auth:
            return g.swarm_node.rm(nodeip, nodeflag, force)
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res

    @classmethod
    def put(self):
        """update node info in swarm cluster"""

        data=dict(request.form)
        if g.auth:
            return g.swarm_node.updateNode(**data)
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res


class Label(Resource):

    @classmethod
    def get(self):

        #Initialize Request Query Parameters
        if g.auth:
            return g.swarm_node.LabelQuery(
                start      = request.args.get("start", 0),
                length     = request.args.get("length", 10),
                search     = request.args.get("search[value]", request.args.get("search", '')),
                orderindex = request.args.get("order[0][column]", 0),
                ordertype  = request.args.get("order[0][dir]", 'asc')
            )
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res

class NodeForLabel(Resource):

    @classmethod
    def get(self):

        #Initialize Request Query Parameters
        if g.auth:
            return g.swarm_node.Node_for_Label(
                start      = request.args.get("start", 0),
                length     = request.args.get("length", 10),
                search     = request.args.get("search[value]", request.args.get("search", '')),
                orderindex = request.args.get("order[0][column]", 0),
                ordertype  = request.args.get("order[0][dir]", "asc")
            )
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res


class Info(Resource):

    def get(self):
        Application={
                        "Host": libs.public.get_ip(True),
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

        if g.auth:
            return {"Application": Application, "Launch": config.PRODUCT.get('ProductType') if __product__ else None, "Version": Version}
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res


#Router rules
api.add_resource(Index, '/', endpoint='index')
api.add_resource(Swarm, '/swarm', '/swarm/', endpoint='swarm')
api.add_resource(Service, '/service', '/service/', endpoint='service')
api.add_resource(Node, '/node', '/node/', endpoint='node')
api.add_resource(Info, '/misc/info', '/misc/info/', endpoint='misc.info')
api.add_resource(Label, '/misc/label', '/misc/label/', endpoint='misc.label')
api.add_resource(NodeForLabel, '/misc/node_for_label', '/misc/node_for_label/', endpoint='misc.node_for_label')


if __name__ == '__main__':
    Host  = config.GLOBAL.get('Host')
    Port  = config.GLOBAL.get('Port')
    Debug = config.GLOBAL.get('Debug', True)
    app.run(host=Host, port=int(Port), debug=Debug)
