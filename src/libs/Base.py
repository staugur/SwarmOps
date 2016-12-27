# -*- coding: utf8 -*-

import requests, json
from SpliceURL import Splice
from utils.public import logger
from random import choice

class BASE_SWARM_ENGINE_API:


    def __init__(self, port=2375, timeout=3):
        self.port      = port
        self.timeout   = timeout
        self.verify    = False

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

        logger.info("check swarm %s leader, the request swarm manager is %s" %(swarm.get("name"), swarm.get("manager")))
        if swarm:
            try:
                url  = Splice(netloc=swarm.get("manager")[0], port=self.port, path='/nodes').geturl
                data = requests.get(url, timeout=self.timeout, verify=self.verify).json()
            except requests.exceptions.Timeout, e:
                logger.warn(e, exc_info=True)
                url  = Splice(netloc=swarm.get("manager")[-1], port=self.port, path='/nodes').geturl
                data = requests.get(url, timeout=self.timeout, verify=self.verify).json()
            except requests.exceptions.Timeout, e:
                logger.warn(e, exc_info=True)
                url  = Splice(netloc=choice(swarm.get("manager")), port=self.port, path='/nodes').geturl
                data = requests.get(url, timeout=self.timeout, verify=self.verify).json()
            except Exception,e:
                logger.error(e, exc_info=True)
            else:
                if isinstance(data, (list, tuple)):
                    leader = ( _.get('ManagerStatus', {}).get('Addr').split(':')[0] for _ in data if _.get('ManagerStatus', {}).get('Leader') ).next()
                else:
                    leader = None
                logger.info("get %s leader, request url is %s, get leader is %s" %(swarm["name"], url, leader))
                return leader

    def _checkSwarmHealth(self, leader):
        """ 根据Leader查询某swarm集群是否健康 """

        state = []
        mnum  = 0
        logger.info("To determine whether the cluster is healthy, starting, swarm leader is %s" %leader)
        try:
            nodes = requests.get(Splice(netloc=leader, port=self.port, path='/nodes').geturl, timeout=self.timeout, verify=self.verify).json()
            logger.debug("check swarm health, swarm nodes length is %d" % len(nodes))
            for node in nodes:
                if node['Spec'].get('Role') == 'manager':
                    mnum += 1
                    isHealth = True if node['Status']['State'] == 'ready' and node['Spec'].get('Availability') == 'active' and node.get('ManagerStatus', {}).get('Reachability') == 'reachable' else False
                    if isHealth:
                        state.append(isHealth)
        except Exception,e:
            logger.warn(e, exc_info=True)
            return "ERROR"
        else:
            logger.info("To determine whether the cluster is healthy, ending, the state is %s, manager number is %d" %(state, mnum))
            if len(state) == mnum and state:
                return 'Healthy'
            else:
                return 'Unhealthy'

    def _checkSwarmNodeinfo(self, ip):
        """ 查询节点信息 """

        try:
            NodeUrl  = Splice(netloc=ip, port=self.port, path="/info").geturl
            NodeInfo = requests.get(NodeUrl, timeout=self.timeout, verify=self.verify).json()
        except Exception,e:
            logger.error(e, exc_info=True)
            return {}
        else:
            logger.info("check node info, request url is %s ,response is %s" %(NodeUrl, NodeInfo))
            return NodeInfo

    def _checkSwarmNode(self, leader, node=None):
        """ 查询节点 """
        try:
            path     = "/nodes/" + node if node else "/nodes"
            NodeUrl  = Splice(netloc=leader, port=self.port, path=path).geturl
            NodeData = requests.get(NodeUrl, timeout=self.timeout, verify=self.verify).json()
        except Exception,e:
            logger.error(e, exc_info=True)
        else:
            logger.info("check node, request url is %s ,response is %s" %(NodeUrl, NodeData))
            return NodeData

    def _checkSwarmManager(self, ip):
        """ 查询节点的Manager """

        url   = Splice(netloc=ip, port=self.port, path='/info').geturl
        logger.info("Get or Update swarm manager, that url is %s" %url)
        try:
            nodeinfo = requests.get(url, timeout=self.timeout, verify=self.verify).json()
            logger.debug("Get or Update swarm manager, response is %s" %nodeinfo)
            managers = [ nodes["Addr"].split(":")[0] for nodes in nodeinfo["Swarm"]["RemoteManagers"] ]
        except Exception,e:
            logger.error(e, exc_info=True)
            return []
        else:
            return managers

    def _checkServiceTaskNode(self, leader, service):
        """ 查询某service的实例节点 """

        url   = Splice(netloc=leader, port=self.port, path='/tasks').geturl
        logger.info("Get service %s task, that url is %s" %(service, url))
        data  = requests.get(url, params={"filters": json.dumps({'desired-state':{'running':True}})}).json()
        #data  = requests.get(url).json()
        nodes = [ _['NodeID'] for _ in data if _['Status']['State'] == 'running' and _['ServiceID'] == service ]
        ips   = []
        for node in nodes:
            nodeinfo = self._checkSwarmNode(leader, node)
            ip = nodeinfo.get('ManagerStatus', {}).get('Addr', '').split(':')[0] or nodeinfo['Spec'].get('Labels', {}).get('ipaddr')
            ips.append(ip)
        return {"ips": ips, "nodes": nodes}
