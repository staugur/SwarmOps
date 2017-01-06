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


## Api Design
![Design][1]


## ChangeLog

**v0.0.1**

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



  [1]: ./misc/SwarmOpsApi.png
  [2]: ./misc/swarm.png "集群"
  [3]: ./misc/service.png "服务"
  [4]: ./misc/node.png "节点"