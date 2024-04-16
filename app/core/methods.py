#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *********************************************************#
# @@Author: 张某某
# @@Create Date: 2021-03-25 22:24:14
# @@Description: 集合可调用方法，统一调用即可
# @@Copyright © 91duobaoyu, Inc. All rights reserved.
# *********************************************************#

import pytest
import platform
import allure
import random
import os
import json
import sys
import yaml
import datetime
import pymysql
import redis
import re
import platform
import time
import calendar
import string
import random
import requests
import warnings
from time import sleep
from typing import List, Dict, Set, Tuple, overload, Any
from app.utils.logger_constructor import Log
from dbutils.pooled_db import PooledDB
from sshtunnel import SSHTunnelForwarder
from app.utils.yaml_constructor import YamlConstructor
from read_config import env, uuid, local_switch, server_switch, ding_token
from app.core.decorator import response_decorator, login_decorator
from app.core.http_generator import HttpGenerator
from app.core.login_generator import LoginGenerator
from app.utils.mysql_constructor import MysqlConstructor
from app.utils.redis_constructor import RedisConstructor
from app.core.specific_generator import SpecificGenerator
from app.core.parser import ParserJson
from app.core.normal_generator import NormalGenarator
from deepdiff import DeepDiff, grep, DeepSearch
from app.utils.assert_constructor import AssertConstructor
from app.core.generator import Genetator

SYSTEM_VERSION = platform.platform()

__all__ = [
    'os',
    'sys',
    'pytest',
    'allure',
    'Log',
    'env',
    'uuid',
    'local_switch',
    'server_switch',
    'yaml',
    'datetime',
    'pymysql',
    're',
    'time',
    'PooledDB',
    'SSHTunnelForwarder',
    'YamlConstructor',
    'platform',
    'redis',
    'random',
    'List',
    'Dict',
    'Set',
    'Tuple',
    'overload',
    'Any',
    'calendar',
    'string',
    'requests',
    'json',
    'response_decorator',
    'HttpGenerator',
    'LoginGenerator',
    'MysqlConstructor',
    'RedisConstructor',
    'ParserJson',
    'sleep',
    'NormalGenarator',
    'DeepDiff',
    'grep',
    'AssertConstructor',
    'DeepSearch',
    'ding_token',
    'login_decorator',
    'SpecificGenerator',
    'Genetator',
    'warnings',
]
