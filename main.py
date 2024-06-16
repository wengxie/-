# -*- coding: UTF-8 -*-
"""
@Date  2022/7/14 16:31
@auth  翁勰         
@File  main.py1
@Email  Nelson.weng@aishu.cn
@Description  主函数，也是直接运行函数
"""
import os
import pytest


def main(type):
    # --clean-alluredir 会清空历史执行记录
    pytest.main(['-vs', '--alluredir=./result', './testcase', '--clean-alluredir', '-m', type])
    os.system('allure generate ./result -o ./report --clean')


if __name__ == '__main__':
    # 控制执行分组['smoke', 'testcase', 'all'], 默认'all'，要执行多个时，如'smoke or testcase'
    type = 'all'
    main(type)