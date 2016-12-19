# SwarmOps
Operation of swarm cluster, providing an intermediate layer application of API interface and UI.Source from the company's docker management needs, modify the open part of the public, and now open source out.


## LICENSE
MIT


## Environment
> 1. Python Version: 2.6, 2.7
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
    3.2 sh Control.sh   #生产模式
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


## Design
![Design][1]


[1]: ./misc/SwarmOps.png