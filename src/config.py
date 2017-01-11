# -*- coding:utf8 -*-
#
# SwarmOps配置文件, 默认先读取环境变量, 格式: os.getenv("环境变量", "默认值")
#

import os

#全局配置段
GLOBAL={

    "Host": os.getenv("swarmops_host", "0.0.0.0"),
    #应用监听地址

    "Port": int(os.getenv("swarmops_port", 10130)),
    #应用监听端口

    "Debug": os.getenv("swarmops_debug", True),
    #Debug, 开发环境是True, 生产环境是False, 这是默认配置

    "LogLevel": os.getenv("swarmops_loglevel", "DEBUG"),
    #应用程序写日志级别，目前有DEBUG，INFO，WARNING，ERROR，CRITICAL

    "SwarmStorageMode": os.getenv("swarmops_swarmstoragemode", "local"),
    #存储Swarm集群信息的方式, 可选`local(本地文件存储)`, `redis`
}

#生产环境配置段
PRODUCT={

    "ProcessName": "SwarmOps",
    #自定义进程名称

    "ProductType": os.getenv("swarmops_producttype", "tornado"),
    #生产环境启动方法，可选`gevent`, `tornado`。
}

#STORAGE配置段
STORAGE={
    "Connection": os.getenv("swarmops_StorageConnection", "redis://ip:port:password"),
    #存储后端连接信息(对应`SwarmStorageMode`选项值不为local的清空),redis没有密码则留空:password部分

    "SwarmKey": os.getenv("swarmops_StorageSwarmKey", "Swarm_All"),
    #存储后端存储所有Swarm数据的Key索引

    "ActiveKey": os.getenv("swarmops_StorageActiveKey", "Swarm_Active"),
    #存储后端存储活跃集群数据的Key索引
}

SSO={

    "SSO.URL": os.getenv("swarmops_ssourl", "https://passport.saintic.com"),
    #认证系统passport的地址

    "SSO.PROJECT": PRODUCT["ProcessName"],
    #SSO请求的应用名称

    "SSO.AllowedUserList": ("admin", )
    #SSO允许登陆的用户列表
}
