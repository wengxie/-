# -*- coding: UTF-8 -*-
"""
@Date  2022/8/19 20:05
@auth  翁勰         
@File  getSQLValue.py
@Email  Nelson.weng@aishu.cn
@Description   获取数据库参数化的值
"""
import random

from tools.parameters_tools.parameters_fromSQL.DBConnection import execute_SQL
from tools.parameters_tools.parameters_fromSQL.SQLMapping.SQLMapping import get_sql_statement_from_key

# 实现key获取对应数据库中值
class GetSQLValues(object):

    def __init__(self, key):
        '''
        :param key: 要检索的参数化关键字
        '''
        self.key = key

    # 先通过key，去获取key对应的sql语句，再通过sql语句，去获取值。从而实现key获取对应数据库中值
    def get_parameters_fromSQL(self):
        values_list = []
        # 步骤一：先通过key，去获取key对应的sql语句
        sql_statement = get_sql_statement_from_key(self.key)
        # 判断通过key能否取到对应sql语句值
        if isinstance(sql_statement, bool):
            return False

        # 步骤二：再通过sql语句，去获取值。
        sql_value = execute_SQL(sql_statement)
        # 判断sql语句是否能够真正取到值
        if isinstance(sql_value, bool):
            return False

        # 如果sql语句取到空值，也说明无意义
        if len(sql_value) == 0:
            return False
        else:
            # 返回值sql_value格式是 (('values1',), ('values2',))
            for value in sql_value:
                # 提取每一个返回值values，都压入到list中，然后从list中随机抽取一个
                values_list.append(value[0])
            return random.choice(values_list)

# 自测使用-测试通过key能够获得对应数据库中的值
if __name__ == '__main__':
    a = GetSQLValues('UserID').get_parameters_fromSQL()
    print(a)
