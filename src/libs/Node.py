# -*- coding:utf8 -*-

import requests
from SpliceURL import Splice
from utils.public import logger, ip_check, timeChange
from .Base import BASE_SWARM_ENGINE_API


class NodeManager(BASE_SWARM_ENGINE_API):


    def __init__(self, port=2375, timeout=3, ActiveSwarm=None):
        self.port      = port
        self.timeout   = timeout
        self.verify    = False
        self.swarm     = ActiveSwarm
        self.leader    = self._checkSwarmLeader(self.swarm)
        logger.info("Node Api, ActiveSwarm is %s, the leader is %s" %(self.swarm, self.leader))

    def GET(self):
        """ 查询所有可用的节点群，并组织返回节点信息 """

        res = {"code": 0, "msg": None, "data": []}
        if self.leader:
            #format (host, id, role, status, availability, reachability, containers, cpu, mem, label, UpdatedAt, Version).
            node = []
            for i in self._checkSwarmNode(self.leader):
                try:
                    node_id            = i['ID']
                    node_role          = 'Leader' if i.get('ManagerStatus', {}).get('Leader') else i['Spec'].get('Role')
                    node_host          = i.get('ManagerStatus', {}).get('Addr', '').split(':')[0] or i['Spec'].get('Labels', {}).get('ipaddr', i['Description']['Hostname'])
                    node_status        = i['Status']['State']
                    node_availability  = i['Spec'].get('Availability')
                    node_reachability  = i.get('ManagerStatus', {}).get('Reachability')
                    node_containers    = self._checkSwarmNodeinfo(node_host).get("ContainersRunning") if ip_check(node_host) else 'Unknown'
                    node_cpu           = int(i['Description']['Resources']['NanoCPUs'] / 1e9)
                    node_mem           = int(i['Description']['Resources']['MemoryBytes'] / 1e6 / 1024) #bytes to G
                    node_label         = i['Spec'].get('Labels')
                    if isinstance(node_label, dict):
                        _node_label = ''
                        for k,v in node_label.iteritems():
                            _node_label += '%s:%s, ' %(k, v)
                        node_label = _node_label.strip(' ,')
                    node_UpdatedAt     = timeChange(i['UpdatedAt'])
                    node_dockerversion = i['Description']['Engine']['EngineVersion']
                except Exception,e:
                    logger.error(e, exc_info=True)
                    logger.debug(i)
                    node.append((i.get("ID"), ))
                else:
                    node.append((node_host, node_id, node_role, node_status, node_availability, node_reachability, node_containers, node_cpu, node_mem, node_label, node_UpdatedAt, node_dockerversion))
            res.update(data=node)
        logger.info(res)
        return res