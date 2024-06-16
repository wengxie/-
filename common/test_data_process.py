# -*- coding: UTF-8 -*-
"""
@Date  2022/7/25 19:57
@auth  翁勰         
@File  test_data_process.py.py
@Email  Nelson.weng@aishu.cn
@Description   YAML传入的测试用例数据处理，返回给info，用于调用
"""
import copy
import json
import traceback

from common.Interface_parameters import Parameters
from common.environment_util import Splice_url, get_json_path
from config.headers import header


class TestDataProcess:

    def __init__(self, info, data, path):
        '''
        :param info: all_request.py传入的info，用于每个接口用例的信息，如name、url等
        :param data: 传入读取的YAML数据，字典格式，将YAML读取结果传入进来进行解析
        :param path: 传入执行接口脚本path路径，path格式经过解析后传入，格式为  ('绝对路径' , '文件名.py')
        '''
        self.info = info
        self.data = data
        self.path = path

    # 每一步step内的参数处理，如 url = self.info['Test']['interface_1']['url']
    def initial_each_step_data(self, step):
        '''
        :param step: 传入yaml的第几个接口，如['interface_1', 'interface_2']
        :return: 返回解析处理完的yaml文件，赋值给self.info
        '''
        # self.info[step] 将会包含对应step下的所有的Description、baseUrl、method、headers、req_body等等
        self.info[step] = {}
        # 开始一个一个对应step下的接口参数进行处理、赋值
        Description = self.data['Test'][step]['Description']
        baseUrl = Splice_url(self.data['Test'][step]['baseUrl'])
        method = self.data['Test'][step]['method']

        # self.info[step]['headers'] = header
        headers = header

        # 判断YAML中header有没有额外增加，有就补上，get('xxx') 表示正常获取xxx的值，没有就返回None
        if self.data['Test'][step].get('headers') is not None:
            header_add_seq = self.data['Test'][step]['headers']
            # 获取YAML中新加的header的key，如jwt-token，然后把值补充到总的headers中
            for key in header_add_seq.keys():
                headers.update({key: header_add_seq[key]})
        # 深复制，即将被复制对象完全再复制一遍作为独立的新个体单独存在，如果不用深复制，下一个接口的headers改变，会影响到上一个接口
        self.info[step]['headers'] = copy.deepcopy(headers)

        # 接口发送参数req_body、断言verify
        req_body = self.data['Test'][step]['req_body']
        verify = self.data['Test'][step]['verify']

        self.info[step]['Description'] = Description
        self.info[step]['baseUrl'] = baseUrl
        self.info[step]['method'] = method
        self.info[step]['verify'] = verify

        # 接口依赖
        if self.data['Test'][step].get('rely') is not None:
            self.info[step]['rely'] = self.data['Test'][step]['rely']

        # 接口进程挂起的时间（函数推迟调用），单位 秒
        if self.data['Test'][step].get('sleep') is not None:
            self.info[step]['sleep'] = self.data['Test'][step]['sleep']

        # 前置处理模块，即接口请求前处理操作模块
        if self.data['Test'][step].get('preconfig') is not None:
            self.info[step]['preconfig'] = self.data['Test'][step]['preconfig']

        # 后置处理模块，即接口请求后处理操作模块
        if self.data['Test'][step].get('teardown') is not None:
            self.info[step]['teardown'] = self.data['Test'][step]['teardown']

        # 文件上传模块
        if self.data['Test'][step].get('req_file') is not None:
            self.info[step]['req_file'] = self.data['Test'][step]['req_file']

        # req_body请求体 为空时
        if len(req_body) == 0:
            self.info[step]['req_body'] = json.dumps('')
        # req_body请求体 不为空时
        else:
            # 如 req_body: '$jsonname$'时，说明通过json文件传参
            if '$' in req_body:
                jsonname = str(req_body).strip('$')
                jsonpath = get_json_path(self.path, jsonname)
                try:
                    # json.load 读取json文件，返回为dict类型，这里也需要转换为str类型
                    self.info[step]['req_body'] = json.dumps(json.load(open(file=jsonpath, mode='r', encoding='utf-8')))
                except:
                    self.info['run'] = False
                    self.info['msg'].append('程序处理异常:{msg}'.format(msg=traceback.format_exc()))
                finally:
                    return self.info
            # 直接通过键值对传参
            else:
                self.info[step]['req_body'] = json.dumps(req_body)


    # 先处理YAML中的step,如 execute: [interface_1,interface_2]即接口执行循序，赋值给step，用于一步步处理测试用例数据
    def step_data_process(self):
        all_step = self.data['Test']['execute']
        # 赋值Yaml中的两个属性execute、describe；server在之前赋值过
        self.info['step_execute'] = all_step
        self.info['describe'] = self.data['Test']['describe']

        # 按照接口逻辑处理测试用例数据
        for step in all_step:
            # 赋值每一个step的测试用例数据
            self.initial_each_step_data(step)

            if self.info['run']:
                # 处理每一个接口self.info[self]内容中存在的参数化数据处理 -> ${Key}$
                Parameters(self.info).handle_each_step_parameters(step)
        return self.info