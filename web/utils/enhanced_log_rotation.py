# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------


import re
from logging import handlers


class EnhancedRotatingFileHandler(handlers.TimedRotatingFileHandler,
                                  handlers.RotatingFileHandler):
    """
    Handler for logging to a set of files, which switches from one file
    to the next when the current file reaches a certain size, or at certain
    timed intervals
    @filename - log file name
    @max_bytes - file size in bytes to rotate  file
    @interval - Duration to rotate file
    @backup_count - Maximum number of files to retain
    @encoding - file encoding
    @when -  'when' events supported:
            # S - Seconds
            # M - Minutes
            # H - Hours
            # D - Days
            # midnight - roll over at midnight
            # W{0-6} - roll over on a certain day; 0 - Monday
    Here we are defaulting rotation with minutes interval
    """
    def __init__(self, filename, max_bytes=1, interval=60, backup_count=0,
                 encoding=None, when='M'):
        max_bytes = max_bytes * 1024 * 1024
        handlers.TimedRotatingFileHandler.__init__(self, filename=filename,
                                                   when=when,
                                                   interval=interval,
                                                   backupCount=backup_count,
                                                   encoding=encoding)

        handlers.RotatingFileHandler.__init__(self, filename=filename,
                                              mode='a',
                                              maxBytes=max_bytes,
                                              backupCount=backup_count,
                                              encoding=encoding)

    # Time & Size combined rollover
    def shouldRollover(self, record):
        return handlers.TimedRotatingFileHandler.shouldRollover(self, record) \
            or handlers.RotatingFileHandler.shouldRollover(self, record)

    # Roll overs current file
    def doRollover(self):
        self.suffix = "%Y-%m-%d_%H-%M-%S"
        self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}(\.\w+)?$"
        self.extMatch = re.compile(self.extMatch, re.ASCII)
        handlers.TimedRotatingFileHandler.doRollover(self)