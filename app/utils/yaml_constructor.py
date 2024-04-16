#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *********************************************************#
# @@Author: 张某某
# @@Create Date: 2021-03-25 22:24:14
# @@Description: yaml文件相关操作
# @@Copyright © 91duobaoyu, Inc. All rights reserved.
# *********************************************************#

from app.core.methods import sys, os, yaml
from read_config import env
from app.utils.logger_constructor import Log
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

# 获取当前脚本所在文件夹路径
CURPATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
URL_PATH = os.path.join(CURPATH, "..\\conf\\info.yaml")
MYSQL_PATH = os.path.join(CURPATH, "..\\conf\\mysql.yaml")
REDIS_PATH = os.path.join(CURPATH, "..\\conf\\redis.yaml")

class YamlConstructor(object):
    """
    读取操作yaml文件
    """
    @staticmethod
    def get_base_info(project):
        """
        获取接口前缀地址
        project: 项目名
        """
        try:
            # 处理项目类型和登录方式
            with open(URL_PATH, 'rb') as f:
                cont = f.read()
            cf = yaml.load(cont, Loader=yaml.FullLoader)
            data = cf.get(project)[env]
            if 'base_url' not in data or data['base_url'] is None or data['base_url'] == '':
                Log().warning(f'<<info.yaml配置异常>>未找到接口前缀地址，请检查对应值是否存在')
            return data
        except Exception as e:
            Log().error(f"<<info.yaml配置异常>>未找到对应配置信息，请检查对应值是否存在：{e}")
            raise

    @staticmethod
    def get_mysql_info(project, type):
        """
        获取mysql连接信息
        type: 连接类型，分为business业务/case用例
        """
        try:
            with open(MYSQL_PATH, 'rb') as f:
                cont = f.read()
            cf = yaml.load(cont, Loader=yaml.FullLoader)
            # 区分是用例库还是业务库
            if project is None:
                data = cf.get('CaseDb')[env]
            else:
                data = cf.get(project)[env][type]
            return {'ip': data[0], 'port': data[1], 'username': data[2], 'password': data[3]}
        except Exception as e:
            Log().error(f"<<mysql.yaml配置异常>>未找到对应配置信息，请检查对应值是否存在：{e}")

    @staticmethod
    def get_redis_info(project=None, type=None):
        """
        获取redis连接信息
        type: 连接类型，分为business业务/case用例
        """
        try:
            with open(REDIS_PATH, 'rb') as f:
                cont = f.read()
            cf = yaml.load(cont, Loader=yaml.FullLoader)
            if project is None:
                data = cf.get('CaseDb')[env]
            else:
                data = cf.get(project)[env][type]
            return {'ip': data[0], 'port': data[1], 'password': data[2], 'db_num': data[3]}
        except Exception as e:
            Log().error(f"<<redis.yaml配置异常>>未找到对应项目名为[{project}]的配置信息，请检查redis.yaml或mysql用例数据是否正确：{e}")
            raise

if __name__ == "__main__":
    YamlConstructor.get_mysql_info('project_name', 'case_db')
