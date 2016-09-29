# -*- coding:utf8 -*-

import requests
from utils.public import logger

def auth(auth_url, username, token, service="o=swarmApi,o=sys"):
    logger.info("User(%s) want to sign in, token(sessionid) is %s." %(username, token))
    query = {"username": username, "token": token, "service": service}
    if auth_url:
        try:
            r = requests.get(auth_url, params=query, timeout=3, verify=False)
        except Exception, e:
            logger.error(e, exc_info=True)
        else:
            if r.status_code == requests.codes.ok:
                res = r.json()
                if res.get("token") == token:
                    logger.info("Sign in successfully.")
                    return True
    return False
