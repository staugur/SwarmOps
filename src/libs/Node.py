# -*- coding:utf8 -*-

from SpliceURL import Splice
from utils.public import ip_check, timeChange, string2dict
from utils.tool import logger
from .Base import BASE_SWARM_ENGINE_API


class NodeManager(BASE_SWARM_ENGINE_API):


    def __init__(self, port=2375, timeout=2, ActiveSwarm=None):
        self.port      = port
        self.timeout   = timeout
        self.verify    = False
        self.swarm     = ActiveSwarm
        self.leader    = self._checkSwarmLeader(self.swarm) if self.swarm != {} else None
        logger.info("Node Api Init, ActiveSwarm is %s, the leader is %s" %(self.swarm, self.leader))

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
                    node_host          = i['Spec'].get('Labels', {}).get('ipaddr', i['Description']['Hostname']) or i.get('ManagerStatus', {}).get('Addr', '').split(':')[0]
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
                    node_host = i['Spec'].get('Labels', {}).get('ipaddr', i['Description']['Hostname']) or i.get('ManagerStatus', {}).get('Addr', '').split(':')[0]
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