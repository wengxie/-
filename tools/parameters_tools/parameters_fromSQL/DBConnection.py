# -*- coding: UTF-8 -*-
"""
@Date  2022/8/19 20:45
@auth  翁勰         
@File  DBConnection.py
@Email  Nelson.weng@aishu.cn
@Description   数据库连接，创建PooledDB连接池，后期数据库连接直接调用连接池即可
"""
import traceback

import pymysql
from DBUtils.PooledDB import PooledDB

from config.mysql import mysql_config

# 设定数据库连接池，开放数据库连接（知识点：传统数据库连接 与 连接池 之间的对比）
def mysql_connection():
    POOL = PooledDB(
        creator=pymysql,    # 设定数据库驱动模块，常见：pymysql、cx_Oracle等
        mincached=2,        # 初始化连接池时创建的连接数
        maxcached=5,        # 链接池中最多闲置的链接
        maxshared=0,        # 池中共享连接的最大数量,0和None表示全部共享。PS: 无用，pymysql和MySQLdb等模块的threadsafety都为1
                            # 所以值无论设置为多少，永远是所有链接都共享。
        maxconnections=30,  # 连接池允许的最大连接数，0和None表示不限制连接数
        blocking=True,      # 连接数达到最大时，新连接是否可阻塞，True，等待；False，不等待然后报错。
                            # (建议True，达到最大连接数时，新连接阻塞，等待连接数减少再连接)
        maxusage=None,      # 连接的最大使用次数。建议无使用次数限制
        setsession=[],      # 开始会话前执行的命令列表，例如设置时区。如：["set datestyle to ...", "set time zone ..."]
        ping=0,             # 确定何时使用ping()检查连接。默认1，即当连接被取走，做一次ping操作；0是从不ping；
                            # 2是当该连接创建游标时ping；4是执行sql语句时ping；7是总是ping

        host=mysql_config['host'],
        port=mysql_config['port'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database'],
        charset=mysql_config['charset']
    )
    # 每次需要数据库连接就是用PooledDB连接池调用connection（）函数获取连接就好了
    conn = POOL.connection()
    return conn

# 执行传入的key也就是sql语句，获取sql结果，并返回
def execute_SQL(sql_statement):
    try:
        # 直接调用连接池创建的连接
        conn = mysql_connection()
        # 创建游标
        cur = conn.cursor()
        # 执行sql
        cur.execute(sql_statement)
        # 获取执行完的数据结果
        data = cur.fetchall()
        # 关闭游标
        cur.close()
        # 关闭连接
        conn.close()
        return data
    except Exception as e:
        traceback.print_exc()
        return False

# 自测使用-能否获取数据库数据
if __name__ == '__main__':
    a=execute_SQL('SELECT userId From User where status = "1";')
    print(a)