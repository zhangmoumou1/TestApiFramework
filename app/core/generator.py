#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *********************************************************#
# @@Author: 张某某
# @@Create Date: 2021-03-25 22:24:14
# @@Description: 请求生成器，组成完成的功能
# @@Copyright © 91duobaoyu, Inc. All rights reserved.
# *********************************************************#

from app.core.methods import HttpGenerator, env, MysqlConstructor, Log, YamlConstructor, NormalGenarator, AssertConstructor

class Genetator(object):
    """
    请求生成器
    """
    # project = 'project_name'
    # type = 'Wx'
    # way = 'token'
    @staticmethod
    def global_generator(table_name, case_id, logFlag=False):
        """
        主调度入口：获取用例数据->生成请求头->生成接口url->生成传参->处理前置->发起请求->处理后置->断言
        """
        case_data = (Genetator.case_reader(table_name, case_id))
        # 当api_way为空，则此条用例不进行接口请求
        if case_data['api_way'] in [None, '']:
            Genetator.post_genetator(case_data, '')
        else:
            Genetator.preset_genetator(case_data)
            headers = Genetator.header_genetator(case_data)
            url = Genetator.url_genetator(case_data)
            data = Genetator.body_genetator(case_data)
            response = HttpGenerator(case_data['api_way'], url, headers, data).__call__()
            Genetator.post_genetator(case_data, response)
            Genetator.assert_genetator(response, case_data)
            # 优化控制台日志：执行登录用例和引用历史用例时，不执行下列日志
            if logFlag is True:
                pass
            else:
                Log().info('\n\n')

    @staticmethod
    def case_reader(table_name, case_id):
        """
        读取用例数据
        """
        try:
            case_data = MysqlConstructor.single_case_detail(table_name, case_id)
            log_title = '获取用例数据成功'
            log = f'获取{table_name}.id={case_id}的用例数据成功，{case_data}'
            Log().info(f'<<{log_title}>>{log}')
            return case_data
        except Exception as e:
            log_title = '获取用例数据失败'
            log = f'<<获取用例数据>>获取{table_name}.id={case_id}的用例数据失败，{case_data}。Exception：{e}'
            Log().error(f'<<{log_title}>>{log}')
        finally:
            # NormalGenarator.allure_step(log_title, log)
            pass
    @staticmethod
    def header_genetator(data):
        """
        请求头生成器
        :return:
        """
        project, add_header = data['project_name'], data['headers']
        headers = {
            'content-type': 'application/json; charset=UTF-8',
            'X-Ca-Stage': env
        }
        # 无值时，需要传入token
        # if add_headers not in [None, '']:
        #     headers['token'] = LoginGenerator.login_base(project, type_way)
        try:
            # 如果请求头字段有数据，请求头合并
            if add_header not in [None, '']:
                handle_add_header = NormalGenarator.obtain_global_variable_any(add_header)
                add_headers = NormalGenarator.header_generator(handle_add_header)
                headers.update(add_headers)
            log_title = '请求头设置成功'
            log = f'{headers}'
            Log().info(f'<<{log_title}>>{log}')
            return headers
        except Exception as e:
            log_title = '请求头设置失败'
            log = f'<<请求头>>请求头设置失败。Exception：{e}'
            Log().error(f'<<{log_title}>>{log}')
        finally:
            # NormalGenarator.allure_step(log_title, log)
            pass

    @staticmethod
    def url_genetator(data):
        """
        请求地址生成器
        :return:
        """
        try:
            base_url = YamlConstructor.get_base_info(data['project_name'])['base_url']
            preanalytic_url = NormalGenarator.obtain_global_variable_any(data['case_url'])
            api_url = base_url + preanalytic_url
            log_title = '获取接口地址成功'
            log = f'{api_url}'
            Log().info(f'<<{log_title}>>{log}')
            return api_url
        except Exception as e:
            log_title = '获取接口地址失败'
            log = f'<<接口地址>>获取接口地址失败，{data["case_url"]}。Exception：{e}'
            Log().error(f'{log}')
        finally:
            # NormalGenarator.allure_step(log_title, log)
            pass
    @staticmethod
    def preset_genetator(data):
        """
        前置条件生成器
        :return:
        """
        project, preset_values = data['project_name'], data['prepose_control']
        NormalGenarator.save_global_variable_any(project, preset_values, flag='preposition')

    @staticmethod
    def post_genetator(data, post_result):
        """
        后置生成器
        :return:
        """
        project, post_values = data['project_name'], data['postpose_control']
        NormalGenarator.save_global_variable_any(project, post_values, post_result, flag='postposition')

    @staticmethod
    def body_genetator(data):
        """
        请求体生成器
        :return:
        """
        try:
            body = NormalGenarator.obtain_global_variable_any(data['case_param'])
            log_title = '获取传参成功'
            log = f'{body}'
            Log().info(f'<<{log_title}>>{log}')
            return body
        except Exception as e:
            log_title = '获取传参失败'
            log = f'获取传参失败，{data["case_param"]}。Exception：{e}'
            Log().error(f'<<{log_title}>>{log}')
        finally:
            # NormalGenarator.allure_step(log_title, log)
            pass


    @staticmethod
    def assert_genetator(response, data):
        """
        断言生成器
        :return:
        """
        if AssertConstructor.assert_verify(response, data['assert']) is False:
            raise '断言失败，请及时排查具体原因（接口缺陷/期望值书写有误等！！！）'

if __name__ == "__main__":


    Genetator.global_generator('baseprocess', 'back-zyc-8.0')
