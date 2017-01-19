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

**v0.0.2**

> 1. 调整UI页面
> 2. network
> 3. 私有仓查询, 私有仓删除镜像确认, 私有仓镜像搜索
> 4. 调整当ActiveSwarm默认值时leader值
> 5. fix api update service type bug
> 6. 服务滚动升级
> 7. 添加FontAwesome图标库
