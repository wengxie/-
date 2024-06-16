# -*- coding: UTF-8 -*-
"""
@Date  2022/7/27 21:09
@auth  翁勰         
@File  Allure_util.py
@Email  Nelson.weng@aishu.cn
@Description   Allure元素统一处理
"""
import json

import allure
import pytest


class AllureUtils(object):

    def __init__(self, info):
        '''
        :param info: 每个模块测试执行完所有的参数赋值、返回结果
        '''
        self.info = info

    def initial_allure_step(self):

        if len(self.info['msg']) > 0:
            with allure.step('error message'):
                for errorMessage in self.info['msg']:
                    allure.attach('error', 'error : {error}'.format(error=errorMessage))

        # 遍历接口执行序列，如[interface_1,interface_2,interface_3]
        for step in self.info['finish']:
            # with 所求值的对象必须有一个enter()方法，一个exit()方法。帮助自动进入，结束后自动退出，简化代码
            # allure.step 对比 @allure.step 代码可读性更好，不会带上函数里面的传参和对应的值。
            with allure.step(step):
                if self.info[step].get('Description') is not None:
                    with allure.step('测试用例描述 : {Description}'.format(Description=self.info[step]['Description'])):
                        allure.attach('Description', 'Description')

                # url
                with allure.step('baseUrl'):
                    if self.info[step].get('baseUrl') is not None:
                        allure.attach('baseUrl', 'url : {baseUrl}'.format(baseUrl=self.info[step]['baseUrl']))

                # 请求方式
                with allure.step('method'):
                    if self.info[step].get('method') is not None:
                        allure.attach('method', 'method : {method}'.format(method=self.info[step]['method']))

                # headers 按照 key ：values 方式输出
                with allure.step('headers'):
                    if self.info[step].get('headers') is not None:
                        for key in self.info[step]['headers'].keys():
                            allure.attach('headers', '{key} : {headers}'.format(key=key, headers=self.info[step]['headers'][key]))

                # 延迟请求，接口休眠
                if self.info[step].get('sleep') is not None:
                    with allure.step('sleep'):
                        allure.attach('sleep', 'sleep : {sleep}'.format(sleep=self.info[step]['sleep']))

                # 接口前置处理操作
                if self.info[step].get('preconfig') is not None:
                    with allure.step('preconfig'):
                        file = self.info[step]['preconfig']['file']
                        setup = self.info[step]['preconfig']['setup']
                        allure.attach('preconfig', '前置处理 : 调用前置处理{file}模块中{setup}命令'.format(file=file, setup=setup))

                # 请求体
                if self.info[step].get('req_body') is not None:
                    with allure.step('body'):
                        # 判断接口请求体是否是文件上传'MultipartEncoder'类型，因为 MultipartEncoder没有len，用了会报错
                        if str(type(self.info[step].get('req_body'))) == "<class 'requests_toolbelt.multipart.encoder.MultipartEncoder'>":
                            allure.attach('body', 'body : {body}'.format(body=self.info[step]['req_body']))
                        else:
                            if len(self.info[step].get('req_body')) != 0:
                                try:
                                    # 转为json格式，因为请求体中有些是文字，不转会显示乱码
                                    allure.attach('body', 'body : {body}'.format(body=json.loads(self.info[step]['req_body'])))
                                except Exception as e:
                                    allure.attach('body', 'body : {body}'.format(body=self.info[step]['req_body']))

                # 响应体
                if self.info[step].get('res') is not None:
                    with allure.step('response'):
                        allure.attach('status', 'status : {status}'.format(status=self.info[step]['res'].status_code))
                        allure.attach('res_time', 'res_time : {res_time} s'.format(res_time=self.info[step]['res'].elapsed.total_seconds()))
                        res_body = self.info[step]['res'].text
                        if len(res_body) != 0:
                            try:
                                # 默认返回内容用json()解析，会输出中文；如果返回类型是json()无法解析的，如xml，就用text输出。两不误
                                allure.attach('res_body', 'res_body : {res_body}'.format(res_body=self.info[step]['res'].json()))
                            except Exception as e:
                                allure.attach('res_body', 'res_body : {res_body}'.format(res_body=res_body))
                        else:
                            allure.attach('res_body', 'res_body : {res_body}'.format(res_body='返回内容为空'))

                # 接口后置处理操作
                if self.info[step].get('teardown') is not None:
                    with allure.step('teardown'):
                        file = self.info[step]['teardown']['file']
                        setup = self.info[step]['teardown']['setup']
                        allure.attach('teardown', '后置处理 : 调用后置处理{file}模块中{setup}命令'.format(file=file, setup=setup))

                # 断言错误内容提示
                if self.info[step].get('assertMsg') is not None:
                    with allure.step('assertMsg'):
                        assertMsg = self.info[step]['assertMsg']
                        if len(assertMsg) != 0:
                            for assertText in assertMsg:
                                allure.attach('assertMsg', 'assertText : {assertText}'.format(assertText=assertText))

                # 设置的断言
                if self.info[step].get('verify') is not None:
                    with allure.step('assertInfo'):
                        for verify_body in self.info[step]['verify']:
                            allure.attach('verify', 'verify : {verify}'.format(verify=verify_body))

    # allure关于断言的配置
    def allure_assert_result(self):
        if len(self.info['finish']) == 0:
            pytest.fail('测试运行未执行,请检查')

        for step in self.info['finish']:
            # 判断是否有记录断言结果
            if self.info[step].get('assertResult') is not None:
                if self.info[step]['assertResult']:
                    assert True
                else:
                    # 当assert()语句失败的时候，就会引发AssertionError,所有遇到AssertionError不要怕，是正常的
                    assert False, '<{step}>接口断言失败'.format(step=step)
            # 没记录的话，说明执行到断言结果之前就出现错误，输出错误
            else:
                pytest.fail(self.info['msg'])