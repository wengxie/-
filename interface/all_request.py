# -*- coding: UTF-8 -*-
"""
@Date  2022/7/21 20:00
@auth  翁勰         
@File  all_request.sh.py
@Email  Nelson.weng@aishu.cn
@Description   所有接口调用的请求（GET、POST、PUT、DELETE）都从这里经过
"""

# 统一处理所有的接口请求
import os
import time
import traceback

import requests

from common.Assert_util import AssertUtil
from common.InterfaceException import InterfaceException
from common.Interface_preconfig import PreConfig
from common.Interface_rely import Rely
from common.Interface_teardown import TearDown
from common.environment_util import get_yaml_path
from common.test_data_process import TestDataProcess
from common.yaml_util import read_yaml
from tools.uploadFile_tools.uploadFile import UploadFile


class AllRequest(object):

    def __init__(self, path, info):
        '''
        :param path:  传入执行接口脚本path路径，path格式经过解析后传入，格式为  ('绝对路径' , '文件名.py')
        :param info:  空字典格式，往里不断填入键值对
        '''
        self.path = path
        self.info = info
        self.__server = str(self.path[0]).split(os.sep)[-3]
        self.__model = str(self.path[0]).split(os.sep)[-1]
        self.info['path'] = self.path[0]
        self.info['server'] = self.__server
        self.info['model'] = self.__model
        self.info['test_caseName'] = str(self.path[1]).split('.')[0]
        self.info['run'] = True
        self.info['msg'] = []    # 专门记录各种错误消息
        self.info['finish'] = []

    def test_data_from_yaml(self):
        # 方法步骤1: 获取每个测试模块对应yaml路径，根据路径获取yaml内容
        yaml_path = get_yaml_path(self.path)
        TestCaseFromYaml = read_yaml(yaml_path)

        # 步骤2: 将yaml内容传入对应方法进行解析，获取并赋值给self.info
        self.info = TestDataProcess(self.info, TestCaseFromYaml, self.path).step_data_process()
        return self.info

    # 发送每一个接口请求
    def send_request(self):
        # 按照YAML文件中定义的接口执行循序，依次执行接口
        for step in self.info['step_execute']:
            # self.info['run'] == True 时，代表正常运行，遇到异常时，比如断言不通过，就会设置为False，从而终止运行
            if self.info['run']:

                # 判断接口是否存在推迟调用时间，即sleep休眠挂起时间
                if self.info[step].get('sleep') is not None:
                    time.sleep(self.info[step]['sleep'])

                # 判断接口是否存在依赖关系,并处理依赖关系
                if self.info[step].get('rely') is not None:
                    self.info = Rely(self.info).handle_rely(step)

                # 判断接口是否存在文件上传，并处理文件上传操作
                if self.info[step].get('req_file') is not None:
                    self.info = UploadFile(self.info).handle_upload_file(step)

                # 前置处理模块，即接口请求前先完成的处理操作
                if self.info[step].get('preconfig') is not None:
                    self.info = PreConfig(self.info).handle_preconfig(step)

                baseUrl = self.info[step]['baseUrl']
                req_body = self.info[step]['req_body']
                header = self.info[step]['headers']

                # 接口的方法（method），这里统一转换小写
                method = str(self.info[step]['method']).lower()
                self.info['finish'].append(step)
                # 根据接口方法，传递对应接口请求
                if method == "get":
                    try:
                        res = requests.get(url=baseUrl, params=req_body, headers=header)
                        self.info[step]['res'] = res
                    except Exception as e:
                        self.info['msg'].append("<{step}>接口执行get请求报错，错误信息为：{msg}".format(step=step, msg=traceback.print_exc()))

                elif method == "post":
                    try:
                        res = requests.post(url=baseUrl, data=req_body, headers=header)
                        self.info[step]['res'] = res
                    except Exception as e:
                        self.info['msg'].append("<{step}>接口执行post请求报错，错误信息为：{msg}".format(step=step, msg=traceback.print_exc()))

                elif method == "put":
                    try:
                        res = requests.put(url=baseUrl, data=req_body, headers=header)
                        self.info[step]['res'] = res
                    except Exception as e:
                        self.info['msg'].append("<{step}>接口执行put请求报错，错误信息为：{msg}".format(step=step, msg=traceback.print_exc()))

                elif method == "delete":
                    try:
                        res = requests.delete(url=baseUrl, data=req_body, headers=header)
                        self.info[step]['res'] = res
                    except Exception as e:
                        self.info['msg'].append("<{step}>接口执行delete请求报错，错误信息为：{msg}".format(step=step, msg=traceback.print_exc()))
                else:
                    self.info['run'] = False
                    # raise 支持自定义异常输出 ，f 是格式化字符串的一种，｛｝是变量的一种，如 {method} 变成变量
                    # raise InterfaceException(f"{self.info['test_caseName']}.yaml文件中，接口{step}的填写的method请求方法为：{method},未找到对应的请求方法, 请检查！")
                    self.info['msg'].append(f"{self.info['test_caseName']}.yaml文件中，接口{step}的填写的method请求方法为：{method},未找到对应的请求方法, 请检查！")

                # 接口后置处理模块
                if self.info[step].get('teardown') is not None:
                    self.info = TearDown(self.info).handle_teardown(step)

                # 每个断言执行记录,assertResult: 记录每个断言是否成功；assertMsg: 记录断言失败原因
                self.info[step]['assertResult'] = True
                self.info[step]['assertMsg'] = []
                self.info = AssertUtil(self.info, step).assert_rule()

    # 总控制，测试模块调用这个方法作为起点
    def AnyrobotSmokeTest(self):
        try:
            # 从YAML中读取解析测试用例数据
            self.test_data_from_yaml()
            # 发送接口请求
            self.send_request()
            return self.info
        except Exception as e:
            self.info['run'] = False
            self.info['msg'].append('程序处理异常:{msg}'.format(msg=traceback.format_exc()))
            return self.info