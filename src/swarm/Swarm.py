# -*- coding: utf8 -*-

from config import REDIS
from utils.public import logger, RedisConnection


class MultiSwarmManager:

    def __init__(self):
        self.key   = REDIS["Key"]
        self.redis = RedisConnection

    def _pickle(self, string):
        """Serialization information, set data"""
        pass

    def _unpickle(self):
        """Anti serialization information, take out the data"""
        return self.redis.hgetall(self.key)

    def GET(self, get, checkState=False):
        """ R, read, get swarm info """

        res = {"msg": None, "code": 0}
        logger.info("GET request, the query params is %s, get state is %s" %(get, checkState))

        #Check query
        if not isinstance(get, (str, unicode)) or not get:
            res.update(msg="GET: query params type error or none", code=-10000)
        else:
            if get == "all":
                res.update(data=self._unpickle())
            elif get == "active":
                res.update(data=self.getActive)
            elif get == "leader":
                res.update(data=self.getLeader)
            else:
                res.update(data=self.getOne(get))
        logger.info(res)
        return res

