# -*- coding: UTF-8 -*-
"""
@Date  2022/7/14 17:11
@auth  翁勰         
@File  test_default_Login.py
@Email  Nelson.weng@aishu.cn
@Description   用户登录接口测试场景 模块
"""
import json

import allure
import pytest
import requests
import yaml
import os

from common.Allure_util import AllureUtils
from common.yaml_util import read_yaml
from common.environment_util import get_yaml_path
from interface.all_request import AllRequest

# 获取当前py文件路径，os.path.abspath获取绝对路径，os.path.split对路径镜像拆分，拆为 ('路径' , '文件名.py')
path = os.path.split(os.path.abspath(__file__))
# 执行YAML文件每一个接口用例，将过程每一个参数，每一个接口返回结果都赋值给 case_result_info
case_result_info = AllRequest(path, info={}).AnyrobotSmokeTest()

@allure.feature(case_result_info['server'])
class TestDefaultLogin2:

    @pytest.mark.testcase
    @pytest.mark.all
    @allure.story(case_result_info['model'])
    @allure.title(case_result_info['describe'])
    def test_admin_login(self):
        # allure 信息处理
        AllureUtils(case_result_info).initial_allure_step()
        AllureUtils(case_result_info).allure_assert_result()

if __name__ == '__main__':
    pytest.main(['-vs', 'test_default_Login.py'])




