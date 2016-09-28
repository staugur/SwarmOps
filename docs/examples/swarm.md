## SwarmOpsApi examples for /swarm


1. 查询swarm集群示例

```
curl -sL --cookie "username=taochengwei;Esessionid=00207be625ab0446beedaa7dfb33fa61b9d01b4c" "http://127.0.0.1:10030/swarm" | jq .
false


curl -sL --cookie "username=taochengwei;Esessionid=00207be625ab0446beedaa7dfb33fa61b9d01b4c" "http://127.0.0.1:10030/swarm?only_default=true" | jq .
{
  "managerToken": "SWMTKN-1-3wvqcj41bvehpbqlokndycgm2vw74u4jo3leg1731mmms146fm-2jdxb9itdakfbhpd2d6l8v9zp",
  "workerToken": "SWMTKN-1-3wvqcj41bvehpbqlokndycgm2vw74u4jo3leg1731mmms146fm-9hbphmx7az0hul1v1jnrkzsnc",
  "manager": [
    "101.254.242.23"
  ],
  "type": "engine",
  "name": "default"
}


curl -sL --cookie "username=taochengwei;Esessionid=00207be625ab0446beedaa7dfb33fa61b9d01b4c" "http://127.0.0.1:10030/swarm?all=true" | jq .
[
  {
    "managerToken": "SWMTKN-1-3wvqcj41bvehpbqlokndycgm2vw74u4jo3leg1731mmms146fm-2jdxb9itdakfbhpd2d6l8v9zp",
    "workerToken": "SWMTKN-1-3wvqcj41bvehpbqlokndycgm2vw74u4jo3leg1731mmms146fm-9hbphmx7az0hul1v1jnrkzsnc",
    "manager": [
      "101.254.242.23"
    ],
    "type": "engine",
    "name": "default"
  }
]
```

2. 添加一个swarm集群

```
>>> 
>>> import requests, json
>>> 
>>> url = 'http://127.0.0.1:10030/swarm/'
>>> data
{'managerToken': 'SWMTKN-1-2n96dz2nuj6661zbm1udphldolx0mvcpnv1wairil83ejqa217-3n1sioyu7z7adrnqo2rofdhqo', 'manager': '106.38.251.206', 'workerToken': 'SWMTKN-1-2n96dz2nuj6661zbm1udphldolx0mvcpnv1wairil83ejqa217-bxv1n748g643a7v6eb7b3myd5', 'type': 'engine', 'name': 'kvmtest'}
>>> 
>>> cookies
{'username': 'taochengwei', 'Esessionid': '00207be625ab0446beedaa7dfb33fa61b9d01b4c'}
>>> 
>>> 
>>> requests.post(url, cookies=cookies, data=data).json()
{u'msg': None, u'code': 0, u'success': True}
>>> 
```

3. 删除一个swarm集群

```
curl -sL --cookie 'username=taochengwei;Esessionid=8a3f96bdcc8022afbbb137ac36c6c0e84754202b' http://127.0.0.1:10030/swarm/?name=test -XDELETE
{
    "code": 0, 
    "msg": null, 
    "success": true
}

curl -sL --cookie 'username=taochengwei;Esessionid=8a3f96bdcc8022afbbb137ac36c6c0e84754202b' http://127.0.0.1:10030/swarm/?name=kvm -XDELETE | jq
{
  "code": 0,
  "msg": null,
  "success": true
}
```

4. 设置当前活跃集群(默认活跃集群是default)

```
curl -sL --cookie 'username=taochengwei;Esessionid=8a3f96bdcc8022afbbb137ac36c6c0e84754202b' "http://127.0.0.1:10030/swarm/?name=yzSwarm&setActive=true" -XPUT | jq .
{
  "code": 0,
  "msg": null,
  "success": true
}

curl -sL --cookie 'username=taochengwei;Esessionid=8a3f96bdcc8022afbbb137ac36c6c0e84754202b' http://127.0.0.1:10030/swarm/?get=active | jq .
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
