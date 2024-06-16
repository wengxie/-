# -*- coding: UTF-8 -*-
"""
@Date  2022/8/19 21:39
@auth  翁勰         
@File  SQLMapping.py
@Email  Nelson.weng@aishu.cn
@Description   存储对应数据服务的sql语句，通过key去获取key对应的sql语句，用于接口参数化
"""
from config.mysql import mysql_config


def get_sql_statement_from_key(key):

    # sql语句集，存储参数化所需的key对应的sql语句，包含两部分：sql语句 + 使用的数据库
    sql_statements = {
        'UserID': {'sql': 'SELECT userId From User where status = "1";', 'database': 'AnyRobot'},
        'RoleId': {'sql': 'SELECT roleId From Role where roleName ="admin";', 'database': 'AnyRobot'}
    }

    # key在sql语句集中要有对应关键字，并且关键字值中要有sql项，例子 如要有UserID，并且UserID中要有sql
    if sql_statements.get(key) is not None and sql_statements[key].get('sql') is not None:
        # 看sql调用的数据库是否需要修改，默认是AnyRobot
        if sql_statements[key].get('database') is not None:
            if len(sql_statements[key]['database']) == 0:
                mysql_config['AnyRobot'] = 'AnyRobot'
            else:
                # 修改SQL调用的数据库
                mysql_config['AnyRobot'] = sql_statements[key]['database']

        return sql_statements[key]['sql']
    else:
        return False

# 自测使用
if __name__ == '__main__':
    sql = get_sql_statement_from_key('UserID')
    print(sql)