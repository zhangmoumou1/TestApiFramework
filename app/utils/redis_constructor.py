#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @@Author: 张某某
# @@Create Date: 2023/02/16 10:28
# @@Description: redis功能构造
# @@Copyright © zhangmoumou, Inc. All rights reserved.

from app.core.methods import Log, SSHTunnelForwarder, YamlConstructor, platform, env, local_switch, server_switch, \
    redis, random, warnings
from read_config import ssh_ip, ssh_port, ssh_password, ssh_username

SYSTEM_VERSION = platform.platform()

class RedisConstructor(object):
    """
    redis操作
    """
    @staticmethod
    def __select_conn_mode(switch: str, project: str, instance: str, db_num: int):
        """
        选择连接模式，直连或者ssh连接
        :project:项目名
        :instance:实例类型（case_db/business_db）
        :db_num:库索引0.1.2....
        :return:
        """
        if switch == 'on':
            server = SSHTunnelForwarder(
                ssh_address_or_host=(ssh_ip, int(ssh_port)),
                ssh_username=ssh_username,
                ssh_password=ssh_password,
                local_bind_address=('localhost', random.randint(1000, 9999)),
                remote_bind_address=(YamlConstructor.get_redis_info(project, instance)['ip'],
                                     YamlConstructor.get_redis_info(project, instance)['port']))
            server.start()
            pool = redis.ConnectionPool(host='localhost',
                                        port=server.local_bind_port,
                                        db=db_num,
                                        password=YamlConstructor.get_redis_info(project, instance)['password'],
                                        decode_responses=True)
            redis_con = redis.Redis(
                connection_pool=pool
            )
            return redis_con
        elif switch == 'off':
            pool = redis.ConnectionPool(host=YamlConstructor.get_redis_info(project, instance)['ip'],
                                        port=YamlConstructor.get_redis_info(project, instance)['port'],
                                        password=YamlConstructor.get_redis_info(project, instance)['password'],
                                        db=db_num)
            redis_con = redis.Redis(connection_pool=pool)
            return redis_con
        else:
            Log().error(
                f'<<redis连接异常>>连接{env}环境{project}项目{instance}.{db_num}库异常，请检查config.ini连接模式是否正确')
    @staticmethod
    def __get_conn(db_num: int, project=None, instance=None):
        """
        从连接池中取出连接
        :param project: 项目名称
        :param instance: 类型，用例库、业务库
        :return: Redis.connection
        :当环境为非Linux环境，使用ssh连接
        """
        try:
            # 判断运行系统
            if 'Linux' in SYSTEM_VERSION:
                # 服务器运行进行直连
                return RedisConstructor.__select_conn_mode(server_switch, project, instance, db_num)
            else:
                # 本地运行通过ssh隧道连接
                return RedisConstructor.__select_conn_mode(local_switch, project, instance, db_num)
        except Exception as e:
            Log().error(f'<<redis连接异常>>连接{env}环境{project}项目{instance}.{db_num}库异常，请检查配置是否正常: {e}')

    @staticmethod
    def handle_case_redis(type: str, key: str, value = None):
        """
        对全局变量进行操作，插入或者查询(哈希类型)
        :param project:项目名称
        :param instance:实例类型（case_db/business_db）
        :param type:操作类型，select/insert
        :param key:键名称
        :param value: 插入的数据
        :return 查询结果
        """
        try:
            db_name = YamlConstructor.get_redis_info()['db_num']
            _redis_conn = RedisConstructor.__get_conn(db_name)
            if type == 'insert':
                _redis_conn.hset("qa_{}_interface_params".format(env), key, value)
                return None
            elif type == 'select':
                result = _redis_conn.hget(name='qa_{}_interface_params'.format(env), key=key)
                return result.decode('UTF-8')
        except Exception as e:
            Log().error(f'<<redis操作>>{env}环境，对全局变量【{key}.{value}】进行{type}操作失败：请检查写法是否正确: {e}')
        finally:
            _redis_conn.connection_pool.disconnect()

    @staticmethod
    def handle_redis(project: str, instance: str, db_num: int, type: str, action: str, *args: list):
        """
        （已废弃）对用例/业务redis进行增删改查操作，分为字符串、列表、哈希、集合类型
        :param project 项目
        :param type 库类型
        :param db_num 库索引
        :param action 增删改查
        :param *args key/name/valuer
        :return:
        """
        warnings.warn('此方法已弃用，不推荐使用', DeprecationWarning)
        try:
            _redis_conn = RedisConstructor.__get_conn(db_num, project, instance)
            if action == 'delete':
                # 删除整个键值
                _redis_conn.delete(args[0][0])
                result = True
            else:
                if type == 'str':
                    """
                    1、新增：redis.1.str.add.key.value
                    2、查询：redis.1.str.select.key(结果为字符串、列表、字典、数组)
                    3、删除：redis.1.str.delete.key(结果为字符串、列表、字典、数组)
                    """
                    if action in ['add', 'update']:
                        result = _redis_conn.set(args[0][0], args[0][1])
                    elif action == 'delete':
                        result = _redis_conn.delete(args[0][0])
                    elif action == 'select':
                        result = _redis_conn.get(args[0][0])
                elif type == 'list':
                    """
                    1、头部新增：redis.1.list.ladd.key.name
                    2、尾部新增：redis.1.list.radd.key.name
                    3、查询：redis.1.list.select.key.-1(查询指定索引值)
                    4、指定值删除：redis.1.list.delete.key.1.name(lrem key count)
                    """
                    if action == 'ladd':
                        result = _redis_conn.rpush(args[0][0], args[0][1])
                    elif action == 'radd':
                        result = _redis_conn.lpush(args[0][0], args[0][1])
                    elif action == 'delete':
                        result = _redis_conn.lrem(args[0][0], int(args[0][1]), args[0][2])
                    elif action == 'select':
                        result = _redis_conn.lindex(args[0][0], int(args[0][1]))
                elif type == 'hash':
                    """
                    1、新增/编辑：redis.1.hash.add.key.name.value
                    2、查询：redis.1.hash.select.key.name(结果为字符串、列表、字典、数组)
                    3、删除：redis.1.hash.delete.key.name(结果为字符串、列表、字典、数组)
                    """
                    if action == 'add':
                        result = _redis_conn.hset(args[0][0], args[0][1], args[0][2])
                    elif action == 'select':
                        result = _redis_conn.hget(args[0][0], args[0][1])
                    elif action == 'delete':
                        result = _redis_conn.hdel(args[0][0], args[0][1])
                elif type == 'set':
                    """
                    1、新增：redis.1.zet.add.key.name
                    2、查看所有数据：redis.1.zet.select.key
                    3、指定删除：redis.1.zet.select.key.name
                    """
                    if action == 'add':
                        result = _redis_conn.sadd(args[0][0], args[0][1])
                    elif action == 'select':
                        result = _redis_conn.smembers(args[0][0])
                    elif action == 'delete':
                        result = _redis_conn.srem(args[0][0], args[0][1])
                else:
                    Log().warning(f'<<redis操作>>{env}环境{project}项目{type}类型{db_num}库，'
                                    f'对键名【{args[0]}】进行{action}操作失败：请检查写法是否正确')
                    result = None
                Log().info(f'<<redis操作>>{env}环境{project}项目{type}类型{db_num}库，'
                           f'对键名【{args[0]}】进行{action}操作成功：{result}')
        except Exception as e:
            Log().error(f'<<redis操作>>{env}环境{project}项目{type}类型{db_num}库，'
                            f'对键名【{args[0]}】进行{action}操作失败：请检查写法是否正确: {e}')
        finally:
            _redis_conn.connection_pool.disconnect()
            return result

    @staticmethod
    def command_redis(project: str, db_num: int, command, instance='business_db'):
        """
        对用例/业务redis进行增删改查操作，分为字符串、列表、哈希、集合类型
        :param project 项目
        :param type 库类型
        :param db_num 库索引
        :param action 增删改查
        :param *args key/name/valuer
        :return:
        """
        import json
        from app.core.normal_generator import NormalGenarator
        try:
            _redis_conn = RedisConstructor.__get_conn(db_num, project, instance)
            result_data = _redis_conn.execute_command(command)
            if isinstance(result_data, bytes):
                results = result_data.decode('utf-8')
            elif isinstance(result_data, list):
                results = []
                for list_data in result_data:
                    data = (list_data.decode('utf-8')).replace("'", '"')
                    if NormalGenarator.check_json(data) is True:
                        result = json.loads(data)
                    else:
                        result = data
                    results.append(result)
            Log().info(f'<<业务redis操作>>{env}环境{project}项目{db_num}库，执行redis语句【{command}】成功，结果为：{results}')
            return result
        except Exception as e:
            Log().error(f'<<业务redis操作>>{env}环境{project}项目{db_num}库，执行redis语句【{command}】失败')
            raise
        finally:
            _redis_conn.connection_pool.disconnect()
            return results

if __name__ == "__main__":
    # command = 'hmget qa_TEST_interface_params zyc_case_name'
    command = 'get aa'
    print(RedisConstructor.command_redis('BlogProject', 1, command))