# 软件介绍
## 依赖环境
```
python = "^3.10"
```
## 软件安装
可以在python虚环境或docker中安装，执行如下命令：
```
pip install code-exec-hz
```
## 默认端口
默认端口是8080，如果需要修改服务端口，请修改文件：site-packages/code_exec/controller/api.py

## 服务运行
pip安装**code-exec-hz**后，在当前python环境会增加**code-exec**命令，直接执行即可启动服务：
```
code-exec
```

## api调用
按照如下方式，调用接口，可执行code参数中的python代码
```
curl -XPOST '127.0.0.1:8080/api/exec' \
-H 'Content-Type: application/json' \
-d '{
    "language": "python",
    "inputs":
    {
        "arg1": "参数1"
    },
    "code": "import json\ndata = {\"name\": arg1, \"age\": 18}\njson_str = json.dumps(data, ensure_ascii=False)\nresult = {\"data\": json_str}\n"
}'
```
response:
```json
{
    "trcid": "oaxdde998771",

    "status": "0",

    "msg": "",

    "result": {}    ## 返回结果，json字符串
}
```

## 依赖增加
如果需要增加依赖，比如numpy，直接在安装code-exec的python环境中，安装numpy即可，然后重启服务即可。
```
pip install numpy
# 结束进程
ps -ef | grep code-exec | grep -v grep | awk '{print $2}' | xargs kill -9
# 启动服务
code-exec
```

# 孔明问答集成
## 配置外部代码执行环境
1. 调用位置: [孔明问答] -> [控制台] -> [智能体构建] -> 增加[代码执行]节点;
2. 代码执行节点选择Python语言;
3. 打开外部环境开关;
4. 配置外部环境(输入框内填写code-exec服务调用地址),例如: http://127.0.0.1:8080/api/exec ;
5. 写pyton代码运行智能体。

## 注意事项
1. 返回结果参数添加到"data"字段
```python
import json
data = {'name': arg1, 'age': 18}
json_str = json.dumps(data, ensure_ascii=False)
result = {"data": json_str}
```
在上面代码中，arg1是输入参数，通过上一个节点传入，中间为处理逻辑，最后的result是返回结果，需要遵循json格式，并且将处理好的结果添加到"data"字段中。
因为输出变量是data，这样下一个节点可以获取到data字段中的数据。

2. 只有在code-exec运行的python环境添加了相应依赖，才能在孔明-代码执行节点引入
