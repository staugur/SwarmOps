# -*- coding:utf8 -*-
#
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
