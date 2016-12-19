# -*- coding:utf8 -*-
#
# Docker Engine Swarm模式接口程序。
# 封装了Engine Swarm接口，组织信息并返回。
# 每一个共有类函数(除了Node基函数和功能性函数)都是一个URL接口。
# Engine Swarm API类似Docker Remote Api。
# Docker Engine Swarm模式，版本应当不小于1.12.0，API版本应当不小于1.24，官方API文档地址是：
# https://github.com/docker/docker/blob/v1.12.0/docs/reference/api/docker_remote_api_v1.24.md
#

import re
import time
import json
import requests
import libs.ssh
from utils.public import logger, Ot2Bool, ip_check, timeChange, commaPat, commaConvert
from random import choice
from SpliceURL import Splice


class SWARM_ENGINE_API(object):


    def __init__(self, Managers):
        """
        Random read the configuration file SWARM management node information, select a management IP.
        """

        #Check parameters.
        if not isinstance(Managers, (list, tuple)):
            errmsg = "Managers parameter error in SWARM_ENGINE_API, only list or tuple is allowed."
            logger.error(errmsg)
            raise TypeError(errmsg)

        #Get `self.Managers` random ip for quering RESTFul Api.
        self.Managers  = Managers
        self.ManagerIp = choice(self.Managers)

        #Define global timeout seconds and so on.
        self.port    = 2375
        self.timeout = 3
        self.verify  = False

        #Regular expressions and functions that depend on it.
        self.commaPat = commaPat
        self.commaConvert = commaConvert

        #Check Leader and get itself ip
        self.LeaderIp = self.getSwarmLeader()


    def getSwarmInfo(self, node_ip=None):
        """Get SwarmEngine Info"""
        try:
            ip = node_ip or self.LeaderIp
            SwarmEngineInfoUrl  = Splice(ip=ip, port=2375, path="/info").geturl
            SwarmEngineInfoRes  = requests.get(SwarmEngineInfoUrl, timeout=self.timeout, verify=False)
            SwarmEngineInfoData = SwarmEngineInfoRes.json() or {}
        except Exception,e:
            logger.info({"SwarmEngineInfoUrl": SwarmEngineInfoUrl})
            logger.error(e, exc_info=True)
            return {}
        else:
            logger.info("Swarm Engine Manager is %s, request url that the info interface is %s." %(self.Managers, SwarmEngineInfoUrl))
            logger.debug(SwarmEngineInfoData)
            #Define global docker swarm info(now engine), only swarm cluster, it has not SystemStatus in docker swarm(version>=1.12.0).
            return SwarmEngineInfoData

    def getSwarmNode(self, flag=None):
        """#Get SwarmEngine Nodes"""
        try:
            path = "/nodes/%s" %flag if flag else "/nodes" 
            SwarmEngineNodeUrl  = Splice(ip=self.LeaderIp, port=self.port, path=path).geturl
            SwarmEngineNodeRes  = requests.get(SwarmEngineNodeUrl, timeout=self.timeout, verify=self.verify)
            SwarmEngineNodeData = SwarmEngineNodeRes.json()
            SwarmEngineNodeCode = SwarmEngineNodeRes.status_code
        except Exception,e:
            logger.info({"SwarmEngineNodeUrl": SwarmEngineNodeUrl})
            logger.error(e, exc_info=True)
        else:
            logger.info("Swarm Engine Manager is %s, request url that the nodes interface is %s." %(self.Managers, SwarmEngineNodeUrl))
            logger.debug(SwarmEngineNodeData)
            #Define global docker swarm nodes informations.
            if flag:
                return SwarmEngineNodeData,SwarmEngineNodeCode
            else:
                return SwarmEngineNodeData

    def getSwarmLeader(self):
        """ get the swarm cluster leader """

        """
        for manager in self.Managers:
            try:
                nodes = requests.get(Splice(ip=manager, port=self.port, path='/nodes').geturl, timeout=self.timeout, verify=self.verify).json()
                if isinstance(nodes, (list, tuple)):
                    for node in nodes:
                        if node.get('ManagerStatus', {}).get('Leader') and node.get('Status', {}).get('State') == 'ready' and node.get('Spec', {}).get('Availability') == 'active' and node.get('ManagerStatus', {}).get('Reachability') == 'reachable':
                            return node.get('ManagerStatus', {}).get('Addr').split(':')[0]
                continue
            except Exception,e:
                logger.warn(e, exc_info=True)
        """
 
        for manager in self.Managers:
            try:
                leader = ( _.get('ManagerStatus', {}).get('Addr', '').split(':')[0] for _ in requests.get(Splice(ip=manager, port=self.port, path='/nodes').geturl, timeout=self.timeout, verify=self.verify).json() if _.get('ManagerStatus', {}).get('Leader') ).next()
            except Exception,e:
                logger.warn(e, exc_info=True)
            else:
                logger.info(leader)
                return leader

class SWARM_NODE_API(SWARM_ENGINE_API):

    """Manager swarm node, add/delete/modify => POST/DELETE/PUT"""

    def add(self, ip, role, manager_token, worker_token, **kwargs):
        """Add ip(node) and role(node) to the swarm cluster defined in the config.py"""
        res = {"msg": None, "code": 0, "success": False}
        logger.info(kwargs)

        if not ip or not role:
            res.update(msg="ip or role is empty", code=20010)
            logger.info(res)
            return res
        else:
            if role == "manager":
                cmd = ["docker swarm join --token %s %s --advertise-addr %s --listen-addr 0.0.0.0" %(manager_token,self.LeaderIp, ip), "hostname"]
            else:
                cmd = ["docker swarm join --token %s %s --advertise-addr %s --listen-addr 0.0.0.0" %(worker_token, self.LeaderIp, ip), "hostname"]

        data = libs.ssh.ssh2(ip=ip, cmd=cmd)
        if data:
            success = True if "This node joined a swarm as a %s." %role in data else False
            node_flag = data[-1] if len(data) > 0 else None
            logger.info("Add a node to the docker swarm cluster, command is %s, return is %s, success is %s, node flag is %s" %(cmd, data, success, node_flag))
            res.update(success=success)
            if success:
                kwargs.update(node=node_flag, ipaddr=[ip, ])
                if not self.updateNode(**kwargs).get("success"):
                    res.update(msg="Add node success, but update node the ipaddr label fail.", code=20000)

        logger.info(res)
        return res

    def rm(self, node_ip, flag, force=False):
        """Remove flag(nodeId or hostname) to the swarm cluster defined in the config.py, and force?
        1. If manager, demote.
        2. Login node_ip, and exec cmd(docker swarm leave), get the result.
        3. Login self.LeaderIp, when the flag's status isn't "ready", rm it.
        """
        res      = {"msg": None, "code": 0}
        flagData = self.getSwarmNode(flag)[0]
        flagRole = flagData.get("Spec").get("Role")

        #check args
        if not flagRole in ("worker", "manager"):
            res.update(msg="No such role", code=20001)
            logger.info(res)
            return res
        if node_ip == self.LeaderIp:
            res.update(msg="Delete leader not allowed", code=20004)
            logger.info(res)
            return res

        #demote manager to worker
        step1 = True
        if flagRole == "manager":
            step1Res = libs.ssh.ssh2(ip=self.LeaderIp, cmd="docker node demote %s" %flag)
            logger.info("Step1, %s is manager, demote it, result is %s" %(flag, step1Res))
            if not "Manager %s demoted in the swarm." %flag in step1Res:
                res.update("%s demote fail in manager(%s)" %(flag, self.LeaderIp))
                logger.info(res)
                return res

        #login worker(anything is worker), leave swarm
        step2 = True
        step2Cmd = "docker swarm leave --force" if force else "docker swarm leave"
        step2Res = libs.ssh.ssh2(ip=node_ip, cmd=step2Cmd)
        logger.info("Step2, login %s, exec command to leave swarm, result is %s" %(node_ip, step2Res))
        if not "Node left the swarm." in step2Res:
            res.update(msg="In node_ip(%s), leave fail with force=%s." %(node_ip, force), code=20002)
            logger.info(res)
            return res

        #login leader and rm flag
        step3 = False
        step3Cmd = "docker node rm %s" %flag
        i=1
        while i < 6:
            State = self.getSwarmNode(flag)[0].get("Status").get("State")
            logger.info("Try, the No.%d, State is %s" %(i, State))
            if State == "down":
                step3Res = libs.ssh.ssh2(ip=self.LeaderIp, cmd=step3Cmd)
                logger.info("Step3, login leader(%s), exec command to rm node, result is %s" %(self.LeaderIp, step3Res))
                step3 = True if flag in step3Res else False
                break
            i+=1
            time.sleep(6)
        logger.info("Remove %s(%s) with %s, step1: %s, step2: %s, step3: %s" %(flag, node_ip, force, step1, step2, step3))

        #check remove result
        flagCode = self.getSwarmNode(flag)[-1]
        if flagCode == 404:
            res.update(success=True)
        else:
            res.update(msg="Node(%s) rm fail" %flag, code=20003, success=False)
 
        logger.info(res)
        return res

    def addApi(self, ip, role, manager_token, worker_token):
        """
        1. get and check params.
        2. post data to swarm api.
        """
        res = {"msg": None, "code": 0}
        logger.debug({"ip": ip, "role": role, "manager_token": manager_token, "worker_token": worker_token})
        if not ip or not role in ("manager", "worker"):
            res.update(msg="The parameters ip or role error", code=20000)
            logger.info(res)
            return res

        #ip, it can be a real ip, or ip:port(default port is 2377).
        token = manager_token if role.lower() == "manager" else worker_token
        baseData = {
            'JoinToken': token,
            'RemoteAddrs': self.Managers,
            'ListenAddr': None,
            'AdvertiseAddr': ip
        }
        logger.info("Add a node to the docker swarm cluster, post data is %s" %baseData)
        try:
            SwarmEngineJoinUrl  = Splice(ip=self.LeaderIp, port=2375, path="/swarm/join").geturl
            SwarmEngineJoinRes  = requests.post(SwarmEngineJoinUrl, timeout=self.timeout, verify=False, data=json.dumps(baseData))
            SwarmEngineJoinData = SwarmEngineJoinRes.json() or {}
            SwarmEngineJoinCode = SwarmEngineJoinRes.status_code
        except Exception,e:
            logger.error(e, exc_info=True)
        else:
            logger.info("Request url that the swarm join interface is %s." %SwarmEngineJoinUrl)
            logger.debug(SwarmEngineJoinData)
            logger.debug(SwarmEngineJoinCode)
            if SwarmEngineJoinCode == 200:
                res.update(success=True)
            else:
                res.update(success=False)
        logger.info(res)
        return res

    def updateNode(self, **kwargs):
        """Update ip(node) the labels(kwargs)"""

        res = {"msg": None, "code": 0}
        logger.info(kwargs)

        node = kwargs.get("node")
        try:
            kwargs.pop("node")
        except KeyError,e:
            logger.warn(e)
            res.update(msg="node is empty", code=20011)
            logger.info(res)
            return res
        else:
            if isinstance(node, (list, tuple)) and len(node) > 0:
                node = node[0]

        #check params
        if not node:
            res.update(msg="node is empty", code=20012)
            logger.info(res)
            return res

        sourceCmd = "docker node update"
        if kwargs:
            for k,v in kwargs.iteritems():
                if isinstance(v, (list, tuple)) and len(v) > 0:
                    v=v[0]
                    sourceCmd += " --label-add %s=%s " %(k, v)
                else:
                    logger.warn("invaild key/value label, %s:%s" %(k, v))

        sourceCmd += node
        sourceRes = libs.ssh.ssh2(ip=self.LeaderIp, cmd=sourceCmd)
        logger.info("Update a node label command is %s, return is %s" %(sourceCmd, sourceRes))
        success = True if node in sourceRes else False
        res.update(success=success)
        logger.info(res)
        return res

    def NodeQuery(self, **query):
        """Query all available nodes on the Swarm, and organize the return of the node information."""
        #node= self.Node

        #Get Node Info, the format is (host, id, role, status, availability, reachability, containers, cpu, mem, label, UpdatedAt, Version).
        node = []
        for i in self.getSwarmNode():
            try:
                node_id            = i['ID']
                node_role          = 'Leader' if i.get('ManagerStatus', {}).get('Leader') else i['Spec'].get('Role')
                node_host          = i.get('ManagerStatus', {}).get('Addr', '').split(':')[0] or i['Spec'].get('Labels', {}).get('ipaddr', i['Description']['Hostname'])
                node_status        = i['Status']['State']
                node_availability  = i['Spec'].get('Availability')
                node_reachability  = i.get('ManagerStatus', {}).get('Reachability')
                node_containers    = self.getSwarmInfo(node_host).get("ContainersRunning") if ip_check(node_host) else 'Unknown'
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
                logger.warn(i)
            else:
                node.append((node_host, node_id, node_role, node_status, node_availability, node_reachability, node_containers, node_cpu, node_mem, node_label, node_UpdatedAt, node_dockerversion))
        logger.info(node)

        res = {"data": node, "code": 0, "msg": None}
        logger.info({"Query": query})
        try:
            start      = int(query.get("start"))
            length     = int(query.get("length"))
            orderindex = int(query.get("orderindex"))
            search     = str(query.get("search"))
            ordertype  = str(query.get("ordertype"))
        except Exception, e:
            logger.error(e, exc_info=True)
            res.update(msg="A query parameter may not be a number in start, length or order[0][column]", data=[], code=10000)
        else:
            res["start"]           = start
            res["length"]          = length
            res["search[value]"]   = search
            res["order[0][column]"]= orderindex
            res["order[0][dir]"]   = ordertype
            res['recordsFiltered'] = len(node)
            res['recordsTotal']    = len(node)
            if start == 0 and length == 10 and search == '' and orderindex == 0 and ordertype == "asc":
                pass
            else:
                """
                Analyze different parameters and return data.
                :: Search(search[value] or search) the greatest priority, swarm node data in any one of the search content will be appended to the return and presentation. \n
                   Does not support the search label!
                :: The returned data need to sort(order[0][dir]), the default sort is the index 0 column in ascending order by (order[0][column]) control index.
                :: After the search and index sorting is completed, the final data is returned through the start:start+length section.
                """
                try:
                    if search != '':
                        node = [ n for n in node for _n in n if str(_n).find(search) >= 0 ]
                        #Traverse each API of the node information, when the search is found to match the content, that is, the node append to the results.
                        #if there is dict content in node, such as label, then do not support, please select the label related URL.
                except Exception,e:
                    logger.error(e, exc_info=True)
                try:
                    logger.info("ordertype(reverse) is %s" %Ot2Bool(ordertype))
                    node.sort(key=lambda x:x[orderindex], reverse=Ot2Bool(ordertype))
                except IndexError,e:
                    logger.error(e, exc_info=True)
                    res.update(msg="order[0][column] index out of range", data=[], code=10001)
                else:
                    res["data"] = node[start: start + length]
                    res["msg"]  = "Get node success."
        logger.info(res)
        return res

    def LabelQuery(self, **query):
        """Query Label on all available nodes of the Swarm, and organize the return of the node information."""
        node   = self.getSwarmNode()
        res    = {"data": node, "code": 0, "msg": None}
        labels = []
        logger.info({"Query": query})
        for n in node:
            logger.debug("A node:%s, type:%s" %(n, type(n)))
            try:
                alabel = n['Spec']['Labels']
            except KeyError,e:
                logger.warn(e, exc_info=True)
                logger.warn(n.get("Spec"))
            else:
                alabel.update(Hostname=n['Description']['Hostname'], NodeId=n['ID'])
                logger.debug("A label:%s, type:%s" %(alabel, type(alabel)))
                labels.append(alabel)
        logger.info(labels)
        res["data"]    = labels
        try:
            start      = int(query.get("start"))
            length     = int(query.get("length"))
            orderindex = int(query.get("orderindex"))
            search     = str(query.get("search"))
            ordertype  = str(query.get("ordertype"))
        except Exception, e:
            logger.error(e, exc_info=True)
            res.update(msg="A query parameter may not be a number in start, length or order[0][column]", data=[], code=10002)
        else:
            res["start"]           = start
            res["length"]          = length
            res["search[value]"]   = search
            res["order[0][column]"]= orderindex
            res["order[0][dir]"]   = ordertype
            res['recordsFiltered'] = len(labels)
            res['recordsTotal']    = len(labels)
            if start == 0 and length == 10 and search == '' and orderindex == 0 and ordertype == "asc":
                pass
            else:
                try:
                    if search != '':
                        labels = [ label for label in labels for _label in label.values() if _label.find(search) >= 0 ]
                    logger.debug("orderindex(%s), result is %s" %(orderindex, [ d.values()[orderindex] for d in labels ]))
                    res["data"] = sorted(labels, key=lambda d:d.values()[orderindex], reverse=Ot2Bool(ordertype))[start: start + length]
                except Exception,e:
                    logger.error(e, exc_info=True)
                    res.update(msg="order[0][column] index out of range", data=[], code=10003)
        logger.info(res)
        return res

    def Node_for_Label(self, **query):
        """Query Swarm on one or some of the Label where the node, and organize the return of the node information."""
        logger.info({"Query": query})
        pat    = re.compile(r",\s?")
        labels = []
        for i in self.getSwarmNode():
            try:
                node_host  = "%s=%s" %("Hostname", i['Description']['Hostname'])
                node_id    = "%s=%s" %("NodeId", i['ID'])
                node_label = i['Spec'].get('Labels')
            except Exception,e:
                logger.error(e, exc_info=True)
            else:
                _i_label = [ node_host, node_id ]
                if node_label:
                    try:
                        for k,v in node_label.iteritems():
                            _i_label.append("%s=%s" %(k, v))
                    except Exception,e:
                        logger.error(e, exc_info=True)
                labels.append(_i_label)
        res  = {"data": labels, "code": 0, "msg": None}
        logger.info("Initital labels is %s" %labels)

        try:
            start      = int(query.get("start"))
            length     = int(query.get("length"))
            orderindex = int(query.get("orderindex"))
            search     = str(query.get("search"))
            ordertype  = str(query.get("ordertype"))
        except Exception, e:
            logger.error(e, exc_info=True)
            res.update(msg="A query parameter may not be a number in start, length or order[0][column]", data=[], code=10004)
        else:
            res["start"]           = start
            res["length"]          = length
            res["search[value]"]   = search
            res["order[0][column]"]= orderindex
            res["order[0][dir]"]   = ordertype
            res['recordsFiltered'] = len(labels)
            res['recordsTotal']    = len(labels)

            if start == 0 and length == 10 and search == '' and orderindex == 0 and ordertype == "asc":
                pass
            else:
                """
                Analyze different parameters and return data.
                :: Search(search[value]) the greatest priority, swarm node data in any one of the search content will be appended to the return and presentation.
                :: Search content like this, "A:a,B:b" or "A:a"and so on, it's a key:value, and use multiple criteria, inclusive ",".
                """
                if search: #check format with re
                    #search.count(":") < 0 
                    node= []
                    ss  = [ s for s in re.split(pat, search) if s ]
                    #`ss` is the all labels, result is a list, such as ['A:a', 'B:b'].
                    sl  = len(ss)
                    #`sl` is the length for labels.
                    logger.info("~~Search content result is %s, length is %d" %(ss, sl))
                    for Alabel in labels:
                        si = 0
                        logger.info("!!!Start search match in node label %s" %Alabel)
                        for s in ss:
                            s = s.replace(":", "=")
                            logger.debug("Start search match, a search content is %s" %s)
                            #Search content element into a list, such as 'A=a', 'B=b' and so on.
                            if s in Alabel:
                                si += 1
                                logger.debug("%s match, si will add 1, is %d" %(s, si))
                            else:
                                logger.debug("%s miss match, si is still %d" %(s, si))
                        if sl == si:
                            node.append(Alabel[0].split("=")[-1])
                            #Append node's hostname, maybe nodeId
                    logger.info("Search after the screening of the label is %s" %node)
                    try:
                        node.sort(reverse=Ot2Bool(ordertype))
                        res["data"] = node[start: start + length]
                    except IndexError,e:
                        logger.error(e, exc_info=True)
                        res.update(msg="order[0][column] index out of range", data=[], code=10005)
                else:
                    try:
                        labels.sort(key=lambda x:x[orderindex], reverse=Ot2Bool(ordertype))
                        res["data"] = labels[start: start + length]
                    except IndexError,e:
                        logger.error(e, exc_info=True)
                        res.update(msg="order[0][column] index out of range", data=[], code=10006)

        logger.info(res)
        return res

class SWARM_SERVICE_API(SWARM_ENGINE_API):

    """
    Through the cluster swarm service interface management (Create/Retrieve/Update/Delete|POST/GET/PUT/DELETE).
    Note: Service operations require to first be part of a Swarm.
    """

    def Retrieve(self, service=None, core=False, conversion=False):
        """Retrieve, list services."""
        res = {"msg": None, "code": 0}
        logger.info("Get service(%s), core is %s" %(service, core))

        self.ServiceUrl = Splice(ip=self.LeaderIp, port=2375, path="/services/%s" %service).geturl if service else Splice(ip=self.LeaderIp, port=2375, path="/services").geturl
        try:
            r = requests.get(self.ServiceUrl, timeout=self.timeout, verify=False)
        except Exception,e:
            logger.error(e, exc_info=True)
            res.update(msg="Retrieve service fail", code=30000)
        else:
            if r.status_code == 404:
                res.update(msg="No such service<%s>" %service, data=[], code=30010)
                logger.info(res)
                return res
            else:
                services = r.json()
                recordsTotal = len(services)

            services = (services,) if not isinstance(services, (list, tuple)) else services
            services_core=[]

            if core == False:
                res.update(data=services)

            elif core == True and conversion == True:
                try:
                    for i in services:
                        logger.debug(i)
                        i_ID        = i.get("ID")
                        i_Name      = i.get("Spec", {}).get("Name")
                        i_CreatedAt = timeChange(i.get("CreatedAt"))
                        i_UpdatedAt = timeChange(i.get("UpdatedAt"))
                        i_Labels    = i.get("Spec", {}).get("Labels")
                        i_Image     = i.get("Spec", {}).get("TaskTemplate", {}).get("ContainerSpec", {}).get("Image")
                        i_Env       = i.get("Spec", {}).get("TaskTemplate", {}).get("ContainerSpec", {}).get("Env")
                        #### start convert mount
                        i_Mounts    = i.get("Spec", {}).get("TaskTemplate", {}).get("ContainerSpec", {}).get("Mounts", [])
                        _i_Mounts   = []
                        for _ in i_Mounts:
                            _i_Mounts.append("%s:%s:%s:%s" %(_.get("Source"), _.get("Target"), _.get("ReadOnly", ""), _.get("Type")))
                        i_Mounts    = _i_Mounts
                        #### end convert mount
                        i_Replicas  = i.get("Spec", {}).get("Mode", {}).get("Replicated", {}).get("Replicas")  or "global"
                        i_NetMode   = i.get("Endpoint", {}).get("Spec", {}).get("Mode") or i.get("Spec", {}).get("EndpointSpec", {}).get("Mode")
                        #### start convert publish
                        i_NetPorts  = i.get("Endpoint", {}).get("Spec", {}).get("Ports", [])
                        _i_NetPorts = []
                        for _ in i_NetPorts:
                            _i_NetPorts.append("%s:%s:%s" %(_.get("PublishedPort"), _.get("TargetPort"), _.get("Protocol")))
                        i_NetPorts  = _i_NetPorts
                        #### end convert publish
                        #### start convert vip
                        i_NetVip    = i.get("Endpoint", {}).get("VirtualIPs", [])
                        _i_NetVip   = []
                        for _ in i_NetVip:
                            _i_NetVip.append(_.get("Addr"))
                        i_NetVip    = _i_NetVip
                        #### end convert vip
                        i_Version   = i.get("Version",  {}).get("Index")
                        i_UpdateStatus = "%s(%s)" %(i.get("UpdateStatus").get("State"), timeChange(i.get("UpdateStatus").get("CompletedAt"))) if i.get("UpdateStatus").get("State") else None
                            
                        services_core.append({
                            "ID":        i_ID,
                            "Name":      i_Name,
                            "CreatedAt": i_CreatedAt,
                            "UpdatedAt": i_UpdatedAt,
                            "Labels":    i_Labels,
                            "Image":     i_Image,
                            "Env":       i_Env,
                            "Mounts":    i_Mounts,
                            "Replicas":  i_Replicas,
                            "NetMode":   i_NetMode,
                            "NetPorts":  i_NetPorts,
                            "NetVip":    i_NetVip,
                            "Version":   i_Version,
                            "UpdateStatus": i_UpdateStatus
                        })
                except Exception,e:
                    logger.error(e, exc_info=True)
                res.update(data=services_core)

            elif core == True and conversion == False:
                try:
                    for i in services:
                        logger.debug(i)
                        services_core.append({
                            "ID":        i.get("ID"),
                            "Name":      i.get("Spec", {}).get("Name"),
                            "CreatedAt": timeChange(i.get("CreatedAt")),
                            "UpdatedAt": timeChange(i.get("UpdatedAt")),
                            "Labels":    i.get("Spec", {}).get("Labels"),
                            "Image":     i.get("Spec", {}).get("TaskTemplate", {}).get("ContainerSpec", {}).get("Image"),
                            "Env":       i.get("Spec", {}).get("TaskTemplate", {}).get("ContainerSpec", {}).get("Env"),
                            "Mounts":    i.get("Spec", {}).get("TaskTemplate", {}).get("ContainerSpec", {}).get("Mounts", []),
                            "Replicas":  i.get("Spec", {}).get("Mode", {}).get("Replicated", {}).get("Replicas")  or "global",
                            "NetMode":   i.get("Endpoint", {}).get("Spec", {}).get("Mode") or i.get("Spec", {}).get("EndpointSpec", {}).get("Mode"),
                            "NetPorts":  i.get("Endpoint", {}).get("Spec", {}).get("Ports"),
                            "NetVip":    i.get("Endpoint", {}).get("VirtualIPs"),
                            "Version":   i.get("Version",  {}).get("Index"),
                            "UpdateStatus": "%s(%s)" %(i.get("UpdateStatus").get("State"), timeChange(i.get("UpdateStatus").get("CompletedAt"))) if i.get("UpdateStatus").get("State") else None
                        })
                except Exception,e:
                    logger.error(e, exc_info=True)
                res.update(data=services_core)

        res.update(recordsTotal=recordsTotal, recordsFiltered=len(res.get('data')))
        logger.info(res)
        return res

    def Create(self, image, **params):
        """Create a service in docker swarm mode cluster with api.
        1. get, convert, check params,
        2. post data to swarm api.
        """
        res = {"msg": None, "code": 0}
        logger.info("Create service, the required image is %s" %image)

        ###get params, in version 0.1.10, optional only is "name, env, mount, publish, replicas", required "image".
        logger.debug(params)
        try:
            name     = params.get("name")
            #str, needn't convert
            env      = self.commaConvert(params.get("env")) if params.get("env") else []
            #source data likes "key=value, key2=value2", convert to list or tuple, \n,
            #`env`'ask likes this, [key=value, key2=value2] or (key3=value3, key4=value4).
            mount    = self.commaConvert(params.get("mount")) if params.get("mount") else []
            #source data likes "src:dst:true:mode, src:dst:true|false:mode", example "/data/swarmopsapi-logs:/SwarmOpsApi/logs:true:bind, /data/cmlogs:/data/cmdata/logs:false:bind", convert it, \n,
            #`mount`'ask likes this, [src:dst:true|false(default false, rw):mode, ].
            publish  = self.commaConvert(params.get("publish")) if params.get("publish") else []
            #source data likes "src:desc:protocol, src2:desc2", such as `env`, convert it, \n
            #list or tuple, `publish`'ask likes this, [src:desc, src2:desc2] or ().
        except Exception,e:
            logger.warn(e, exc_info=True)
            res.update(msg="parameters error", code=40000)
            logger.info(res)
            return res
        try:
            replicas = params.get("replicas", 1)
            replicas = int(replicas) or 1
            #int, number of instances, detault is 1.
        except ValueError,e:
            logger.warn(e)
            res.update(msg="replicas not an integer", code=40001)
            logger.info(res)
            return res

        #check params
        if not image:
            logger.warn("image is empty")
            res.update(msg="image is empty", code=40002)
            logger.info(res)
            return res
        elif not isinstance(env, (str, unicode)) and not isinstance(env, (list, tuple)):
            logger.warn("env not a list or tuple, type is %s" %type(env))
            res.update(msg="env not a list or tuple", code=40003)
            logger.info(res)
            return res
        elif not isinstance(mount, (str, unicode)) and not isinstance(mount, (list, tuple)):
            logger.warn("mount not a list or tuple, type is %s" %type(mount))
            res.update(msg="mount not a list or tuple", code=40004)
            logger.info(res)
            return res
        elif not isinstance(publish, (str, unicode)) and not isinstance(publish, (list, tuple)):
            logger.warn("publish not a list or tuple, type is %s" %type(publish))
            res.update(msg="publish not a list or tuple", code=40005)
            logger.info(res)
            return res
        elif not isinstance(replicas, int):
            logger.warn("replicas not an integer, type is %s" %(type(replicas)))
            res.update(msg="replicas not an integer", code=40006)
            logger.info(res)
            return res
        else:
            logger.info("Create service, check parameters pass.")

        #Organize the data to create the service, and login manager to execute it.
        Mounts=[]
        for m in mount:
            try:
                source, target, readonly, mountype = m.split(":")
                readonly = True if readonly in ("true", "True", True) else False
            except Exception, e:
                logger.warn(e, exc_info=True)
                res.update(msg="mount format error", code=40007)
                logger.info(res)
                return res
            else:
                #Like this [{'source': '/data/swarmopsapi-logs', 'readonly': False, 'Type': 'bind', 'target': '/SwarmOpsApi/logs'}]
                Mounts.append({"Source": source, "Target": target, "ReadOnly": readonly, "Type": mountype})

        Ports=[]
        for p in publish:
            try:
                port = p.split(":")
                if len(port) == 2:
                    PublishedPort = int(port[0])
                    TargetPort    = int(port[-1])
                    Protocol      = "tcp"
                elif len(port) == 3:
                    PublishedPort = int(port[0])
                    TargetPort    = int(port[1])
                    Protocol      = port[2]
                else:
                    res.update(msg="publish format error", code=40008)
                    logger.error(p)
                    logger.info(res)
                    return res
            except Exception,e:
                logger.warn(e, exc_info=True)
                res.update(msg="publish format error", code=40009)
                logger.info(res)
                return res
            else:
                #Like this [{'Protocol': 'tcp', 'TargetPort': 10035, 'PublishedPort': 10035}]
                Ports.append({"Protocol": Protocol, "TargetPort": TargetPort, "PublishedPort": PublishedPort})

        baseData = {
            'Mode': {'Replicated': {'Replicas': replicas}},
            'EndpointSpec': {'Ports': Ports},
            'TaskTemplate': {'ContainerSpec': {
                                'mounts': Mounts,
                                'image': image,
                                'env': env
                            }},
            'Name': name
        }
        logger.info("Create service, the post data is %s" %baseData)

        #post data and check result
        try:
            SwarmEngineServiceCreateUrl  = Splice(ip=self.LeaderIp, port=2375, path="/services/create").geturl
            SwarmEngineServiceCreateRes  = requests.post(SwarmEngineServiceCreateUrl, timeout=self.timeout, verify=False, data=json.dumps(baseData))
            SwarmEngineServiceCreateData = SwarmEngineServiceCreateRes.json()
        except Exception,e:
            logger.error(e, exc_info=True)
            res.update(success=False, code=40010, msg="create service fail")
            logger.info(res)
            return res
        else:
            logger.info("Request url that the create services interface is %s." %SwarmEngineServiceCreateUrl)
            logger.info(SwarmEngineServiceCreateRes.text)
            serviceId = SwarmEngineServiceCreateData.get("ID", "")
            logger.info("Create service, get the serviceId is %s" %serviceId)
            if len(serviceId) == 25:
                self.Retrieve(service=serviceId, core=True)
                res.update(success=True, serviceId=serviceId)
            else:
                res.update(success=False, code=40011, msg="create service fail")

        logger.info(res)
        return res

    def Delete(self, serviceFlag):
        #delete a service

        res = {"msg": None, "code": 0}
        logger.info(serviceFlag)

        if not serviceFlag:
            res.update(msg="no service id or name<%s>" %serviceFlag, code=50100)
            logger.info(res)
            return res

        logger.info("check parameters pass")
        try:
            SwarmEngineServiceDeleteUrl  = Splice(ip=self.LeaderIp, port=2375, path="/services/%s" %serviceFlag).geturl
            SwarmEngineServiceDeleteRes  = requests.delete(SwarmEngineServiceDeleteUrl, timeout=self.timeout, verify=False)
            SwarmEngineServiceDeleteCode = SwarmEngineServiceDeleteRes.status_code
        except Exception,e:
            logger.error(e, exc_info=True)
            res.update(success=False, code=50200, msg="delete service<%s> fail" %serviceFlag)
            logger.info(res)
            return res
        else:
            logger.info("Request url that the delete services interface is %s." %SwarmEngineServiceDeleteUrl)
            logger.info(SwarmEngineServiceDeleteRes.text)
            logger.info(SwarmEngineServiceDeleteCode)
            if SwarmEngineServiceDeleteCode in (200, 204):
                res.update(success=True)
            else:
                res.update(msg="delete service<%s> fail" %serviceFlag, code=50300, success=False)

        logger.info(res)
        return res

    def Update(self, serviceFlag, **params):
        """update a service in docker swarm mode cluster with api.
        1. get, convert, check params,
        2. post data to swarm api.
        """
        res = {"msg": None, "code": 0}
        logger.info("Update service flag(id/name) is %s, other params is %s" %(serviceFlag, params))

        #check params
        if not serviceFlag:
            logger.warn("service id/name is empty")
            res.update(msg="service id/name is empty", code=50000)
            logger.info(res)
            return res

        serviceSourceData = self.Retrieve(serviceFlag, core=True, conversion=False).get("data")
        if isinstance(serviceSourceData, (list, tuple)) and len(serviceSourceData) > 0:
            serviceSourceData = serviceSourceData[0]
            serviceFlag2ID  = serviceSourceData.get("ID")
            defaultName     = serviceSourceData.get("Name")
            defaultEnv      = serviceSourceData.get("Env")
            defaultMount    = serviceSourceData.get("Mounts")
            defaultPublish  = serviceSourceData.get("NetPorts")
            defaultImage    = serviceSourceData.get("Image")
            defaultReplicas = serviceSourceData.get("Replicas")
            defaultVersion  = serviceSourceData.get("Version")
            try:
                image       = params.get("image") or defaultImage
                name        = params.get("name") or defaultName
                env         = self.commaConvert(params.get("env")) if params.get("env") else defaultEnv
                mount       = self.commaConvert(params.get("mount")) if params.get("mount") else defaultMount
                publish     = self.commaConvert(params.get("publish")) if params.get("publish") else defaultPublish
                replicas    = int(params.get("replicas")) if params.get("replicas") else defaultReplicas
                delay       = int(params.get("delay")) if params.get("delay") else 10
                parallelism = int(params.get("parallelism")) if params.get("parallelism") else 1
            except Exception,e:
                logger.warn(e, exc_info=True)
                res.update(msg="parameters error", code=50001)
                logger.info(res)
                return res
        else:
            logger.error("The service<%s> get data error, result is %s" %(serviceFlag, serviceSourceData))
            res.update(msg="The service get error", code=50007)
            logger.info(res)
            return res
        logger.info("update service after read default, will update service name is %s(%s), the request params result is %s" %(serviceFlag, serviceFlag2ID, dict(image=image, name=name, env=env, mount=mount, publish=publish, replicas=replicas, delay=delay, parallelism=parallelism)))

        #Organize the data to update the service
        if isinstance(mount, (list, tuple)):
            Mounts=[]
            for m in mount:
                if isinstance(m, dict):
                    Mounts.append(m)
                else:
                    try:
                        source, target, readonly, mountype = m.split(":")
                        readonly = True if readonly in ("true", "True", True) else False
                    except Exception, e:
                        logger.warn(e, exc_info=True)
                        res.update(msg="mount format error", code=50002)
                        logger.info(res)
                        return res
                    else:
                        #Like this [{'source': '/data/swarmopsapi-logs', 'readonly': False, 'Type': 'bind', 'target': '/SwarmOpsApi/logs'}]
                        Mounts.append({"Source": source, "Target": target, "ReadOnly": readonly, "Type": mountype})
            mount = Mounts
            logger.debug(mount)

        if isinstance(publish, (list, tuple)):
            Ports=[]
            for p in publish:
                logger.debug("publish a port data for split is %s" %p)
                if isinstance(p, dict):
                    Ports.append(p)
                else:
                    try:
                        port = p.split(":")
                        if len(port) == 2:
                            logger.debug("split port 2")
                            PublishedPort = int(port[0])
                            TargetPort    = int(port[-1])
                            Protocol      = "tcp"
                        elif len(port) == 3:
                            logger.debug("split port 3")
                            PublishedPort = int(port[0])
                            TargetPort    = int(port[1])
                            Protocol      = port[2]
                        else:
                            res.update(msg="publish format error", code=50003)
                            logger.error(p)
                            logger.info(res)
                            return res
                    except Exception,e:
                        logger.warn(e, exc_info=True)
                        res.update(msg="publish format error", code=50004)
                        logger.info(res)
                        return res
                    else:
                        #Like this [{'Protocol': 'tcp', 'TargetPort': 10035, 'PublishedPort': 10035}]
                        Ports.append({"Protocol": Protocol, "TargetPort": TargetPort, "PublishedPort": PublishedPort})
            publish = Ports
            logger.debug(publish)

        baseData = {
            'Mode': {'Replicated': {'Replicas': replicas}},
            'EndpointSpec': {'Ports': publish},
            'TaskTemplate': {'ContainerSpec': {
                                'mounts': mount,
                                'image': image,
                                'env': env
                            }},
            'UpdateConfig': {
                'Parallelism': parallelism,
                'Delay ': delay,
            },
            'Name': name,
        }
        logger.info("Update service, the post data is %s" %baseData)

        #post data to update service
        try:
            SwarmEngineServiceUpdateUrl  = Splice(ip=self.LeaderIp, port=2375, path="/services/%s/update?version=%d" %(serviceFlag2ID, defaultVersion)).geturl
            SwarmEngineServiceUpdateRes  = requests.post(SwarmEngineServiceUpdateUrl, headers={"Content-type": "application/json"}, timeout=self.timeout, verify=False, data=json.dumps(baseData))
            SwarmEngineServiceUpdateCode = SwarmEngineServiceUpdateRes.status_code
            SwarmEngineServiceUpdateData = SwarmEngineServiceUpdateRes.text or '{}'
            SwarmEngineServiceUpdateData = json.loads(SwarmEngineServiceUpdateData)
        except Exception,e:
            logger.error(e, exc_info=True)
            res.update(success=False, code=50005, msg="update service fail")
            logger.info(res)
            return res
        else:
            logger.info("Request url that the update services interface is %s" %SwarmEngineServiceUpdateUrl)
            logger.debug(type(SwarmEngineServiceUpdateData))
            logger.debug(SwarmEngineServiceUpdateCode)
            if SwarmEngineServiceUpdateCode == 200:
                res.update(success=True)
            else:
                res.update(msg="update service fail, %s" %SwarmEngineServiceUpdateData.get("message"), code=50006, success=False)

        logger.info(res)
        return res
