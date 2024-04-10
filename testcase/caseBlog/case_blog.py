#!/usr/bin/env python
# -*- coding:utf-8 -*-

# *********************************************************#
# @@Author: 张xx
# @@Create Date: 2021/10/12 10:44
# @@Modify Date: 2021/10/12 10:44
# @@Description: 测试用例举例
# *********************************************************#

from app.core.methods import *

@allure.epic("测试用例")
@allure.feature("博客项目")
@pytest.mark.skipif(env in ['RELEASE'], reason='线上环境不执行')
class TestExample():

    @login_decorator
    def setup_class(self):
        Log().debug('----------------------【测试用例开始执行】----------------------')

    @allure.story("文章管理")
    @allure.title('{title}')
    @pytest.mark.parametrize('case_id, title, table_name', MysqlConstructor.parameterization_data('article', 'zmm-1.0#zmm-1.4'))
    def test_example(self, case_id, title, table_name):
        Genetator.global_generator(table_name=table_name, case_id=case_id)

    def teardown_class(self):
        Log().debug('-----------------------【测试用例执行完毕】-----------------------\n')
