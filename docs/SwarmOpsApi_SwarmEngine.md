## **SwarmOps Api Document for Swarm Engine**

* 动作类接口通常返回success=True/False, 数据类接口通常返回data *

----------



### 1.节点接口

**查询Swarm上所有可用节点，并组织好节点信息返回。**
*说明：必须在cookies中传入username和Esessionid。*

1.1 URL
http://127.0.0.1:10030/node/

1.2 请求方式
GET, POST, DELETE, PUT

1.3 是否需要登录
请求需要cookies

1.4 参数(查询参数(参数类型:含义)

*GET方法query参数*

start(int)：起始长度，
length(int)：结果长度，
search[value](str) 或 search(str)：搜索内容，在所有数据值中符合搜索的内容,
order[0][column](int)：默认排序列,表示哪一列需要排序,
order[0][dir](str)：排序方式，升序(asc，默认)，降序(desc)。

*POST方法data参数*

ip(str):   加入Swarm集群的节点IPv4地址，
role(str): 节点作为什么角色加入Swarm集群，只有两个值，worker和manaager，默认值worker。

*DELETE方法data参数*

ip(str):   从Swarm集群中要删除的节点IPv4地址，
flag(str): 从Swarm集群中要删除的节点ID或节点hostname，
force(bool): 是否强制删除，默认值False。

*PUT方法data参数*

**kwargs(dict):  dict参数，其中node(str)是必须参数，指定swarm集群中节点HOSTNAME或者ID，其他key/value均为label。

1.5 返回值与错误代码（错误代码:含义）
10000	查询参数类型错误
10001	查询参数order[0][column]超出索引错误

20000   添加节点成功，但更新节点label时错误
20001   查询参数role值错误
20002   节点执行leave出错
20003   节点仍存在，删除失败
20004   删除的节点是leader，不允许

1.5.1 GET返回数据如下格式(data中表示的信息依次为node_host, node_id, role, status, availability, containers, cpu, mem, label, UpdatedAt, dockerversion)：
```
{
    "code": 0,
    "data": [
        [
            "101.254.242.25",
            "1gfj0rqyv9vx9wnlutuym6jem",
            "manager",
            "ready",
            "active",
            5,
            6,
            13,
            "ipaddr:101.254.242.25",
            "2016-08-25 06:59:43",
            "1.12.0"
        ],
        [
            "101.254.242.23",
            "62o607vmdyx2qc3cqeq9thvwx",
            "manager",
            "ready",
            "active",
            8,
            6,
            13,
            "ipaddr:101.254.242.23",
            "2016-08-25 06:59:43",
            "1.12.0"
        ],
        [
            "101.254.242.24",
            "6736ulu3u905jmn2lw70djzbi",
            "manager",
            "ready",
            "active",
            6,
            6,
            13,
            "ipaddr:101.254.242.24",
            "2016-08-25 06:59:43",
            "1.12.0"
        ],
        [
            "101.254.242.42",
            "bvkm1drcclyk2entqtg0hr215",
            "manager",
            "ready",
            "active",
            6,
            6,
            13,
            "ipaddr:101.254.242.42",
            "2016-08-25 06:59:43",
            "1.12.0"
        ],
        [
            "101.254.242.22",
            "cssrqfw548x313qyh896rv8wy",
            "worker",
            "ready",
            "active",
            10,
            6,
            13,
            "ipaddr:101.254.242.22",
            "2016-08-31 15:37:47",
            "1.12.0"
        ],
        [
            "101.254.242.43",
            "ehexaq4sp4d9yvfwftbxodzbo",
            "Leader",
            "ready",
            "active",
            5,
            6,
            13,
            "ipaddr:101.254.242.43",
            "2016-08-25 06:59:43",
            "1.12.0"
        ]
    ],
    "length": 10,
    "msg": null,
    "order[0][column]": 0,
    "order[0][dir]": "asc",
    "recordsFiltered": 6,
    "recordsTotal": 6,
    "search[value]": "",
    "start": 0
}
```

1.5.2 POST返回数据如下格式(仅当success为True时代表添加节点成功)：
```
{
    "code": 0,
    "msg": null,
    "success": true
}
```

1.5.3 DELETE返回数据如下格式(仅当success为True时代表删除节点成功)
```
{
    "code": 0,
    "msg": null,
    "success": false
}
```

1.5.4 PUT返回数据如下格式(仅当success为True时代表更新节点成功)：
```
{
    "code": 0,
    "msg": null,
    "success": true
}
```

1.6 搜索示例
* docs/examples/node.md *




### 2.标签接口

**查询Swarm上所有可用节点的Label，并组织好节点信息返回。**
*说明：必须在cookies中传入username和Esessionid。*

2.1 URL
http://127.0.0.1:10030/label/

2.2 请求方式
GET

2.3 是否需要登录
请求需要cookies

2.4参数(查询参数(参数类型):含义)
start(int)：起始长度，
length(int)：结果长度，
search[value](str) 或 search：搜索内容，在所有数据值中符合搜索的内容,
order[0][column](int)：默认排序列,表示哪一列需要排序,
order[0][dir](str)：排序方式，升序(asc，默认)，降序(desc)。

2.5 返回值与错误代码（错误代码:含义）
10002	查询参数类型错误
10003	查询参数order[0][column]超出索引错误
返回数据如下格式(data返回中每个节点额外包含了节点的Ip或Hostname或NodeId信息以判断节点归属，并非节点的Label)：
```
{
    "code": 0,
    "data": [
        {
            "Hostname": "yz-mbg-017214",
            "IDC": "yz",
            "NodeId": "4821e53tqyv51jd360x5f7qln"
        },
        {
            "Hostname": "yz-mbg-017216",
            "IDC": "yz",
            "NodeId": "asjizqbfmdzja5h8mo0s798fx"
        },
        {
            "Hostname": "host215",
            "IDC": "yz",
            "NodeId": "atlabppl7gjsws1kbjqqcs6nc",
            "dev": "true"
        },
        {
            "Hostname": "yz-mbg-017217",
            "IDC": "yz",
            "NodeId": "cuz0lcdup3slzu0v3egqz5lgr"
        },
        {
            "Hostname": "yz-mbg-017212",
            "IDC": "yz",
            "NodeId": "d8sqce5vu0umtshekj1ngjvis",
            "environment": "gray"
        }
    ],
    "length": 10,
    "msg": null,
    "order[0][column]": 0,
    "order[0][dir]": "asc",
    "recordsFiltered": 5,
    "recordsTotal": 5,
    "search[value]": "",
    "start": 0
}
```



### 3.标签查询节点接口

**查询Swarm上某个或某些Label所在的节点，并组织好节点信息返回。**
*说明：必须在cookies中传入username和Esessionid。*

3.1 URL
http://127.0.0.1:10030/node_for_label/

3.2 请求方式
GET

3.3 是否需要登录
请求需要cookies

3.4参数(查询参数(参数类型):含义)
start(int)：起始长度，
length(int)：结果长度，
search[value](str) 或 search(str)：搜索内容，在所有数据值中符合搜索的内容,搜索格式为A:a,B:b，例如environment:product,service:mysql，
order[0][column](int)：默认排序列,表示哪一列需要排序,
order[0][dir](str)：排序方式，升序(asc，默认)，降序(desc)。

3.5 返回值与错误代码（错误代码:含义）
10004	查询参数类型错误
10005 查询参数order[0][column]超出索引错误
10006	查询参数order[0][column]超出索引错误
返回数据格式如下(data返回中每个节点额外包含了节点的Ip或Hostname或NodeId信息以判断节点归属，并非节点的Label，同Label接口)：
```
{
    "code": 0,
    "data": [
        [
            "Hostname=yzdmp006069",
            "NodeId=3innkae9cwzu4pf21i3qve3dv"
        ],
        [
            "Hostname=yz-mbg-017214",
            "NodeId=4821e53tqyv51jd360x5f7qln",
            "IDC=yz"
        ],
        [
            "Hostname=yz-mbg-017216",
            "NodeId=asjizqbfmdzja5h8mo0s798fx",
            "IDC=yz"
        ],
        [
            "Hostname=host215",
            "NodeId=atlabppl7gjsws1kbjqqcs6nc",
            "IDC=yz",
            "dev=true"
        ],
        [
            "Hostname=yz-mbg-017217",
            "NodeId=cuz0lcdup3slzu0v3egqz5lgr",
            "IDC=yz"
        ],
        [
            "Hostname=yz-mbg-017212",
            "NodeId=d8sqce5vu0umtshekj1ngjvis",
            "environment=gray",
            "IDC=yz"
        ]
    ],
    "length": 10,
    "msg": null,
    "order[0][column]": 0,
    "order[0][dir]": "asc",
    "recordsFiltered": 6,
    "recordsTotal": 6,
    "search[value]": "",
    "start": 0
}
```



### 4.服务管理接口

**CURL/增删查改 SWARM集群的services**
*说明：必须在cookies中传入username和Esessionid。*

4.1 URL
http://127.0.0.1:10030/service/
http://127.0.0.1:10030/services/

4.2 请求方式
GET,POST,PUT,DELETE

4.3 是否需要登录
请求需要cookies

4.4 参数(查询参数(参数类型:含义)

*GET方法query参数*

core(bool):    当为真时，返回services简要信息。
id/name(str):  此参数即services的Id或Name，查询某个services。
convert(bool): 表示是否需要转化为易读模式，默认True。


*POST方法data参数*

image(str):     镜像，必需参数。
name(str):      服务名称。
env(str):       环境变量，格式是"key=value, key2=value2"。
mount(str):     挂载，格式是src:dst:true|false:mode，其中true|false代表是否只读，默认false，即可读写。
publish(str):   端口映射，格式是"src:desc:protocol, src2:desc2"，protocol协议默认是tcp。
replicas(int):  实例数

*POST参数样例*
env="swarmopsapi_port=10031, swarmopsapi_loglevel=ERROR"
mount="/data/swarmopsapi-logs:/SwarmOpsApi/logs:true:bind, /data/cmlogs:/data/cmdata/logs:false:bind"
publish="10031:10031"

*更多实际样例可参考docs/examples/service.md*


*PUT方法data参数*

与POST方法一致外，多一个flag标识，即:
flag/serviceId/serviceName: 服务的Name或Id


*DELETE参考样例*

flag/serviceId/serviceName/id/name: 服务的Name或Id


4.5 返回值与错误代码（错误代码:含义）
30000: 读取services接口数据错误
30010: service不存在，读取数据错误

40000: POST data 参数错误
40001: replicas不是整数
40002: image不存在
40003: env参数错误
40004: mount参数错误
40005: publish参数错误
40006: replicas不是整数
40007: mount参数错误导致格式化错误
40008: publish参数错误导致格式化错误
40009: publish参数错误导致格式化错误
40010: 服务创建失败
40011: 服务创建失败

50100: swarm集群中不存在这个service的id或name
50200: 服务删除失败
50300: 服务删除失败

50000: 服务id/name为空
50001: PUT的参数错误
50002: mount参数错误
50003: publish参数错误
50004: publish参数错误
50005: 更新服务失败，请求时异常
50006: 更新服务失败，请求结果异常
50007: 标识flag的服务获取数据出错，swarm集群没有这个服务


4.5.1 GET返回数据如下格式
```
{
  "msg": null,
  "code": 0,
  "data": [
    {
      "Endpoint": {
        "VirtualIPs": [
          {
            "NetworkID": "3t0zqgctjl5vvgsh7on38hrp4",
            "Addr": "10.255.0.4/16"
          }
        ],
        "Spec": {
          "Mode": "vip",
          "Ports": [
            {
              "TargetPort": 13180,
              "PublishedPort": 13182,
              "Protocol": "tcp"
            }
          ]
        },
        "Ports": [
          {
            "TargetPort": 13180,
            "PublishedPort": 13182,
            "Protocol": "tcp"
          }
        ]
      },
      "ID": "bnzhi6ot0fk2ro4muvpas9pjc",
      "Version": {
        "Index": 1762
      },
      "UpdatedAt": "2016-08-17T09:01:46.163334089Z",
      "UpdateStatus": {
        "StartedAt": "0001-01-01T00:00:00Z",
        "CompletedAt": "0001-01-01T00:00:00Z"
      },
      "Spec": {
        "Mode": {
          "Replicated": {
            "Replicas": 3
          }
        },
        "EndpointSpec": {
          "Mode": "vip",
          "Ports": [
            {
              "TargetPort": 13180,
              "PublishedPort": 13182,
              "Protocol": "tcp"
            }
          ]
        },
        "Name": "yigao-cm-13182",
        "TaskTemplate": {
          "ContainerSpec": {
            "Mounts": [
              {
                "Source": "/data/java",
                "Type": "bind",
                "Target": "/data/java"
              },
              {
                "Source": "/data/yigao/cm",
                "Type": "bind",
                "Target": "/data/yigao-cm"
              }
            ],
            "Image": "docker.emarbox.com/release/yigao-cookiematch:20160805-srcV23056-dokV1555"
          }
        }
      },
      "CreatedAt": "2016-08-17T09:01:46.046895981Z"
    },
    {
      "Endpoint": {
        "VirtualIPs": [
          {
            "NetworkID": "3t0zqgctjl5vvgsh7on38hrp4",
            "Addr": "10.255.0.4/16"
          }
        ],
        "Spec": {
          "Mode": "vip",
          "Ports": [
            {
              "TargetPort": 13180,
              "PublishedPort": 13181,
              "Protocol": "tcp"
            }
          ]
        },
        "Ports": [
          {
            "TargetPort": 13180,
            "PublishedPort": 13181,
            "Protocol": "tcp"
          }
        ]
      },
      "ID": "db8i2pwpk7apxfowpnkkulhy6",
      "Version": {
        "Index": 1753
      },
      "UpdatedAt": "2016-08-17T08:52:41.499131354Z",
      "UpdateStatus": {
        "StartedAt": "0001-01-01T00:00:00Z",
        "CompletedAt": "0001-01-01T00:00:00Z"
      },
      "Spec": {
        "Mode": {
          "Replicated": {
            "Replicas": 1
          }
        },
        "EndpointSpec": {
          "Mode": "vip",
          "Ports": [
            {
              "TargetPort": 13180,
              "PublishedPort": 13181,
              "Protocol": "tcp"
            }
          ]
        },
        "Name": "yigao-cm-13181",
        "TaskTemplate": {
          "ContainerSpec": {
            "Mounts": [
              {
                "Source": "/data/java",
                "Type": "bind",
                "Target": "/data/java"
              },
              {
                "Source": "/data/yigao/cm",
                "Type": "bind",
                "Target": "/data/yigao-cm"
              }
            ],
            "Image": "docker.emarbox.com/release/yigao-cookiematch:20160805-srcV23056-dokV1555",
            "Env": [
              "swarmopsapi_port=10036"
            ]
          }
        }
      },
      "CreatedAt": "2016-08-17T08:52:41.442185237Z"
    },
    {
      "Endpoint": {
        "VirtualIPs": [
          {
            "NetworkID": "3t0zqgctjl5vvgsh7on38hrp4",
            "Addr": "10.255.0.4/16"
          }
        ],
        "Spec": {
          "Mode": "vip",
          "Ports": [
            {
              "TargetPort": 10036,
              "PublishedPort": 10036,
              "Protocol": "tcp"
            }
          ]
        },
        "Ports": [
          {
            "TargetPort": 10036,
            "PublishedPort": 10036,
            "Protocol": "tcp"
          }
        ]
      },
      "ID": "f1dmdzagsrziwjvqofhlb6xs1",
      "Version": {
        "Index": 1743
      },
      "UpdatedAt": "2016-08-17T08:40:59.041462415Z",
      "UpdateStatus": {
        "StartedAt": "0001-01-01T00:00:00Z",
        "CompletedAt": "0001-01-01T00:00:00Z"
      },
      "Spec": {
        "Mode": {
          "Replicated": {
            "Replicas": 1
          }
        },
        "EndpointSpec": {
          "Mode": "vip",
          "Ports": [
            {
              "TargetPort": 10036,
              "PublishedPort": 10036,
              "Protocol": "tcp"
            }
          ]
        },
        "Name": "swarmopsapi-10036",
        "TaskTemplate": {
          "ContainerSpec": {
            "Mounts": [
              {
                "Source": "/data/swarmopsapi-10036",
                "Type": "bind",
                "Target": "/SwarmOpsApi/logs"
              }
            ],
            "Image": "docker.emarbox.com/release/swarmopsapi",
            "Env": [
              "swarmopsapi_port=10036"
            ]
          }
        }
      },
      "CreatedAt": "2016-08-17T08:40:58.939792532Z"
    }
  ]
}
```

4.5.2 POST返回数据如下格式(success为真是创建成功)
```
{u'msg': None, u'code': 0, u'success': True}
```

4.5.3 DELETE返回数据如下格式(success为真是创建成功)
```
{u'msg': None, u'code': 0, u'success': True}
```



### 5.SWARM管理接口

**CURL/增删查改 SWARM集群信息，默认集群配置在config.py中，允许添加swarm集群，添加完后默认集群为刚添加的集群。**
*说明：必须在cookies中传入username和Esessionid。*

5.1 URL
http://127.0.0.1:10030/swarm/

5.2 请求方式
GET,POST,PUT,DELETE

5.3 是否需要登录
请求需要cookies

5.4 参数(查询参数(参数类型:含义)

*GET方法query参数*

get(str):  查询get值的swarm集群信息。

*get值有几个保留字*

> default:   返回系统默认swarm集群信息
> active:    返回系统当前活跃的swarm集群信息
> all:       返回系统所有swarm集群信息
> method:    返回系统当前定义的swarm集群存储方式
> leader:    返回系统中当前活跃集群的leader
> 其他值均认为是获取此值所在的name集群


*POST方法data参数*

name(str):       集群名称。
type(str):       集群类型，支持cluster或engine。
ip/manager(str): 集群任意IP(manager or worker)，形如"ip1, ip2, ipn......"

*更多实际样例可参考docs/examples/swarm.md*


*PUT方法query/data参数*
** 目前仅支持更新 当前活跃集群 **
** ！！！注意！！！ **
** 仅仅使用此接口更改活跃集群，所有操作均基于活跃集群 **

setActive(bool):  布尔值，当为真时，表示要设置当前活跃集群
name(str):        与setActive同用，表示要设置哪个集群为当前活跃集群

*更多实际样例可参考docs/examples/swarm.md*


*DELETE方法query/data参数*

name(str): 将删除的swarm集群名称

*更多实际样例可参考docs/examples/swarm.md*


5.5 返回值与错误代码（错误代码:含义）
-1000: GET查询是get参数错误，可能为str、unicode类型
-1020: POST时，name参数，已存在于swarm集群
-1021: manager IP存在访问异常
-1022: 参数值错误
-1031: DELETE时，name为系统保留关键字
-1030: DELETE时，名为name的swarm集群不存在
-1010: PUT更新时，参数不正确或名为name的集群不存在

5.6 返回示例

5.6.1 获取当前活跃集群
```
curl -sL --cookie 'username=taochengwei;Esessionid=8a3f96bdcc8022afbbb137ac36c6c0e84754202b' http://127.0.0.1:10030/swarm/?get=active
{
    "code": 0, 
    "data": {
        "manager": [
            "106.38.251.206", 
            "106.38.251.207"
        ], 
        "managerToken": "SWMTKN-1-2n96dz2nuj6661zbm1udphldolx0mvcpnv1wairil83ejqa217-3n1sioyu7z7adrnqo2rofdhqo", 
        "name": "yzSwarm", 
        "type": "engine", 
        "workerToken": "SWMTKN-1-2n96dz2nuj6661zbm1udphldolx0mvcpnv1wairil83ejqa217-bxv1n748g643a7v6eb7b3myd5"
    }, 
    "msg": null
}
```

5.6.2 获取默认集群
```
curl -sL --cookie 'username=taochengwei;Esessionid=8a3f96bdcc8022afbbb137ac36c6c0e84754202b' http://127.0.0.1:10030/swarm/?get=default
{
    "code": 0, 
    "data": {
        "manager": [
            "101.254.242.23"
        ], 
        "managerToken": "SWMTKN-1-3wvqcj41bvehpbqlokndycgm2vw74u4jo3leg1731mmms146fm-2jdxb9itdakfbhpd2d6l8v9zp", 
        "name": "default", 
        "type": "engine", 
        "workerToken": "SWMTKN-1-3wvqcj41bvehpbqlokndycgm2vw74u4jo3leg1731mmms146fm-9hbphmx7az0hul1v1jnrkzsnc"
    }, 
    "msg": null
}
```

5.6.3 添加一个swarm集群
```
>>> import requests, json
>>> url = 'http://127.0.0.1:10030/swarm/'
>>> data
{'managerToken': 'SWMTKN-1-2n96dz2nuj6661zbm1udphldolx0mvcpnv1wairil83ejqa217-3n1sioyu7z7adrnqo2rofdhqo', 'manager': '106.38.251.206, 106.38.251.207', 'workerToken': 'SWMTKN-1-2n96dz2nuj6661zbm1udphldolx0mvcpnv1wairil83ejqa217-bxv1n748g643a7v6eb7b3myd5', 'type': 'engine', 'name': 'kvmtest'}
>>> cookies
{'username': 'taochengwei', 'Esessionid': '00207be625ab0446beedaa7dfb33fa61b9d01b4c'}
>>> requests.post(url, cookies=cookies, data=data).json()
{u'msg': None, u'code': 0, u'success': True}
>>> 
```

5.6.4 设置当前活跃集群
```
curl -sL --cookie 'username=taochengwei;Esessionid=8a3f96bdcc8022afbbb137ac36c6c0e84754202b' "http://127.0.0.1:10030/swarm/?name=yzSwarm&setActive=true" -XPUT | jq .
{
  "code": 0,
  "msg": null,
  "success": true
}
```

5.6.5 删除一个集群
```
curl -sL --cookie 'username=taochengwei;Esessionid=8a3f96bdcc8022afbbb137ac36c6c0e84754202b' http://127.0.0.1:10030/swarm/?name=kvm -XDELETE | jq
{
  "code": 0,
  "msg": null,
  "success": true
}
```

5.6.6 获取当前系统所有集群
curl -sL --cookie 'username=taochengwei;Esessionid=8a3f96bdcc8022afbbb137ac36c6c0e84754202b' http://127.0.0.1:10030/swarm/?get=all | jq
```
{
    "code": 0,
    "data": [
        {
            "manager": [
                "101.254.242.23"
            ],
            "managerToken": "SWMTKN-1-3wvqcj41bvehpbqlokndycgm2vw74u4jo3leg1731mmms146fm-2jdxb9itdakfbhpd2d6l8v9zp",
            "name": "default",
            "state": "Healthy",
            "type": "engine",
            "workerToken": "SWMTKN-1-3wvqcj41bvehpbqlokndycgm2vw74u4jo3leg1731mmms146fm-9hbphmx7az0hul1v1jnrkzsnc"
        },
        {
            "manager": [
                "101.254.242.42",
                "101.254.242.43",
                "101.254.242.25",
                "101.254.242.23",
                "101.254.242.24"
            ],
            "managerToken": "M",
            "name": "ht",
            "state": "Healthy",
            "type": "engine",
            "workerToken": "W"
        },
        {
            "manager": [
                "106.38.251.206",
                "106.38.251.207"
            ],
            "managerToken": "M",
            "name": "test",
            "state": "Healthy",
            "type": "engine",
            "workerToken": "W"
        }
    ],
    "msg": null
}
```
