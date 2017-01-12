# -*- coding:utf8 -*-

from SpliceURL import Splice
from utils.public import logger, ip_check, timeChange, string2dict
from .Base import BASE_SWARM_ENGINE_API


class NetworkManager(BASE_SWARM_ENGINE_API):


    def __init__(self, port=2375, timeout=2, ActiveSwarm=None):
        self.port      = port
        self.timeout   = timeout
        self.verify    = False
        self.swarm     = ActiveSwarm
        self.leader    = self._checkSwarmLeader(self.swarm) if self.swarm != {} else None
        logger.info("Network Api Init, ActiveSwarm is %s, the leader is %s" %(self.swarm, self.leader))

    def GET(self, networkId=None):
        """ 查询所有可用的网络, 并组织返回网络信息 """

        res = {"code": 0, "msg": None, "data": []}

        if self.leader:
            req_data = self._checkSwarmNetwork(self.leader, networkId)
            req_data = req_data if isinstance(req_data, (list, tuple)) else (req_data,)
            Net_data = []
            for i in req_data:
                try:
                    NetId      = i['Id']
                    Name       = i['Name']
                    Driver     = i['Driver']
                    Scope      = i['Scope']
                    IPAM       = i['IPAM']
                    Containers = i['Containers']
                except Exception,e:
                    logger.error(e, exc_info=True)
                    Net_data.append((i['Name'], i.get("Id")))
                else:
                    Net_data.append((NetId, Name, Driver, Scope, IPAM, Containers))
            res.update(data=Net_data)
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

        #Get Active Swarm Nodes Id Before adding a node
        nodesId1 = [ node[1] for node in self.GET()["data"] ]
        logger.info("The nodesId one before adding a node is {}".format(nodesId1))
        #Add a node
        res.update(success=self._JoinSwarm(node_ip=ip.strip(), role=role, swarm=self.swarm))
        #Set node labels and Update it
        nodesId2 = [ node[1] for node in self.GET()["data"] ]
        logger.info("The nodesId one after adding a node is {}".format(nodesId2))
        for nodeId in nodesId2:
            if nodeId not in nodesId1:
                logger.info("POST node, id is {}".format(nodeId))
                UpdateMsg = self.PUT(node_id=nodeId, node_role=role, node_labels={"ipaddr": ip.strip()})
                if UpdateMsg["success"] == False:
                    res.update(msg="Update Node Labels Failed")
                else:
                    res.update(msg=UpdateMsg["msg"])

        logger.info(res)
        return res

    def PUT(self, node_id, node_role, node_labels):
        """ 更新节点 """

        res = {"msg": None, "code": 0, "success": False}

        if not self.leader:
            res.update(msg="No Active Swarm", code=-1005)
            logger.info(res)
            return res

        if not node_role in ("Manager", "Worker"):
            res.update(msg="role error", code=-1006)
            logger.info(res)
            return res

        if isinstance(node_labels, (str, unicode)):
            labels = string2dict(node_labels)
        elif isinstance(node_labels, dict):
            labels = node_labels
        else:
            res.update(msg="node_labels error", code=-1007)
            logger.info(res)
            return res

        res.update(success=self._UpdateNode(leader=self.leader, node_id=node_id, node_role=node_role, labels=labels))
        logger.info(res)
        return res

    def DELETE(self, ip, force):
        """ 节点离开集群 """

        res   = {"msg": None, "code": 0, "success": False}
        force = True if force in ("true", "True", True) else False

        if not self.leader:
            res.update(msg="No Active Swarm", code=-1008)
            logger.info(res)
            return res

        res.update(success=self._LeaveSwarm(node_ip=ip.strip(), force=force))
        logger.info(res)
        return res