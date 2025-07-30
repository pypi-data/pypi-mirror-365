# Xiyou SDK

Xiyou OpenAPI Python SDK，提供完整的API功能。

**当前版本包含：**
- ✅ **认证模块 (Auth)** - 完整的加签认证功能

**规划中的模块：**
- 📋 API客户端模块
- 📊 数据分析模块  
- 🔧 工具模块

## 特性

- ✅ **纯Python标准库实现** - 无需外部依赖
- ✅ **HMAC-SHA256签名** - 安全可靠的签名算法
- ✅ **简单易用** - 几行代码即可完成认证
- ✅ **灵活集成** - 可与任何HTTP客户端库配合使用
- ✅ **模块化设计** - 可扩展的架构设计

## 安装

```bash
pip install xiyou_sdk
```

## 快速开始

### 1. 基本使用

```python
from xiyou_sdk import XiyouAuth

# 初始化认证对象
auth = XiyouAuth(
    client_id="your_client_id",
    secret_key="your_secret_key"
)

# 获取认证头部
headers = auth.get_auth_headers(
    method="POST",
    path="/v1/asins/traffic",
    body='{"entities":[{"country":"US","asin":"B09PCSR9SX"}]}'
)

print(headers)
# 输出:
# {
#     'X-Client-Id': 'your_client_id',
#     'X-Timestamp': '1753776583',
#     'X-Sign': '5572ae2572e2aef8fa23623a3f56fa245f2f74950b533fe63100ad8f688b254f',
#     'Content-Type': 'application/json'
# }
```

### 2. 与requests库结合使用

```python
import requests
import json
from xiyou_sdk import XiyouAuth

auth = XiyouAuth("your_client_id", "your_secret_key")

# 构建请求数据
data = {"entities": [{"country": "US", "asin": "B09PCSR9SX"}]}
body = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

# 获取认证头部
headers = auth.get_auth_headers(
    method="POST",
    path="/v1/asins/traffic",
    body=body
)

# 发起请求
response = requests.post(
    "https://api.xiyou.com/v1/asins/traffic",
    headers=headers,
    data=body
)
```

### 3. 与urllib结合使用

```python
import urllib.request
import json
from xiyou_sdk import XiyouAuth

auth = XiyouAuth("your_client_id", "your_secret_key")

# 构建请求数据
data = {"entities": [{"country": "US", "asin": "B09PCSR9SX"}]}
body = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

# 获取认证头部
headers = auth.get_auth_headers(
    method="POST",
    path="/v1/asins/traffic",
    body=body
)

# 发起请求
req = urllib.request.Request(
    "https://api.xiyou.com/v1/asins/traffic",
    data=body.encode(),
    headers=headers
)
response = urllib.request.urlopen(req)
```

## API参考

### XiyouAuth

#### 构造函数

```python
XiyouAuth(client_id: str, secret_key: str)
```

**参数:**
- `client_id`: 客户端ID
- `secret_key`: 密钥

#### 方法

##### get_auth_headers()

```python
get_auth_headers(
    method: str = "POST",
    path: str = "",
    body: str = "",
    timestamp: Optional[str] = None
) -> Dict[str, str]
```

生成包含认证信息的完整头部。

**参数:**
- `method`: HTTP方法 (GET, POST, PUT, DELETE等)
- `path`: API路径 (如: /v1/asins/traffic)
- `body`: 请求体内容
- `timestamp`: 自定义时间戳，默认使用当前时间

**返回:** 包含认证头部的字典

##### generate_signature()

```python
generate_signature(
    timestamp: str,
    method: str = "POST",
    path: str = "",
    body: str = ""
) -> str
```

生成API请求签名。

**参数:**
- `timestamp`: 时间戳字符串
- `method`: HTTP方法
- `path`: API路径
- `body`: 请求体内容

**返回:** 签名字符串

## 签名算法

签名使用HMAC-SHA256算法，签名字符串格式为：

```
client_id + timestamp + method + path + body
```

## 支持的API

该SDK适用于所有Xiyou OpenAPI接口，包括：

- `/v1/asins/traffic` - ASIN流量得分
- `/v1/asins/infoChange/trends/daily` - ASIN基础信息变动趋势（天）
- `/v1/asins/trafficScore/trend/daily` - ASIN流量得分趋势（天）
- `/v1/asins/trafficScore/trend/weekly` - ASIN流量得分趋势（周）
- `/v1/asins/trafficScore/trend/monthly` - ASIN流量得分趋势（月）
- 以及其他所有API接口

## 模块架构

```
xiyou_sdk/
├── __init__.py          # 主包入口
├── auth.py              # 认证模块 ✅
├── client.py            # API客户端模块 (规划中)
├── models.py            # 数据模型模块 (规划中)
└── utils.py             # 工具模块 (规划中)
```

## 示例

查看 `examples/` 目录中的示例代码：

- `basic_usage.py` - 基本使用示例
- `signature_test.py` - 签名验证测试

运行示例：

```bash
PYTHONPATH=. python examples/basic_usage.py
PYTHONPATH=. python examples/signature_test.py
```

## 许可证

MIT License 