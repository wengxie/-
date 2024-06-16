# -*- coding: UTF-8 -*-
"""
@Date  2022/8/20 11:22
@auth  翁勰         
@File  name.py
@Email  Nelson.weng@aishu.cn
@Description   用于生成随机字符串
"""
import random

class data():
    def random_name(self):
        name = str(random.choice(range(1, 999))) + '_' + str(random.choice(range(1, 999)))
        return name

# 自测
if __name__ == '__main__':
    print(data().random_name())