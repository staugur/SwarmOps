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
