#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @@Author: 张某某
# @@Create Date: 2023/02/16 10:28
# @@Description: 装饰器
# @@Copyright © zhangmoumou, Inc. All rights reserved.
from app.core.methods import json, Log, platform
def response_decorator(info):
    """
    接口响应装饰器，用于处理响应结果
    """
    def outer(func):
        def inner(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
                if res.status_code == 200:
                    if 'code' in json.loads(res.text):
                        text = json.loads(res.text)
                        if text['code'] == '401':
                            Log().warning(f'<<{info}请求异常>>'
                                          f'token已过期：{res.text}')
                            # 重新调用登录接口
                            Log().info(f'----------------------登录失效，重新获取token-------------------------')
                            from app.utils.mysql_constructor import MysqlConstructor
                            from app.core.generator import Genetator
                            case_ids = MysqlConstructor.parameterization_data('base_login', 'all')
                            for case_id in case_ids:
                                Genetator.global_generator(table_name='base_login', case_id=case_id[0])
                        if text['code'] == '404':
                            Log().warning(f'<<{info}请求异常>'
                                          f'接口地址有误：{res.text}')
                        elif '50' in text['code']:
                            Log().warning(f'<<{info}请求异常>>'
                                          f'服务/系统异常：{res.text}')
                        else:
                            pass
                            # Log().info(f'<<{info}请求成功>>'
                            #            f'{res.text}')
                        return text
                    else:
                        text = json.loads(res.text)
                        return text
                elif res.status_code == 404:
                    Log().warning(f'<<{info}请求失败>>'
                                  f'接口地址有误：{res}')
                    raise
                else:
                    Log().warning(f'<<{info}请求失败>>'
                                  f'{res}')
                    raise
            except Exception as e:
                Log().error(f'<<{info}请求失败>>'
                                  f'{e}')
                raise
        return inner
    return outer


def login_decorator(func):
    """
    登录装饰器，在非linux服务器上运行用例，前置处先获取token
    :param func:
    :return:
    """
    def wrapper(self):
        SYSTEM_VERSION = platform.platform()
        if 'Linux' not in SYSTEM_VERSION:
            Log().critical(f'\n')
            Log().critical(f'-------------------开始获取登录信息[base_login表]-------------------')
            from app.utils.mysql_constructor import MysqlConstructor
            from app.core.generator import Genetator
            case_ids = MysqlConstructor.parameterization_data('base_login', 'all')
            for case_id in case_ids:
                Genetator.global_generator(table_name='base_login', case_id=case_id[0], logFlag=True)
            Log().critical(f'-----------------------获取登录信息结束-----------------------\n')
        func(self)
    return wrapper
