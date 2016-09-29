# -*- coding:utf8 -*-
#
# Swarm集群模式接口程序。
# 封装了Swarm集群接口，组织信息并返回。
# 每一个共有类函数(除了Node基函数和功能性函数)都是一个URL接口。
# Swarm集群API类似Docker Remote Api。
#

import requests
from utils.public import logger, Ot2Bool
from random import choice
from SpliceURL import Splice

class SWARM_CLUSTER_API:


    def __init__(self, Managers):
        """
        Random read the configuration file SWARM management node information, select a management IP.
        Query SWARM cluster information (with requests or docker-py official(when version updated) module), calculated leader. 
        """

        #Check parameters.
        if not isinstance(Managers, (list, tuple)):
            errmsg = "Managers parameter error, only list or tuple is allowed."
            logger.error(errmsg)
            raise TypeError(errmsg)

        #Get `Managers` random ip for quering RESTFul Api.
        self.RandomIp  = choice(Managers)

        #Define global timeout seconds.
        self.timeout = 3

        #Get SwarmCluster Info
        try:
            SwarmClusterInfoUrl  = Splice(ip = self.RandomIp, path = "/info").geturl
            SwarmClusterInfoRes  = requests.get(SwarmClusterInfoUrl, timeout = self.timeout)
            SwarmClusterInfoData = SwarmClusterInfoRes.json() or {}
        except ImportError,e:
            logger.error(e)
        except Exception,e:
            logger.error({"SwarmClusterInfoUrl": SwarmClusterInfoUrl, "SwarmClusterInfoRes": SwarmClusterInfoRes, "SwarmClusterInfoData": SwarmClusterInfoData})
            logger.error(e, exc_info=True)
        else:
            logger.info("Swarm Cluster Manager is %s, request url that the info interface is %s." %(Managers, SwarmClusterInfoUrl))
            #Define global swarm info(now cluster), only swarm cluster, it has not SystemStatus in docker swarm(version>=1.12.0).
            self.swarminfo = SwarmClusterInfoData.get("SystemStatus")
            try:
                if self.swarminfo[0][-1] == "primary":
                    self.base  = 3
                    self.leader= self.RandomIp
                else:
                    self.base  = 4
                    self.leader= self.swarminfo[1][-1]
            except Exception,e:
                logger.error(e, exc_info=True)
                self.base  = ''
                self.leader= ''
            else:
                logger.info("Swarm Cluster Leader is %s" %self.leader)

    @property
    def Leader(self):
        return self.leader

    @property
    def Info(self):
        """ Get Swarm Cluster SystemStatus Info """
        SwarmClusterSystemInfo = self.swarminfo
        logger.debug(SwarmClusterSystemInfo)
        return SwarmClusterSystemInfo

    @property
    def Node(self):
        """This function is based on the swarm node used to obtain information."""
        res  = {"data": (), "msg": None, "code": 0}
        node = []
        base = i = self.base or ''
        systeminfo = self.Info
        if not systeminfo:
            res.update(msg = "Swarm SystemStatus Error", code = 30010)
        else:
            try:
                node_num = int(systeminfo[base][-1])
                #It should be a number, otherwise the exception should be thrown.
            except Exception,e:
                logger.error(e, exc_info=True)
                res.update(msg = "node_num(%s) get fail" %systeminfo[base][-1], code = 30020)
            else:
                while base < len(systeminfo) - i:
                    node.append((
                        systeminfo[base+1][-1],
                        systeminfo[base+2][-1],
                        systeminfo[base+3][-1],
                        systeminfo[base+4][-1],
                        systeminfo[base+5][-1],
                        systeminfo[base+6][-1],
                        systeminfo[base+7][-1],
                        systeminfo[base+8][-1],
                        systeminfo[base+9][-1],
                    ))
                    #Every nine is a node message in swarm info.
                    #format is (node_host, node_id, status, containers, cpu, mem, label, UpdatedAt, dockerversion)
                    base+=9
                if len(node) != node_num:
                    #In addition, the number of node_num should be equal to the calculated results(when node_num).
                    logger.error("length not equal, len(node)=%d, but swarm api node_num is %d" %(len(node), node_num))
                    res.update(msg="node length not equal node_num", code=30030)
                else:
                    res.update(data=node, recordsTotal=node_num, recordsFiltered=node_num)
        logger.info(res)
        return res

    def NodeQuery(self, **query):
        """Query all available nodes on the Swarm, and organize the return of the node information."""
        res = self.Node
        logger.debug("Query is %s" %query)
        if res.get("code") != 0:
            logger.error(res)
            return res
        else:
            node = res.get("data")
            try:
                start      = int(query.get("start"))
                length     = int(query.get("length"))
                orderindex = int(query.get("orderindex"))
            except (ValueError, Exception), e:
                logger.error(e, exc_info=True)
                res.update(msg="A query parameter may not be a number in start, length or order[0][column]", data=[], code=30040)
            else:
                search    = str(query.get("search"))
                ordertype = str(query.get("ordertype"))
                res["start"]           = start
                res["length"]          = length
                res["search[value]"]   = search
                res["order[0][column]"]= orderindex
                res["order[0][dir]"]   = ordertype
                if start == 0 and length == 10 and search == '' and orderindex == 0 and ordertype == "asc":
                    pass
                elif orderindex >= len(node[0]):
                    res.update(msg="order[0][column] index out of range", data=[], code=30050)
                else:
                    """
                    Analyze different parameters and return data.
                    :: Search(search[value]) the greatest priority, swarm node data in any one of the search content will be appended to the return and presentation.
                    :: The returned data need to sort(order[0][dir]), the default sort is the index 0 column in ascending order by (order[0][column]) control index.
                    :: After the search and index sorting is completed, the final data is returned through the start:start+length section.
                    """
                    if search != '':
                        node = [ n for n in node for _n in n if str(_n).find(search) >= 0 ]
                    node.sort(key=lambda x:x[orderindex], reverse=Ot2Bool(ordertype))
                    res["data"] = node[start: start + length]
            logger.info(res)
            return res

    def LabelQuery(self, **query):
        """Query Label on all available nodes of the Swarm, and organize the return of the node information."""
        res = self.Node
        logger.debug("Query is %s" %query)
        if res.get("code") != 0:
            logger.error(res)
            return res
        else:
            import re
            node = []
            pat  = re.compile(r",\s?")
            for n in res.get("data"):
                #Split label(n[6]), and compose a new dictionary(with host info). Such as [[a,b], [c,d], [e,f]], with dict.
                label_dict = dict([ label.split("=") for label in pat.split(n[6]) ])
                label_dict["host"] = n[0]
                node.append(label_dict)
                logger.debug(label_dict)
            try:
                start      = int(query.get("start"))
                length     = int(query.get("length"))
                orderindex = int(query.get("orderindex"))
            except (ValueError, Exception), e:
                logger.error(e, exc_info=True)
                res.update(msg="A query parameter may not be a number in start, length or order[0][column]", data=[], code=30060)
            else:
                search    = str(query.get("search"))
                ordertype = str(query.get("ordertype"))
                res["start"]           = start
                res["length"]          = length
                res["search[value]"]   = search
                res["order[0][column]"]= orderindex
                res["order[0][dir]"]   = ordertype
                res["data"] = node
                if start == 0 and length == 10 and search == '' and orderindex == 0 and ordertype == "asc":
                    pass
                else:
                    try:
                        if search != '':
                            node = [ n for n in node for _n in n.values() if _n.find(search) >= 0 ]
                        logger.debug("orderindex(%s), result is %s" %(orderindex, [ d.values()[orderindex] for d in node ]))
                        res["data"] = sorted(node, key=lambda d:d.values()[orderindex], reverse=Ot2Bool(ordertype))[start: start + length]
                    except Exception,e:
                        logger.error(e, exc_info=True)
                        res.update(msg="order[0][column] index out of range", data=[], code=30070)
            logger.info(res)
            return res

    def Node_for_Label(self, **query):
        """Query Swarm on one or some of the Label where the node, and organize the return of the node information."""
        res = self.Node
        logger.debug("Query is %s" %query)
        if res.get("code") != 0:
            logger.error(res)
            return res
        else:
            import re
            node = []
            pat  = re.compile(r",\s*")
            for n in res.get("data"):
                label_list = pat.split(n[6])
                label_list.insert(0, "host=%s" %n[0])
                node.append(label_list)
                logger.debug(label_list)
            try:
                start      = int(query.get("start"))
                length     = int(query.get("length"))
                orderindex = int(query.get("orderindex"))
            except (ValueError, Exception), e:
                logger.error(e, exc_info=True)
                res.update(msg="A query parameter may not be a number in start, length or order[0][column]", data=[], code=30080)
            else:
                search    = str(query.get("search"))
                ordertype = str(query.get("ordertype"))
                res["start"]           = start
                res["length"]          = length
                res["search[value]"]   = search
                res["order[0][column]"]= orderindex
                res["order[0][dir]"]   = ordertype
                res["data"] = node
                if start == 0 and length == 10 and search == '' and orderindex == 0 and ordertype == "asc":
                    pass
                else:
                    """
                    Analyze different parameters and return data.
                    :: Search(search[value]) the greatest priority, swarm node data in any one of the search content will be appended to the return and presentation.
                    :: Search content like this, "A:a,B:b" or "A:a" and so on, it's a key:value, and use multiple criteria, inclusive ",".
                    """
                    if search: #check format with re
                        new=[]
                        for Alabel in node:
                            ss = [ s for s in re.split(pat, search) if s ]
                            sl = len(ss)
                            si = 0
                            logger.debug("Start search match, search content is %s, content split length is %d, si=%d" %(ss, sl, si))
                            for s in ss:
                                s = s.replace(":", "=")
                                if s in Alabel:
                                    si+=1
                                    logger.debug("%s in Alabel, si will add 1, is %d" %(s, si))
                            if sl == si:
                                new.append(Alabel[0].split("=")[-1])
                        node=new
                        try:
                            node.sort(reverse=Ot2Bool(ordertype))
                            res["data"] = node[start: start + length]
                        except IndexError,e:
                            logger.error(e, exc_info=True)
                            res.update(msg="order[0][column] index out of range", data=[], code=30090)
                    else:
                        try:
                            node.sort(key=lambda x:x[orderindex], reverse=Ot2Bool(ordertype))
                            res["data"] = node[start: start + length]
                        except IndexError,e:
                            logger.error(e, exc_info=True)
                            res.update(msg="order[0][column] index out of range", data=[], code=30100)
            logger.info(res)
            return res
