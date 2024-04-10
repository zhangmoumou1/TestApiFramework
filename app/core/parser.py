#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *********************************************************#
# @@Author: 张某某
# @@Create Date: 2021-03-25 22:24:14
# @@Description: 解析处理##xx##，{{xxx}}
# @@Copyright © 91duobaoyu, Inc. All rights reserved.
# *********************************************************#
from app.core.methods import Log
class ParserJson(object):
    """
    从json中取出指定值
    """
    list_value = []

    @staticmethod
    def parser_json(dic_json, key):
        """
        相对路径解析json，jsonpath_rela.xxx
        :param: dic_json 被处理的json
        :param: k 对应的key
        """
        try:
            if isinstance(dic_json, dict):
                for key_one in dic_json:
                    if key_one == key:
                        ParserJson.list_value.append(dic_json[key_one])
                    elif isinstance(dic_json[key_one], list):
                        for a in dic_json[key_one]:
                            ParserJson.parser_json(a, key)
                    elif isinstance(dic_json[key_one], dict):
                        ParserJson.parser_json(dic_json[key_one], key)
        except Exception as e:
            Log().error(f'<<响应提取>>使用相对路径提取[{key}]值失败，json中不存在此字段：{e}')
            raise

    @staticmethod
    def json_relative(dic_json, key):
        """
        处理json取出的值
        param: dic_json 接口响应结果
               key 要查看的key
        return:
            key  默认取第1个值
            key.0 取第1个值
            key.2 取第2个值
            key.all 取所有值，列表的形式
        """
        try:
            ParserJson.parser_json(dic_json, key)
            if len(ParserJson.list_value) == 0:
                return f'<<响应提取>>使用相对路径提取[{key}]值失败，json中不存在此字段'
            elif len(ParserJson.list_value) == 1:
                return ParserJson.list_value[0]
            else:
                if '.' not in key:
                    return ParserJson.list_value[0]
                elif key.split('.')[-1] == 'all':
                    return ParserJson.list_value
                elif isinstance(key.split('.')[-1], int):
                    if int(key.split('.')[-1]) == 0:
                        return ParserJson.list_value[0]
                    else:
                        return ParserJson.list_value[int(key.split('.')[-1]) - 1]
                else:
                    return ParserJson.list_value[0]
        except Exception as e:
            Log().error(f'<<响应提取>>使用相对路径提取[{key}]值失败，请检查书写格式是否正确：{e}')
            return f'<<响应提取>>使用相对路径提取[{key}]值失败，请检查书写格式是否正确'
        finally:
            ParserJson.list_value = []

    @staticmethod
    def json_absolute(dic_json, paths):
        """
        使用绝对路径进行提取
        :param dic_json:
        :param path: jsonpath_abs.xxx.xxx.xxx
        :return:
        """
        try:
            global deal_data
            deal_data = dic_json
            if '.' in paths:
                data_end = paths.split('.', 1)
                for path in data_end[-1].split('.'):
                    if path.isdigit() is True:
                        deal_data = deal_data[int(path)]
                    else:
                        deal_data = deal_data[path]
            else:
                if paths.isdigit() is True:
                    deal_data = deal_data[int(paths)]
                else:
                    deal_data = deal_data[paths]
            return deal_data
        except Exception as e:
            Log().error(f'<<响应提取>>使用绝对路径提取失败<{paths}>，请检查书写格式是否正确：{e}')
            return f'<<响应提取>>使用绝对路径提取失败<{paths}>，请检查书写格式是否正确'
        finally:
            ParserJson.list_value = []

from app.core.methods import re


def replace_specific(func):
    """
    处理{{xxx}}
    :param func:
    :return:
    """
    def inner(str):
        if ('{{' in str) and ('}}' in str):
            specific_list = re.findall("{{(.+?)}}", str)
            if len(specific_list) == 1:
                func(specific_list[0])
            else:
                raise '1111111111'
    return inner

@replace_specific
def aa(cc):
    print(cc)


if __name__ == "__main__":
    # aa('{{xxx}}')
    # aa = {"aa": 111111, "bb":22222222, "cc": [{"dd": 444, "aa": 55}]}
    # bb = ParserJson.json_value_result(aa, 'aa')
    # print(bb)
    aa = {
    "acId": 53,
    "acName": "i云保",
    "activityCommission": False,
    "baseCommission": False,
    "dealTime": "2023-04-23",
    "dealWay": "顾问成交",
    "icId": 12,
    "icName": "众安在线财产保险股份有限公司1",
    "insureAmount": None,
    "isSalaried": False,
    "isSelfInsuredComponent": "",
    "orderItemParamDto": [{
        "sort": "",
        "productList": [],
        "product": {
            "icId": 12,
            "icName": "众安在线财产保险股份有限公司1",
            "type": 4,
            "productId": 10807,
            "productName": "爱心人寿守护神长期意外险",
            "acId": None,
            "acName": None,
            "settleType": None,
            "productType": 0,
            "hesitateTime": None,
            "productCode": None,
            "paymentType": None,
            "typeCode": None,
            "checkstandType": None,
            "acCode": None,
            "pcId": 784,
            "saleType": None,
            "dealType": 0,
            "exemptionType": None,
            "ageDiscount": False
        },
        "productType": 0,
        "type": 4,
        "productCode": "",
        "planCode": "",
        "insureAmount": "",
        "insurancePremium": "100",
        "insureDuration": "终身",
        "paymentMethod": "一次交清",
        "insurancePremiumConvert": "10",
        "commission": "10",
        "activityCommission": "10",
        "stepCommission": 0,
        "productId": 10807,
        "productName": "爱心人寿守护神长期意外险",
        "pcId": 784
    }],
    "payTimes": "1",
    "paymentMethodType": 1,
    "policyCancellation": False,
    "policyNumber": "zhangyc000",
    "policyType": "1",
    "policyYear": "1",
    "salariedMonth": "",
    "insuredInfos": [{
        "name": "ddd",
        "idCardType": "1",
        "idCard": "330726199603094422"
    }],
    "applicantInfo": {
        "name": "ddd",
        "idCardType": "1",
        "idCard": "330726199603094422",
        "mobile": "15868167543"
    }
}
    ParserJson.json_absolute(aa, 'jsonpath_abs.orderItemParamDto.0.product.icName')