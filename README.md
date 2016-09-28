# SwarmOpsApi
Operation of swarm cluster, providing an intermediate layer application of API interface.Source from the company's docker management needs, modify the open part of the public, and now open source out.


## LICENSE
MIT


## Environment
> 1. Python Version: 2.6, 2.7
> 2. Web Framework: Flask, Flask-RESTful
> 3. Required Modules:

```
Flask            基础WEB框架
Flask-RESTful    基础WEB框架构建RESTful HTTP API扩展
tornado          生产环境启动方式, WSGI
gevent           生产环境启动方式, WSGI
setproctitle     LinuxOS设定进程
SpliceURL        URL拼接分割叠加模块
docker-py        docker for python模块
requests         URL请求处理模块
paramiko         SSH登陆模块
```


## Usage

```
1. Requirement:
    1.0 yum install -y gcc gcc-c++ python-devel libffi-devel openssl-devel
    1.1 pip install -r requirements.txt
    2.2 etcd(if putEtcd=True, SwarmStorageMode=etcd(config.GLOBAL))
    2.3 Login Auth Server(AuthSysUrl(config.GLOBAL))
    
2. modify config.py or add environment variables(os.getenv key in the reference configuration item):

3. run:
    3.1 python main.py        #开发模式
    3.2 sh ControlDSMRun.sh   #生产模式
    3.3 python -O Product.py  #生产模式，3.2中方式实际调用此脚本
    3.4 python super_debug.py #性能分析模式
```


## Usage for Docker

```
   cd misc ; docker build -t alpine:gcc .
   cd .. ;   docker build -t swarmopsapi .
   docker run -tdi --name swarmopsapi --net=host --always=restart swarmopsapi
   ps aux|grep SwarmOpsApi //watch the process
```


## Front Usage

> 1. With SwarmOpsFront(Will be open source in the future)

> 2. With Jenkins(See misc/jenkins/)


## Design
![Design][1]


[1]: ./misc/SwarmOpsApi.png