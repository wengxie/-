# -*- coding: UTF-8 -*-
"""
@Date  2022/8/5 16:55
@auth  翁勰         
@File  string_process.py
@Email  Nelson.weng@aishu.cn
@Description   字符串,字典 统一处理模块
                1. 处理接口依赖时，/manager/ruleEngine/alert/$relation_1$ 的参数化处理
"""

# 依赖url内容参数化替换
import re
import traceback


def rely_baseUrlstr_replace(baseUrlstr, replace_dic, left_Separator, right_Separator):
    '''
    :param baseUrlstr: 用于处理的带有参数化的url，如/manager/ruleEngine/alert/$relation_1$
    :param replace_dic: 用于替换参数化内容，如 {'relation_1': '111111'}
    :param left_Separator: 左分隔符，如 '$'
    :param right_Separator: 右分隔符，如 '$'
    :return: 返回处理完的url，如/manager/ruleEngine/alert/111111
    '''
    for key in replace_dic.keys():
        # 如果 baseUrlstr 中有识别到对应参数 如 relation_1 ，就进行字符串替换操作
        if key in str(baseUrlstr):
            # 替换关键字 ，如 $relation_1$
            replace_key = left_Separator + key + right_Separator
            baseUrlstr = str(baseUrlstr).replace(replace_key, replace_dic[key])
    return baseUrlstr

# 请求头依赖替换，各参数与rely_baseUrlstr_replace方法中参数替换类似
def rely_headers_replace(headersBody, replace_dic, replace_key,left_Separator, right_Separator):
    '''
    就记录了不同的地方，容易晕，请注意
    :param headersBody: 传参是headers，所以返回也是headers
    :param replace_key: 用来识别要替换headers中那个关键字的值，如果这个关键字不存在，就把 key: value直接加入headers中
    '''
    # 提取headers中所有的关键字如user、token、Content-Type等等
    headersBody_key = list(headersBody.keys())
    # replace_dic类似于 {'relation_1': '111111'}，取其中的relation_1，做下方处理
    for replace_dic_key in replace_dic.keys():
        # 判断识别要替换headers中的那个关键字在不在,如replace_key对应user，在就替换关键字对应的内容headers中原有user的值
        if replace_key in headersBody_key:
            # replace_dic_key对应relation_1，判断relation_1在不在headers的对应key的值中，在就替换对应relation_1的值
            if replace_dic_key in headersBody[replace_key]:
                # 替换关键字 ，如 $relation_1$
                key = left_Separator + replace_dic_key + right_Separator
                headersBody[replace_key] = str(headersBody[replace_key]).replace(key, replace_dic[replace_dic_key])
            # relation_1不在headers的对应key的值中，就直接替换掉key的整个值
            else:
                headersBody[replace_key] = replace_dic[replace_dic_key]

        # 如果这个关键字不存在，就把 key: value直接加入headers中
        else:
            headersBody[replace_key] = replace_dic[replace_dic_key]

    return headersBody


# 取到所有关键字key（键值对key:value）的位置路径，便于JSON通过路径访问key对应的value参数
def findKeyPath(reqJsonBody, keyName, currentPath, keyPath):
    '''
    取到所有关键字key（键值对key:value）的位置路径，便于JSON通过路径访问key对应的value参数
    :param reqJsonBody: 当前接口JSON请求体
    :param keyName: JSON请求体要用来替换的关键字，如 'b'
    :param currentPath: 包含对应关键字的最终路径，如['b']['a'][0][3]['b']
    :param keyPath: 空list，用于存储存储了所有的包含keyName关键字的路径
    :return:  keyPath[]，存储了所有的包含keyName关键字的路径，如["reqJsonBody['b']['b']","reqJsonBody['b']['a'][0][3]['b']","reqJsonBody['b']"]
    '''
    # 运行目的：遍历JSON，取到所有关键字key（键值对key:value）的位置路径，便于JSON通过路径访问key对应的value参数
    # 如果是list，路径就用[0]、[1]、[2]去标记；如果是dict，路径就用[key](如['name'])去标记；不断递归，直至没有list以及dict为止
    # 示例：比如要找到所有键值对关键字是'b'的路径，最终返回的keyPath如["reqJsonBody['b']['b']","reqJsonBody['b']['a'][0][3]['b']","reqJsonBody['b']"]，方便json通过路径取到值
    for index, obj_key in enumerate(reqJsonBody):
        # list
        if isinstance(reqJsonBody, list):
            if isinstance(obj_key, list):
                print(f"{currentPath}{[index]}")
                findKeyPath(obj_key, keyName, f"{currentPath}{[index]}", keyPath)

            elif isinstance(obj_key, dict):
                findKeyPath(obj_key, keyName, f"{currentPath}{[index]}", keyPath)

        # dict
        elif isinstance(reqJsonBody, dict):
            if isinstance(reqJsonBody[obj_key], list):
               findKeyPath(reqJsonBody[obj_key], keyName, f"{currentPath}{[obj_key]}", keyPath)

            elif isinstance(reqJsonBody[obj_key], dict):
                findKeyPath(reqJsonBody[obj_key], keyName, f"{currentPath}{[obj_key]}", keyPath)

            # 到这里，说明dict子对象下没有list与dict了，说明遍历到了最底端，此时路径就是遍历到key的最底端路径
            if obj_key == keyName:
                keyPath.append(f"{currentPath}{[obj_key]}")

    return keyPath


# 依赖的JSON请求体，指定内容替换
def rely_reqJsonBody_replace(reqJsonBody, key, relation_NUM, replaceValue):
    '''
    JSON请求体指定关键字下，对应 $relation$ 替换为依赖接口返回内容，如请求体中"name": "$relation_1$" -> 替换为"name": "wengxie"
    :param reqJsonBody: 当前接口JSON请求体
    :param key: JSON请求体要用来替换的关键字，如上方示例中的name
    :param relation_NUM: JSON请求体要用来替换的relation_1，只要key与relation一一对应后，才能成功替换
    :param replaceValue: 要替换的内容，这里内容是从指定的依赖接口返回值中，通过指定关键字获取的值
    :return: 处理完的请求体
    '''
    # 取到所有关键字key（键值对key:value）的位置路径，便于JSON通过路径访问key对应的value参数
    keyPath = findKeyPath(reqJsonBody=reqJsonBody, keyName=key, currentPath='reqJsonBody', keyPath=[])
    # keyPath如["reqJsonBody['b']['b']","reqJsonBody['b']['a'][0][3]['b']","reqJsonBody['b']"]，遍历path就是遍历JSON对应关键字b每一个的值
    for path in keyPath:
        # 取当前JSON路径下，请求体对应的值，eval是运行参数命令并返回结果，如（reqJsonBody['b']['b'] -> 返回当前位置的值）
        json_path_value = eval(path)
        # 判断 relation_1 等在不在其中，在说明有参数化，需要替换 $relation_1$
        if relation_NUM in str(json_path_value):
            replace_key = '$' + relation_NUM + '$'
            json_path_replacedValue = str(json_path_value).replace(replace_key, replaceValue)
            # exec 执行参数（先将字符串解析为命令，执行命令，即reqJsonBody['b']['b'] = 替换完字符串），从而替换整个请求体
            exec(path + '=json_path_replacedValue')
    return reqJsonBody

# 参数化替换，即将YAML文件中识别到${key}$参数化替换为对应的参数内容
def parameters_replace(stepInfoBody, param_keys_values):
    '''
    批量替换包含${key}$参数化的值，并返回替换结果
    :param stepInfoBody: self.info[step]对应的每一步接口的body，正常是dict格式
    :param param_keys_values: 要用来转换的key->value, 字典格式，示例：{'AnyRobotNameID': '589_381', 'RandomIntNumber': 445961}
    :return: 返回参数化替换处理完的结果
    '''
    try:
        # 统一先强转换为字符串格式进行替换
        str_stepInfoBody = str(stepInfoBody)
        # 依次取出要用来替换的关键字,如上方示例中的AnyRobotNameID、RandomIntNumber
        for key in param_keys_values.keys():
            replace_key = '${' + key + '}$'
            replaceValue = param_keys_values[key]
            # 将全部参数化都替换完成, replace只支持str类型参数，eval会把原有类型转回，不用担心int等替换后，类型发生变化
            str_stepInfoBody = str_stepInfoBody.replace(replace_key, str(replaceValue))
        # 判断原来传入的stepInfoBody是什么格式，如果是dict、list，就变回原来的格式
        if isinstance(stepInfoBody, (dict, list)):
            return eval(str_stepInfoBody)
        else:
            return str_stepInfoBody
    # 替换过程遇到错误
    except Exception as e:
        traceback.print_exc()
        return False


# 提取字符串中所有的${key}$的key, 最终输出一个无序不重复元素[key]集
def find_keys_from_data(data):
    # compile 函数用于编译正则表达式，生成一个 Pattern 对象,然后利用 pattern 的一系列方法对文本进行匹配查找
    pattern = re.compile(r'\$\{(\w*)\}\$')
    # compile()与findall()一起使用，返回一个列表，找到文本的所有匹对返回值
    allkeys = pattern.findall(string=str(data))
    # set() 函数创建一个无序不重复元素集
    key_list = list(set(allkeys))
    # sort对原列表进行排序,比较函数设定key为list下标，目的在于保证list元素排序顺序按照元素出现的先后排序。
    key_list.sort(key=allkeys.index)
    return key_list



if __name__ == "__main__":

    jsonObj = {
        "a": 1,
        "j": "iii",
        "b": {
            "c": 2,
            "d": 3,
            "b": 4,
            "a":
            [
                [
                    0,
                    1,
                    2,
                    {
                        "a": 1,
                        "b": "qq"
                    }
                ],
                "b",
                {
                    "g": 7,
                    "b": 8
                }
            ]
        },
    }
    jsonObj2 = [
    {
        "userId": "$relation_1$",
        "roleId": "$relation_3$"
    },
    {
        "userId": "$relation_2$",
        "roleId": "$relation_3$"
    }
]

    #body = rely_reqJsonBody_replace(jsonObj2, 'userId', 'relation_2', 'wxxxxxx')
    #print(body)
    a = find_keys_from_data("aaaa${a}$,aaaa${h}$,aaaa${b}$,aa${b}$aa")
    print(a)
    str_jsonObj = str(jsonObj)
    str_jsonObj = str_jsonObj.replace(str(1), str(2))
    hhh = eval(str_jsonObj)
    print(type(hhh))
    print(type(hhh['a']))