#!/usr/bin/env python
# -*- coding:utf-8 -*-

# *********************************************************#
# @@Author: 张xx
# @@Create Date: 2021/10/12 10:44
# @@Modify Date: 2021/10/12 10:44
# @@Description: 登录
# *********************************************************#

from app.core.methods import *
from app.core.generator import Genetator

@allure.epic("测试用例")
@allure.feature("登录")
@pytest.mark.skipif(env in ['RELEASE'], reason='线上环境不执行')
class Test_Login(object):

    @login_decorator
    def setup_class(self):
        Log().info('测试用例开始执行')

    @allure.story("各项目登录")
    @allure.title('{title}')
    @pytest.mark.parametrize('case_id, title', MysqlConstructor.parameterization_data('base_login', 'zmm-1.0'))
    def test_login(self, case_id, title):
        Genetator.global_generator(table_name='base_login', case_id=case_id)

    def teardown_class(self):
        Log().info('测试用例执行完毕')
        Log().info('----------------------------------' + '\n')
