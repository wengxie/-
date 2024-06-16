# -*- coding: UTF-8 -*-
"""
@Date  2022/8/19 16:57
@auth  翁勰         
@File  mysql.py
@Email  Nelson.weng@aishu.cn
@Description   数据库配置
"""
from config.host import host_dict

mysql_config = {
    'host': host_dict['ip'],
    'port': 30006,
    'user': 'anyrobot',
    'password': 'eisoo.com123',
    'database': 'AnyRobot',
    'charset': 'utf8',
}

