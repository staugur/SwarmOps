# -*- coding:utf8 -*-


import docker
from utils.public import logger


class DOCKER_ENGINE_API(object):

    """
    封装所需要的docker操作指令,基于docker官方接口docker-py,支持docker socket、remote api，所以也可用来操作swarm api。
    安装: pip install docker-py
    """

    def __init__(self, url='unix:///var/run/docker.sock'):
        """url is a socket or tcp remote api, eg: tcp://127.0.0.1:2375"""
        self.docker = docker.Client(base_url=url, timeout=5)

    def Images(self, image=None):
        return self.docker.images(image)

    def Inspect(self, cid=None):
        info = self.docker.inspect_container(resource_id=cid)
        return {"StartAt": info.get("State").get("StartedAt"), "Volumes": info.get("Volumes")}

    def Containers(self, all=False):
        cs = []
        for c in self.docker.containers(all=all):
            cs.append({
            "Name":   c.get("Names")[0].split("/")[-1],
            "Cid":    c.get("Id")[:12],
            "Image":  c.get("Image"),
            "ImgaeId":c.get("ImageId").split(":")[-1][:12],
            "Status": c.get("Status"),
            #"Label":  c.get("Labels"),
            "Vomues": self.Inspect(cid=c.get("Id")).get("Volumes"),
            "StartAt":self.Inspect(cid=c.get("Id")).get("StartAt"),
            })
        logger.debug(cs)
        return cs

    def Pull(self, image):
        for line in self.docker.pull(image, stream=True):  #a generator
            print line

    def Create(self, **kwargs):
        image   = kwargs.get('image')          #container start from something image
        name    = kwargs.get('name')           #container name

        cport   = kwargs.get('port', None)     #container open port
        bind    = kwargs.get('bind', None)     #should be tuple,(host_ip,host_port), all is a dict => {container_port, (host_ip, host_port)}.

        volume  = kwargs.get('volume', None)   #host_dir, mount it in container with cvolume
        cvolume = kwargs.get('cvolume', None)  #container dir

        mode    = kwargs.get('mode', 'bridge')

        cports=None
        if cport and bind:
            #cports.append(cport)
            port_bindings={cport:bind}
        else:
            #cports=None
            port_bindings=None

        volumes=[]
        if volume and cvolume:
            volume_bindings=[ '%s:%s' % (volume, cvolume), ]  #ask list ['container_dir:host_dir:mode(rw,ro)']
            volumes.append(volume)                #Only this, more access=>https://github.com/docker/docker-py/issues/849
        else:
            volume_bindings=None

        if not image or not name:
            errmsg = "No image or name!"
            logger.error(errmsg)

        if not self.Images(image): self.Pull(image)
        cid=self.docker.create_container(image=image, name=name, stdin_open=True, tty=True, ports=cports, volumes=None, host_config=self.docker.create_host_config(restart_policy={"MaximumRetryCount": 0, "Name": "always"}, binds=volume_bindings, port_bindings=port_bindings, network_mode=mode), mem_limit=None, memswap_limit=None, cpuset=None).get('Id')[:12]
        return cid

    def Start(self, cid=None):
        r=self.docker.start(resource_id=cid)
        if r is not None:
            print "\033[0;31;40mStart failed, id => %s\033[0m" % cid