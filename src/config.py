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

    "SwarmStorageMode": os.getenv("swarmopsapi_swarmstoragemode", "redis")
    #存储Swarm集群信息的方式
}

#生产环境配置段
PRODUCT={

    "ProcessName": "SwarmOpsApi",
    #Custom process, you can see it with "ps aux|grep ProcessName".

    "ProductType": os.getenv("swarmopsapi_producttype"),
    #生产环境启动方法，可选`gevent`, `tornado`。
}

#REDIS配置段
REDIS={
    "Connection": os.getenv("swarmopsapi_RedisConnection", "redis://ip:port:password"),

    "SwarmKey": os.getenv("swarmopsapi_RedisSwarmKey", "Swarm_All"),

    "ActiveKey": os.getenv("swarmopsapi_RedisSwarmKey", "Swarm_Active"),
}
