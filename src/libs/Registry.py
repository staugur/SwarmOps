# -*- coding: utf8 -*-

import requests, SpliceURL
from utils.public import logger

class V1Registry_ENGINE_API:


    def __init__(self, RegistryAddr, timeout=2):
        self.timeout   = timeout
        self.verify    = False
        self._baseUrl  = SpliceURL.Modify(RegistryAddr, path="/v1/").geturl
        logger.info("V1Registry_ENGINE_API, the _baseUrl is {}".format(self._baseUrl))

    @property
    def _ping(self):
        try:
            code = requests.head(self._baseUrl, timeout=self.timeout, verify=self.verify).status_code
        except Exception,e:
            logger.error(e, exc_info=True)
        else:
            if code == 200:
                return True
        return False

    def _search_all_repository(self, q):
        """ 搜索私有仓所有镜像 """

        ReqUrl = self._baseUrl.strip("/") + "/search"
        logger.info("_search_all_repository for url {}".format(ReqUrl))
        try:
            Images = requests.get(ReqUrl, timeout=self.timeout, verify=self.verify, params={"q": q}).json()
        except Exception,e:
            logger.error(e, exc_info=True)
            return False
        else:
            return Images["results"]

    @property
    def _list_all_repository(self):
        """ 列出私有仓所有镜像名称 """

        return self._search_all_repository(q="")

    def _list_repository_tag(self, ImageName):
        """ 列出某个镜像所有标签 """

        ReqUrl = SpliceURL.Modify(self._baseUrl, path="/repositories/{}/tags".format(ImageName)).geturl
        logger.info("_list_repository_tag for url {}".format(ReqUrl))
        try:
            Tags = requests.get(ReqUrl, timeout=self.timeout, verify=self.verify).json()
        except Exception,e:
            logger.error(e, exc_info=True)
            return False
        else:
            return Tags

    def _get_imageId(self, ImageName, tag="latest"):
        """ 查询某个镜像tag的imageId """

        ReqUrl = SpliceURL.Modify(self._baseUrl, path="/repositories/{}/tags/{}".format(ImageName, tag)).geturl
        logger.info("_get_imageId for url {}".format(ReqUrl))
        try:
            ImageId = requests.get(ReqUrl, timeout=self.timeout, verify=self.verify).json()
        except Exception,e:
            logger.error(e, exc_info=True)
            return False
        else:
            return ImageId

    def _delete_repository_tag(self, ImageName, tag):
        """ 删除一个镜像的某个标签 """

        ReqUrl = SpliceURL.Modify(self._baseUrl, path="/repositories/{}/tags/{}".format(ImageName, tag)).geturl
        logger.info("_delete_repository_tag for url {}".format(ReqUrl))
        try:
            delete_repo_result = requests.delete(ReqUrl, timeout=self.timeout, verify=self.verify).json()
        except Exception,e:
            logger.error(e, exc_info=True)
            return False
        else:
            return delete_repo_result

    def _delete_repository(self, ImageName):
        """ 删除一个镜像 """

        ReqUrl = SpliceURL.Modify(self._baseUrl, path="/repositories/{}/".format(ImageName)).geturl
        logger.info("_delete_repository for url {}".format(ReqUrl))
        try:
            delete_repo_result = requests.delete(ReqUrl, timeout=self.timeout, verify=self.verify).json()
        except Exception,e:
            logger.error(e, exc_info=True)
            return False
        else:
            return delete_repo_result

    def _list_imageId_ancestry(self, ImageId):
        """ 列出某个镜像所有父镜像 """

        ReqUrl = SpliceURL.Modify(self._baseUrl, path="/images/{}/ancestry".format(ImageId)).geturl
        logger.info("_list_imageId_ancestry for url {}".format(ReqUrl))
        try:
            ImageIds = requests.get(ReqUrl, timeout=self.timeout, verify=self.verify).json()
        except Exception,e:
            logger.error(e, exc_info=True)
            return False
        else:
            return ImageIds

    def _get_imageId_info(self, ImageId):
        """ 查询某个镜像的信息 """

        ReqUrl = SpliceURL.Modify(self._baseUrl, path="/images/{}/json".format(ImageId)).geturl
        logger.info("_get_imageId_info for url {}".format(ReqUrl))
        try:
            ImageInfo = requests.get(ReqUrl, timeout=self.timeout, verify=self.verify).json()
        except Exception,e:
            logger.error(e, exc_info=True)
            return False
        else:
            return ImageInfo


class V2Registry_ENGINE_API:

    pass


class RegistryManager:


    def __init__(self, timeout=2, Registry={}):
        self.timeout = timeout
        #Base Registry info
        self._url  = Registry["RegistryAddr"]
        self._ver  = Registry["RegistryVersion"]
        self._auth = Registry["RegistryAuthentication"]
        #Instantiation the registry
        self.registry = V1Registry_ENGINE_API(RegistryAddr=self._url) if int(self._ver) == 1 else None
        self.status   = self.registry._ping
        logger.info("Registry API, registry is {}, status is {}".format(self._url, self.status))

    def GET(self, **kwargs):
        """  查询类操作 """

        return self.registry._list_all_repository