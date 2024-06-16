# -*- coding: UTF-8 -*-
"""
@Date  2022/7/15 10:54
@auth  翁勰         
@File  yaml_util.py
@Email  Nelson.weng@aishu.cn
@Description   封装yaml文件操作，实现读取、写入、清空等功能
"""
import traceback
import yaml


# 其中path: str表示path是string类型
from common.InterfaceException import InterfaceException


def read_yaml(path: str):
    with open(file=path, encoding="utf-8") as openfile:
        try:
            data = yaml.load(stream=openfile, Loader=yaml.FullLoader)
            return data
        except Exception as e:
            # 检测到异常时 traceback.print_exc() 会自动输出详细的异常信息
            raise InterfaceException('程序处理异常:{msg}'.format(msg=traceback.format_exc()))
