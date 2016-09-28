## **SwarmOpsApi Api Document for Swarm Cluster**

----------



### 1.节点接口

**查询Swarm上所有可用节点，并组织好节点信息返回。**
*说明：必须在cookies中传入username和Esessionid。*

1.1 URL
http://127.0.0.1:10030/node/

1.2 请求方式
GET

1.3 是否需要登录
请求需要cookies

1.4参数(查询参数(参数类型:含义)
start(int)：起始长度，
length(int)：结果长度，
search[value](str)：搜索内容，在所有数据值中符合搜索的内容,
order[0][column](int)：默认排序列,表示哪一列需要排序,
order[0][dir](str)：排序方式，升序(asc，默认)，降序(desc)。

1.5 返回值与错误代码（错误代码:含义）
30010	Swarm错误
30020	Swarm接口获取节点数量错误
30030	Swarm接口获取节点数量与计算数量不相等错误
30040	查询参数类型错误
30050	查询参数order[0][column]超出索引错误
返回数据如下格式：
```
{
  "recordsFiltered": 2,
  "recordsTotal": 2,
  "length": 10,
  "code": 0,
  "start": 0,
  "msg": null,
  "order[0][column]": 0,
  "search[value]": "",
  "data": [
    [
      "123.59.17.70:2375",
      "DSPV:QLTC:GHTI:BJZM:76K2:VDTM:I6FJ:Y6AH:J6MB:WEL2:FUOE:GK4Z",
      "Healthy",
      "4",
      "0 / 25",
      "0 B / 132 GiB",
      "auto=test, environment=production, executiondriver=native-0.2, kernelversion=3.10.0-229.el7.x86_64, operatingsystem=CentOS Linux 7 (Core), role=node01, service=node01, storagedriver=overlay",
      "2016-07-20T08:10:50Z",
      "1.9.1"
    ],
    [
      "123.59.17.71:2375",
      "XUJ7:J2ZI:2ZTS:THYQ:A44K:35FW:UPGJ:PYJY:CSH6:NM2J:SAXP:3XNZ",
      "Healthy",
      "4",
      "0 / 25",
      "0 B / 98.92 GiB",
      "environment=production, executiondriver=native-0.2, kernelversion=3.10.0-229.el7.x86_64, operatingsystem=CentOS Linux 7 (Core), role=node02, service=node02, storagedriver=overlay",
      "2016-07-20T08:11:13Z",
      "1.9.1"
    ]
  ],
  "order[0][dir]": "asc"
}
```



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
search[value](str)：搜索内容，在所有数据值中符合搜索的内容,
order[0][column](int)：默认排序列,表示哪一列需要排序,
order[0][dir](str)：排序方式，升序(asc，默认)，降序(desc)。

2.5 返回值与错误代码（错误代码:含义）
30060	查询参数类型错误
30070	查询参数order[0][column]超出索引错误
返回数据如下格式：
```
{
  "recordsFiltered": 2,
  "recordsTotal": 2,
  "length": 10,
  "code": 0,
  "start": 0,
  "msg": null,
  "order[0][column]": 0,
  "search[value]": "",
  "data": [
    {
      "kernelversion": "3.10.0-229.el7.x86_64",
      "service": "node01",
      "auto": "test",
      "environment": "production",
      "host": "123.59.17.70:2375",
      "role": "node01",
      "executiondriver": "native-0.2",
      "storagedriver": "overlay",
      "operatingsystem": "CentOS Linux 7 (Core)"
    },
    {
      "kernelversion": "3.10.0-229.el7.x86_64",
      "service": "node02",
      "environment": "production",
      "host": "123.59.17.71:2375",
      "role": "node02",
      "executiondriver": "native-0.2",
      "storagedriver": "overlay",
      "operatingsystem": "CentOS Linux 7 (Core)"
    }
  ],
  "order[0][dir]": "asc"
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
search[value](str)：搜索内容，在所有数据值中符合搜索的内容,搜索格式为A:a,B:b，例如environment:product,service:mysql，
order[0][column](int)：默认排序列,表示哪一列需要排序,
order[0][dir](str)：排序方式，升序(asc，默认)，降序(desc)。

3.5 返回值与错误代码（错误代码:含义）
30080	查询参数类型错误
30090	查询参数order[0][column]超出索引错误
30100	查询参数order[0][column]超出索引错误
返回数据格式如下：
```
{
  "recordsFiltered": 2,
  "recordsTotal": 2,
  "length": 10,
  "code": 0,
  "start": 0,
  "msg": null,
  "order[0][column]": 0,
  "search[value]": "",
  "data": [
    [
      "host=123.59.17.70:2375",
      "auto=test",
      "environment=production",
      "executiondriver=native-0.2",
      "kernelversion=3.10.0-229.el7.x86_64",
      "operatingsystem=CentOS Linux 7 (Core)",
      "role=node01",
      "service=node01",
      "storagedriver=overlay"
    ],
    [
      "host=123.59.17.71:2375",
      "environment=production",
      "executiondriver=native-0.2",
      "kernelversion=3.10.0-229.el7.x86_64",
      "operatingsystem=CentOS Linux 7 (Core)",
      "role=node02",
      "service=node02",
      "storagedriver=overlay"
    ]
  ],
  "order[0][dir]": "asc"
}
```


### 4.查询集群容器列表接口

**查询Swarm上所有的容器及其信息，并组织好节点信息返回。**
*说明：必须在cookies中传入username和Esessionid。*
