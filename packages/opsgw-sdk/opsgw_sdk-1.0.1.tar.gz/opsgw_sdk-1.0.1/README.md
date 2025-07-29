# OpsGW HTTP SDK

一个具有健康监测功能的HTTP SDK，支持自动检测域名IP的健康状态，并只向健康的IP发送请求。

## 特性

- 自动DNS解析和IP健康监测
- 后台健康检查，实时更新IP状态
- 智能负载均衡，只向健康IP发送请求
- 支持同步和异步请求
- 可配置的健康检查参数
- 自动故障转移

## 安装

```bash
pip install -r requirements.txt
```

## 使用示例

```python
from opsgw_sdk import OpsGWClient

# 初始化客户端
client = OpsGWClient(
    domain="api.example.com",
    health_check_interval=30,  # 健康检查间隔（秒）
    health_check_timeout=5,    # 健康检查超时（秒）
    max_retries=3              # 最大重试次数
)

# 发送GET请求
response = client.get("/users", params={"page": 1})

# 发送POST请求
response = client.post("/users", json={"name": "John", "email": "john@example.com"})

# 发送PUT请求
response = client.put("/users/1", json={"name": "John Updated"})

# 发送DELETE请求
response = client.delete("/users/1")
```

## 异步使用

```python
import asyncio
from opsgw_sdk import AsyncOpsGWClient

async def main():
    async with AsyncOpsGWClient("api.example.com") as client:
        # 异步请求
        response = await client.get("/users")
        data = await response.json()
        print(data)

asyncio.run(main())
``` 