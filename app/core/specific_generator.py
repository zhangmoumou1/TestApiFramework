#!/usr/bin/env python
# -*- coding:utf-8 -*-
# *********************************************************#
# @@Author: 张某某
# @@Create Date: 2021-03-25 22:24:14
# @@Description: 自定义写法生成替换，{{xxxx}}
# @@Copyright © 91duobaoyu, Inc. All rights reserved.
# *********************************************************#

from app.core.methods import datetime, re, time, calendar, Log, string, random

class SpecificGenerator(object):

    def __call__(self, values):
        return SpecificGenerator.main_generator(values)

    @staticmethod
    def main_generator(values):
        """
        处理入口
        :param values:
        :return:
        """
        global original_data
        original_data = values
        if ('{{' in values) and ('}}' in values):
            specific_list = re.findall("{{(.+?)}}", values)
            for specific_str in specific_list:
                if '截止' in specific_str:
                    parser_data = SpecificGenerator.__time_generator(specific_str)
                elif 'mobile' in specific_str:
                    parser_data = SpecificGenerator.__mobile_generator(specific_str)
                elif 'number' in specific_str and '-' in specific_str:
                    parser_data = SpecificGenerator.__random_with_size_generator(specific_str)
                elif 'number' in specific_str and '-' not in specific_str:
                    parser_data = SpecificGenerator.__random_with_long_generator(specific_str)
                else:
                    Log().error(f'<<用例数据解析替换>>[{specific_str}]生成内容失败，请检查格式是否正确')
                    parser_data = values
                original_data = original_data.replace('{{' + specific_str + '}}', parser_data)
        else:
            original_data = values
        return original_data
    @staticmethod
    def __time_generator(values):
        """
        生成指定时间，如{{日截止-1}}
        :param values: 日截止-1
        :return:
        """
        try:
            now_time = datetime.datetime.now()
            if '+' in values:
                value = values.split('+')
                number = int(value[-1][:-1])
                if value[0] == '秒截止':
                    if 's' in value[1]:
                        times = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + number))
                    elif 'm' in value[1]:
                        times = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + number * 60))
                    elif 'h' in value[1]:
                        times = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + number * 3600))
                    elif 'd' in value[1]:
                        times = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + number * 3600 * 24))
                    elif 'M' in value[1]:
                        time1 = datetime.datetime(month=now_time.month + number, year=now_time.year,
                                                  day=now_time.day, hour=now_time.hour, minute=now_time.minute)
                        times = time1.strftime('%Y-%m-%d %H:%M:%S')
                    elif 'Y' in value[1]:
                        time1 = datetime.datetime(month=now_time.month, year=now_time.year + number,
                                                  day=now_time.day, hour=now_time.hour, minute=now_time.minute)
                        times = time1.strftime('%Y-%m-%d %H:%M:%S')
                elif value[0] == '分截止':
                    if 's' in value[1]:
                        times = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() + number))
                    elif 'm' in value[1]:
                        times = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() + number * 60))
                    elif 'h' in value[1]:
                        times = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() + number * 3600))
                    elif 'd' in value[1]:
                        times = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() + number * 3600 * 24))
                    elif 'M' in value[1]:
                        time1 = datetime.datetime(month=now_time.month + number, year=now_time.year,
                                                  day=now_time.day, hour=now_time.hour, minute=now_time.minute)
                        times = time1.strftime('%Y-%m-%d %H:%M')
                    elif 'Y' in value[1]:
                        time1 = datetime.datetime(month=now_time.month, year=now_time.year + number,
                                                  day=now_time.day, hour=now_time.hour, minute=now_time.minute)
                        times = time1.strftime('%Y-%m-%d %H:%M')

                elif value[0] == '日截止':
                    if 'd' in value[1]:
                        times = time.strftime('%Y-%m-%d', time.localtime(time.time() + number * 3600 * 24))
                    elif 'M' in value[1]:
                        time1 = datetime.datetime(month=now_time.month + number, year=now_time.year,
                                                  day=now_time.day)
                        times = time1.strftime('%Y-%m-%d')
                    elif 'Y' in value[1]:
                        time1 = datetime.datetime(month=now_time.month, year=now_time.year + number,
                                                  day=now_time.day)
                        times = time1.strftime('%Y-%m-%d')
                elif value[0] == '月截止':
                    if 'M' in value[1]:
                        # 获取指定月的天数，可能会存在超出天数的情况
                        if now_time.month - number <= 0:
                            new_year = now_time.year - 1
                            new_month = 12 - (now_time.month - number)
                        else:
                            new_year = now_time.year
                            new_month = now_time.month - number
                        monthRange = calendar.monthrange(new_year, new_month)
                        if monthRange[-1] < now_time.day:
                            day = monthRange[-1]
                        else:
                            day = now_time.day
                        time1 = datetime.datetime(month=now_time.month + number, year=day,
                                                  day=now_time.day)
                        times = time1.strftime('%Y-%m')
                    elif 'Y' in value[1]:
                        time1 = datetime.datetime(month=now_time.month, year=now_time.year + number,
                                                  day=now_time.day)
                        times = time1.strftime('%Y-%m')
                elif value[0] == '年截止':
                    if 'Y' in value[1]:
                        time1 = datetime.datetime(month=now_time.month, year=now_time.year + number,
                                                  day=now_time.day)
                        times = time1.strftime('%Y')
            elif '-' in values:
                value = values.split('-')
                number = int(value[-1][:-1])
                if value[0] == '秒截止':
                    if 's' in value[1]:
                        times = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - number))
                    elif 'm' in value[1]:
                        times = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - number * 60))
                    elif 'h' in value[1]:
                        times = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - number * 3600))
                    elif 'd' in value[1]:
                        times = time.strftime('%Y-%m-%d %H:%M:%S',
                                              time.localtime(time.time() - number * 3600 * 24))
                    elif 'M' in value[1]:
                        time1 = datetime.datetime(month=now_time.month - number, year=now_time.year,
                                                  day=now_time.day, hour=now_time.hour, minute=now_time.minute)
                        times = time1.strftime('%Y-%m-%d %H:%M:%S')
                    elif 'Y' in value[1]:
                        time1 = datetime.datetime(month=now_time.month, year=now_time.year - number,
                                                  day=now_time.day, hour=now_time.hour, minute=now_time.minute)
                        times = time1.strftime('%Y-%m-%d %H:%M:%S')
                elif value[0] == '分截止':
                    if 's' in value[1]:
                        times = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - number))
                    elif 'm' in value[1]:
                        times = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - number * 60))
                    elif 'h' in value[1]:
                        times = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - number * 3600))
                    elif 'd' in value[1]:
                        times = time.strftime('%Y-%m-%d %H:%M',
                                              time.localtime(time.time() - number * 3600 * 24))
                    elif 'M' in value[1]:
                        time1 = datetime.datetime(month=now_time.month - number, year=now_time.year,
                                                  day=now_time.day, hour=now_time.hour, minute=now_time.minute)
                        times = time1.strftime('%Y-%m-%d %H:%M')
                    elif 'Y' in value[1]:
                        time1 = datetime.datetime(month=now_time.month, year=now_time.year - number,
                                                  day=now_time.day, hour=now_time.hour, minute=now_time.minute)
                        times = time1.strftime('%Y-%m-%d %H:%M')

                elif value[0] == '日截止':
                    if 'd' in value[1]:
                        times = time.strftime('%Y-%m-%d', time.localtime(time.time() - number * 3600 * 24))
                    elif 'M' in value[1]:
                        time1 = datetime.datetime(month=now_time.month - number, year=now_time.year,
                                                  day=now_time.day)
                        times = time1.strftime('%Y-%m-%d')
                    elif 'Y' in value[1]:
                        time1 = datetime.datetime(month=now_time.month, year=now_time.year - number,
                                                  day=now_time.day)
                        times = time1.strftime('%Y-%m-%d')
                elif value[0] == '月截止':
                    if 'M' in value[1]:
                        # 获取指定月的天数，可能会存在超出天数的情况
                        if now_time.month - number <= 0:
                            new_year = now_time.year - 1
                            new_month = 12 - (now_time.month - number)
                        else:
                            new_year = now_time.year
                            new_month = now_time.month - number
                        monthRange = calendar.monthrange(new_year, new_month)
                        if monthRange[-1] < now_time.day:
                            day = monthRange[-1]
                        else:
                            day = now_time.day
                        time1 = datetime.datetime(month=new_month, year=now_time.year, day=day)
                        times = time1.strftime('%Y-%m')
                    elif 'Y' in value[1]:
                        time1 = datetime.datetime(month=now_time.month, year=now_time.year - number,
                                                  day=now_time.day)
                        times = time1.strftime('%Y-%m')
                elif value[0] == '年截止':
                    if 'Y' in value[1]:
                        time1 = datetime.datetime(month=now_time.month, year=now_time.year - number,
                                                  day=now_time.day)
                        times = time1.strftime('%Y')
            return times

        except Exception as e:
            Log().error(f'<<用例数据解析替换>>指定时间{values}生成失败，请检查书写格式是否正确：如{{日截止-1}}，{e}')

    @staticmethod
    def __mobile_generator(values):
        """
        生成随机手机号，如{{mobile}}
        :param values: mobile
        :return:
        """
        try:
            prefix = [
                '130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                '145', '147', '149', '150', '151', '152', '153', '155', '156', '157',
                '158', '159', '165', '171', '172', '173', '174', '175', '176', '177',
                '178', '180', '181', '182', '183', '184', '185', '186', '187', '188',
                '189', '191'
            ]
            pos = random.randint(0, len(prefix) - 1)
            suffix = ''.join(random.sample(string.digits, 8))
            return prefix[pos] + suffix
        except Exception as e:
            Log().error(f'<<用例数据解析替换>>手机号{values}生成失败，请检查书写格式是否正确：如{{mobile}}，{e}')

    @staticmethod
    def __random_with_size_generator(values):
        """
        根据指定区间生成数字随机数，{{number1-333}}，随机取1-333之间的数值
        :param values: number1-333
        :return:
        """
        try:
            start = int(values.split('-')[0])
            end = int(values.split('-')[-1])
            return str(random.randint(start, end))
        except Exception as e:
            Log().error(f'<<用例数据解析替换>>{values}区间数字随机数生成失败，请检查书写格式是否正确：如{{number1-50}}，{e}')

    @staticmethod
    def __random_with_long_generator(values):
        """
        生成指定长度的数字随机数，如{{number5}}，随机生成5位数
        :param values: number5
        :return:
        """
        try:
            n = int(values.split('number')[-1])
            range_start = 10 ** (n - 1)
            range_end = (10 ** n) - 1
            return str(random.randint(range_start, range_end))
        except Exception as e:
            Log().error(
                f'<<用例数据解析替换>>{values}位长度数字随机数生成失败，请检查书写格式是否正确：如{{number5}}，{e}')

if __name__ == "__main__":
    SpecificGenerator().__call__(values='sdfsdf{{mobile}}dsgd{{mobile}}gfdfg{{number3}}')