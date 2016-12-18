# -*- coding: utf8 -*-


import json, requests
from config import REDIS
from SpliceURL import Splice
from utils.public import logger, RedisConnection, ip_check


class MultiSwarmManager:


    def __init__(self, port=2375, timeout=2):
        self.storage   = RedisConnection
        self.swarmKey  = REDIS["SwarmKey"]
        self.ActiveKey = REDIS["ActiveKey"]
        self.port      = port
        self.timeout   = timeout
        self.verify    = False
        self._swarm    = self._unpickle
        self._active   = self._unpickleActive

    def _pickle(self, data):
        """ 序列化所有数据写入存储 """
        res = self.storage.set(self.swarmKey, json.dumps(data))
        logger.info("pickle data, content is %s, write result is %s" %(data, res))
        return res

    @property
    def _unpickle(self):
        """ 反序列化信息取出所有数据 """
        res = self.storage.get(self.swarmKey)
        logger.info("unpickle data is %s" %res)
        if res:
            return json.loads(res)
        else:
            return []

    def _checkSwarmToken(self, leader):
        """ 根据Leader查询集群令牌 """

        try:
            swarm = requests.get(Splice(netloc=leader, port=self.port, path='/swarm').geturl, timeout=self.timeout, verify=self.verify).json()
            token = swarm.get('JoinTokens')
        except Exception,e:
            logger.warn(e, exc_info=True)
        else:
            #dict, {u'Manager': u'xxx', u'Worker': u'xxx'}
            logger.info(token)
            return token

    def _checkSwarmLeader(self, swarm):
        """ 查询swarm集群Leader """

        if swarm:
            try:
                url  = Splice(netloc=swarm.get("manager")[0], port=self.port, path='/nodes').geturl
                data = requests.get(url, timeout=self.timeout, verify=self.verify).json()
                if isinstance(data, (list, tuple)):
                    leader = ( _.get('ManagerStatus', {}).get('Addr').split(':')[0] for _ in data if _.get('ManagerStatus', {}).get('Leader') ).next()
                else:
                    leader = None
                logger.info("get %s leader, request url is %s, response is %s, get leader is %s" %(swarm["name"], url, data, leader))
            except Exception,e:
                logger.warn(e, exc_info=True)
            else:
                return leader

    def _checkSwarmHealth(self, leader):
        """ 根据Leader查询某swarm集群是否健康 """

        state = []
        logger.info("To determine whether the cluster is healthy, starting, swarm leader is %s" %leader)
        try:
            nodes = requests.get(Splice(netloc=leader, port=self.port, path='/nodes').geturl, timeout=self.timeout, verify=self.verify).json()
            logger.debug("check swarm health, swarm nodes length is %d" % len(nodes))
            for node in nodes:
                if node['Spec'].get('Role') == 'manager':
                    isHealth = True if node['Status']['State'] == 'ready' and node['Spec'].get('Availability') == 'active' and node.get('ManagerStatus', {}).get('Reachability') == 'reachable' else False
                    if isHealth:
                        state.append(isHealth)
        except Exception,e:
            logger.warn(e, exc_info=True)
            return "ERROR"
        else:
            logger.info("To determine whether the cluster is healthy, ending, the state is %s" %state)
            if len(state) == len(nodes) and state:
                return 'Healthy'
            else:
                return 'Unhealthy'

    def _pickleActive(self, data):
        """ 序列化活跃集群数据写入存储 """
        res = self.storage.set(self.ActiveKey, json.dumps(data))
        logger.info("pickle active data, content is %s, write result is %s" %(data, res))
        return res

    @property
    def _unpickleActive(self):
        """ 反序列化信息取出活跃集群 """
        res = self.storage.get(self.ActiveKey)
        logger.info("init active data is %s" %res)
        if res:
            return json.loads(res)

    def isActive(self, name):
        """ 判断某name的swarm集群是否为活跃集群 """
        return name == self._active.get("name")

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

    def isMember(self, name):
        """ 查询某name的swarm集群是否在存储中 """
        return name in [ _.get("name") for _ in self._swarm ]

    def getOne(self, name):
        """ 查询某name的swarm集群信息 """

        if self.isMember(name):
            return ( _ for _ in self._swarm if _.get("name") == name ).next()
        else:
            logger.warn("get %s, but no data" %name)

    def getSwarm(self, checkState=False):
        """ 查询存储中所有Swarm集群信息(并检查健康状态) """

        logger.debug(self._swarm)
        if checkState:
            logger.info("get and check all swarm cluster, start")
            return [ swarm for swarm in self._swarm if swarm.update(state=self._checkSwarmHealth(self._checkSwarmLeader(swarm))) == None ]
        else:
            swarms = []
            for swarm in self._swarm:
                if "state" in swarm:
                    swarm.pop("state")
                swarms.append(swarm)
            return swarms

    def GET(self, get, checkState=False):

        res = {"msg": None, "code": 0}
        logger.info("get request, the query params is %s, get state is %s" %(get, checkState))

        if not isinstance(get, (str, unicode)) or not get:
            res.update(msg="GET: query params type error or none", code=-10000)
        else:
            get = get.lower()
            if get == "all":
                res.update(data=self.getSwarm(checkState))
            elif get == "active":
                res.update(data=self._active)
            elif get == "leader":
                res.update(data=self._checkSwarmLeader(self._active))
            else:
                if self.isMember(get):
                    res.update(data=self.getOne(get))
                else:
                    res.update(msg="No such swarm", code=-10000)

        logger.info(res)
        return res

    def POST(self, swarmName, swarmIp):
        """ add a swarm cluster into current, check, pickle. """

        res = {"msg": None, "code": 0}
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
                self._swarm.append(swarm)
                self._pickle(self._swarm)
                res.update(success=True, code=0)
                logger.info("check all pass and added")

        logger.info(res)
        return res

    def DELETE(self, name):
        """ 删除当前存储中的群集 """

        res = {"msg": None, "code": 0}
        logger.info("the name that will delete is %s" %name)

        if name in ("leader", "active", "all"):
            res.update(msg="DELETE: name reserved for the system key words", code=-1031)

        elif self.isActive(name):
            res.update(msg="DELETE: not allowed to delete the active cluster", code=-1032)

        elif self.isMember(name):
            swarm = self.getOne(name)
            logger.info("Will delete swarm cluster is %s" %swarm)
            self._swarm.remove(swarm)
            if self.isMember(name):
                logger.info("Delete fail")
                res.update(success=False)
            else:
                logger.info("Delete successfully, pickle current swarm")
                self._pickle(self._swarm)
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
                res.update(msg="PUT: setActive, but no name param or name non-existent", code=-1010)
        else:
            pass
            #update swarm info

        logger.info(res)
        return res

