# SwarmOps
Operation of swarm cluster, providing an intermediate layer application of API interface and UI.


## LICENSE
MIT


## Environment
> 1. Python Version: 2.7
> 2. Web Framework: Flask, Flask-RESTful
> 3. Required Modules: requirements.txt


## Usage

```
1. Requirement:
    1.0 yum install -y gcc gcc-c++ python-devel libffi-devel openssl-devel
    1.1 pip install -r requirements.txt
    
2. modify config.py or add environment variables(os.getenv key in the reference configuration item):

3. run:
    3.1 python main.py        #开发模式
    3.2 sh Control.sh         #生产模式
    3.3 python -O Product.py  #生产模式，3.2中方式实际调用此脚本
    3.4 python super_debug.py #性能分析模式
```


## Usage for Docker

```
   cd misc ; docker build -t alpine:gcc .
   cd .. ;   docker build -t swarmops .
   docker run -tdi --name swarmops --net=host --always=restart swarmops
   ps aux|grep SwarmOps //watch the process
```


## UI
![Swarms][2]
![Services][3]
![Nodes][4]
![Storages][5]
![Nginx][6]


## Api Design
![Design][1]


## ChangeLog

**v0.0.1-rc1**

> 0. SwarmOps Api、UI
> 1. 集群查询、添加、删除与设置活跃集群
> 2. 活跃集群的服务查询、添加、删除、更新
> 3. 活跃集群的节点查询
> 4. Swarm集群查询健康状态、Leader等
> 5. Swarm集群添加设置name和ip
> 6. Swarm集群内删除
> 7. Swarm活跃集群(关于服务、节点的操作均建立在当前活跃集群上)
> 8. Service查询Image、Env、Replicas(实例所在节点)、Vip等
> 9. Service添加、更新(查询已存在数据填充更新)
> 10. Service服务内删除
> 11. Node查询
> 12. 存储后端UI

**v0.0.1-rc2**
> 0. 调整403返回
> 1. Swarm数据存储方式增加本地存储
> 2. 修复manager降级后健康检查的bug
> 3. 修复无法更新集群的bug，UI增加更新集群按钮
> 4. 删除功能采用Jquery chosen plugin选择多项
> 5. 修复更新时读取默认配置的逻辑错误
> 6. UI展现服务的replicas, 增加url显示
> 7. 增加初始化Swarm集群功能按钮
> 8. 增加节点加入集群的功能(并自动更新一条节点label)
> 9. 增加更新节点(Role、Labels)的功能

**v0.0.1**
> 1. SSO登录设置允许的登录列表
> 2. 服务的Nginx配置样例生成
> 3. 添加操作增加disable submit防止重复提交


## Release Note

*Release 0.0.1*

作为第一个正式发布版本，SwarmOps实现了对Docker Swarm模式的集群管理。

```
1. UI/API可以初始化、管理多个Swarm集群
2. UI/API可以增删查服务
3. UI/API可以增删查改节点
4. UI/API可以查询服务的其他属性, 例如replicas节点，并生成Nginx样例配置
5. 数据持久化存储local或redis, 使用redis可以多点部署
```


  [1]: ./misc/SwarmOpsApi.png
  [2]: ./misc/swarm.png "集群"
  [3]: ./misc/service.png "服务"
  [4]: ./misc/node.png "节点"
  [5]: ./misc/storage.png "存储"
  [6]: ./misc/nginx.png "Nginx配置样例"