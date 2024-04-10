#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *********************************************************#
# @@Author: 张某某
# @@Create Date: 2021-03-25 22:24:14
# @@Description: 登录请求生成器
# @@Copyright © 91duobaoyu, Inc. All rights reserved.
# *********************************************************#

from app.core.methods import HttpGenerator, env, YamlConstructor, json, Log
class LoginGenerator():

    headers = {
        'content-type': 'application/json; charset=UTF-8',
        'X-Ca-Stage': env
    }
    @staticmethod
    def login_base(project, type_way):
        """
        账密登录、token写死、短验登录
        :param project:项目名称
        :param type:项目类型 Web、App、Wx
        :param way:登录方式 userpwd、token、mobile_code
        :return:
        """
        login_info = YamlConstructor.get_base_info(project)
        login_url = login_info['base_url'] + login_info['login_url']
        data = login_info['login_params']
        try:
            way = type_way.split('-')[-1]
            if way == 'userpwd':
                # 账密登录方式，获取token
                info = YamlConstructor.get_base_info(project)
                username, password = info['user'], info['pwd']
                data.update({'username': username, 'password': password})
                login_res = HttpGenerator('POST', login_url, LoginGenerator.headers, json.dumps(data)).__call__()
                token = login_res['data']['token']
                log = f'使用账密方式登录成功，账号：{username}，密码：{password}，token：{token}'
            elif way == 'token':
                # 直接获取写死的token
                token = YamlConstructor.get_login_info(project, type)['token']
                log = f'写死token：{token}'
            elif way == 'mobile_code':
                # 通过手机号验证码登录获取token，具体逻辑按照自身功能来实现（一般先调取获取验证码接口然后验证码登录或者直接写死验证码登录）
                info = YamlConstructor.get_login_info(project, type)
                mobile, code = info['mobile'], info['code']
                ###具体实现按照自身情况而定###
                """
                实现步骤，最后返回token
                """
                ###具体实现按照自身情况而定###
                token = 'xxxxxx'
                log = f'使用短验方式登录成功，手机号：{mobile}，验证码：{code}，token：{token}'
            Log().info(
                f'<<获取token>>\n'
                f'{env}环境{type_way}类型{project}项目, {log}')
            return token
        except Exception as e:
            Log().error(f'<<获取token>>\n'
                            f'{env}环境{type_way}类型{project}项目，[登录信息：{info}]获取token失败：{e}')
            return 'not exist token'


if __name__ == "__main__":
    LoginGenerator.login_base('project_name', 'Web')
