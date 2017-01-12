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
}

#生产环境配置段
PRODUCT={

    "ProcessName": "SwarmOps",
    #自定义进程名称

    "ProductType": os.getenv("swarmops_producttype", "tornado"),
    #生产环境启动方法，可选`gevent`, `tornado`。
}

#认证系统配置段
SSO={

    "SSO.URL": os.getenv("swarmops_ssourl", "https://passport.saintic.com"),
    #认证系统passport的地址

    "SSO.PROJECT": PRODUCT["ProcessName"],
    #SSO请求的应用名称

    "SSO.AllowedUserList": ("admin", )
    #SSO允许登陆的用户列表
}

#存储配置段
STORAGE={

    "SwarmStorageMode": os.getenv("swarmops_swarmstoragemode", "local"),
    #存储Swarm集群信息的方式, 可选`local(本地文件存储)`, `redis`
    #使用local存储，数据将会序列化存储到logs/SwarmKey、ActiveKey文件中；
    #使用redis存储，便可以多点部署，数据将会序列化存储到redis中。

    "Connection": os.getenv("swarmops_StorageConnection", "redis://ip:port:password"),
    #当SwarmStorageMode不为local时，此配置项有意义。
    #此配置项设置存储后端的连接信息, 如redis, redis没有密码则留空:password部分

    "SwarmKey": os.getenv("swarmops_StorageSwarmKey", "Swarm_All"),
    #存储后端存储所有Swarm数据的Key索引

    "ActiveKey": os.getenv("swarmops_StorageActiveKey", "Swarm_Active"),
    #存储后端存储活跃集群数据的Key索引
}
