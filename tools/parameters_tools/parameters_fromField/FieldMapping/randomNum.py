# -*- coding: UTF-8 -*-
"""
@Date  2022/8/20 13:54
@auth  翁勰         
@File  randomNum.py
@Email  Nelson.weng@aishu.cn
@Description  用于生成随机INT类型数字
"""
import random


class RandomNum():
    def random_number(self):
        number = int(random.choice(range(1, 999999)))
        return number

if __name__ == '__main__':
    a = RandomNum().random_number()
    print(a)
    print(type(a))