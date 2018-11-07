# -*- coding: utf8 -*-


import json, requests, os
from config import STORAGE
from SpliceURL import Splice
from utils.public import RedisConnection, ip_check
from utils.tool import logger
from .Base import BASE_SWARM_ENGINE_API

class MultiSwarmManager(BASE_SWARM_ENGINE_API):


    def __init__(self, port=2375, timeout=2, SwarmStorageMode="redis"):
        self.storage   = RedisConnection
        self.swarmKey  = STORAGE["SwarmKey"]
        self.ActiveKey = STORAGE["ActiveKey"]
        self.port      = port
        self.timeout   = timeout
        self.verify    = False
        self._BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._ssm      = SwarmStorageMode
        self._ssSwarms = os.path.join(self._BASE_DIR, 'logs', self.swarmKey)
        self._ssActive = os.path.join(self._BASE_DIR, 'logs', self.ActiveKey)
        self._swarms   = self._unpickle
        self._active   = self._unpickleActive

    def _pickle(self, data):
        """ 序列化所有数据写入存储 """

        if self._ssm == "local":
            try:
                with open(self._ssSwarms, "w") as f:
                    json.dump(data, f)
            except Exception,e:
                logger.error(e, exc_info=True)
                res = False
            else:
                res = True

        elif self._ssm == "redis":
            res = self.storage.set(self.swarmKey, json.dumps(data))

        logger.info("pickle data, content is %s, write result is %s" %(data, res))
        return res

    @property
    def _unpickle(self):
        """ 反序列化信息取出所有数据 """

        if self._ssm == "local":
            try:
                with open(self._ssSwarms, "r") as f:
                    data = json.load(f)
            except Exception,e:
                logger.warn(e, exc_info=True)
                res = []
            else:
                res = data or []

        elif self._ssm == "redis":
            res = self.storage.get(self.swarmKey)
            res = json.loads(res) if res else []

        logger.info("unpickle swarms data is %s" %res)
        return res

    def _pickleActive(self, data):
        """ 序列化活跃集群数据写入存储 """

        if self._ssm == "local":
            try:
                with open(self._ssActive, "w") as f:
                    json.dump(data, f)
            except Exception,e:
                logger.error(e, exc_info=True)
                res = False
            else:
                res = True

        elif self._ssm == "redis":
            res = self.storage.set(self.ActiveKey, json.dumps(data))

        logger.info("pickle active data, content is %s, write result is %s" %(data, res))
        return res

    @property
    def _unpickleActive(self):
        """ 反序列化信息取出活跃集群 """

        if self._ssm == "local":
            try:
                with open(self._ssActive, "r") as f:
                    data = json.load(f)
            except Exception,e:
                logger.warn(e, exc_info=True)
                res = {}
            else:
                res = data or {}

        elif self._ssm == "redis":
            res = self.storage.get(self.ActiveKey)
            res = json.loads(res) if res else {}

        logger.info("unpickle active data is %s" %res)
        return res

    @property
    def getMethod(self):
        """ 查询当前系统Swarm数据存储方式 """
        return self._ssm

    @property
    def getMember(self):
        """ 查询所有节点名称 """
        return [ _.get("name") for _ in self._swarms ]

    def isMember(self, name):
        """ 查询某name的swarm集群是否在存储中 """
        res = name in self.getMember
        logger.info("check %s, is member? %s" %(name, res))
        return res

    def isActive(self, name):
        """ 判断某name的swarm集群是否为活跃集群 """
        return name == self._active.get("name")

    @property
    def getActive(self):
        """ 查询活跃集群 """
        return self._active

    def setActive(self, name):
        """ 设置活跃集群 """
        logger.info("setActive, request name that will set is %s" % name)

        if self.isActive(name):
            logger.info("The name of the request is already active, think it successfully")
        else:
            logger.info("The name of the request is not current active swarm, will update it to be active.")
            self._active = self.getOne(name)
            self._pickleActive(self._active)
            if self.isActive(name):
                logger.info("setActive, the request name sets it for active, successfully")
            else:
                logger.info("setActive, the request name sets it for active, but fail")
                return False
        return True

    def getOneLeader(self, name):
        """ 查询某name的swarm集群leader """
        return self._checkSwarmLeader(self.getOne(name))

    def getOne(self, name):
        """ 查询某name的swarm集群信息 """

        if self.isMember(name):
            return ( _ for _ in self._swarms if _.get("name") == name ).next()
        else:
            logger.warn("get one swarm named %s, but no data" %name)

    def getSwarm(self, checkState=False, UpdateManager=False):
        """ 查询存储中所有Swarm集群信息(并检查健康状态) """

        logger.info("get all swarm and check state(%s) for all swarm cluster with UpdateManager(%s), start" %(checkState, UpdateManager))
        swarms = []
        for swarm in self._swarms:
            if checkState == True:
                swarm.update(state=self._checkSwarmHealth(self._checkSwarmLeader(swarm)))
            elif "state" in swarm:
                swarm.pop("state")
            if UpdateManager == True:
                logger.info("Update manager in getSwarm, start")
                try:
                    manager=self._checkSwarmManager(self._checkSwarmLeader(swarm))
                except Exception, e:
                    logger.error(e, exc_info=True)
                    logger.info("Update manager in getSwarm, end, fail")
                else:
                    if manager:
                        swarm.update(manager=manager)
                    logger.info("Update manager in getSwarm, end, successfully, manager is %s" %manager)
            swarms.append(swarm)
        if UpdateManager == True:
            self._swarms = swarms
            res = self._pickle(self._swarms)
            logger.info("Update manager in getSwarm, over, %s" % res)
        return swarms

    def GET(self, get, **kwargs):

        res = {"msg": None, "code": 0}
        checkState    = kwargs.get("checkState", False)
        UpdateManager = kwargs.get("UpdateManager", False)
        logger.info("get %s request, the query params is %s" %(get, kwargs))

        if not isinstance(get, (str, unicode)) or not get:
            res.update(msg="GET: query params type error or none", code=-1010)
        else:
            get = get.lower()
            if get == "all":
                res.update(data=self.getSwarm(checkState, UpdateManager))
            elif get == "active":
                res.update(data=self.getActive)
            elif get == "leader":
                res.update(data=self._checkSwarmLeader(self.getActive))
            elif get == "member":
                res.update(data=self.getMember)
            elif get == "method":
                res.update(data=self.getMethod)
            else:
                if self.isMember(get):
                    res.update(data=self.getOne(get))
                else:
                    res.update(msg="No such swarm", code=-1011)

        logger.info(res)
        return res

    def POST(self, swarmName, swarmIp):
        """ add a swarm cluster into current, check, pickle. """

        res = {"msg": None, "code": 0}
        swarmIp = swarmIp.strip()
        swarmName = swarmName.strip()
        logger.debug("post a swarm cluster, name is %s, ip is %s, check ip is %s" %(swarmName, swarmIp, ip_check(swarmIp)))

        if not swarmName or not swarmIp or not ip_check(swarmIp):
            res.update(msg="POST: data params error", code=-1020)
        elif self.isMember(swarmName):
            res.update(msg="POST: swarm cluster already exists", code=-1021)
        else:
            #access node ip's info, and get all remote managers
            url   = Splice(netloc=swarmIp, port=self.port, path='/info').geturl
            swarm = dict(name=swarmName)
            logger.info("init a swarm cluter named %s, will get swarm ip info, that url is %s" %(swarmName, url))
            try:
                nodeinfo = requests.get(url, timeout=self.timeout, verify=self.verify).json()
                logger.debug("get swarm ip info, response is %s" %nodeinfo)
                swarm["manager"] = [ nodes["Addr"].split(":")[0] for nodes in nodeinfo["Swarm"]["RemoteManagers"] ]
            except Exception,e:
                logger.error(e, exc_info=True)
                res.update(msg="POST: access the node ip has exception", code=-1022)
            else:
                token = self._checkSwarmToken(self._checkSwarmLeader(swarm))
                swarm.update(managerToken=token.get('Manager'), workerToken=token.get('Worker'))
                self._swarms.append(swarm)
                self._pickle(self._swarms)
                res.update(success=True, code=0)
                logger.info("check all pass and added")

        logger.info(res)
        return res

    def DELETE(self, name):
        """ 删除当前存储中的群集 """

        res = {"msg": None, "code": 0, "success": False}
        logger.info("the name that will delete is %s" %name)

        if name in ("leader", "active", "all"):
            res.update(msg="DELETE: name reserved for the system key words", code=-1031)

        elif self.isActive(name):
            res.update(msg="DELETE: not allowed to delete the active cluster", code=-1032)

        elif self.isMember(name):
            swarm = self.getOne(name)
            logger.info("Will delete swarm cluster is %s" %swarm)
            self._swarms.remove(swarm)
            if self.isMember(name):
                logger.info("Delete fail")
                res.update(success=False)
            else:
                logger.info("Delete successfully, pickle current swarm")
                self._pickle(self._swarms)
                res.update(success=True)

        else:
            res.update(msg="DELETE: this swarm cluster does not exist", code=-1030)

        logger.info(res)
        return res

    def PUT(self, name, setActive=False):
        """ 更新集群信息、设置活跃集群 """

        res = {"msg": None, "code": 0}
        logger.info("PUT request, setActive(%s), will set %s as active" %(setActive, name))

        if setActive:
            if name and self.isMember(name):
                res.update(success=self.setActive(name))
            else:
                res.update(msg="PUT: setActive, but no name param or name non-existent", code=-1040)
        else:
            pass

        logger.info(res)
        return res

    def InitSwarm(self, AdvertiseAddr, ForceNewCluster=False):
        """ 初始化集群 """
        res  = {"msg": None, "code": 0, "success": False}

        AdvertiseAddr = AdvertiseAddr.strip()
        ForceNewCluster = True if ForceNewCluster in ("true", "True", True) else False

        url = Splice(netloc=AdvertiseAddr, port=self.port, path='/swarm/init').geturl
        try:
            r = requests.post(url, data=json.dumps({"ListenAddr": "0.0.0.0", "AdvertiseAddr": AdvertiseAddr, "ForceNewCluster": ForceNewCluster}), headers={"Content-Type": "application/json"})
        except Exception,e:
            logger.error(e, exc_info=True)
            res.update(msg="Node Error", code=-1001)
        else:
            if r.status_code == 200:
                res.update(success=True, data=r.text)
            else:
                res.update(msg="InitSwarm Error", code=-1002)

        logger.info(res)
        return res
