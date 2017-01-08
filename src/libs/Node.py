# -*- coding:utf8 -*-

import requests
from SpliceURL import Splice
from utils.public import logger, ip_check, timeChange, string2dict
from .Base import BASE_SWARM_ENGINE_API


class NodeManager(BASE_SWARM_ENGINE_API):


    def __init__(self, port=2375, timeout=2, ActiveSwarm=None):
        self.port      = port
        self.timeout   = timeout
        self.verify    = False
        self.swarm     = ActiveSwarm
        self.leader    = self._checkSwarmLeader(self.swarm)
        logger.info("Node Api, ActiveSwarm is %s, the leader is %s" %(self.swarm, self.leader))

    def GET(self, node=None):
        """ 查询所有可用的节点群，并组织返回节点信息 """

        res = {"code": 0, "msg": None, "data": []}
        if self.leader:
            #format (host, id, role, status, availability, reachability, containers, cpu, mem, label, UpdatedAt, DockerVersion).
            req_data  = self._checkSwarmNode(self.leader, node)
            req_data  = req_data if isinstance(req_data, (list, tuple)) else (req_data,)
            node_data = []
            for i in req_data:
                try:
                    node_id            = i['ID']
                    node_role          = 'Leader' if i.get('ManagerStatus', {}).get('Leader') else i['Spec'].get('Role')
                    node_host          = i.get('ManagerStatus', {}).get('Addr', '').split(':')[0] or i['Spec'].get('Labels', {}).get('ipaddr', i['Description']['Hostname'])
                    node_status        = i['Status']['State']
                    node_availability  = i['Spec'].get('Availability')
                    node_reachability  = i.get('ManagerStatus', {}).get('Reachability')
                    node_containers    = self._checkSwarmNodeinfo(node_host).get("ContainersRunning") if ip_check(node_host) and node_status == "ready" and node_availability == "active" else 'Unknown'
                    node_cpu           = int(i['Description']['Resources']['NanoCPUs'] / 1e9)
                    node_mem           = int(i['Description']['Resources']['MemoryBytes'] / 1e6 / 1024) #bytes to G
                    node_label         = i['Spec'].get('Labels')
                    if isinstance(node_label, dict):
                        _node_label = ''
                        for k,v in node_label.iteritems():
                            _node_label += '%s=%s, ' %(k, v)
                        node_label = _node_label.strip(' ,')
                    node_CreatedAt     = timeChange(i['CreatedAt'])
                    node_UpdatedAt     = timeChange(i['UpdatedAt'])
                    node_dockerVersion = i['Description']['Engine']['EngineVersion']
                    node_indexVersion  = i.get("Version",  {}).get("Index")

                except Exception,e:
                    logger.error(e, exc_info=True)
                    logger.debug(i)
                    node_host = i.get('ManagerStatus', {}).get('Addr', '').split(':')[0] or i['Spec'].get('Labels', {}).get('ipaddr', i['Description']['Hostname'])
                    node_data.append((node_host, i.get("ID")))
                else:
                    node_data.append((node_host, node_id, node_role, node_status, node_availability, node_reachability, node_containers, node_cpu, node_mem, node_label, node_CreatedAt, node_UpdatedAt, node_dockerVersion))
            res.update(data=node_data)
        logger.info(res)
        return res

    def POST(self, ip, role):
        """ 节点加入集群 """

        res  = {"msg": None, "code": 0, "success": False}

        if not self.leader:
            res.update(msg="No Active Swarm", code=-1003)
            logger.info(res)
            return res

        if not role in ("Manager", "Worker"):
            res.update(msg="role error", code=-1004)
            logger.info(res)
            return res

        res.update(success=self._JoinSwarm(node_ip=ip.strip(), role=role, swarm=self.swarm))
        logger.info(res)
        return res

    def PUT(self, node_id, node_role, labels=''):
        """ 更新节点 """

        res  = {"msg": None, "code": 0, "success": False}

        if not self.leader:
            res.update(msg="No Active Swarm", code=-1005)
            logger.info(res)
            return res

        if not role in ("Manager", "Worker"):
            res.update(msg="role error", code=-1006)
            logger.info(res)
            return res

        labels = string2dict(labels)

        res.update(success=self._UpdateNode(leader=self.leader, node_id=node_id, node_role=node_role, labels=labels))
        logger.info(res)
        return res

