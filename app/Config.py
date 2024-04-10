#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *********************************************************#
# @@Author: 张某某
# @@Create Date: 2021-03-25 22:24:14
# @@Description: 配置文件内的值
# @@Copyright © zhangmoumou, Inc. All rights reserved.
# *********************************************************#

import os
from app.utils.config_constructor import ConfigConstructor

# 读取配置文件路径
prj_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
read_config = ConfigConstructor()

# 读取配置文件里的参数
env = read_config.getValue('envConfig', 'environment')
# 读取服务器的uuid
uuid = read_config.getValue('serverUUid', 'uuid')
# 将日志存储路径加入环境变量
log_path = os.path.join(prj_path, 'report', 'logs')
# ssh连接信息
ssh_ip = read_config.getValue('sshInfo', 'ip')
ssh_port = read_config.getValue('sshInfo', 'port')
ssh_username = read_config.getValue('sshInfo', 'username')
ssh_password = read_config.getValue('sshInfo', 'password')
# ssh开关
local_switch = read_config.getValue('sshSwitch', 'localhost')
server_switch = read_config.getValue('sshSwitch', 'server')
# 钉钉token
ding_token = read_config.getValue('dingtalkToken', 'token')