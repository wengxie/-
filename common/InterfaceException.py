# -*- coding: UTF-8 -*-
"""
@Date  2022/7/26 20:51
@auth  翁勰         
@File  InterfaceException.py.py
@Email  Nelson.weng@aishu.cn
@Description   使用raise自定义触发异常，终止运行，场景：
                    1. 比如当方法不是（get、put、post、delete）时的场景
"""

class InterfaceException(Exception):

    def __init__(self, exception_message):
        self.exception_message = exception_message