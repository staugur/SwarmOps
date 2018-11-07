# -*- coding: utf-8 -*-
"""
    SwarmOps.utils.log
    ~~~~~~~~~~~~~~

    Define logging base class.

    :copyright: (c) 2018 by staugur.
    :license: MIT, see LICENSE for more details.
"""

import os
import logging, logging.handlers
from config import GLOBAL

class Logger: 

    def __init__(self, logName, backupCount=10):
        self.logName = logName
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        self.logFile = os.path.join(self.log_dir, '{0}.log'.format(self.logName))
        self._levels = {
            "DEBUG" : logging.DEBUG,
            "INFO" : logging.INFO,
            "WARNING" : logging.WARNING,
            "ERROR" : logging.ERROR,
            "CRITICAL" : logging.CRITICAL
        }
        self._logfmt = '%Y-%m-%d %H:%M:%S'
        self._logger = logging.getLogger(self.logName)
        if not os.path.exists(self.log_dir): os.mkdir(self.log_dir)

        handler = logging.handlers.TimedRotatingFileHandler(filename=self.logFile,
                              backupCount=backupCount,
                              when="midnight")
        handler.suffix = "%Y%m%d"
        formatter = logging.Formatter('[ %(levelname)s ] %(asctime)s %(filename)s:%(lineno)d %(message)s', datefmt=self._logfmt)
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        self._logger.setLevel(self._levels.get(GLOBAL.get('LogLevel', "INFO")))

    @property
    def getLogger(self):
        return self._logger

if __name__ == "__main__":
        syslog = Logger("sys").getLogger
        reqlog = Logger("req").getLogger

        syslog.info("sys hello info")
        syslog.debug("sys hello debug")
        syslog.error("sys hello error")
        syslog.warning("sys hello warning")

        reqlog.info("req hello info")
        reqlog.debug("req hello debug")
        reqlog.error("req hello error")
        reqlog.warning("req hello warning")
