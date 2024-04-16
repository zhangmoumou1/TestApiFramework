#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @@Author: 张某某
# @@Create Date: 2023/02/16 10:28
# @@Description: 日志
# @@Copyright © zhangmoumou, Inc. All rights reserved.

import os
import logging
import time
import colorlog
from read_config import log_path

class Log(object):
    def __init__(self):
        self.now = time.strftime("%Y-%m-%d--%H-%M")
        self.logname = os.path.join(log_path, '{0}.log'.format(self.now))

    def __printconsole(self, level, message):
        # 创建一个logger
        log_colors_config = {
            'DEBUG': 'cyan',  # cyan white
            'INFO': 'green',
            'WARNING': 'bold_yellow',
            'ERROR': 'bold_red',
            'CRITICAL': 'bold_purple',
            'EXCEPTION': 'bold_red',
        }

        logger = logging.getLogger('logger_name')

        # 输出到控制台
        console_handler = logging.StreamHandler()
        # 输出到文件
        file_handler = logging.FileHandler(filename=self.logname, mode='a', encoding='utf8')

        # 日志级别，logger 和 handler以最高级别为准，不同handler之间可以不一样，不相互影响
        logger.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.DEBUG)
        file_handler.setLevel(logging.INFO)

        # 日志输出格式
        file_formatter = logging.Formatter(
            fmt='[%(asctime)s.%(msecs)03d] -> [%(levelname)s] : %(message)s',
            datefmt='%Y-%m-%d  %H:%M:%S'
        )
        console_formatter = colorlog.ColoredFormatter(
            fmt='%(log_color)s[%(asctime)s.%(msecs)03d] -> [%(levelname)s] : %(message)s',
            datefmt='%Y-%m-%d  %H:%M:%S',
            log_colors=log_colors_config
        )
        console_handler.setFormatter(console_formatter)
        file_handler.setFormatter(file_formatter)
        if not logger.handlers:
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)

        console_handler.close()
        file_handler.close()

        # 记录一条日志
        if level == 'info':
            # if len(message) > 500:
            #     message = message[:500] + '...'
            logger.info(message)
        elif level == 'debug':
            logger.debug(message)
        elif level == 'warning':
            logger.warning(message)
        elif level == 'error':
            logger.error(message)
        elif level == 'critical':
            logger.critical(message)
        elif level == 'exception':
            logger.exception(message)

    def debug(self, message):
        self.__printconsole('debug', message)

    def info(self, message):
        self.__printconsole('info', message)

    def warning(self, message):
        self.__printconsole('warning', message)

    def error(self, message):
        self.__printconsole('error', message)

    def critical(self, message):
        self.__printconsole('critical', message)

    def exception(self, message):
        self.__printconsole('exception', message)

if __name__ == "__main__":
    Log().debug('debug')
    Log().info('info')
    Log().warning('warning')
    Log().error('error')
    Log().exception('exception')