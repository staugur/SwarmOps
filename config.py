# -*- coding:utf8 -*-

import os

#全局配置段
GLOBAL={

    "Host": os.getenv("swarmopsapi_host", "0.0.0.0"),
    #Application run network address, you can set it `0.0.0.0`, `127.0.0.1`, ``;

    "Port": int(os.getenv("swarmopsapi_port", 10130)),
    #Application run port, default port;

    "Debug": os.getenv("swarmopsapi_debug", True),
    #The development environment is open, the production environment is closed, which is also the default configuration.

    "LogLevel": os.getenv("swarmopsapi_loglevel", "DEBUG"),
    #应用程序写日志级别，目前有DEBUG，INFO，WARNING，ERROR，CRITICAL

    "AuthSysUrl": "xxxxxxxxxxx",
    #token认证接口地址

    "putEtcd": os.getenv("swarmopsapi_putetcd", True),
    #是否开启put至etcd的线程

    "SwarmStorageMode": os.getenv("swarmopsapi_swarmstoragemode", "file")
    #存储swarm集群信息的方式，可选`file`, `etcd`, `consul`
    #file方式仅可以保存多集群信息
    #etcd方式在file功能基础上，可多点分布部署、活跃集群推送
    #consul
}

#生产环境配置段
PRODUCT={

    "IsProduction": os.getenv("swarmopsapi_isproduction", False),
    #定义是否为生产环境(暂时认为用Product.py(包括ControlDSMRun.sh)启动的均为生产，即此项为True。否则默认False)，此选项只影响swarm集群信息写入etcd，若写入file则不影响。

    "ProcessName": "SwarmOpsApi",
    #Custom process, you can see it with "ps aux|grep ProcessName".

    "ProductType": os.getenv("swarmopsapi_producttype", "tornado"),
    #生产环境启动方法，可选`gevent`, `tornado`。
}

#Swarm集群默认配置段
SWARM={
    "name": "default",
    #SWARM Name

    "type": "engine",
    #SWARM Mode，engine or cluster

    "manager": (
        "127.0.0.1",
    ),
    #SWARM Ip(worker or manager), type is list or tuple
}

#Etcd集群配置段
ETCD={
    
    "ETCD_SCHEME": "http",
    #etcd RESTfulAPI 访问协议

    "ETCD_HOST": "xxx.xxx.xxx.xxx",
    #etcd主机地址(FQDN or IP)

    "ETCD_PORT": 4001,
    #etcd主机端口

    "ETCD_VERSION": "v2",
    #etcd服务版本

    "ETCD_SWARMKEY": "/SwarmOpsApi/sys/Swarm"
}


#Ssh登陆信息配置段
SSH={
    "USERNAME": 'xxx',
    #ssh 用户名

    "PRIVATE_KEY": 'xxx',
    #ssh USERNAME配置项的用户私钥

    "PASSWD": 'xxx',
    #ssh USERNAME配置项的用户私钥的加密口令(当非密钥登录，此项为用户密码)

    "TIMEOUT": 5,
    #ssh超时时间设定
}
