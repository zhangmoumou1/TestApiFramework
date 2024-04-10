#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *********************************************************#
# @@Author: 张某某
# @@Create Date: 2021-03-25 22:24:14
# @@Description: http请求生成器
# @@Copyright © 91duobaoyu, Inc. All rights reserved.
# *********************************************************#
from app.core.methods import requests, json, Log, response_decorator

class HttpGenerator(object):

    _slots__ = ['headers', 'url', 'data', 'timeout']
    def __init__(self, http_way, url, header, data, timeout=20):
        self.http_way = http_way
        self.header = header
        self.url = url
        self.data = data
        self.timeout = timeout

    @property
    def data(self):
        return self._data

    @property
    def http_way(self):
        return self._http_way

    @data.setter
    def data(self, value):
        try:
            if value is None or value == '':
                self._data = json.dumps({})
            # elif isinstance(json.loads(value), dict):
            #     self._data = value
            else:
                self._data = value
        except:
            self._data = value
            Log().error(f'<<http请求>>传参{value}有误，请检查数据库用例写法是否正确')

    @http_way.setter
    def http_way(self, way):
        try:
            if way not in ['get', 'post', 'put', 'delete', 'GET', 'POST', 'PUT', 'DELETE']:
                Log().warning(f'<<http请求>>请求方式{way}有误，请检查数据库用例写法是否正确，仅支持GET/POST/PUT/DELETE')
            else:
                self._http_way = way
        except:
            Log().error(f'<<http请求>>请求方式{way}有误，请检查数据库用例写法是否正确，仅支持GET/POST/PUT/DELETE')

    def __call__(self):
        # Log().info(f'<<发起{self.http_way.lower()}请求>>\n'
        #            f'地 址：{self.url}\n'
        #            f'请求头：{self.header}\n'
        #            f'传 参：{self.data}\n')
        try:
            if self.http_way.lower() == 'get':
                response = self.__get_generator()
            elif self.http_way.lower() == 'post':
                response = self.__post_generator()
            elif self.http_way.lower() == 'put':
                response = self.__put_generator()
            elif self.http_way.lower() == 'delete':
                response = self.__delete_generator()
            log_title = f'{self.http_way.lower()}接口请求成功'
            log = f'{json.dumps(response, ensure_ascii=False)}'
            Log().info(f'<<{log_title}>>{log}')
            return response
        except Exception as e:
            log_title = f'self.http_way.lower()接口请求失败'
            log = f'{json.dumps(response)}。{e}'
            Log().error(f'<<{log_title}>>{log}')
        finally:
            # from app.core.normal_generator import NormalGenarator
            # NormalGenarator.allure_step(log_title, log)
            pass

    @response_decorator('get')
    def __get_generator(self):
        """
        get请求
        :return:
        """
        try:
            res = requests.get(url=self.url, headers=self.header, params=self.data.encode('utf-8'), timeout=self.timeout)
            return res
        except requests.exceptions.ConnectTimeout:
            Log().error(f'<<post请求失败>>\n'
                        f'请求超时timeout：{res}')

    @response_decorator('post')
    def __post_generator(self):
        """
        post请求
        :return:
        """
        try:
            res = requests.post(url=self.url, headers=self.header, data=self.data.encode('utf-8'), timeout=self.timeout)
            return res
        except requests.exceptions.ConnectTimeout as e:
            Log().error(f'<<post请求失败>>\n'
                        f'请求超时timeout：{e}')

    @response_decorator('put')
    def __put_generator(self):
        """
        put请求
        :return:
        """
        try:
            res = requests.put(url=self.url, headers=self.header, data=self.data.encode('utf-8'), timeout=self.timeout)
            return res
        except requests.exceptions.ConnectTimeout:
            Log().error(f'<<put请求失败>>\n'
                        f'请求超时timeout：{res}')

    @response_decorator('delete')
    def __delete_generator(self):
        """
        delete请求
        :return:
        """
        try:
            res = requests.delete(url=self.url, headers=self.header, data=self.data.encode('utf-8'), timeout=self.timeout)
            return res
        except:
            Log().error(f'<<delete请求失败>>\n'
                        f'请求超时timeout：{res}')


if __name__ == "__main__":
    header = {
        'content-type': 'application/json; charset=UTF-8',
        'X-Ca-Stage': 'TEST',
        'moduleid': '1858',
        'token': '6557afd0-81da-4f4f-8816-d33fe3326909'
    }
    url = 'https://gw2.91duobaoyu.com/managergateway/customercore/v1/customer/list.do'
    data = '{"bizPhase":"","intentionLevel":"","followType":"","beginCreatedTime":"","endCreatedTime":"","beginUpdatedTime":"","endUpdatedTime":"","beginNextPlanningTime":"","endNextPlanningTime":"","userKey":"","empIds":[],"tags":[],"orgIds":[],"sortedRules":[],"pageSize":10,"currentPage":1}'

    HttpGenerator('POST', url, header, json.dumps(data), 2).__call__()