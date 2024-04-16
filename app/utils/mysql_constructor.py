#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @@Author: 张某某
# @@Create Date: 2023/02/16 10:28
# @@Description: mysql功能构造
# @@Copyright © zhangmoumou, Inc. All rights reserved.

from app.core.methods import Log, PooledDB, SSHTunnelForwarder, YamlConstructor, platform, pymysql, env, re, \
    datetime, local_switch, server_switch, List, Dict
from read_config import ssh_ip, ssh_port, ssh_password, ssh_username

SYSTEM_VERSION = platform.platform()

class MysqlConstructor(object):
    """
    mysql操作
    """

    @staticmethod
    def __select_conn_mode(switch: str, project: str, type: str, db_name: str):
        """
        选择连接模式，直连或者ssh连接
        :param switch ssh连接开关
        :param project 项目名
        :param type 库类型
        :param db_name 库名
        :return:
        """
        if switch == 'on':
            server = SSHTunnelForwarder(
                ssh_address_or_host=(ssh_ip, int(ssh_port)),
                ssh_username=(ssh_username),
                ssh_password=(ssh_password),
                remote_bind_address=(YamlConstructor.get_mysql_info(project, type)['ip'],
                                     YamlConstructor.get_mysql_info(project, type)['port'])
            )
            server.start()
            connect = pymysql.connect(
                user=YamlConstructor.get_mysql_info(project, type)['username'],
                passwd=YamlConstructor.get_mysql_info(project, type)['password'],
                host='127.0.0.1',
                db=db_name,
                port=server.local_bind_port
            )
            return connect
        elif switch == 'off':
            __pool = PooledDB(creator=pymysql, mincached=1, maxcached=20,
                              host=YamlConstructor.get_mysql_info(project, type)['ip'],
                              port=YamlConstructor.get_mysql_info(project, type)['port'],
                              user=YamlConstructor.get_mysql_info(project, type)['username'],
                              passwd=str(YamlConstructor.get_mysql_info(project, type)['password']),
                              db=db_name,
                              charset='utf8')
            return __pool.connection()
        else:
            Log().warning(
                f'<<mysql连接异常>>连接{env}环境{project}项目{type}.{db_name}库异常，请检查config.ini连接模式是否正确')
    @staticmethod
    def __get_conn(type: str, db_name: str, project=None):
        """
        从连接池中取出连接
        :param project: 项目名称
        :param type: 类型，用例库、业务库
        :return: MySQLdb.connection
        :当环境为非Linux环境，使用ssh连接
        """
        try:
            # 判断运行系统
            if 'Linux' in SYSTEM_VERSION:
                # 服务器运行进行直连
                return MysqlConstructor.__select_conn_mode(server_switch, project, type, db_name)
            else:
                # 本地运行通过ssh隧道连接
                return MysqlConstructor.__select_conn_mode(local_switch, project, type, db_name)
        except Exception as e:
            Log().warning(f'<<mysql连接异常>>连接{env}环境{project}项目{type}.{db_name}库异常，请检查配置是否正常: {e}')

    @staticmethod
    def __check_single_id(ids: str):
        """
        校验存在一个用例id区间
        """
        try:
            if '#' in ids.replace('zyc-', ''):
                id_str = ''
                bb = ids.split('#')
                point_start = bb[0].split('.')[0]
                point_end = bb[1]
                start = int(bb[0].split('.')[1])
                num = int(bb[1].split('.')[1]) - int(bb[0].split('.')[1])
                for i in range(num):
                    ids = point_start + '.' + str(start + i)
                    id_str += (ids + ',')
                return (id_str + point_end)
            else:
                return ids
        except Exception as e:
            Log().warning(f'<<处理mysql用例异常>>请检查{ids}写法是否正常: {e}')

    @staticmethod
    def __deal_with_caseid(case_id: str):
        """
        处理用例id，整合成zyc-1.1、zyc-1.2...
        """
        try:
            if ',' in case_id.replace(' ', '') and '#' in case_id.replace(' ', ''):
                id_all = ''
                for aa in case_id.split(','):
                    id_all += MysqlConstructor.__check_single_id(aa) + ','
                if id_all[-1] == ',':
                    id_result = id_all[:-1]
                return id_result
            else:
                return MysqlConstructor.__check_single_id(case_id)
        except Exception as e:
            Log().warning(f'<<处理mysql用例异常>>请检查{case_id}写法是否正常: {e}')

    @staticmethod
    def structure_case_data(project_name: str, table_name: str, case_id: str) -> List[tuple]:
        """
        构造用例数据，用户多个用例参数化数据，一次性查询多个用例数据,合成数组，[(), ()]
        :param table_name 表名
        :param case_id 如zyc-1.1#zyc-1.3
        return [('zyc-1.1', 'case_name'), ('zyc-1.2', 'case_name'), ('zyc-1.3', 'case_name')]
        """
        try:
            # 处理case_id，处理成'zyc-1.1,zyc-1.2...'
            case_ids = MysqlConstructor.__deal_with_caseid(case_id)
            __db_name = f'{env}_case_data'.lower()
            # 获取MySQL连接信息，创建连接
            _conn = MysqlConstructor.__get_conn(project_name, 'case_db', f'{env.lower()}_cases')
            _cursor = _conn.cursor()
            case_id = case_ids.replace(' ', '')
            str_all = ''
            for id in case_id.split(','):
                str_all += '"{}",'.format(id)
            cases_id = str_all[:-1]
            __sql = 'select case_id, case_name from {} where case_id in ({}) and is_deleted = 0;'.format(
                table_name, cases_id)
            _cursor.execute(__sql)
            value_results = _cursor.fetchall()
            # 处理sql查询结果的顺序，正序
            values = []
            for i in str_all.split(','):
                key_new_1 = ()
                for b in value_results:
                    if '"{}"'.format(b[0]) == i:
                        key_new_1 += (b[0], b[1])
                values.append(key_new_1)
            values.pop()
            _conn.close()
            return values
        except Exception as e:
            _conn.close()
            Log().warning(f'<<组装mysql用例异常>>请检查{table_name}.{case_id}写法是否正常/是否存在: {e}')

    @staticmethod
    def single_case_detail(table_name: str, case_id: str) -> Dict[str, str]:
        """
        获取单个用例的数据明细
        :param case_id: 用例id
        :return:
        """
        try:
            _conn = MysqlConstructor.__get_conn('case_db', f'{env.lower()}_cases')
            _cursor = _conn.cursor()
            __sql = 'select * from {} where case_id = "{}" or case_name = "{}";'.format(table_name, case_id,
                                                                                        case_id)
            # 获取表里的所有字段名
            global __column_name_sql
            __column_name_sql = 'select COLUMN_NAME from information_schema.COLUMNS where table_name = ' \
                                '"{}" and table_schema = "{}" ORDER BY ordinal_position;'.format(table_name, f'{env.lower()}_cases')
            _cursor.execute(__column_name_sql)
            key_results = _cursor.fetchall()
            _cursor.execute(__sql)
            value_results = _cursor.fetchall()
            if len(value_results) > 1:
                Log().warning(f"<<查询mysql用例失败>>{env}环境{env}_case库{table_name}表的id/name={case_id}用例数据"
                                f"存在多条，请检查数据是否正常！")
            # 将字段名和对应字段值，拼装成字典，以便获取
            dict_results = {}
            for number in range(len(key_results)):
                key = key_results[number][0]
                if key == 'case_param':
                    value = value_results[0][number]
                else:
                    # value = str(value_results[0][number]).replace(' ', '')
                    value = value_results[0][number]
                dict_results[key] = value
            # Log().info(f"<<查询mysql用例>>\n"
            #            f"成功登录{env}环境{env.lower()}_cases库，获取到表{table_name}.id/name={case_id}的"
            #            f"用例数据：{dict_results}")
            _conn.close()
            return dict_results
        except Exception as e:
            # Log().error(f"<<查询mysql用例失败>>{env}环境{env}_case库{table_name}表获取id/name={case_id}用例数据失败，"
            #                 f"请检查数据是否正常：{e}")
            _conn.close()

    @staticmethod
    def check_single_id(ids):
        """
        校验存在一个用例id区间
        """
        try:
            if '#' in ids.replace('zyc-', ''):
                id_str = ''
                bb = ids.split('#')
                point_start = bb[0].split('.')[0]
                point_end = bb[1]
                start = int(bb[0].split('.')[1])
                num = int(bb[1].split('.')[1]) - int(bb[0].split('.')[1])
                for i in range(num):
                    ids = point_start + '.' + str(start + i)
                    id_str += (ids + ',')
                return (id_str + point_end)
            else:
                return ids
        except:
            raise

    @staticmethod
    def deal_with_caseid(case_id):
        """
        处理用例id，整合成zyc-1.1,zyc-1.2...
        """
        try:
            if ',' in case_id.replace(' ', '') and '#' in case_id.replace(' ', ''):
                id_all = ''
                for aa in case_id.split(','):
                    id_all += MysqlConstructor.check_single_id(aa) + ','
                if id_all[-1] == ',':
                    id_result = id_all[:-1]
                return id_result
            else:
                return MysqlConstructor.check_single_id(case_id)
        except:
            raise

    @staticmethod
    def parameterization_data(table_name, case_id):
        """
        用户多个用例参数化数据，一次性查询多个用例数据,合成数组，[(), ()]
        params：case_id 如zyc-1.1#zyc-1.3
        return：[('case_id', 'case_name'), ('case_id', 'case_name')]
        """
        try:
            # 获取MySQL连接信息，创建连接
            _conn = MysqlConstructor.__get_conn('case_db', f'{env.lower()}_cases')
            _cursor = _conn.cursor()
            # 当case_id字段数据为all或者ALL，说明查询表内所有用例数据
            if case_id in ['all', 'ALL']:
                __sql = 'select case_id, case_name from {} where is_deleted = 0;'.format(table_name)
                _cursor.execute(__sql)
                values = _cursor.fetchall()
            else:
                # 处理case_id，处理成'zyc-1.1,zyc-1.2...'
                case_ids = MysqlConstructor.deal_with_caseid(case_id)
                case_id = case_ids.replace(' ', '')
                str_all = ''
                for id in case_id.split(','):
                    str_all += '"{}",'.format(id)
                cases_id = str_all[:-1]
                __sql = 'select case_id, case_name from {} where case_id in ({}) and is_deleted = 0;'.format(table_name, cases_id)
                _cursor.execute(__sql)
                value_results = _cursor.fetchall()
                # 处理sql查询结果的顺序，正序
                values = []
                for i in str_all.split(','):
                    key_new_1 = ()
                    for b in value_results:
                        if '"{}"'.format(b[0]) == i:
                            key_new_1 += (b[0], b[1], table_name)
                    values.append(key_new_1)
                values.pop()
            _conn.close()
            return values
        except Exception as e:
            Log().warning(
                f"<<查询mysql用例失败>>{env}环境{env}_case库{table_name}表获取id/name={case_id}用例数据失败，"
                f"请检查数据是否正常：{e}")
            _conn.close()
            return [('id', '未找到用例数据，请检查对应case_id是否存在')]

    @staticmethod
    def structure_business_data(project_name, sql: str, type: str, db_name: str) -> List[dict]:
        """
        操作业务数据库表，增删改查操作,返回单/多个字段和记录
        :param sql
        :param type 库类型
        :param db_name 库名
        :return: {"key": "value"} 或 [{"key1": "value1"},{"key2": "value2"}]
        """
        try:
            # 获取MySQL连接信息，创建连接
            _conn = MysqlConstructor.__get_conn(type, db_name, project_name)
            _cursor = _conn.cursor()
            __sql = sql.strip()
            _cursor.execute(__sql)
            results = _cursor.fetchall()
            sql1 = __sql.replace(' ', '')
            if len(re.findall("^select", __sql)) == 1:
                sql1 = sql1.replace('SELECT', 'select').replace('FROM', 'from')
                # 执行查询操作
                find_keys = re.findall("^select(.+?)from", sql1)
                # 校验sql查询结果是表的全量*字段还是部分字段
                if '*' == find_keys[0]:
                    del_null_sql = __sql.replace(' ', '')
                    find_table_name = re.findall("from(.+?)$", del_null_sql)
                    # 校验sql，从里面取出表名
                    if 'where' in find_table_name[0]:
                        table_name = re.findall("from(.+?)where", del_null_sql)[0]
                    else:
                        table_name = find_table_name[0]
                    __column_name_sql = 'select COLUMN_NAME from information_schema.COLUMNS where table_name = ' \
                                        '"{}" and table_schema = "{}";'.format(table_name, db_name)
                    _cursor.execute(__column_name_sql)
                    key_results = _cursor.fetchall()
                    _cursor.execute(__sql)
                    value_results = _cursor.fetchall()
                    dict_results = {}
                    for number in range(len(key_results)):
                        key, value = key_results[number][0], value_results[0][number]
                        dict_results[key] = value
                    return dict_results
                else:
                    keys = find_keys[0].split(",")
                    list_result = []
                    dict_result = {}
                    # 处理单个结果，单个结果为字典{结果}
                    if len(results) == 1:
                        for i in results:
                            for num in range(len(i)):
                                # 处理连接查询字段处理，如a.id
                                if '.' in keys[num] and 'join' in sql1:
                                    key = keys[num].split('.')[-1]
                                else:
                                    key = keys[num]
                                # 如果查询结果是datetime类型，处理成str
                                if isinstance(i[num], datetime.datetime):
                                    dict_result[key] = str(i[num])
                                else:
                                    dict_result[key] = i[num]
                                list_result.append(dict_result)
                        results = dict_result
                        Log().info(f'<<业务mysql库>>执行{type}.{db_name}业务库的查询sql[{sql}]成功，结果为：' + '\n' +
                                        f'{results}')
                        return results
                    # 处理多个结果，多个结果为数组[{结果1},{结果2}]
                    elif len(results) > 1:
                        for i in results:
                            dict_result1 = {}
                            for num in range(len(i)):
                                # 处理连接查询字段处理，如a.id
                                if '.' in keys[num] and 'join' in sql1:
                                    key = keys[num].split('.')[-1]
                                else:
                                    key = keys[num]
                                if isinstance(i[num], datetime.datetime):
                                    dict_result1[key] = str(i[num])
                                else:
                                    dict_result1[key] = i[num]
                                list_result.append(dict_result1)
                        results = list_result
                        Log().info(f'<<业务mysql库>>执行{type}.{db_name}业务库的查询sql[{sql}]成功，结果为：' + '\n' +
                                        f'{results}')
                        return results

            elif len(re.findall("^delete", __sql)) == 1:
                # 执行删除操作
                _conn.commit()
                Log().info(f'<<业务mysql库>>执行{type}.{db_name}业务库的删除sql[{sql}]成功')
            elif len(re.findall("^insert into", __sql)) == 1:
                # 执行新增操作
                _conn.commit()
                Log().info(f'<<业务mysql库>>执行{type}.{db_name}业务库的新增sql[{sql}]成功')
            elif len(re.findall("^update", __sql)) == 1:
                # 执行更新操作
                _conn.commit()
                Log().info(f'<<业务mysql库>>执行{type}.{db_name}业务库的更新sql[{sql}]成功')
            _conn.close()
        except Exception as e:
            _conn.close()
            Log().warning(f'<<业务mysql库>>执行{type}.{db_name}业务库的sql[{sql}]失败，请检查语法是否正确：{e}')

if __name__ == "__main__":
    _conn = MysqlConstructor.get_conn('BlogProject', 'case_db', f'{env.lower()}_cases')
    print(_conn)



