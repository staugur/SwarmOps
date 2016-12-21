# -*- coding:utf-8 -*-

from flask import Blueprint, request, g
from flask_restful import Api, Resource
from utils.public import logger


class Swarm(Resource):

    def get(self):
        """ 查询存储的swarm集群信息 """

        get   = request.args.get("get")
        state = True if request.args.get("state", False) in ('true', 'True', True) else False

        if g.auth:
            return g.swarm.GET(get, state)
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res, 403

    def post(self):
        """ 向存储里添加一个swarm集群 """

        swarmname = request.form.get("name")
        swarmip   = request.form.get("ip")

        if g.auth:
            return g.swarm.POST(swarmName=swarmname, swarmIp=swarmip)
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res, 403 

    def put(self):
        """ 设置活跃集群 """

        setActive = True if request.args.get("setActive") in ("true", "True", True) else False
        swarmname = request.args.get("name")

        if g.auth:    
            return g.swarm.PUT(name=swarmname, setActive=setActive)
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res, 403 

    def delete(self):
        """ 删除存储中的一个swarm集群 """

        swarmname = request.args.get("name")

        if g.auth:    
            return g.swarm.DELETE(name=swarmname)
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res, 403

class Service(Resource):

    def get(self):
        """ 查询swarm活跃集群集群service信息 """

        service = request.args.get("id", request.args.get("name", None))
        core    = True if request.args.get("core", True) in ("True", "true", True) else False
        core_convert = True if request.args.get("core_convert", True) in ("True", "true", True) else False

        if g.auth:
            return g.service.GET(service, core, core_convert)
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res, 403

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
            return res, 403

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
            return res, 403

    def delete(self):
        """delete a service"""

        flag = request.form.get("flag", request.form.get("serviceId", request.form.get("serviceName", request.form.get("id", request.form.get("name")))))

        if g.auth:
            return g.swarm_service.Delete(serviceFlag=flag)
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res, 403 

class Node(Resource):

    def get(self):

        if g.auth:
            return g.node.GET()
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res, 403

    def post(self):
        """create a node into swarm cluster"""

        Ip   = request.form.get("ip")
        Role = request.form.get("role", "worker")
        if g.auth:
            return g.swarm_node.add(Ip, Role, g.swarm.getActive.get("managerToken"), g.swarm.getActive.get("workerToken"))
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res, 403

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
            return res, 403

    def put(self):
        """update node info in swarm cluster"""

        data=dict(request.form)
        if g.auth:
            return g.swarm_node.updateNode(**data)
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res, 403


core_blueprint = Blueprint(__name__, __name__)
api = Api(core_blueprint)
api.add_resource(Swarm, '/swarm', '/swarm/', endpoint='swarm')
api.add_resource(Service, '/service', '/service/', endpoint='service')
api.add_resource(Node, '/node', '/node/', endpoint='node')
