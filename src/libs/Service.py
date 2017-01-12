# -*- coding:utf8 -*-
#
# Docker Engine Swarm模式，版本应当不小于1.12.0，API版本应当不小于1.24，官方API文档地址是：
# https://github.com/docker/docker/blob/v1.12.0/docs/reference/api/docker_remote_api_v1.24.md
#

import requests, json, re
from SpliceURL import Splice
from utils.public import logger, Ot2Bool, ip_check, timeChange, comma_Pat
from .Base import BASE_SWARM_ENGINE_API


class ServiceManager(BASE_SWARM_ENGINE_API):

    """
    Through the cluster swarm service interface management.
    Note: Service operations require to first be part of a Swarm.
    """

    def __init__(self, port=2375, timeout=2, ActiveSwarm={}):
        self.port      = port
        self.verify    = False
        self.timeout   = timeout
        self.swarm     = ActiveSwarm
        self.leader    = self._checkSwarmLeader(self.swarm) if self.swarm != {} else None
        self.commaConvert = lambda string:[ l for l in re.split(comma_Pat, string) if l ]
        logger.info("Service Api Init, ActiveSwarm is %s, the leader is %s" %(self.swarm, self.leader))

    def GET(self, service=None, core=False, core_convert=False):

        res = {"msg": None, "code": 0, "data": ()}

        if self.leader:
            ServiceUrl = Splice(netloc=self.leader, port=self.port, path="/services/%s" %service).geturl if service else Splice(netloc=self.leader, port=self.port, path="/services").geturl
            logger.info("Get service url is %s, core is %s, core_convert is %s" %(ServiceUrl, core, core_convert))

            try:
                r = requests.get(ServiceUrl, timeout=self.timeout, verify=self.verify)
                services = r.json()
                services = services if isinstance(services, (list, tuple)) else (services,)
                services_core = []
            except Exception,e:
                logger.error(e, exc_info=True)
                res.update(msg="Retrieve service fail", code=30000)
            else:
                if r.status_code == 404:
                    res.update(msg="No such service<%s>" %service, data=[], code=30010)
                    logger.info(res)
                    return res
                elif core == False:
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
                                _i_Mounts.append("%s:%s:%s:%s" %(_.get("Source"), _.get("Target"), _.get("ReadOnly", ""), _.get("Type", "")))
                            i_Mounts    = _i_Mounts
                            #### end convert mount
                            i_Replicas  = "global" if "Global" in i.get("Spec", {}).get("Mode", {}) else i.get("Spec", {}).get("Mode", {}).get("Replicated", {}).get("Replicas")
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
                    else:
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
                    else:
                        res.update(data=services_core)
        else:
            res.update(msg="No active swarm cluster", code=30020)

        logger.info(res)
        return res

    def GetServiceNode(self, serviceId, getBackend=False):
        """ 查询某service(ID)正在运行的实例数所在node(IP), 并且生成nginx配置样例 """

        res = {"msg": None, "code": 0}

        if self.leader:
            data = self._checkServiceTaskNode(leader=self.leader, serviceId=serviceId)
            if getBackend in ("true", "True", True):
                serviceData    = self.GET(service=serviceId, core=True, core_convert=True)["data"][0]
                upstreamName   = "{}_{}".format(serviceData["Name"], serviceId)
                upstreamServer = ""
                upstreamMisc   = []
                for ip in data["ips"]:
                    for port in serviceData["NetPorts"]:
                        if port:
                            port = port.split(':')[0]
                            entry= "{}:{}".format(ip, port)
                            upstreamMisc.append(entry)
                            upstreamServer += "server {};\n".format(entry)
                NginxExampleForManager = """upstream %s {
%s
}
server {
    listen 80;
    server_name your.domain.com;
    charset utf8;
    location / {
        proxy_pass http://%s;
        proxy_set_header X-Forwared-For $proxy_add_x_forwarded_for ;
        proxy_set_header Host $http_host ;
        proxy_set_header X-Real-IP  $remote_addr;
        proxy_set_header X-Forwarded-For $remote_addr;
    }
}
""" %(upstreamName, upstreamServer.strip(), upstreamName)
                logger.info("GetServiceNode and getBackend, serviceId is {}, generate nginx example is {}".format(serviceId, NginxExampleForManager))
                data.update(nginx=NginxExampleForManager, misc=upstreamMisc)
            res.update(data=data)
        else:
            res.update(msg="No active swarm cluster", code=30021)

        logger.info(res)
        return res

    def POST(self, image, **params):
        """
        Create a service in docker swarm mode cluster with api.
        1. get, convert, check params,
        2. post data to swarm api.
        """
        res = {"msg": None, "code": 0}
        logger.info("Create service, the required image is %s" %image)

        #check leader
        if not self.leader:
            res.update(msg="No active swarm", code=-1000)
            logger.info(res)
            return res

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
            replicas = int(params.get("replicas", 1))
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
                mountype = mountype or "bind"
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
            SwarmEngineServiceCreateUrl  = Splice(netloc=self.leader, port=self.port, path="/services/create").geturl
            SwarmEngineServiceCreateRes  = requests.post(SwarmEngineServiceCreateUrl, timeout=self.timeout, verify=self.verify, data=json.dumps(baseData))
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
                self.GET(service=serviceId, core=True)
                res.update(success=True, serviceId=serviceId)
            else:
                res.update(success=False, code=40011, msg="create service fail")

        logger.info(res)
        return res

    def DELETE(self, serviceFlag):
        #delete a service

        res = {"msg": None, "code": 0}
        logger.info(serviceFlag)

        if not self.leader:
            res.update(msg="No active swarm", code=-1000)
            logger.info(res)
            return res

        if not serviceFlag:
            res.update(msg="no service id or name<%s>" %serviceFlag, code=50100)
            logger.info(res)
            return res

        logger.info("delete service, check parameters pass")
        try:
            SwarmEngineServiceDeleteUrl  = Splice(netloc=self.leader, port=self.port, path="/services/%s" %serviceFlag).geturl
            SwarmEngineServiceDeleteRes  = requests.delete(SwarmEngineServiceDeleteUrl, timeout=self.timeout, verify=self.verify)
            SwarmEngineServiceDeleteCode = SwarmEngineServiceDeleteRes.status_code
        except Exception,e:
            logger.error(e, exc_info=True)
            res.update(success=False, code=50200, msg="delete service<%s> fail" %serviceFlag)
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

    def PUT(self, serviceFlag, **params):
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

        #check leader
        if not self.leader:
            res.update(msg="No active swarm", code=-1000)
            logger.info(res)
            return res

        serviceSourceData = self.GET(service=serviceFlag, core=True).get("data")
        logger.debug(serviceSourceData)
        if isinstance(serviceSourceData, (list, tuple)) and len(serviceSourceData) > 0:
            serviceSourceData = serviceSourceData[0]
            serviceFlag2ID  = serviceSourceData.get("ID")
            defaultVersion  = serviceSourceData.get("Version")
            try:
                image       = params.get("image")
                name        = params.get("name")
                env         = self.commaConvert(params.get("env"))
                mount       = self.commaConvert(params.get("mount"))
                publish     = self.commaConvert(params.get("publish"))
                replicas    = int(params.get("replicas"))
                delay       = int(params.get("delay", 10))
                parallelism = int(params.get("parallelism", 1))
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
                        mountype = mountype or "bind"
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
            SwarmEngineServiceUpdateUrl  = Splice(netloc=self.leader, port=self.port, path="/services/%s/update?version=%d" %(serviceFlag2ID, defaultVersion)).geturl
            SwarmEngineServiceUpdateRes  = requests.post(SwarmEngineServiceUpdateUrl, headers={"Content-type": "application/json"}, timeout=self.timeout, verify=self.verify, data=json.dumps(baseData))
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

