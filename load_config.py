#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @@Author: 张某某
# @@Create Date: 2023/02/16 10:28
# @@Description: 写入配置
# @@Copyright © zhangmoumou, Inc. All rights reserved.

import os
import sys
from app.utils.config_constructor import ConfigConstructor
from app.utils.logger_constructor import Log

""""
config.ini写入环境
"""
env = sys.argv[1:2]
ConfigConstructor().update_env_conf(env[0])