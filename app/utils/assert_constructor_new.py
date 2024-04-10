#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @@Author: 张某某
# @@Create Date: 2023/02/16 10:28
# @@Description: 接口断言功能构造，可忽略指定字段报错、字段顺序、字段大小写
# @@Copyright © zhangmoumou, Inc. All rights reserved.
from app.core.methods import DeepDiff, Log, re, json


class AssertConstructor(object):
    """
    可进行全字段校验，校验多次
    断言内容：相等(排序生效;类型生效;root['applicantInfo']['mobile'])**{xxx}**;包含**{xxx}**
    """

    @staticmethod
    def check_order_case(settings_text):
        """
        区分排序和大小写
        """
        try:
            if '排序生效' in settings_text and '大小写生效' in settings_text:
                ignore_order, ignore_type = True, True
            elif '排序生效' in settings_text and '大小写生效' not in settings_text:
                ignore_order, ignore_type = True, False
            elif '排序生效' not in settings_text and '大小写生效' in settings_text:
                ignore_order, ignore_type = False, True
            elif '排序生效' not in settings_text and '大小写生效' not in settings_text:
                ignore_order, ignore_type = False, False
            else:
                ignore_order, ignore_type = False, False
        except:
            ignore_order, ignore_type = False, False
        finally:
            return ignore_order, ignore_type
    @staticmethod
    def assert_verify(actual, assert_text):
        """
        处理多个断言数据格式
        相等(排序生效,大小写生效,root['applicantInfo']['mobile'])$${xxx}$$;包含**{xxx}**
        """
        if assert_text in ['', None]:
            raise '断言内容不能为空'
        results = ''
        for text in assert_text.split(';;'):
            # 不存在校验类型跳过
            if '相等(' in text and ')&&' in text:
                settings_match = text.split('&&')[0]
                settings_text = settings_match.replace('相等(', '').replace(')', '')
                # 校验指定设置
                order_case = AssertConstructor.check_order_case(settings_text)
                ignore_order, ignore_type = order_case[0], order_case[-1]
                specify = list()
                for settings in settings_text.split(','):
                    if 'root' in settings:
                        specify.append(settings)
                assert_match = json.loads((re.findall("&&(.+?)&&", text)[0]).replace("'", '"'))
                result = AssertConstructor.assert_equal(actual, assert_match, ignore_order, ignore_type, specify)
            elif '包含(' in text and ')&&' in text:
                settings_match = text.split('&&')[0]
                settings_text = settings_match.replace('包含(', '').replace(')', '')
                # 校验指定设置
                order_case = AssertConstructor.check_order_case(settings_text)
                ignore_order, ignore_type = order_case[0], order_case[-1]
                specify = list()
                for settings in settings_text.split(','):
                    if 'root' in settings:
                        specify.append(settings)
                assert_match = json.loads((re.findall("&&(.+?)&&", text)[0]).replace("'", '"'))
                result = AssertConstructor.assert_contain(actual, assert_match, ignore_order, ignore_type, specify)
            elif '相等' in text and '&&' in text:
                # 不填写规则，顺序和字母大小写校验默认忽略
                ignore_order, ignore_type, specify = True, True, []
                assert_match = (re.findall("&&(.+?)&&", text)[0]).replace("'", '"')
                result = AssertConstructor.assert_equal(actual, assert_match, ignore_order, ignore_type, specify)
            elif '包含' in text and '&&' in text:
                # 不填写规则，顺序和字母大小写校验默认忽略
                ignore_order, ignore_type, specify = True, True, []
                assert_match = json.loads((re.findall("&&(.+?)&&", text)[0]).replace("'", '"'))
                result = AssertConstructor.assert_contain(actual, assert_match, ignore_order, ignore_type, specify)
            results += result
        # 断言成功
        if results == '':
            Log().info(f'<<断言结果>>对【期望字段】断言成功')
            import allure
            allure.attach(
                body=f'<<断言结果>>对【期望字段】断言成功',
                name="断言结果",
                attachment_type=allure.attachment_type.TEXT
            )
        # 断言失败
        else:
            aseert_base = f'<<断言结果>>断言失败，结果如下：\n' \
                          f'{results}'
            Log().warning(aseert_base)

    @staticmethod
    def assert_equal(actuals, expects, order=False, string_case=False, exclude_paths=None):
        """
        校验期望和实际所有字段相等，则通过
        可忽略字段顺序(默认忽略)、字母大小写(默认忽略)、指定字段
        报错类型：type_changes：类型改变的key
                values_changed：值发生变化的key
                dictionary_item_added：字典key添加
                dictionary_item_removed：字段key删除
        :return:
        """
        result = DeepDiff(actuals, expects, view='tree', ignore_order=order, ignore_string_case=string_case,
                          exclude_paths=exclude_paths)
        # 没有差异，则断言成功
        flag = [i for i in ['dictionary_item_removed', 'type_changes', 'values_changed', 'values_changed'] if i in result]
        if result == {} or flag == []:
            return ''
        else:
            global errors
            errors = str()
            # 实际里面不存在字段
            if 'dictionary_item_added' in result:
                actual_exist = result['dictionary_item_added']
                error_str = str()
                for num in range(len(actual_exist)):
                    # 如果报错字段大于指定个数，防止日志过长，停止打印
                    if num > 10:
                        error_str += '......**报错过多详见接口响应**'
                        break
                    actual_error = actual_exist[num]
                    # 去掉字段路径
                    # re_strs = re.findall("root(.+?) t1:", str(actual_error))
                    # replace_old = re_strs[0]
                    # replace_new = replace_old.split('[')[-1].replace(']', '')
                    error_str += str(actual_error)
                error = f'实际值内不存在，期望值内存在的字段【{error_str}】\n'
                errors += error
            # 期望里面不存在字段
            if 'dictionary_item_removed' in result:
                expect_exist = result['dictionary_item_removed']
                error_str = str()
                for num in range(len(expect_exist)):
                    # 如果报错字段大于指定个数，防止日志过长，停止打印
                    if num > 10:
                        error_str += '......**报错过多详见接口响应**'
                        break
                    actual_error = expect_exist[num]
                    error_str += str(actual_error)
                error = f'实际值内存在，期望值内不存在的字段【{error_str}】\n'
                errors += error
            # 格式不一致
            if 'type_changes'in result:
                type_error = result['type_changes']
                error_str = str()
                for num in range(len(type_error)):
                    # 如果报错字段大于指定个数，防止日志过长，停止打印
                    if num > 10:
                        error_str += '......**报错过多详见接口响应**'
                        break
                    actual_error = type_error[num]
                    error_str += str(actual_error)
                error = f'字段格式类型不一致【{error_str}】\n'
                errors += error
            # 字段值不一致
            if 'values_changed' in result:
                values_error = result['values_changed']
                error_str = str()
                for num in range(len(values_error)):
                    # 如果报错字段大于指定个数，防止日志过长，停止打印
                    if num > 10:
                        error_str += '......**报错过多详见接口响应**'
                        break
                    actual_error = values_error[num]
                    error_str += str(actual_error)
                error = f'字段值不一致【{error_str}】\n'
                errors += error
            struct_error = errors.replace('root', '路径').replace('><路径', '>；<路径').replace('t1', '实际').\
                replace('t2', '期望').replace('not present', '不存在')
            return struct_error

    @staticmethod
    def assert_contain(actuals, expects, order, string_case, exclude_paths):
        """
        校验期望在实际值内存在则通过
        :return:
        """
        result = DeepDiff(actuals, expects, view='tree', ignore_order=order, ignore_string_case=string_case,
                          exclude_paths=exclude_paths)
        # 没有差异或者只返回dictionary_item_removed，则断言成功
        flag = [i for i in ['dictionary_item_removed', 'dictionary_item_added', 'type_changes', 'values_changed', 'values_changed'] if i in result]
        Log().error(f'{flag}')
        if result == {}:
            return ''
        else:
            global errors
            errors = str()
            # 实际里面不存在字段
            if 'dictionary_item_added' in result:
                actual_exist = result['dictionary_item_added']
                error_str = str()
                for num in range(len(actual_exist)):
                    # 如果报错字段大于指定个数，防止日志过长，停止打印
                    if num > 10:
                        error_str += '......**报错过多详见接口响应**'
                        break
                    actual_error = actual_exist[num]
                    # 去掉字段路径
                    # re_strs = re.findall("root(.+?) t1:", str(actual_error))
                    # replace_old = re_strs[0]
                    # replace_new = replace_old.split('[')[-1].replace(']', '')
                    error_str += str(actual_error)
                error = f'实际值内不存在期望值【{error_str}】\n'
                errors += error
            # 格式不一致
            if 'type_changes' in result:
                type_error = result['type_changes']
                error_str = str()
                for num in range(len(type_error)):
                    # 如果报错字段大于指定个数，防止日志过长，停止打印
                    if num > 10:
                        error_str += '......**报错过多详见接口响应**'
                        break
                    actual_error = type_error[num]
                    error_str += str(actual_error)
                error = f'字段格式类型不一致【{error_str}】\n'
                errors += error
            # 字段值不一致
            if 'values_changed' in result:
                values_error = result['values_changed']
                error_str = str()
                for num in range(len(values_error)):
                    # 如果报错字段大于指定个数，防止日志过长，停止打印
                    if num > 10:
                        error_str += '......**报错过多详见接口响应**'
                        break
                    actual_error = values_error[num]
                    error_str += str(actual_error)
                error = f'字段值不一致【{error_str}】\n'
                errors += error
            struct_error = errors.replace('root', '路径').replace('><路径', '>；<路径').replace('t1', '实际'). \
                replace('t2', '期望').replace('not present', '不存在')
            return struct_error

    @staticmethod
    def assert_exist(actuals, expects, use_regexp, strict_checking, case_sensitive):
        """
        actuals: 实际
        expects: 期望
        use_regexp: 使用正则表达式
        strict_checking: 对象类型强校验
        case_sensitive: 大小写敏感
        """


if __name__ == "__main__":
    actual = {'success': True, 'code': '200', 'data': [{'fsUserId': 'fs_293281997005131776', 'cardNo': '202305271262994896'}], 'pageInfo': {'pageSize': 20}}
    expect = {'fsUserId': 'fs_293281997005131776'}
    # print(AssertConstructor.assert_contain(actual, expect))
    # AssertConstructor.assert_contain(expect, actual, order=True, string_case=True, exclude_paths=[])
    # AssertConstructor.assert_detail()
    # AssertConstructor.assert_verify(actual1, "相等(排序生效,大小写生效,root['applicantInfo']['mobile'],root['applicantInfo']['idCard'])&&{'aa':11, 'bb': 22}&&;;包含(排序生效)&&{'aa':11, 'bb': 22}&&")
    # print('--------------------')
    AssertConstructor.assert_verify(actual, '包含&&{"data": [{"fsUserId": "fs_2932819970051317761", "cardNo": "2023052712629948961"}]}&&')

    # aa = {None}
    # bb = {'11', '22'}
    # aa.update(bb)
    # aa.pop(None)
    # print(aa)
    # def case_03():
    #     datas = {"mikezhou": "狂师", "age": 18, "city": "china", "info": {"author": {"tag": "mikezhou"}}}
    #     item = 18
    #     ds = DeepSearch(datas, item, strict_checking=False)
    #     print(ds)
    # case_03()
    #
    # aa = DeepDiff(actual, {'data': [{'fsUserId': 'fs_2932819970051317761'}]}, view='tree', ignore_order=True, ignore_string_case=True,
    #          exclude_paths=[])
    # print(aa)
    #
    # aa = '{"data": [{"fsUserId": "fs_293281997005131776", "cardNo": "202305271262994896"}]}'
    # bb = json.loads(aa)
    # print(type(bb))