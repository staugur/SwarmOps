# -*- coding: utf8 -*-

import os
import json
import requests
from random import choice
from SpliceURL import Splice
from utils.public import logger, commaConvert

class MultiSwarmManager:

    """
    1. requests
    2. SpliceURL
    3. logger
    4. Etcd(class)
    5. commaConvert
    """
    port = 2375
    timeout = 3
    verify  = False

    def __init__(self, default, method):
        """
        :: Init some varible, set default and swarm data.
        :: 1. `default` is the default swarm cluster of writting in config.py.
        :: 2. `method` is the method to storage swarm cluster infomations.
        :: 3. `IsProduction` is the etcd option for etcd key.
        :: 4. `etcd` is the etcd(cluster) info, if method's value is etcd, you need configure it.
        """

        self.etcd          = Etcd(**etcd)
        self.etcdBaseKey   = etcd.get("ETCD_SWARMKEY") + "/production" if IsProduction else etcd.get("ETCD_SWARMKEY") + "/test"
        self.etcdSwarmKey  = self.etcdBaseKey + "/all"
        self.etcdActiveKey = self.etcdBaseKey + "/active"
        self._BASE_DIR     = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self._PICKLEFILE   = os.path.join(self._BASE_DIR, 'logs/.swarm.db')#Persistent problem, considering the storage to etcd, redis, etc.

        self._method  = method
        self._default = self._initDefault(default)
        self._active  = self._initActive()
        self._swarm   = self._unpickle() or [self.getDefault]

        logger.info({
                       "default":self._default,
                       "active": self._active,
                       "method": self._method,
                       "etcd":   self.etcd.url,
                       "key":    [self.etcdBaseKey, self.etcdSwarmKey, self.etcdActiveKey]
                    })

    def isActive(self, name):
        logger.info("The request of checking active name is %s" %name)
        return name == self.getActive.get("name")

    def isMember(self, name):
        logger.info("The request of checking memeber name is %s" %name)
        return name in [ _.get("name") for _ in self._swarm ]

    def _pickle(self, string):
        """Serialization information, set data"""

        if self.getMethod == "file":
            try:
                with open(self._PICKLEFILE, "w") as f:
                    json.dump(string, f)
            except Exception,e:
                logger.error(e, exc_info=True)
            else:
                return True

        elif self.getMethod == "etcd":
            return self.etcd._put(self.etcdSwarmKey, data={"value": json.dumps(string)})

        else:
            return False

    def _unpickle(self):
        """Anti serialization information, take out the data"""

        if self.getMethod == "file":
            try:
                with open(self._PICKLEFILE, "r") as f:
                    data = json.load(f)
            except Exception,e:
                logger.warn(e, exc_info=True)
            else:
                if data:
                    return data
                else:
                    logger.warn("unpicke for file, but no data")

        elif self.getMethod == "etcd":
            try:
                data = json.loads(self.etcd._get(self.etcdSwarmKey).get('node').get('value'))
            except Exception,e:
                logger.warn(e, exc_info=True)
            else:
                return data

        else:
            return False

    def _initActive(self):

        if self.getMethod == "file":
            return self.getDefault

        elif self.getMethod == "etcd":
            return json.loads(self.etcd._get(self.etcdActiveKey).get('node', {}).get('value', '{}')) or self.getDefault

    def _initDefault(self, default):
        token = self._checkSwarmToken(self._checkSwarmLeader(default))
        logger.debug(token)
        default.update(managerToken=token.get('Manager'), workerToken=token.get('Worker'))
        return default

    def _checkSwarmToken(self, leader):
        """ According to the management of IP query cluster token """
        logger.debug(leader)

        try:
            swarm = requests.get(Splice(netloc=leader, port=self.port, path='/swarm').geturl, timeout=self.timeout, verify=self.verify).json()
            token = swarm.get('JoinTokens')
        except Exception,e:
            logger.warn(e, exc_info=True)
        else:
            #dict, {Manager:xxx, Worker:xxx}
            return token

    def _checkSwarmLeader(self, swarm):
        """ get the swarm cluster leader """
 
        for manager in swarm.get("manager"):
            try:
                leader = ( _.get('ManagerStatus', {}).get('Addr').split(':')[0] for _ in requests.get(Splice(ip=manager, port=self.port, path='/nodes').geturl, timeout=self.timeout, verify=self.verify).json() if _.get('ManagerStatus', {}).get('Leader') ).next()
            except Exception,e:
                logger.warn(e)
            else:
                logger.info(leader)
                return leader

    def _checkSwarmHealth(self, swarm):
        """ According to the manager IP to determine whether the cluster is healthy """

        state = False
        logger.info("To determine whether the cluster is healthy, starting")
        try:
            nodes = requests.get(Splice(ip=self._checkSwarmLeader(swarm), port=self.port, path='/nodes').geturl, timeout=self.timeout, verify=self.verify).json()
            for node in nodes:
                role = 'Leader' if node.get('ManagerStatus', {}).get('Leader') else node['Spec'].get('Role')
                # Logic to determine whether a cluster is healthy!
                if role == 'Leader':
                    state = True if node['Status']['State'] == 'ready' and node['Spec'].get('Availability') == 'active' and node.get('ManagerStatus', {}).get('Reachability') == 'reachable' else False
        except Exception,e:
            logger.warn(e, exc_info=True)
        logger.info("To determine whether the cluster is healthy, ending, the state is %s" %state)
        if state:
            return 'Healthy'
        else:
            return 'Unhealthy'

    def getOne(self, name):
        """ return the swarm cluster for a name """
        if self.isMember(name):
            return ( _ for _ in self._swarm if _.get("name") == name ).next()
        else:
            logger.warn("get %s, but no data" %name)
            return {}

    def getSwarm(self, checkState=False):
        """ show all swarm cluster """
        res = []
        if checkState == True:
            logger.info("get and check all swarm cluster, start")
            for swarm in self._swarm:
                swarm.update(state=self._checkSwarmHealth(swarm))
                res.append(swarm)
            return res
        else:
            return self._swarm

    @property
    def getLeader(self):
        """get the active swarm leader """
        return self._checkSwarmLeader(self._active)
    
    @property
    def getMethod(self):
        """ return storage swarm method(in config.py) """
        return self._method

    @property
    def getDefault(self):
        """ return default(in config.py) swarm cluster """
        return self._default

    @property
    def getActive(self):
        """ return active swarm cluster """
        return self._active

    def setActive(self, name):
        """ set current active swarm, otherwise, it must be self._default """
        logger.info("setActive, request name that will set is %s, now current active swarm name is %s" %(name, self.getActive.get("name")))

        if self.isActive(name):
            logger.info("The name of the request is already active.")
        else:
            logger.info("The name of the request is not current active swarm, will update it to be active.")
            self._active = self.getOne(name)
            if self.getMethod == "etcd":
                put2etcdRes = self.etcd._put(self.etcdActiveKey, data={"value": json.dumps(self._active)})
                logger.info("setActive, put2etcd => %s" %put2etcdRes)
            if not self.isActive(name):
                logger.info("setActive, the request name sets it for active, but fail")
                return False
        return True

    def GET(self, get, checkState=False):
        """ R, read, get swarm info """
        res = {"msg": None, "code": 0}
        logger.info("GET request, the query params is %s, get state is %s" %(get, checkState))

        #Check query
        if not isinstance(get, (str, unicode)) or not get:
            res.update(msg="query params type error", code=-1000)
        else:
            get = get.lower()
            if get == "all":
                res.update(data=self.getSwarm(checkState))
            elif get == "default":
                res.update(data=self.getDefault)
            elif get == "active":
                res.update(data=self.getActive)
            elif get == "method":
                res.update(data=self.getMethod)
            elif get == "leader":
                res.update(data=self.getLeader)
            else:
                res.update(data=self.getOne(get))
        logger.info(res)
        return res

    def POST(self, **swarm):
        """ add a swarm cluster into current, check, pickle. """
        res = {"msg": None, "code": 0}
        logger.info(swarm)

        swarmName = swarm.get("name")
        swarmType = swarm.get("type")
        swarmIp   = swarm.get("ip")

        if self.isMember(swarmName):
            res.update(msg="swarm cluster already exists", code=-1020)

        else:
            if swarmName and swarmIp and swarmType in ("cluster", "engine"):
                logger.info("check params value pass.")
                #access node ip's info, and get all remote managers
                if isinstance(swarmIp, (str, unicode)):
                    swarmIp = commaConvert(swarmIp)
                node = choice(swarmIp).split(':')
                nodeIp = node[0]
                nodePort = self.port if node[-1] == nodeIp else node[-1]
                url = Splice(ip=nodeIp, port=nodePort, path='/info').geturl
                logger.info("get swarm ip info, that url is %s" %url)
                try:
                    r = requests.get(url, timeout=self.timeout, verify=self.verify).json()
                except Exception,e:
                    logger.warn(e, exc_info=True)
                    res.update(msg="Access the node ip url(%s) has exception" %url, code=-1021)
                    logger.info(res)
                    return res
                else:
                    swarm.update(manager=[ _.get('Addr').split(':')[0] for _ in r.get("Swarm", {}).get("RemoteManagers") ])
                    token = self._checkSwarmToken(self._checkSwarmLeader(swarm))
                    swarm.pop('ip')
                    swarm.update(managerToken=token.get('Manager'), workerToken=token.get('Worker'))
                    self._swarm.append(swarm)
                    logger.debug("pickle now swarm %s" %self._swarm)
                    self._pickle(self._swarm)
                    res.update(success=True)
                    logger.info("check all pass and added")
            else:                    
                res.update(msg="check params value fail, can not add it.", code=-1022, success=False)

        logger.info(res)
        return res

    def DELETE(self, name):
        """ remove a swarm cluster in current swarm """
        res = {"msg": None, "code": 0}
        logger.info("DELETE request, the name that will delete is %s" %name)

        if name in ("default", "active", "all"):
            res.update(msg="name reserved for the system key words", code=-1031)

        elif self.isActive(name):
            res.update(msg="not allowed to delete the active cluster", code=-1032)

        elif self.isMember(name):
            logger.info("Will delete swarm cluster is %s" %self.getOne(name))
            self._swarm.remove(self.getOne(name))
            if self.isMember(name):
                logger.info("Delete fail")
                res.update(success=False)
            else:
                logger.info("Delete pass, pickle current swarm")
                self._pickle(self._swarm)
                res.update(success=True)

        else:
            res.update(msg="This swarm cluster does not exist", code=-1030)

        logger.info(res)
        return res

    def PUT(self, setActive=False, **swarm):
        """ update a swarm cluster info in current swarm """

        res = {"msg": None, "code": 0}
        logger.info("PUT request, setActive(%s), other kwargs:%s" %(setActive, swarm))

        name = swarm.get("name")

        if setActive == True:
            if name and self.isMember(name):
                res.update(success=self.setActive(name))
            else:
                res.update(msg="setActive, but no name param or name non-existent", code=-1010)
        else:
            pass
            #update swarm info

        logger.info(res)
        return res
