# -*- coding: UTF-8 -*-
"""
@Date  2022/7/15 15:50
@auth  翁勰         
@File  environment_util.py
@Email  Nelson.weng@aishu.cn
@Description   用于获取 用例执行要用到的 环境信息：
                1.获取Yaml、Json、Casepy的路径
                2.获取host 拼接最终url
"""
import os
from urllib.parse import urljoin
from config.host import host_dict

# 项目根目录路径
# os.path.dirname 获取父路径
PROJECT_ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

# 获取用例YAML目录路径
def get_yaml_path(path):
    # 通过传入的脚本路径，提取服务名server，如最高一级的Auth-Manager，下方有（requests、json、yaml），再下一层为model
    server = path[0].split(os.sep)[-3]
    # 获取脚本所在模块，这里就是default_Login模块
    model = path[0].split(os.sep)[-1]
    # 获取当前脚本名称，如 test_default_Login.py 取 test_default_Login
    filename = path[1].split('.')[0]
    yaml_path = os.path.join(PROJECT_ROOT_DIR, 'testcase', server, 'test_yaml', model, filename + '.yaml')
    return yaml_path

# 获取用例JSON目录路径
def get_json_path(path, jsonname):
    server = path[0].split(os.sep)[-3]
    model = path[0].split(os.sep)[-1]
    json_path = os.path.join(PROJECT_ROOT_DIR, 'testcase', server, 'test_body', model, jsonname + '.json')
    return json_path

# 获取保存前置处理脚本的目录, 如 tools/interface_tools/preconfig
def get_preconfig_path():
    '''
    :return: 返回保存前置处理脚本的目录，tools —> interface_tools -> preconfig ，如 tools/interface_tools/preconfig
    '''
    file_path = os.path.join(PROJECT_ROOT_DIR, 'tools', 'interface_tools', 'preconfig')
    return file_path

# 获取保存后置处理脚本的目录, 如 tools/interface_tools/teardown
def get_teardown_path():
    '''
    :return: 返回保存后置处理脚本的目录，tools —> interface_tools -> teardown ，如 tools/interface_tools/teardown
    '''
    file_path = os.path.join(PROJECT_ROOT_DIR, 'tools', 'interface_tools', 'teardown')
    return file_path

# 拼接url
def Splice_url(path):
    protocol = host_dict['protocol']
    ip = host_dict['ip']
    port = host_dict['port']
    hosturl = urljoin(base='{protocol}://{ip}:{port}'.format(protocol=protocol, ip=ip, port=port), url=path)
    return hosturl


if __name__ == '__main__':
    print(os.listdir('D:/pytest/Weng_Pytest_Demo/common'))
    print('aaa.py'.split('.')[0])
