#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @@Author: 张某某
# @@Create Date: 2023/02/16 10:28
# @@Description: pytest设置共享
# @@Copyright © zhangmoumou, Inc. All rights reserved.

import time
import pytest
import platform
from app.utils.message_constructor import MessageConstructor
from app.utils.logger_constructor import Log

@pytest.fixture(scope="session", autouse=True)
def login_first() -> None:
    """
    执行pytest命令后，前置执行base_login所有登录操作，获取token
    :return:
    """
    SYSTEM_VERSION = platform.platform()
    if 'Linux' in SYSTEM_VERSION:
        Log().critical(f'\n')
        Log().critical(f'-------------------开始获取登录信息[base_login表]-------------------')
        from app.utils.mysql_constructor import MysqlConstructor
        from app.core.generator import Genetator
        case_ids = MysqlConstructor.parameterization_data('base_login', 'all')
        for case_id in case_ids:
            Genetator.global_generator(table_name='base_login', case_id=case_id[0], logFlag=True)
        Log().critical(f'---------------------获取登录信息结束----------------------')

def pytest_terminal_summary(terminalreporter):
    """
    将运行结果发送至钉钉和预发用例统计数据
    :param terminalreporter:
    :return:
    """
    cases = terminalreporter._numcollected
    case_pass = len(terminalreporter.stats.get('passed', []))
    case_fail = len(terminalreporter.stats.get('failed', []))
    case_error = len(terminalreporter.stats.get('error', []))
    case_skip = len(terminalreporter.stats.get('skipped', []))
    case_time = round(time.time() - terminalreporter._sessionstarttime, 2)
    MessageConstructor.send_ding_msg(cases, case_pass, case_fail, case_error, case_skip, case_time)

