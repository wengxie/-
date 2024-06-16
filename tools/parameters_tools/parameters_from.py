# -*- coding: UTF-8 -*-
"""
@Date  2022/8/19 16:52
@auth  翁勰         
@File  parameters_from.py
@Email  Nelson.weng@aishu.cn
@Description   定义参数化数据来源：
                1. 数据库参数化来源：通过识别关键字key，定位到是要从数据库中取得的参数化
                2. 用户自定义模块参数来源：通过识别关键字key，定位到是要从用户自定义模块中取得的参数化
                注意：先遍历识别key是不是走数据库参数化，然后再识别用户自定义，也就是数据库优先级高于自定义
"""

# 定义参数化数据来源，并从来源中取到key对应的值
from config.mysql import mysql_config
from tools.parameters_tools.parameters_fromField.getFieldValue import get_parameters_fromField
from tools.parameters_tools.parameters_fromSQL.getSQLValue import GetSQLValues


class ParametersFrom(object):

    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    # 从来源中取到key对应的值
    def get_parametersValue(self, key):
        # 判断数据库参数化下，能否取到对应key的值
        keyValues = GetSQLValues(key).get_parameters_fromSQL()
        # 判断数据库来源下，能否取到对应key的值
        if isinstance(keyValues, bool):
            keyValues = get_parameters_fromField(key)
            # 判断用户自定义模块下，能否取到对应key的值
            if isinstance(keyValues, bool):
                # 都取不到，说明没有key对应的参数化的值
                return False
            else:
                return keyValues
        else:
            return keyValues

# 自测使用-验证通过key能否取到值
if __name__ == '__main__':
    data = ParametersFrom(mysql_config['host'], mysql_config['port'], mysql_config['user'],
                          mysql_config['password'], mysql_config['database']).get_parametersValue('AnyRobotNameID')
    print(data)