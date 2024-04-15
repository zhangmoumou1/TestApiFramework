from app.core.methods import Log, env, MysqlConstructor, RedisConstructor, re, SpecificGenerator, \
    ParserJson, sleep
import allure
class NormalGenarator(object):
    """
    测试用例数据正常解析，如存储全局变量(从response/mysql/redis获取)、替换全局变量、处理mysql增删改查、redis增删改查
    """
    @staticmethod
    def save_global_variable_any(project_name, values, json_dict=None, flag='preposition'):
        """
        处理多个前置/后置条件
        :param project_name: 项目名
        :param values: xxx；xxx；xxx
        :param json_dict: 响应
        :param flag: 前后置标记
        :return:
        """
        if values in ['', None]:
            # 为空时不处理
            pass
        else:
            [NormalGenarator.save_global_variable(project_name, values, json_dict, flag) for
             global_data in values.split('；') if global_data != '']

    @staticmethod
    def save_global_variable(project_name, values, json_dict=None, flag='preposition'):
        """
        存储全局变量，一般写在前置（排除响应中存储）或者后置条件中
        从响应中存储：zyc_id=jsonpath_rela.id；zyc_id=jsonpath_abs.data.0.id
        从mysql中存储：mysql_1.db_name.zyc_id=select id from user_basic where code = 'xxx'
        从redis中存储：redis.0.zyc_id=hash.select.name.key
        自定义存储：custom.zyc_token=da173228-29b3-40c0-b9b0-04b364756c91
        调用接口用例：apiCase.base_login=zyc-1.1
        """
        # 处理前置条件
        if flag == 'preposition':
            try:
                log_title = '开始前置处理'
                Log().info(f'<<{log_title}>>')
                if 'jsonpath' in values:
                    Log().error(f'<<处理前置条件>>前置条件内的[{values}]无法使用jsonpath功能')
                elif 'mysql' in values:
                    # 处理mysql操作
                    NormalGenarator.dispose_mysql(project_name, values)
                elif 'redis' in values:
                    # 处理redis操作
                    NormalGenarator.dispose_redis_command(project_name, values)
                elif 'sleep' in values:
                    # 处理等待操作
                    NormalGenarator.sleep_generator(values)
                elif 'custom' in values:
                    # 存储自定义数据
                    key = (values.split('=')[0]).split('.')[-1]
                    value = values.split('=')[1]
                    RedisConstructor.handle_case_redis('insert', key, value)
                elif 'apiCase' in values:
                    # 调用接口用例
                    NormalGenarator.dispose_apiCase( values)
            except Exception as e:
                # Log().error(f'<<前置处理失败，请检查格式>>{values}')
                log_title = '前置处理失败'
                log = f'<请检查书写格式，{values}。Exception：{e}'
                Log().error(f'<<{log_title}>>{log}')
            finally:
                log_title = '前置处理结束'
                Log().info(f'<<{log_title}>>')
        # 处理后置条件
        elif flag == 'postposition':
            try:
                log_title = '开始后置处理'
                Log().info(f'<<{log_title}>>')
                if 'jsonpath' in values:
                    variable_name = values.split('=')[0]
                    variable_value = values.split('=')[-1]
                    # 使用json的相对路径获取
                    if 'jsonpath_rela' in values:
                        json_result = ParserJson.json_relative(json_dict, variable_value.split('.')[-1])
                        RedisConstructor.handle_case_redis('insert', variable_name, str(json_result))
                    elif 'jsonpath_abs' in values:
                        json_result = ParserJson.json_absolute(json_dict, variable_value)
                        RedisConstructor.handle_case_redis('insert', variable_name,
                                                           str(json_result))
                    else:
                        raise f'<<响应提取>>请检查书写格式是否正确：{values}'
                    values = json_result
                elif 'mysql' in values:
                    # 处理mysql操作
                    NormalGenarator.dispose_mysql(project_name, values)
                elif 'redis' in values:
                    # 处理redis操作
                    NormalGenarator.dispose_redis_command(project_name, values)
                elif 'sleep' in values:
                    # 处理等待操作
                    NormalGenarator.sleep_generator(values)
                elif 'custom' in values:
                    # 存储自定义数据
                    key = (values.split('=')[0]).split('.')[-1]
                    value = values.split('=')[1]
                    RedisConstructor.handle_case_redis('insert', key, value)
                elif 'apiCase' in values:
                    # 调用接口用例
                    NormalGenarator.dispose_apiCase(values)
            except Exception as e:
                # Log().error(f'<<后置处理失败，请检查格式>>{values}')
                log_title = '后置处理失败'
                log = f'后置处理失败请检查书写格式，{values}。Exception：{e}'
                Log().info(f'<<{log_title}>>{log}')
            finally:
                log_title = '后置处理结束'
                Log().info(f'<<{log_title}>>')

    @staticmethod
    def dispose_mysql(project_name, values):
        """
        mysql_1.db_name.zyc_id=select id from user_basic where code = 'xxx'；
        (mysql_实例.库名.全局变量名=sql)
        """
        try:
            param_start = values.split('=')[0]
            type = param_start.split('.')[0].split('_')[-1]
            db_name = param_start.split('.')[1]
            redis_key = param_start.split('.')[-1]
            sql = re.findall('(?<==).*$', values)[0]
            sql = SpecificGenerator().__call__(sql)
            # sql中需要传全局变量
            if '##' in sql:
                sql_actual = NormalGenarator.obtain_global_variable_any(sql)
            # sql中不需要传redis变量
            elif '##' not in sql:
                sql_actual = sql
            # 判断查询sql则取出结果值，更新、删除sql执行完结束
            if len(re.findall("^select", sql_actual)) == 1 or len(re.findall("^SELECT", sql_actual)) == 1:
                mysql_results = MysqlConstructor.structure_business_data(project_name, sql_actual, f'business_db_{type}', db_name)
                RedisConstructor.handle_case_redis('insert', redis_key, str(mysql_results))
            else:
                MysqlConstructor.structure_business_data(project_name, sql_actual, f'business_db_{type}', db_name)
        except Exception as e:
            Log().error(f'<<处理/存储mysql数据变量>>[{values}]写法有误，请检查格式及sql语句是否正确：{e}')

    @staticmethod
    def dispose_apiCase(values):
        """
        调用mysql的接口用例
        :param values: apiCase.base_login=zyc-1.1#zyc-1.3（apiCase.表名=用例id）
        :return:
        """
        try:
            Log().info(f'-------------------开始调用接口用例[{values}]-------------------')
            param_start = values.split('=')[0]
            table_name = param_start.split('.')[1]
            param_end = values.split('=')[-1]
            from app.core.generator import Genetator
            # 校验是否有多条用例，且执行接口用例
            if '#' in param_end:
                # zyc-1.1#zyc-1.3处理成zyc-1.1,zyc-1.2,zyc-1.3
                case_ids = MysqlConstructor.deal_with_caseid(param_end)
                for case_id in case_ids.split(','):
                    Genetator.global_generator(table_name=table_name, case_id=case_id, logFlag=True)
            else:
                Genetator.global_generator(table_name=table_name, case_id=param_end, logFlag=True)
        except Exception as e:
            Log().error(f'<<调用用例接口>>[{values}]写法有误，请检查格式及语句是否正确：{e}')
        finally:
            Log().info(f'------------------------调用接口用例结束------------------------')
    @staticmethod
    def dispose_redis(project_name, values):
        """
        redis.1.zyc_id=str.add.key.value(redis.库.全局变量名=类型.key.value)
        str类型
            1、新增：str.add.key.value
            2、查询：str.select.key(结果为字符串、列表、字典、数组)
            3、删除：str.delete.key
        hash类型
            1、新增/编辑：hash.add.key.name.value
            2、查询：hash.select.key.name(结果为字符串、列表、字典、数组)
            3、删除：hash.delete.key.name
        list类型
            1、头部新增：list.ladd.key.name
            2、尾部新增：list.radd.key.name
            3、查询：list.select.key.-1(查询指定索引值, 结果为字符串、列表、字典、数组)
            4、指定值删除：list.delete.key.1.name(lrem key count)
        zet类型(无序集合)
            1、新增：zet.add.key.name
            2、查看所有数据：zet.select.key(结果为字符串、列表、字典、数组)
            3、指定删除：zet.select.key.name
        """
        try:
            param_start = values.split('=')[0]
            redis_num = param_start.split('.')[1]
            param_end = values.split('=')[-1]
            # key/value/name中需要传全局变量
            if '##' in param_end:
                redis_actual = NormalGenarator.obtain_global_variable_any(project_name, param_end)
            all = redis_actual.split('.')
            end_args = all[1:]
            if all[1] == 'select':
                redis_result = RedisConstructor.handle_redis(project_name, 'business_db', redis_num, all[0], end_args)
                RedisConstructor.handle_case_redis('insert', param_start.split('.')[-1],
                                                   str(redis_result))
            else:
                RedisConstructor.handle_redis(project_name, 'business_db', redis_num, all[0], end_args)
        except Exception as e:
            Log().error(f'<<处理/存储redis数据变量>>[{values}]写法有误，请检查格式及语句是否正确：{e}')

    @staticmethod
    def dispose_redis_command(project_name, values):
        """
        redis.1.zyc_id=get key(redis.库.全局变量名=redis命令)
        """
        try:
            param_start = values.split('=')[0]
            redis_num = param_start.split('.')[1]
            param_end = values.split('=')[-1]
            # key/value/name中需要传全局变量
            if '##' in param_end:
                redis_actual = NormalGenarator.obtain_global_variable_any(project_name, param_end)
            else:
                redis_actual = param_end
            # 判断命令是否为查询操作
            select_flag = ['GET', 'GETRANGE', 'MGET', 'HGET', 'HGETALL', 'HKEYS', 'HLEN', 'HMGET',
                           'LINDEX', 'LLEN', 'LRANGE', 'SCARD', 'SDIFF', 'SINTER', 'SMEMBERS', 'SUNION', 'ZCARD', 'ZCOUNT',
                           'ZLEXCOUN', 'ZRANGE', 'ZRANGEBYLEX', 'ZRANGEBYSCORE', 'ZRANK', 'ZREVRANGE', 'ZREVRANGEBYSCORE',
                           'ZREVRANK', 'ZSCORE']
            # redis语句是否为查询语句
            is_need = False
            for flag in select_flag:
                if param_end.startswith(flag) is True:
                    is_need = True
            for flag in select_flag:
                if param_end.startswith(flag.lower()) is True:
                    is_need = True
            if is_need is True:
                redis_result = RedisConstructor.command_redis(project_name, redis_num, redis_actual)
                RedisConstructor.handle_case_redis('insert', param_start.split('.')[-1],
                                                   redis_result)
            else:
                redis_result = RedisConstructor.command_redis(project_name, redis_num, redis_actual)
        except Exception as e:
            Log().error(f'<<处理/存储redis数据变量>>[{values}]写法有误，请检查格式及语句是否正确：{e}')
            raise
        finally:
            return redis_result

    @staticmethod
    def obtain_global_variable_any(values):
        """
        替换多个全局变量
        """
        if values is None or '##' not in values:
            return values
        else:
            re_results = re.findall("##(.+?)##", values)
            values_dict = {}
            for result in re_results:
                values_dict['##' + result + '##'] = NormalGenarator.obtain_global_variable(result)
            actual_base = NormalGenarator.replace_many(values, values_dict)
            actual = SpecificGenerator().__call__(values=actual_base)
            return actual

    @staticmethod
    def obtain_global_variable(values):
        """
        获取全局变量，一般写在请求头、url、传参、前置条件、后置条件、断言
        写法：##zyc_id.id##
        :param zyc_id.id
        """
        try:
            if '.' not in values:
                # 字符串数据
                value = RedisConstructor.handle_case_redis('select', values)
            elif len(values.split('.')) == 2:
                redis_key = values.split('.')[0]
                list_dict = values.split('.')[-1]
                if list_dict.isdigit() or (list_dict.split('-')[-1]).split(".")[-1].isdigit():
                    # 判断是否为数字、负数
                    value = eval(RedisConstructor.handle_case_redis('select', redis_key))[int(list_dict)]
                else:
                    # 普通字典数据
                    value = eval(RedisConstructor.handle_case_redis('select', redis_key))[list_dict]
            elif len(values.split('.')) == 3:
                # 列表嵌套字典数据
                list_value = values.split('.')
                redis_key = list_value[0]
                list_num = int(list_value[1])
                dict_key = list_value[-1]
                value = eval(RedisConstructor.handle_case_redis('select', redis_key))[list_num][dict_key]
            Log().info(f'<<提取全局变量>>{env}环境，全局变量【{values}】提取成功，结果：{str(value)}')
            return str(value)
        except Exception as e:
            Log().error(f'<<提取全局变量>>提取全局变量[{values}]失败：{e}')

    @staticmethod
    def sleep_generator(values):
        """
        强制等待，如sleep5，等待5秒
        :param values: sleep5
        """
        try:
            sec = int(values.split('sleep')[-1])
            sleep(sec)
            Log().info(f'强制等待{sec}秒')
        except Exception as e:
            Log().error(
                f'<<用例数据解析替换>>执行{values}睡眠等待失败，请检查书写格式是否正确：如{{sleep5}}，{e}')

    @staticmethod
    def header_generator(values):
        """
        处理请求头，key1=values1；key2=values2
        """
        try:
            if (values == '') or (values is None) or ('=' not in values):
                return ''
            else:
                header_dict = dict()
                for header_info in values.split('；'):
                    if 'apiCase' in header_info:
                        # 调用接口用例
                        NormalGenarator.dispose_apiCase(values)
                    header_dict[header_info.split('=')[0]] = header_info.split('=')[1]
                return header_dict
        except Exception as e:
            Log().error(
                f'<<用例数据解析替换>>处理{values}请求头失败，请检查书写格式是否正确：如key=value；key=value, {e}')

    @staticmethod
    def replace_many(s, dic):
        """
        处理多个替换
        :param s: str
        :param dic: dict
        :return:
        """
        for key, value in dic.items():
            s = s.replace(key, value)
        return s


    @staticmethod
    def allure_step(step_title: str, content: str) -> None:
        """
        :param step_title: 步骤及附件名称
        :param content: 附件内容
        """
        allure.attach(
            body=content,
            name=step_title,
            attachment_type=allure.attachment_type.TEXT
        )

    @staticmethod
    def check_json(data):
        """
        解析str是否为json类型
        """
        try:
            import json
            json.loads(data)
            return True
        except:
            return False

if __name__ == "__main__":
    # NormalGenarator.header_generator('aa=11；bb=22')
    aa = NormalGenarator.dispose_redis_command('BlogProject', 'redis.1.zyc_business_token=get aa')
    print(aa)