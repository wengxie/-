# -*- coding: UTF-8 -*-
"""
@Date  2022/8/20 11:04
@auth  翁勰         
@File  getFieldValue.py
@Email  Nelson.weng@aishu.cn
@Description   获取用户自定义模块参数化的值
"""
from tools.parameters_tools.parameters_fromField.FieldMapping import name, randomNum


def get_parameters_fromField(key):
    '''
    获取用户自定义模块参数化的值
    :param key: 要检索的参数化关键字
    :return: 参数化关键字对应的值
    '''
    # 自行根据需要添加key与对应模块，key切记不要与SQLMapping中的key冲突
    fields = {
        'AnyRobotNameID': name.data().random_name(),
        'RandomIntNumber': randomNum.RandomNum().random_number()
    }
    # key在自定义模块参数化集中要有对应关键字
    if fields.get(key) is not None:
        # 判断内容是否为空，这里str的原因是，如果是int类型，无法使用len方法，所以统一转为str进行判断是否为空
        if len(str(fields[key])) != 0:
            return fields[key]
        else:
            return False
    else:
        return False

if __name__ == '__main__':
    a = get_parameters_fromField('AnyRobotNameID')
    print(a)
