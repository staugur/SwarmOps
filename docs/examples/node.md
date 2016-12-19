## SwarmOps Api examples for /node


1. 根据单条件标签查询节点信息

```
curl -sL --cookie "username=taochengwei;Esessionid=2e826f741947de73bfb2db88e4f394101d42aee8" "http://127.0.0.1:10030/node_for_label/?search=IDC:yz"
{
    "code": 0,
    "data": [
        "host215",
        "yz-mbg-017212",
        "yz-mbg-017214",
        "yz-mbg-017216",
        "yz-mbg-017217"
    ],
    "length": 10,
    "msg": null,
    "order[0][column]": 0,
    "order[0][dir]": "asc",
    "recordsFiltered": 6,
    "recordsTotal": 6,
    "search[value]": "IDC:yz",
    "start": 0
}
```


2. 根据多条件标签查询节点信息

```
curl -sL --cookie "username=taochengwei;Esessionid=2e826f741947de73bfb2db88e4f394101d42aee8" "http://127.0.0.1:10030/node_for_label/?search=IDC:yz,dev:true"
{
    "code": 0,
    "data": [
        "host215"
    ],
    "length": 10,
    "msg": null,
    "order[0][column]": 0,
    "order[0][dir]": "asc",
    "recordsFiltered": 6,
    "recordsTotal": 6,
    "search[value]": "IDC:yz,dev:true",
    "start": 0
}
```


3. 将ip为106.38.251.206的节点作为管理者(manager)加入到swarm集群中

```
curl -sL --cookie "username=taochengwei;Esessionid=e00265ca214bd44bcb1266e1c6819fd75c77ab0e" "http://127.0.0.1:10030/node" -d "ip=106.38.251.206" -d "role=manager" -XPOST
{
    "code": 0,
    "msg": null,
    "success": true
}
```

4. 将ip为106.38.251.208的节点作为工作者(worker)加入到swarm集群中

```
curl -sL --cookie "username=taochengwei;Esessionid=e00265ca214bd44bcb1266e1c6819fd75c77ab0e" "http://127.0.0.1:10030/node" -d "ip=106.38.251.208" -XPOST
{
    "code": 0,
    "msg": null,
    "success": false
}
```

5. 从swarm集群中删除flag为kvm-yz251208(worker)的节点，这个节点的ip是106.38.251.208

```
curl -sL --cookie "username=taochengwei;Esessionid=e00265ca214bd44bcb1266e1c6819fd75c77ab0e" "http://127.0.0.1:10030/node" -d "ip=106.38.251.208" -d "flag=kvm-yz251208" -XDELETE
{
    "code": 0,
    "msg": null,
    "success": true
}
```

6. 将ip为106.38.251.208的节点作为管理者(manager)加入到swarm集群中

```
curl -sL --cookie "username=taochengwei;Esessionid=e00265ca214bd44bcb1266e1c6819fd75c77ab0e" "http://127.0.0.1:10030/node" -d "ip=106.38.251.208" -d "role=Manager" -XPOST
{
    "code": 0,
    "msg": null,
    "success": true
}
```

7. 从swarm集群中强制删除flag为kvm-yz251208(manager)的节点，这个节点的ip是106.38.251.208

```
curl -sL --cookie "username=taochengwei;Esessionid=e00265ca214bd44bcb1266e1c6819fd75c77ab0e" "http://127.0.0.1:10030/node" -d "ip=106.38.251.208" -d "flag=kvm-yz251208" -d "force=true" -XDELETE
{
    "code": 0,
    "msg": null,
    "success": true
}
```

7.更新节点label，将名称为kvm-yz251209的节点增加ipaddr、env等label。
```
>>> labels={"node": "kvm-yz251209", "idc": "yz", "group": "sys", "env": "gray", "ipaddr": "106.38.251.209"}
>>> import requests
>>> cookies={"username": "taochengwei", "Esessionid": "3a9df09e1599ac8e411009f6fe4bddda1507ef07"}
>>> requests.put("http://127.0.0.1:10030/node", cookies=cookies, data=labels).json()
{u'msg': None, u'code': 0, u'success': True}
```