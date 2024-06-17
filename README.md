# **Introduction**
pytest 接口自动化测试框架搭建  
User：翁勰  
Time：2022/07/14 始 2022/08/27 第一版较为完整的结束了
Version：1.0.0  
Introction：初始pytest自动化框架学习搭建中

# 项目架构
common --- 公共方法封装（断言、前置、数据处理、日志、请求处理等）  
   1. Allure_util : Allure处理工具，控制生成Allure图表
   2. Assert_util : Assert断言处理工具，控制断言判断
   3. environment_util : 采用处理接口变量工具汇总，如（获取YAML、JSON文件路径，获取前置后置文件目录，拼接URL等）  
   4. Interface_parameters : ${key}$参数化处理，key对应两种参数化（数据库获取数据，自定义脚本生成数据）  
   5. Interface_preconfig : 处理每一个接口的前置操作，对应YAML中rely模块-preconfig
   6. Interface_rely : 处理接口依赖，包括BaseUrl依赖、body依赖、headers依赖，对应YAML中-rely  
   7. Interface_teardown : 处理每一个接口的后置操作，对应YAML中rely模块-teardown  
   8. InterfaceException : 使用raise自定义触发异常，终止运行，输出异常(用不到)  
   9. replace_process : 替换处理，用于依赖或者参数化时，字符串、字典等的替换操作。
   10. test_data_process : 数据处理，将YAML中数据处理后赋值给self.info（核心）
   11. yaml_util : YAML文件工具，读取文件（后面删除、更新自己补充）   
   
config --- 配置文件（统一环境变量配置、数据库配置等）  
   1. headers : 请求头配置
   2. host : 环境信息配置
   3. mysql : mysql 数据库信息配置
   
interface --- 接口文件（统一接口处理，所有接口都将从这里发送）  

log --- 日志文件（日志模块，保存生成日志）（目前用不到，欢迎添加）  

report --- 生成报告（allure报告处）（常规使用，没有额外脚本）   

result --- 生成结果（接口运行结果用json保存到这里，便于生成报告）  

testcase --- 测试用例存放处（格式如下）  
   1. 大模块（如Auth_Manager）
      1. requests : 放对应小模块（如default_Login），里面是用例运行.py文件
      2. test_body : 放对应小模块（如default_Login），里面是接口要用到的请求体json文件
      3. test_yaml : 放对应小模块（如default_Login），里面是接口的YAML文件，代表用例信息
      
venv --- 项目python环境文件夹（存放运行环境） 
 
tools ---  存放接口要用到的用户自定义脚本（前后置脚本、参数化脚本、上传文件脚本）
   1. interface_tools  
      1. preconfig : 存放用户自实现的前置脚本
      2. teardown : 存放用户自实现的后置脚本
   2. parameters_tools 参数化脚本(数据库参数化，自定义脚本参数化)
      1. parameters_fromField : 自定义脚本参数化，用户自实现参数，通过${key}$调用
      2. parameters_fromSQL : 数据库参数化，用户通过SQL语句参数，再通过${key}$调用
   3. uploadFile_tools
      1. 存放上传文件处理脚本，同时也可以存放上传的文件
README.md --- readme文件
  
# 运行流程
1. 下载对应文件【Weng_Pytest_Demo】到本地，并打开
2. python的运行环境是python3.6版本的
3. 在下方Terminal中执行 pip install -r requirement.txt --use-deprecated=legacy-resolver 导入依赖包
   1. 其中  --use-deprecated=legacy-resolver 作用在于防止版本冲突导致的死循环
   2. 如果按照后遇到依赖包版本冲突的，就修改为对应不冲突的版本即可
4. testcase 目录下，按照要求添加用例，注意目录名、文件名、（用例+YAML+json要对应）
5. 执行main.py
6. 到report目录下，通过index.html打开Allure查看各接口运行结果
7. 我估摸着前几次不熟悉，大概率会报接口错误，调好就成
  
后面如果有人在看这个框架学习，写的不好的地方，或者注释没写好的地方，多多包含，我也是第一次上手。  
希望共勉，一起进步！


