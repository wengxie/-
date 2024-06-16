# -*- coding: UTF-8 -*-
"""
@Date  2022/8/24 15:53
@auth  翁勰         
@File  uploadFile.py.py
@Email  Nelson.weng@aishu.cn
@Description   处理接口上传文件模块
"""
import json
import os
import random
import traceback

import requests
from requests_toolbelt import MultipartEncoder


class UploadFile(object):

    def __init__(self, info):
        self.info = info

    def handle_upload_file(self, step):
        '''
        处理文件上传操作中需要发送的请求体内容，对应self.info[step]['req_body']
        :param step: 对应所在接口
        :return: 返回处理完的 self.info
        '''
        # 步骤一、判断基础格式是否正确
        if self.info[step]['req_file'].get('key') is not None and self.info[step]['req_file'].get('file_path') is not None and self.info[step]['req_file'].get('file_Mime') is not None:
            req_body = self.info[step]['req_body']
            # 步骤二、判断请求体是否为空：请求体为空，说明上传文件的接口请求体错误
            if len(req_body) == 0:
                self.info['run'] = False
                self.info['msg'].append(
                    "<{step}>接口检测到存在文件上传操作'req_file',但是对应请求体'req_body'却为空,请检查！".format(step=step))
            else:
                try:
                    # 步骤三、由于之前赋值时，经过dumps，变为字符串格式，这里重新变回原有对象格式(dict、list之类的)
                    req_body = json.loads(self.info[step]['req_body'])
                    # 如果loads之后发现不是dict、list类型的，说明文件上传的接口请求体格式就有问题，直接报错
                    if not isinstance(req_body, (dict, list)):
                        self.info['run'] = False
                        self.info['msg'].append("<{step}>接口检测到存在文件上传操作'req_file',但是请求体并不是dict or list类型，请求体类型有误".format(step=step))
                        return self.info

                    # 取Yaml中的值，注意eval文件路径，格式化字符串；不然纯字符串如""r\'D:\\333.png\'""遇到open就会报错
                    req_file_key = self.info[step]['req_file']['key']
                    req_file_filePath = eval(self.info[step]['req_file']['file_path'])
                    req_file_fileMime = self.info[step]['req_file']['file_Mime']
                    # 拼接成MultipartEncoder所需的上传文件固定格式 (文件名, 文件内容, 文件Mime)
                    file_value = (os.path.basename(req_file_filePath), open(req_file_filePath, 'rb'), req_file_fileMime)

                    # 如果请求体中没有req_file_key对应的关键字
                    # 如请求体为 {'logo': (filevalue)},但是Yaml中key设置的值为 key: logoname,请求体中找不到logoname，就报错
                    if req_body.get(req_file_key) is None:
                        self.info['run'] = False
                        self.info['msg'].append(
                            "<{step}>接口上传文件请求体找不到对应key设置的{req_file_key}关键字".format(step=step, req_file_key=req_file_key))
                        return self.info

                    # 文件上传常见请求体格式 {'file_key':  (filename, open(file_path, 'rb'), '文件的MiMe类型，如图片的image/png')}
                    # 步骤四、赋值file_key：服务端约定的上传文件字段名。一般用到的是file，需要和服务端沟通获取
                    req_body[req_file_key] = file_value
                    # 步骤五、上传文件固定格式，利用MultipartEncoder，其中fields为请求体，boundary按照如下固定生成即可
                    self.info[step]['req_body'] = MultipartEncoder(
                        fields=req_body,
                        boundary='-----------------------------' + str(random.randint(1e28, 1e29 - 1))
                    )
                    # 上传文件时，请求头Content-Type采用固定格式替换即可（就是Multipart/form-data文件格式）
                    self.info[step]['headers']['Content-Type'] = self.info[step]['req_body'].content_type

                except Exception as e:
                    self.info['run'] = False
                    self.info['msg'].append('<{step}>接口程序处理异常:{msg}'.format(step=step, msg=traceback.format_exc()))

            return self.info

        else:
            self.info['run'] = False
            self.info['msg'].append(
                "<{step}>接口检测到存在文件上传操作'req_file',但是对应格式错误,缺少key、file_path或者file_Mime关键字,请检查！".format(step=step))
            return self.info

if __name__ == '__main__':
    # 以下为上传文件接口实战，便于读者了解文件接口上传方式
    url = 'http://10.4.117.56/manager/oem/image/?'
    file_path = r'D:\333.png'
    req_body = {
        'logotext': (os.path.basename(file_path), open(file_path, 'rb'), 'image/png')
    }
    header = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'user': 'f5a08cb056c539d76f373bbc94458e39',
        'token': 'fde85f5a2644f97234a83ad5f5246acc676efee3a2d92e853a3454aee6f3a0e3',
        'jwt-token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwicGVybWlzc2lvbiI6eyJJRF9NQUlOUEFHRSI6dHJ1ZSwiSURfU0VBUkNIIjp0cnVlLCJJRF9TRUFSQ0hfQ1JFQVRFIjp0cnVlLCJJRF9TRUFSQ0hfU0FWRSI6dHJ1ZSwiSURfU0VBUkNIX09QRU4iOnRydWUsIklEX1NFQVJDSF9TSEFSRSI6dHJ1ZSwiSURfU0VBUkNIX0RPV05MT0FEIjp0cnVlLCJJRF9SRUxBVElPTlNISVBfR1JBUEgiOnRydWUsIklEX1ZJU1VBTCI6dHJ1ZSwiSURfVklTVUFMX0NSRUFURSI6dHJ1ZSwiSURfVklTVUFMX1NBVkUiOnRydWUsIklEX1ZJU1VBTF9PUEVOIjp0cnVlLCJJRF9WSVNVQUxfU0hBUkUiOnRydWUsIklEX0RBVEVTT1VSQ0UiOnRydWUsIklEX0RBVEFTT1VSQ0VfSU5QVVQiOnRydWUsIklEX0RBVEVTT1VSQ0VfVVBMT0FEIjp0cnVlLCJJRF9EQVRFU09VUkNFX0NPTExFQ1RJT04iOnRydWUsIklEX0RBVEVTT1VSQ0VfQUdFTlRfTUFOQUdFUiI6dHJ1ZSwiSURfREFURVNPVVJDRV9EQkNPTk5FQ1QiOnRydWUsIklEX0RBVEVTT1VSQ0VfSU5ERVhfTUFOQUdFIjp0cnVlLCJJRF9EQVRFU09VUkNFX09QRU5fTE9HIjp0cnVlLCJJRF9EQVRFU09VUkNFX0RBVEFfU1RSRUFNIjp0cnVlLCJJRF9EQVRFU09VUkNFX0FSQ0hJVkUiOnRydWUsIklEX0RBVEVTT1VSQ0VfQUdFTlRfQVVESVQiOnRydWUsIklEX0FMRVJUIjp0cnVlLCJJRF9BTEVSVF9SRUNPUkQiOnRydWUsIklEX0FMRVJUX1JFQ09SRF9DTEVBUiI6dHJ1ZSwiSURfQUxFUlRfUkVDT1JEX0VYUE9SVCI6dHJ1ZSwiSURfQUxFUlRfU1RSQVRFR1kiOnRydWUsIklEX0FMRVJUX1NUUkFURUdZX0NSRUFURSI6dHJ1ZSwiSURfQUxFUlRfU1RSQVRFR1lfVVBEQVRFIjp0cnVlLCJJRF9BTEVSVF9TVFJBVEVHWV9ERUxFVEUiOnRydWUsIklEX0FMRVJUX1NUUkFURUdZX0xJU1QiOnRydWUsIklEX0RBU0hCT0FSRCI6dHJ1ZSwiSURfREFTSEJPQVJEX0NSRUFURSI6dHJ1ZSwiSURfREFTSEJPQVJEX1NBVkUiOnRydWUsIklEX0RBU0hCT0FSRF9PUEVOIjp0cnVlLCJJRF9EQVNIQk9BUkRfU0hBUkUiOnRydWUsIklEX0RBU0hCT0FSRF9BRERfVklTVUFMIjp0cnVlLCJJRF9EQklPIjp0cnVlLCJJRF9EQklPX0JVU0lORVNTX1BBTk9SQU1BIjp0cnVlLCJJRF9EQklPX1NFUlZJQ0VfQU5BTFlaRVIiOnRydWUsIklEX0RCSU9fQUxFUlRTX0NIRUNLIjp0cnVlLCJJRF9EQklPX0tQSV9BTkFMWVpFUiI6dHJ1ZSwiSURfREJJT19DT05GSUdVUkFUSU9OIjp0cnVlLCJJRF9EQklPX0NPTkZJR1VSQVRJT05fU0VSVklDRSI6dHJ1ZSwiSURfREJJT19DT05GSUdVUkFUSU9OX0VOVElUWSI6dHJ1ZSwiSURfREJJT19DT05GSUdVUkFUSU9OX0FMRVJUIjp0cnVlLCJJRF9NTCI6dHJ1ZSwiSURfTUxfQU5PTUFMWV9ERVRFQ1RJT04iOnRydWUsIklEX01MX0FOT01BTFlfREVURUNUSU9OX0NSRUFURSI6dHJ1ZSwiSURfTUxfQU5PTUFMWV9ERVRFQ1RJT05fVVBEQVRFIjp0cnVlLCJJRF9NTF9BTk9NQUxZX0RFVEVDVElPTl9ERUxFVEUiOnRydWUsIklEX01MX1RJTUVfU0VSSUVTX0ZPUkVDQVNUIjp0cnVlLCJJRF9NTF9USU1FX1NFUklFU19GT1JFQ0FTVF9DUkVBVEUiOnRydWUsIklEX01MX1RJTUVfU0VSSUVTX0ZPUkVDQVNUX1VQREFURSI6dHJ1ZSwiSURfTUxfVElNRV9TRVJJRVNfRk9SRUNBU1RfREVMRVRFIjp0cnVlLCJJRF9NTF9ST09UX0NBVVNFX0FOQUxZU0lTIjp0cnVlLCJJRF9NTF9ST09UX0NBVVNFX0FOQUxZU0lTX0NSRUFURSI6dHJ1ZSwiSURfTUxfUk9PVF9DQVVTRV9BTkFMWVNJU19VUERBVEUiOnRydWUsIklEX01MX1JPT1RfQ0FVU0VfQU5BTFlTSVNfREVMRVRFIjp0cnVlLCJJRF9EQVRBX01BTkFHRVIiOnRydWUsIklEX0RBVEFfTUFOQUdFUl9MT0dHUk9VUCI6dHJ1ZSwiSURfREFUQV9NQU5BR0VSX0xPR0dST1VQX0VYUE9SVF9BTEwiOnRydWUsIklEX0RBVEFfTUFOQUdFUl9MT0dHUk9VUF9JTVBPUlQiOnRydWUsIklEX0RBVEFfTUFOQUdFUl9MT0dHUk9VUF9DUkVBVEUiOnRydWUsIklEX0RBVEFfTUFOQUdFUl9MT0dHUk9VUF9VUERBVEUiOnRydWUsIklEX0RBVEFfTUFOQUdFUl9MT0dHUk9VUF9ERUxFVEUiOnRydWUsIklEX0RBVEFfTUFOQUdFUl9MT0dHUk9VUF9FWFBPUlQiOnRydWUsIklEX0RBVEFfTUFOQUdFUl9UQUdTIjp0cnVlLCJJRF9NT05JVE9SX1BBR0UiOnRydWUsIklEX0lOU1BFQ1RJT04iOnRydWUsIklEX0lOU1BFQ1RJT05fSU5TUEVDVElPTlMiOnRydWUsIklEX0lOU1BFQ1RJT05fSU5TUEVDVElPTlNfQUREIjp0cnVlLCJJRF9JTlNQRUNUSU9OX0lOU1BFQ1RJT05TX0VESVQiOnRydWUsIklEX0lOU1BFQ1RJT05fSU5TUEVDVElPTlNfREVMRVRFIjp0cnVlLCJJRF9JTlNQRUNUSU9OX0lOU1BFQ1RJT05TX0RFTEVURV9TSUdOIjp0cnVlLCJJRF9JTlNQRUNUSU9OX0hJU1RPUlkiOnRydWUsIklEX0lOU1BFQ1RJT05fSElTVE9SWV9FWFBPUlQiOnRydWUsIklEX0RBVEFfTUFOQUdFUl9PQkpFQ1QiOnRydWUsIklEX0RBVEFfTUFOQUdFUl9PQkpFQ1RfRVhQT1JUX0FMTCI6dHJ1ZSwiSURfREFUQV9NQU5BR0VSX09CSkVDVF9JTVBPUlQiOnRydWUsIklEX0RBVEFfTUFOQUdFUl9PQkpFQ1RfUlVMRSI6dHJ1ZSwiSURfREFUQV9NQU5BR0VSX09CSkVDVF9EQVNIQk9BUkQiOnRydWUsIklEX0RBVEFfTUFOQUdFUl9PQkpFQ1RfU0VBUkNIIjp0cnVlLCJJRF9EQVRBX01BTkFHRVJfT0JKRUNUX1ZJU1VBTCI6dHJ1ZSwiSURfREFUQV9NQU5BR0VSX09CSkVDVF9BTEVSVCI6dHJ1ZSwiSURfU1lTVEVNX01BTkFHRVIiOnRydWUsIklEX1NZU1RFTV9NQU5BR0VSX1BFUk1JU1NJT04iOnRydWUsIklEX1NZU1RFTV9NQU5BR0VSX1BFUk1JU1NJT05fVVNFUiI6dHJ1ZSwiSURfU1lTVEVNX01BTkFHRVJfUEVSTUlTU0lPTl9ST0xFIjp0cnVlLCJJRF9TWVNURU1fTUFOQUdFUl9QRVJNSVNTSU9OX01PRFVMRSI6dHJ1ZSwiSURfU1lTVEVNX01BTkFHRVJfUEVSTUlTU0lPTl9PUEVOQVBJIjp0cnVlLCJJRF9TWVNURU1fTUFOQUdFUl9BVURJVF9MT0ciOnRydWUsIklEX1NZU1RFTV9NQU5BR0VSX1NZU1RFTSI6dHJ1ZSwiSURfU1lTVEVNX01BTkFHRVJfU1lTVEVNX0xPR0dJTkciOnRydWUsIklEX1NZU1RFTV9NQU5BR0VSX1NZU1RFTV9TRUNVUklUWSI6dHJ1ZSwiSURfU1lTVEVNX01BTkFHRVJfU1lTVEVNX09FTSI6dHJ1ZSwiSURfU1lTVEVNX0FVVEhfTUFOQUdFUiI6dHJ1ZSwiSURfU1lTVEVNX01BTkFHRVJfU1lTVEVNX1dISVRFTElTVCI6dHJ1ZSwiSURfU1lTVEVNX01BTkFHRVJfU1lTVEVNX1NFQVJDSCI6dHJ1ZSwiSURfU1lTVEVNX01BTkFHRVJfU0NIRURVTEVfVEFTSyI6dHJ1ZSwiSURfU1lTVEVNX01BTkFHRVJfU0NIRURVTEVfVEFTS19DUkVBVEUiOnRydWUsIklEX1NZU1RFTV9NQU5BR0VSX1NDSEVEVUxFX1RBU0tfVVBEQVRFIjp0cnVlLCJJRF9TWVNURU1fTUFOQUdFUl9TQ0hFRFVMRV9UQVNLX0RFTEVURSI6dHJ1ZSwiSURfU1lTVEVNX01BTkFHRVJfU0NIRURVTEVfVEFTS19MSVNUIjp0cnVlLCJJRF9TWVNURU1fTUFOQUdFUl9TWVNURU1fTElDRU5TRSI6dHJ1ZSwiSURfQVNfQklHU0NSRUVOIjp0cnVlLCJJRF9DT1JSRUxBVElPTl9TRUFSQ0giOnRydWV9LCJleHAiOjE2NjE2MjI1MDIuOTY4MjIyNn0._RseHs3aAXEY-yloxe739JAcsULBXBtdMFGeqQkBVzw'
    }

    encoder = MultipartEncoder(
        fields=req_body,
        boundary='-----------------------------' + str(random.randint(1e28, 1e29 - 1))
    )
    header['Content-Type'] = encoder.content_type
    res = requests.post(url=url, data=encoder, headers=header)
    print(res)