# -*- coding:utf8 -*-


import requests
from SpliceURL import Splice
from libs.public import logger


class Etcd(object):


    def __init__(self, **etcd):
        self.timeout = 5
        self.verify  = False
        self.etcdUrl = Splice(scheme=etcd.get("ETCD_SCHEME"), domain=etcd.get("ETCD_HOST"), port=etcd.get("ETCD_PORT"), path=etcd.get("ETCD_VERSION") + "/keys").geturl

    @property
    def url(self):
        return self.etcdUrl

    def _get(self, path, params=None, headers=None):
        try:
            r = requests.get(self.etcdUrl + path, headers=headers, timeout=self.timeout, verify=self.verify, params=params)
        except Exception,e:
            logger.warn(e, exc_info=True)
        else:
            logger.info("etcd get url %s" %r.url)
            return r.json()

    def _post(self, path, params=None, data=None, headers=None):
        try:
            r = requests.post(self.etcdUrl + path, headers=headers, timeout=self.timeout, verify=self.verify, params=params, data=data)
        except Exception,e:
            logger.warn(e, exc_info=True)
        else:
            logger.info("etcd post url %s, data is %s" %(r.url, data))
            return True

    def _put(self, path, params=None, data=None, headers=None):
        try:
            r = requests.put(self.etcdUrl + path, headers=headers, timeout=self.timeout, verify=self.verify, params=params, data=data)
        except Exception,e:
            logger.warn(e, exc_info=True)
        else:
            logger.info("etcd put url %s, data is %s" %(r.url, data))
            return True

    def _delete(self, path, params=None, data=None, headers=None):
        try:
            r = requests.delete(self.etcdUrl + path, headers=headers, timeout=self.timeout, verify=self.verify, params=params, data=data)
        except Exception,e:
            logger.warn(e, exc_info=True)
        else:
            logger.info("etcd delete url %s, data is %s" %(r.url, data))
            return True


