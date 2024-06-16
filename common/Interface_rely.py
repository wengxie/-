# -*- coding: UTF-8 -*-
"""
@Date  2022/8/4 11:20
@auth  翁勰         
@File  Interface_rely.py.py
@Email  Nelson.weng@aishu.cn
@Description   接口关联管理

rely的Yaml样式
    rely:
      relation_1:
        baseUrl:
          interface_1: alertRuleId
      relation_2:
        body:
          interface_1: alertRuleId
          key: nameID
          type: string
      relation_3:
        body:
          interface_2: nameID
          key: nameID
          type: string
"""
import json
import traceback

from jsonpath import jsonpath

from common.replace_process import rely_baseUrlstr_replace, rely_reqJsonBody_replace, rely_headers_replace


class Rely(object):

    def __init__(self, info):
        self.info = info

    # 处理接口依赖，包括BaseUrl依赖、body依赖、headers依赖
    def handle_rely(self, step):
        # relation_key对应上方示例中的 relation_1、relation_2
        for relation_key in self.info[step]['rely'].keys():
            # effect_body 表示依赖影响的范围 为上方示例中的 baseUrl（影响url） 或者 body（影响请求体）
            for effect_body in self.info[step]['rely'][relation_key].keys():

                # 第一步：关联接口，对应上方示例的 interface_1，表示要从哪一个接口取得返回参数
                rely_interface = list(self.info[step]['rely'][relation_key][effect_body].keys())[0]
                # 判断关联接口返回体是否为空，为空则终止运行，不为空就取值
                if self.info[rely_interface].get('res') is not None:
                    # 判断返回体是否是json()格式，因为不是json（如xml）时，json()就会报错，说明此时返回体格式不正确
                    try:
                        response_body = self.info[rely_interface]['res'].json()
                    except Exception as e:
                        self.info['run'] = False
                        self.info['msg'].append("<{interface}>接口返回体格式不正确，不是json类型".format(interface=rely_interface))
                        return self.info
                else:
                    self.info['run'] = False
                    self.info['msg'].append("<{interface}>接口返回体格式为空".format(interface=rely_interface))
                    return self.info

                # 第二步：取rely中接口的关键字，如上方示例 interface_1: alertRuleId ，则取 alertRuleId 这个关键字
                # 关联接口关键字，表示从关联接口返回体中，要取值时对应的关键字
                relyInterface_key = self.info[step]['rely'][relation_key][effect_body][rely_interface]
                # 判断关联接口返回体中，是否有该关键字：没有，说明关键字填写错误; 有，就取出返回体中该关键字对应的值
                relyInterface_data = jsonpath(response_body, '$..{name}'.format(name=relyInterface_key))
                # 如果是bool，说明没有该关键字对应的值
                if isinstance(relyInterface_data, bool):
                    self.info['run'] = False
                    self.info['msg'].append('接口<{step}>关联的接口<{interface}>数据源返回体中不存在字段<{relyInterface_key}>的值'.format(step=step, interface=rely_interface, relyInterface_key=relyInterface_key))
                    return self.info

                # 第三步：判断 effect_body 依赖影响的范围，是 baseUrl还是body
                if effect_body == 'baseUrl':
                    # 返回体中取得关键字对应的值，如果是字典、元组、列表的话，是没法赋值给url的，直接报错终止
                    if isinstance(relyInterface_data[0], list) or isinstance(relyInterface_data[0], dict) or isinstance(relyInterface_data[0], tuple):
                        self.info['run'] = False
                        self.info['msg'].append('接口<{step}>关联的接口<{interface}>数据源返回体获取的<{relyInterface_key}>的值不是string类型，无法赋值给baseUrl'.format(step=step, interface=rely_interface, relyInterface_key=relyInterface_key))
                        return self.info
                    else:
                        baseUrl = self.info[step]['baseUrl']
                        left = '$'
                        right = '$'
                        # 用于替换参数化内容，如 {'relation_1': '111111'}
                        replace_dict = {}
                        replace_dict[relation_key] = str(relyInterface_data[0])
                        # 执行关联字符串替换参数化方法，如/manager/$relation_1$ -> {'relation_1': '111111'} 最终返回/manager/111111
                        baseUrl_replace = rely_baseUrlstr_replace(baseUrl, replace_dict, left, right)
                        self.info[step]['baseUrl'] = baseUrl_replace

                elif effect_body == 'body':
                    # body依赖处理：第一步，示例 取得rely->relation_2->body 下包含的关键字，为interface_1、key、type
                    body_keys = list(self.info[step]['rely'][relation_key][effect_body].keys())

                    # 判断关键字中，是否包含interface_1、key、type三要素，interface_1上方检测过了，这里检测key、type
                    if 'key' in body_keys and 'type' in body_keys:
                        key = self.info[step]['rely'][relation_key][effect_body]['key']
                        body_type = self.info[step]['rely'][relation_key][effect_body]['type']

                        # 步骤二，判断type类型，即实际返回体对应关键字的返回类型 与 用户设定的期望类型type是否一致
                        if body_type in str(type(relyInterface_data[0])):
                            try:
                                # 获取当前接口请求体，注意转为json，因为在处理时，都dump过，也就是字符串，所以需要转换一下
                                req_body_json = json.loads(self.info[step]['req_body'])
                                # 判断请求体中是否存在key关键字对应的值，存在就提取
                                req_body_json_keyValue = jsonpath(req_body_json, '$..{key}'.format(key=key))

                                # 步骤三，判断接口请求体中是否有对应关键字key，没有就停止，有就继续替换
                                if isinstance(req_body_json_keyValue, bool):
                                    self.info['run'] = False
                                    self.info['msg'].append('接口<{step}>的req_body请求体没有对应的{key}关键字，请检查'.format(step=step, key=key))
                                else:
                                    # 步骤四，前期检查都通过后，调用请求体替换方法，将请求体中特定关键字下对应relation内容替换
                                    # 分别传入请求体、要替换的关键字、对应relation、替换内容
                                    req_body_replace = rely_reqJsonBody_replace(req_body_json, key, relation_key, relyInterface_data[0])
                                    self.info[step]['req_body'] = json.dumps(req_body_replace)

                            except Exception as e:
                                self.info['run'] = False
                                self.info['msg'].append('接口<{step}>的req_body请求体无法转换为json格式，检查请求体格式'.format(step=step))
                        else:
                            self.info['run'] = False
                            self.info['msg'].append('接口<{step}>下{relation_key} 的body中,用户设定的预期type与实际返回体对应关键字的类型不一致，请检查'.format(
                                step=step, relation_key=relation_key))
                    else:
                        self.info['run'] = False
                        self.info['msg'].append('接口<{step}>中 {relation_key} 的body下缺少key或者type，请保证格式正确'.format(
                            step=step, relation_key=relation_key))

                elif effect_body == 'headers':
                    # 返回体中取得关键字对应的值，如果是字典、列表的话，是没法赋值给headers的，直接报错终止
                    if isinstance(relyInterface_data[0], list) or isinstance(relyInterface_data[0], dict):
                        self.info['run'] = False
                        self.info['msg'].append(
                            '接口<{step}>关联的接口<{interface}>数据源返回体获取的<{relyInterface_key}>的值不是string类型，无法赋值给headers'.format(
                                step=step, interface=rely_interface, relyInterface_key=relyInterface_key))

                    else:
                        # 判断 headers 依赖格式是否正确
                        if 'key' in list(self.info[step]['rely'][relation_key][effect_body].keys()):
                            try:
                                headersBody = self.info[step]['headers']
                                left = '$'
                                right = '$'
                                # 用于替换参数化内容，如 {'relation_1': '111111'}
                                replace_dict = {}
                                replace_dict[relation_key] = str(relyInterface_data[0])
                                # 取出依赖key设定的值，如 YAML中对应依赖下 key: jwt-token 那么下方的key就是jwt-token
                                replace_key = self.info[step]['rely'][relation_key][effect_body]['key']
                                # 执行关联字符串替换参数化方法，如/manager/$relation_1$ -> {'relation_1': '111111'} 最终返回/manager/111111
                                headersBody_replaced = rely_headers_replace(headersBody, replace_dict, replace_key, left, right)
                                self.info[step]['headers'] = headersBody_replaced

                            except Exception as e:
                                self.info['run'] = False
                                self.info['msg'].append('接口<{step}>的{relation_key} 的headers, 出现依赖赋值出错，具体错误：{msg}'.format(
                                    step=step, relation_key=relation_key, msg=traceback.format_exc()))
                        else:
                            self.info['run'] = False
                            self.info['msg'].append('接口<{step}>中 {relation_key} 的headers下缺少key，请保证headers依赖格式正确'.format(
                                step=step, relation_key=relation_key))

                else:
                    self.info['run'] = False
                    self.info['msg'].append('接口<{step}>的rely中<{effect_body}>填写错误，必须为baseUrl或者body'.format(step=step, effect_body=effect_body))
                    return self.info

        # 最终总的返回
        return self.info