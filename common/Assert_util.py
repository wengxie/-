# -*- coding: UTF-8 -*-
"""
@Date  2022/7/30 17:29
@auth  翁勰         
@File  Assert_util.py.py
@Email  Nelson.weng@aishu.cn
@Description   断言处理模块，负责一切断言
"""
import traceback

from common.InterfaceException import InterfaceException
from jsonpath import jsonpath


class AssertUtil(object):

    def __init__(self, info, step):
        self.info = info
        self.step = step

    # 断言类型为eq（相等）时
    def eq(self, step, verify, key):
        if self.info['run']:
            # 对比状态码
            if verify[key][0] == 'STATUS':
                try:
                    response_code = self.info[step]['res'].status_code
                    if verify[key][1] != response_code:
                        self.info['run'] = False
                        self.info[step]['assertResult'] = False
                        self.info['msg'].append('<{step}>接口{verify} 中 实际值: {actual}; 期望值: {expect}'.format(step=step, verify=verify, actual=response_code, expect=verify[key][1]))
                        self.info[step]['assertMsg'].append('<{step}>接口{verify} 中 实际值: {actual}; 期望值: {expect}'.format(step=step, verify=verify, actual=response_code, expect=verify[key][1]))
                except Exception as e:
                    self.info['run'] = False
                    self.info['msg'].append('<{step}>接口 程序处理异常:{msg}'.format(step=step, msg=traceback.format_exc()))
                finally:
                    return self.info

            # 对比返回体中是否有对应关键字，如YAML中 - eq: [RESPONSE,userId]
            elif verify[key][0] == 'RESPONSE':
                try:
                    res_body = self.info[step]['res'].json()
                    # 这里表示用户需要用于判断的关键字，如上方对应的 userId
                    verify_key_yaml = verify[key][1]
                    # 通过用于判断的关键字去获取返回体中对应的内容，如果获取不到，说明返回体中没有这个关键字，返回为False，为bool类型
                    # 如果返回体有对应关键字，那么返回一定是[]型，所以通过判断返回类型，判断返回体中是否有对应关键字
                    verify_key_yaml_data = jsonpath(res_body, "$..{verify_key_yaml}".format(verify_key_yaml=verify_key_yaml))
                    if isinstance(verify_key_yaml_data, bool):
                        self.info['run'] = False
                        self.info[step]['assertResult'] = False
                        self.info['msg'].append('<{step}>接口返回值 : {body}中，没有断言设置的{filed}字段'.format(step=step, body=res_body, filed=verify_key_yaml))
                        self.info[step]['assertMsg'].append('<{step}>接口返回值 : {body}中，没有断言设置的{filed}字段'.format(step=step, body=res_body, filed=verify_key_yaml))
                except Exception as e:
                    self.info['run'] = False
                    self.info['msg'].append('<{step}>接口 程序处理异常:{msg}'.format(step=step, msg=traceback.format_exc()))
                finally:
                    return self.info
            # 其他类型通通为对比实际返回值与预期返回值 如 ：- eq: [message,用户登录名已存在]
            else:
                try:
                    res_body = self.info[step]['res'].json()
                    # 对应上方message
                    verify_key_yaml = verify[key][0]
                    # 取接口返回值中对应 message 的值
                    verify_key_yaml_data = jsonpath(res_body, "$..{verify_key_yaml}".format(verify_key_yaml=verify_key_yaml))
                    # 接口返回值取不到有关于 对应关键字 的值，所以是False
                    if isinstance(verify_key_yaml_data, bool):
                        self.info['run'] = False
                        self.info[step]['assertResult'] = False
                        self.info['msg'].append('<{step}>接口返回值 : {body}中，没有{filed}字段对应的值; 预期值 {filed} = {value}'.format(step=step, body=res_body, filed=verify_key_yaml, value=verify[key][1]))
                        self.info[step]['assertMsg'].append(
                            '<{step}>接口返回值 : {body}中，没有{filed}字段对应的值; 预期值 {filed} = {value}'.format(step=step, body=res_body, filed=verify_key_yaml, value=verify[key][1]))
                    if verify_key_yaml_data[0] != verify[key][1]:
                        self.info['run'] = False
                        self.info[step]['assertResult'] = False
                        self.info['msg'].append('<{step}>接口 {verify} 中 实际值: {actual}; 期望值: {expect}'.format(step=step, verify=verify, actual=verify_key_yaml_data[0], expect=verify[key][1]))
                        self.info[step]['assertMsg'].append(
                            '<{step}>接口 {verify} 中 实际值: {actual}; 期望值: {expect}'.format(step=step, verify=verify, actual=verify_key_yaml_data[0], expect=verify[key][1]))
                except Exception as e:
                    self.info['run'] = False
                    self.info['msg'].append('<{step}>接口 程序处理异常:{msg}'.format(step=step, msg=traceback.format_exc()))
                finally:
                    return self.info

    # 断言类型为uq（不相等）时
    def uq(self, step, verify, key):
        if self.info['run']:
            if verify[key][0] == 'STATUS':
                try:
                    response_code = self.info[step]['res'].status_code
                    if verify[key][1] == response_code:
                        self.info['run'] = False
                        self.info[step]['assertResult'] = False
                        self.info['msg'].append('<{step}>接口 {verify} 中要满足 unequal 实际值: {actual}; 期望值: {expect}'.format(step=step, verify=verify, actual=response_code, expect=verify[key][1]))
                        self.info[step]['assertMsg'].append(
                            '{verify} 中要满足 unequal 实际值: {actual}; 期望值: {expect}'.format(verify=verify, actual=response_code, expect=verify[key][1]))
                except Exception as e:
                    self.info['run'] = False
                    self.info['msg'].append('<{step}>接口 程序处理异常:{msg}'.format(step=step, msg=traceback.format_exc()))
                finally:
                    return self.info
            # 需要实际返回值与预期返回值不同 如 ：- uq: [message,用户登录名已存在]，则message实际返回值 != '用户登录名已存在'
            else:
                try:
                    res_body = self.info[step]['res'].json()
                    verify_key_yaml = verify[key][0]
                    verify_key_yaml_data = jsonpath(res_body, "$..{verify_key_yaml}".format(verify_key_yaml=verify_key_yaml))
                    if not isinstance(verify_key_yaml_data, bool) and verify_key_yaml_data[0] == verify[key][1]:
                        self.info['run'] = False
                        self.info[step]['assertResult'] = False
                        self.info['msg'].append('<{step}>接口 {verify} 中要满足 unequal 实际值: {actual}; 期望值: {expect}'.format(step=step, verify=verify, actual=verify_key_yaml_data[0], expect=verify[key][1]))
                        self.info[step]['assertMsg'].append('<{step}>接口 {verify} 中要满足 unequal 实际值: {actual}; 期望值: {expect}'.format(step=step, verify=verify, actual=verify_key_yaml_data[0], expect=verify[key][1]))
                except Exception as e:
                    self.info['run'] = False
                    self.info['msg'].append('<{step}>接口 程序处理异常:{msg}'.format(step=step, msg=traceback.format_exc()))
                finally:
                    return self.info

    # 处理断言类型填写错误时
    def switcher_with_key(self, step, verify, key):
        '''
        :param step: 执行第几步接口
        :param verify: 具体断言，如 [{'eq': ['success', 1]}]}
        :param key: 提取的断言的关键字，也就是上方的 'eq'
        :return:
        '''
        self.info['run'] = False
        self.info['msg'].append('接口<{step}>填写的断言类型为：{key},未找到对应的断言类型, 请检查！'.format(step=step, key=key))


    # 判断断言类型，根据类型执行对应断言方法
    def assert_rule(self):
        # 对应断言方法，self.eq就是调用 自定义eq等于 方法
        switcher = {
            'eq': self.eq,
            'uq': self.uq
        }
        # 一个用例的断言会有多条，所以遍历处理
        for verify in self.info[self.step]['verify']:
            for key in verify.keys():
                # .get()是指通过key获取，比如key是'eq'，那么获取后就是self.eq，然后执行self.eq(self.step, verify, key) 方法
                # 如果key没有对应值，那么就是self.switcher_with_key(self.step, verify, key) 方法
                switcher.get(key, self.switcher_with_key)(self.step, verify, key)
        return self.info
