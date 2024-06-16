# -*- coding: UTF-8 -*-
"""
@Date  2022/8/19 10:02
@auth  翁勰         
@File  Interface_parameters.py
@Email  Nelson.weng@aishu.cn
@Description   处理接口参数化，即YAML文件中每一个接口出现的 ${key}$，将${key}$更换为指定数据
"""
from common.replace_process import find_keys_from_data, parameters_replace
from config.mysql import mysql_config
from tools.parameters_tools.parameters_from import ParametersFrom


class Parameters(object):

    def __init__(self, info):
        self.info = info

    # 处理接口参数化
    def handle_each_step_parameters(self, step):
        # 每一个接口参数化中截取出 ${Key}$ 的 Key
        param_keys = find_keys_from_data(self.info[step])
        param_keys_values = {}
        if len(param_keys) != 0:
            # 遍历参数key，获取每一个参数key对应的参数化值
            for key in param_keys:
                value = ParametersFrom(mysql_config['host'], mysql_config['port'], mysql_config['user'],
                                       mysql_config['password'], mysql_config['database']).get_parametersValue(key)
                # key取不到值，直接报错，说明参数化有问题
                if isinstance(value, bool):
                    self.info['run'] = False
                    # 补充：这里{{}}会输出 {},然后内部{key}对应变量，所以最终输出${key}$
                    self.info['msg'].append('<{step}>接口对应 ${{{key}}}$ 参数化数据获取失败，请检查'.format(step=step, key=key))
                    return self.info
                else:
                    # 存放所有的 key : value 用于替换
                    param_keys_values[key] = value
            # 每一个接口的参数化替换，即将YAML文件中识别到${key}$参数化替换为对应的参数内容
            parameters_replaced_info = parameters_replace(self.info[step], param_keys_values)
            # 如果替换结果是bool类型，即返回是False，说明替换过程出了错误，需要停止并报错
            if isinstance(parameters_replaced_info, bool):
                self.info['run'] = False
                # 补充：这里{{}}会输出 {},然后内部{key}对应变量，所以最终输出${key}$
                self.info['msg'].append('<{step}>接口参数化数据替换出现错误，请检查'.format(step=step))
                return self.info
            else:
                # 如果不是bool类型，说明替换成功，赋值即可，不用现在return，最终会一起return
                self.info[step] = parameters_replaced_info

        return self.info
