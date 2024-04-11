#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @@Author: 张某某
# @@Create Date: 2023/02/16 10:28
# @@Description: ini配置功能构造
# @@Copyright © zhangmoumou, Inc. All rights reserved.

import configparser
import os

config_file_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
FILENAME = os.path.join(config_file_path, '../conf/config.ini')

class ConfigConstructor(object):
    """
    读取config.ini配置文件
    return：value
    """
    def __init__(self):
        self.configpath = FILENAME
        self.cf = configparser.ConfigParser()

    def getValue(self, key, name):
        """
        读取config.ini文件
        :param env:
        :param name:
        :return:
        """
        try:
            self.cf.read(self.configpath, encoding='utf-8')
            results = self.cf.get(key, name)
            return results
        except Exception as e:
            raise f'<<config.ini配置异常>>未找到{key}下{name}的值，请检查对应值是否存在：{e}'

    def update_env_conf(self, env):
        """
        config.ini写入环境
        """
        from app.utils.logger_constructor import Log
        try:
            self.cf.read(self.configpath, encoding='utf-8')
            self.cf.set("envConfig", "environment", env)
            with open(self.configpath, "w+", encoding='gbk') as f:
                self.cf.write(f)
                Log().info(f'config.ini写入项目环境成功：{env}')
        except Exception as e:
            Log().error(f'项目环境写入.ini文件失败：{e}')
            raise Exception('config.ini写入项目环境失败')

if __name__ == "__main__":
    # print(ConfigConstructor().getValue('envConfig', 'environment'))
    ConfigConstructor().update_env_conf('ONLINE')
