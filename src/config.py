# -*- coding:utf8 -*-

import os

#全局配置段
GLOBAL={

    "Host": os.getenv("swarmops_host", "0.0.0.0"),
    #Application run network address, you can set it `0.0.0.0`, `127.0.0.1`, ``;

    "Port": int(os.getenv("swarmops_port", 10130)),
    #Application run port, default port;

    "Debug": os.getenv("swarmops_debug", True),
    #The development environment is open, the production environment is closed, which is also the default configuration.

    "LogLevel": os.getenv("swarmops_loglevel", "DEBUG"),
    #应用程序写日志级别，目前有DEBUG，INFO，WARNING，ERROR，CRITICAL

    "SwarmStorageMode": os.getenv("swarmops_swarmstoragemode", "redis")
    #存储Swarm集群信息的方式
}

#生产环境配置段
PRODUCT={

    "ProcessName": "SwarmOps",
    #Custom process, you can see it with "ps aux|grep ProcessName".

    "ProductType": os.getenv("swarmops_producttype", "tornado"),
    #生产环境启动方法，可选`gevent`, `tornado`。
}

#REDIS配置段
REDIS={
    "Connection": os.getenv("swarmops_RedisConnection", "redis://ip:port:password"),

    "SwarmKey": os.getenv("swarmops_RedisSwarmKey", "Swarm_All"),

    "ActiveKey": os.getenv("swarmops_RedisActiveKey", "Swarm_Active"),
}
