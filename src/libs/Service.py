# -*- coding:utf8 -*-
#
# Docker Engine Swarm模式，版本应当不小于1.12.0，API版本应当不小于1.24，官方API文档地址是：
# https://github.com/docker/docker/blob/v1.12.0/docs/reference/api/docker_remote_api_v1.24.md
#

import requests
from SpliceURL import Splice
from utils.public import logger, Ot2Bool, ip_check, timeChange
from .Base import BASE_SWARM_ENGINE_API


class ServiceManager(BASE_SWARM_ENGINE_API):

    """
    Through the cluster swarm service interface management.
    Note: Service operations require to first be part of a Swarm.
    """

    def __init__(self, port=2375, timeout=3, ActiveSwarm={}):
        self.port      = port
        self.timeout   = timeout
        self.verify    = False
        self.swarm     = ActiveSwarm
        self.leader    = self._checkSwarmLeader(self.swarm)
        logger.info("Service Api Init, ActiveSwarm is %s, the leader is %s" %(self.swarm, self.leader))

    def GET(self, service=None, core=False, core_convert=False):

        res = {"msg": None, "code": 0, "data": []}

        if self.leader:
            ServiceUrl = Splice(netloc=self.leader, port=self.port, path="/services/%s" %service).geturl if service else Splice(netloc=self.leader, port=self.port, path="/services").geturl
            logger.info("Get service url is %s, core is %s, core_convert is %s" %(ServiceUrl, core, core_convert))

            try:
                r = requests.get(ServiceUrl, timeout=self.timeout, verify=self.verify)
                services = r.json()
            except Exception,e:
                logger.error(e, exc_info=True)
                res.update(msg="Retrieve service fail", code=30000)
            else:
                if r.status_code == 404:
                    res.update(msg="No such service<%s>" %service, data=[], code=30010)
                    logger.info(res)
                    return res
                else:
                    recordsTotal = len(services)

            services = (services,) if not isinstance(services, (list, tuple)) else services
            services_core=[]

            if core == False:
                res.update(data=services)

            elif core == True and core_convert == True:
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

            elif core == True and core_convert == False:
                try:
                    for i in services:
                        logger.debug(i)
                        services_core.append({
                            "ID":        i.get("ID"),
                            "Name":      i.get("Spec", {}).get("Name"),
                            "CreatedAt": i.get("CreatedAt"),
                            "UpdatedAt": i.get("UpdatedAt"),
                            "Labels":    i.get("Spec", {}).get("Labels"),
                            "Image":     i.get("Spec", {}).get("TaskTemplate", {}).get("ContainerSpec", {}).get("Image"),
                            "Env":       i.get("Spec", {}).get("TaskTemplate", {}).get("ContainerSpec", {}).get("Env"),
                            "Mounts":    i.get("Spec", {}).get("TaskTemplate", {}).get("ContainerSpec", {}).get("Mounts", []),
                            "Replicas":  i.get("Spec", {}).get("Mode", {}).get("Replicated", {}).get("Replicas")  or "global",
                            "NetMode":   i.get("Endpoint", {}).get("Spec", {}).get("Mode") or i.get("Spec", {}).get("EndpointSpec", {}).get("Mode"),
                            "NetPorts":  i.get("Endpoint", {}).get("Spec", {}).get("Ports"),
                            "NetVip":    i.get("Endpoint", {}).get("VirtualIPs"),
                            "Version":   i.get("Version",  {}).get("Index"),
                            "UpdateStatus": "%s(%s)" %(i.get("UpdateStatus").get("State"), i.get("UpdateStatus").get("CompletedAt")) if i.get("UpdateStatus").get("State") else None
                        })
                except Exception,e:
                    logger.error(e, exc_info=True)
                res.update(data=services_core)

            res.update(recordsTotal=recordsTotal, recordsFiltered=len(services_core))
        else:
            res.update(msg="No active swarm cluster", code=30020)

        logger.info(res)
        return res
