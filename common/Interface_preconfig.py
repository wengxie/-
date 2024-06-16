# -*- coding: UTF-8 -*-
"""
@Date  2022/8/13 15:23
@auth  翁勰         
@File  Interface_preconfig.py.py
@Email  Nelson.weng@aishu.cn
@Description   接口前置处理模块
                1. 通过处理接口YAML文件中，前置处理preconfig的配置
                2. 调用对应前置处理模块，完成前置处理
YAML样式
    preconfig:
      file: 'add.py'
      setup: 'add_num(1,2)'
"""
import os
import traceback

from common.environment_util import get_preconfig_path


class PreConfig(object):

    def __init__(self, info):
        self.info = info

    def handle_preconfig(self, step):
        '''
        处理每一个接口的前置操作
        :param step: 对应接口步骤
        :return: 返回处理完的self.info
        '''
        if self.info['run']:
            if self.info[step]['preconfig'].get('file') is not None and self.info[step]['preconfig'].get('setup') is not None:
                try:
                    # 第一步：取得前置处理文件夹下包含的所有文件（所有的前置处理文件）
                    file_list = os.listdir(get_preconfig_path())
                    # YAML文件中，接口设定的要调用的前置处理文件的文件名, 要执行的setup
                    preconfig_file = self.info[step]['preconfig']['file']
                    preconfig_setup = self.info[step]['preconfig']['setup']
                    # 判断用户YAML中设置的前置处理文件在对应目录下
                    if preconfig_file in file_list:
                        # 判断 前置处理文件 是一个存在的文件，而不是目录
                        if os.path.isfile(os.path.join(get_preconfig_path(), preconfig_file)):
                            # 取 add.py 中的名字 add
                            preconfig_file_name = preconfig_file.split('.')[0]
                            exec('from tools.interface_tools.preconfig.{name} import *'.format(name=preconfig_file_name))
                            eval(preconfig_setup)

                    else:
                        self.info['run'] = False
                        self.info['msg'].append("<{step}>接口前置处理配置中，{preconfig_file} 文件并不存在，请检查".format(step=step, preconfig_file=preconfig_file))

                except Exception as e:
                    self.info['run'] = False
                    self.info['msg'].append('调用前置处理时，程序处理异常:{msg}'.format(msg=traceback.format_exc()))

                finally:
                    return self.info

            else:
                self.info['run'] = False
                self.info['msg'].append('<{step}>接口的preconfig前置处理配置中，缺少file或setup'.format(step=step))

        return self.info

