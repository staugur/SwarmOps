# -*- coding: utf-8 -*-
"""
    SwarmOps.config
    ~~~~~~~~~~~~~~

    The program configuration file, the preferred configuration item, reads the system environment variable first.

    :copyright: (c) 2018 by staugur.
    :license: MIT, see LICENSE for more details.
"""

from os import getenv

GLOBAL = {

    "ProcessName": "SwarmOps",
    #自定义进程名.

    "Host": getenv("swarmops_host", "0.0.0.0"),
    #监听地址

    "Port": getenv("swarmops_port", 10130),
    #监听端口

    "LogLevel": getenv("swarmops_loglevel", "DEBUG"),
    #应用日志记录级别, 依次为 DEBUG, INFO, WARNING, ERROR, CRITICAL.
}


SSO = {

    "app_name": getenv("swarmops_sso_app_name", GLOBAL["ProcessName"]),
    # Passport应用管理中注册的应用名

    "app_id": getenv("swarmops_sso_app_id", "app_id"),
    # Passport应用管理中注册返回的`app_id`

    "app_secret": getenv("swarmops_sso_app_secret", "app_secret"),
    # Passport应用管理中注册返回的`app_secret`

    "sso_server": getenv("swarmops_sso_server", "YourPassportFQDN"),
    # Passport部署允许的完全合格域名根地址，例如作者的`https://passport.saintic.com`

    "sso_allow": getenv("swarmops_sso_allow"),
    # 允许登录的uid列表，格式是: uid1,uid2,...,uidn

    "sso_deny": getenv("swarmops_sso_deny")
    # 拒绝登录的uid列表, 格式同上
}


# 系统配置
SYSTEM = {

    "HMAC_SHA256_KEY": getenv("swarmops_hmac_sha256_key", "273d32c8d797fa715190c7408ad73811"),
    # hmac sha256 key

    "AES_CBC_KEY": getenv("swarmops_aes_cbc_key", "YRRGBRYQqrV1gv5A"),
    # utils.aes_cbc.CBC类中所用加密key

    "JWT_SECRET_KEY": getenv("swarmops_jwt_secret_key", "WBlE7_#qDf2vRb@vM!Zw#lqrg@rdd3A6"),
    # utils.jwt.JWTUtil类中所用加密key
}


#存储配置段
STORAGE={

    "SwarmStorageMode": getenv("swarmops_swarmstoragemode", "local"),
    #存储Swarm集群信息的方式, 可选`local(本地文件存储)`, `redis`
    #使用local存储，数据将会序列化存储到logs/SwarmKey、ActiveKey文件中；
    #使用redis存储，便可以多点部署，数据将会序列化存储到redis中。

    "Connection": getenv("swarmops_StorageConnection", "redis://ip:port:password"),
    #当SwarmStorageMode不为local时，此配置项有意义。
    #此配置项设置存储后端的连接信息, 如redis, redis没有密码则留空:password部分

    "SwarmKey": getenv("swarmops_StorageSwarmKey", "SwarmOps_All"),
    #存储后端存储所有Swarm数据的Key索引

    "ActiveKey": getenv("swarmops_StorageActiveKey", "SwarmOps_Active"),
    #存储后端存储活跃集群数据的Key索引
}

#私有仓配置段
REGISTRY={
    "RegistryAddr": getenv("swarmops_RegistryAddr", "https://registry.saintic.com"),
    #私有仓地址, 例如https://docker.io, http://ip:port

    "RegistryVersion": getenv("swarmops_RegistryVersion", 1),
    #私有仓版本, 1、2

    "RegistryAuthentication": getenv("swarmops_RegistryAuthentication", None)
    #认证, 目前不可用
}
