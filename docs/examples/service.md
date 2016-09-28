## SwarmOpsApi examples for /service


1. 创建服务示例

```
>>> import requests
>>> data={"image": "registry.saintic.com/release/swarmopsapi", "env": "swarmopsapi_port=10031", "publish":"10031:10031"}
>>> r=requests.post("http://127.0.0.1:10030/services", cookies={"username": 'taochengwei', "Esessionid":"003fb9026b2af950a9c01ba01ad1be357aa00fe3"} ,data=data)
>>> r.json()
{u'msg': None, u'code': 0, u'success': True}
```

查看manager的services列表：

taochengwei@SwarmOpsApi docker service ls
ID            NAME               REPLICAS  IMAGE                                                                     COMMAND
bnzhi6ot0fk2  yigao-cm-13182     1/1       registry.saintic.com/release/yigao-cookiematch:20160805-srcV23056-dokV1555  
db8i2pwpk7ap  yigao-cm-13181     1/1       registry.saintic.com/release/yigao-cookiematch:20160805-srcV23056-dokV1555  
ewzg9gzg9cp4  prickly_boyd       1/1       registry.saintic.com/release/swarmopsapi                                    
f1dmdzagsrzi  swarmopsapi-10036  1/1       registry.saintic.com/release/swarmopsapi                                    


2. 删除服务示例

```
>>> impoer requests
>>> url="http://127.0.0.1:10030/service/"
>>> cookies={"username": "taochengwei", "Esessionid": "8a3f96bdcc8022afbbb137ac36c6c0e84754202b"}
>>> data={"id": "e11yt2psl1iz4mopietdyrihi"}
>>> r=requests.delete(url, cookies=cookies, data=data)
>>> r.json()
{u'msg': None, u'code': 0, u'success': True}
>>> 
```