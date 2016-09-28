# coding:utf8
# request url for json type
# taochengwei <staugur@saintic.com> @2016-09-13

import json, httplib, urllib, urlparse, logging, os


class RequestsException(httplib.HTTPException):
    pass

class RequestsParamError(RequestsException):
    pass

class Requests:

    '''Request API URL type RESTful, return the dictionary data'''

    def __init__(self, url=None, timeout=5, headers=None):

        self.url         = url
        self.timeout  = timeout
        self.headers = headers or {"User-Agent": "SimpleRequestsAgent"}
        self.jsonde   = json.JSONDecoder()
        self.jsonen   = json.JSONEncoder()

    def _url_split(self, url):
        if isinstance(url, (str, unicode)):
            _url = urlparse.urlparse(url)
            return _url.scheme, _url.netloc, _url.path, _url.query
        else:
            raise RequestsParamError

    def get(self, url=None, headers=None, timeout=None):
        """ http method get function """

        if headers and not isinstance(headers, dict):
            raise RequestsParamError("headers not None or dict")
        if timeout and not isinstance(timeout, int):
            raise RequestsParamError("timeout not None or integer")

        url     = self.url or url
        headers = headers or self.headers
        timeout = timeout or self.timeout
        scheme, netloc, path, query = self._url_split(url)
        if query:
            uri = '%s?%s' %(path, query)
        else:
            uri = path
        netloc  = netloc.split(':')
        if len(netloc) == 2:
            server, port = netloc
        else:
            server = netloc[0]
            port   = 443 if scheme == 'https' else 80

        #print server,port,uri,headers
        try:
            if scheme == 'https':
                httpClient = httplib.HTTPSConnection(host=server, port=port, timeout=timeout)
            else:
                httpClient = httplib.HTTPConnection(host=server, port=port, timeout=timeout)
            httpClient.request(method='GET', url=uri, headers=headers)
            response = httpClient.getresponse()
            content  = response.read()  # here is str type
            #print content
            data     = self.jsonde.decode(content)  # convert str to dict
            httpClient.close()
        except Exception,e:
            logging.error(e, exc_info=True)
            data = {}
        return data

    def post(self, url=None, data=None, headers=None, timeout=None):
        """ http method get function """

        if headers and not isinstance(headers, dict):
            raise RequestsParamError("headers not None or dict")
        if timeout and not isinstance(timeout, int):
            raise RequestsParamError("timeout not None or integer")
        if data and not isinstance(data, dict):
            raise RequestsParamError("data not None or dict")

        url     = self.url or url
        headers = headers or self.headers
        timeout = timeout or self.timeout
        scheme, netloc, path, query = self._url_split(url)
        if query:
            uri = '%s?%s' %(path, query)
        else:
            uri = path
        netloc  = netloc.split(':')
        if len(netloc) == 2:
            server, port = netloc
        else:
            server = netloc[0]
            port   = 443 if scheme == 'https' else 80

        #print server,port,uri,headers,data
        try:
            if scheme == 'https':
                httpClient = httplib.HTTPSConnection(host=server, port=port, timeout=timeout)
            else:
                httpClient = httplib.HTTPConnection(host=server, port=port, timeout=timeout)
            httpClient.request(method='POST', url=uri, body=data, headers=headers)
            response = httpClient.getresponse()
            content  = response.read()  # here is str type
            data     = self.jsonde.decode(content)  # convert str to dict
            httpClient.close()
        except Exception,e:
            logging.error(e, exc_info=True)
            data = {}
        return data

    def put(self, url=None, data=None, headers=None, timeout=None):
        """ http method get function """

        if headers and not isinstance(headers, dict):
            raise RequestsParamError("headers not None or dict")
        if timeout and not isinstance(timeout, int):
            raise RequestsParamError("timeout not None or integer")
        if data and not isinstance(data, dict):
            raise RequestsParamError("data not None or dict")

        url     = self.url or url
        headers = headers or self.headers
        timeout = timeout or self.timeout
        scheme, netloc, path, query = self._url_split(url)
        if query:
            uri = '%s?%s' %(path, query)
        else:
            uri = path
        netloc  = netloc.split(':')
        if len(netloc) == 2:
            server, port = netloc
        else:
            server = netloc[0]
            port   = 443 if scheme == 'https' else 80

        #print server,port,uri,headers,data
        try:
            if scheme == 'https':
                httpClient = httplib.HTTPSConnection(host=server, port=port, timeout=timeout)
            else:
                httpClient = httplib.HTTPConnection(host=server, port=port, timeout=timeout)
            httpClient.request(method='PUT', url=uri, body=data, headers=headers)
            response = httpClient.getresponse()
            content  = response.read()  # here is str type
            data     = self.jsonde.decode(content)  # convert str to dict
            httpClient.close()
        except Exception,e:
            logging.error(e, exc_info=True)
            data = {}
        return data

    def delete(self, url=None, data=None, headers=None, timeout=None):
        """ http method get function """

        if headers and not isinstance(headers, dict):
            raise RequestsParamError("headers not None or dict")
        if timeout and not isinstance(timeout, int):
            raise RequestsParamError("timeout not None or integer")
        if data and not isinstance(data, dict):
            raise RequestsParamError("data not None or dict")

        url     = self.url or url
        headers = headers or self.headers
        timeout = timeout or self.timeout
        scheme, netloc, path, query = self._url_split(url)
        if query:
            uri = '%s?%s' %(path, query)
        else:
            uri = path
        netloc  = netloc.split(':')
        if len(netloc) == 2:
            server, port = netloc
        else:
            server = netloc[0]
            port   = 443 if scheme == 'https' else 80

        #print server,port,uri,headers,data
        try:
            if scheme == 'https':
                httpClient = httplib.HTTPSConnection(host=server, port=port, timeout=timeout)
            else:
                httpClient = httplib.HTTPConnection(host=server, port=port, timeout=timeout)
            httpClient.request(method='DELETE', url=uri, body=data, headers=headers)
            response = httpClient.getresponse()
            content  = response.read()  # here is str type
            data     = self.jsonde.decode(content)  # convert str to dict
            httpClient.close()
        except Exception,e:
            logging.error(e, exc_info=True)
            data = {}
        return data

def getEtcdCookie(etcdUrl, username):
    res = Requests(etcdUrl).get()
    for _ in res['node']['nodes']:
        if json.loads(_.get('value', '{}')).get('username') == username:
            key = _.get('key').split('/')[-1]
            return key

if __name__ == "__main__":
    etcdUrl = 'http://etcddocker.emar.com:10020/v2/keys/token/sys'
    apiUrl   = "http://123.59.17.103:10031"
    headers={"User-Agent": "Jenkins/MultiSwarmManager"}
    username = "taochengwei"
    sessionId = getEtcdCookie(etcdUrl, username)
    query       = {"username": username, "Esessionid": sessionId}
    requests   = Requests(headers=headers)

    getValue  = os.getenv("get")
    setActiveName = os.getenv("setActiveName")

    if setActiveName:
        query.update(setActive=True, name=setActiveName)
        swarmUrl = apiUrl + "/swarm?" + urllib.urlencode(query)
        res = requests.put(swarmUrl)
        print json.dumps(res, indent=4)
    elif getValue:
        query.update(get=getValue)
        swarmUrl = apiUrl + "/swarm?" + urllib.urlencode(query)
        res = requests.get(swarmUrl)
        print json.dumps(res, indent=4)