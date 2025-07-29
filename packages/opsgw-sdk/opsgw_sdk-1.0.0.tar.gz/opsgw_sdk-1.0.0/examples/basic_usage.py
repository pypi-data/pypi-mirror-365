#!/usr/bin/env python3
"""
基本使用示例
"""

import asyncio
from opsgw_sdk import OpsGWClient, AsyncOpsGWClient


def sync_example():
    """同步使用示例"""
    print("=== 同步客户端示例 ===")
    
    # 创建客户端
    client = OpsGWClient(
        domain="httpbin.org",
        health_check_interval=30,
        health_check_timeout=5,
        health_check_path="/get",  # 使用 /get 作为健康检查路径
        max_retries=3
    )
    
    try:
        # 获取健康IP列表
        healthy_ips = client.get_healthy_ips()
        print(f"健康IP列表: {healthy_ips}")
        
        # 发送GET请求
        print("\n发送GET请求...")
        response = client.get("/get", params={"test": "value"})
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        # 发送POST请求
        print("\n发送POST请求...")
        response = client.post("/post", json={"name": "test", "value": 123})
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        # 发送PUT请求
        print("\n发送PUT请求...")
        response = client.put("/put", json={"updated": True})
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        # 发送DELETE请求
        print("\n发送DELETE请求...")
        response = client.delete("/delete")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
    except Exception as e:
        print(f"错误: {e}")
    
    finally:
        client.close()


async def async_example():
    """异步使用示例"""
    print("\n=== 异步客户端示例 ===")
    
    # 创建异步客户端
    async with AsyncOpsGWClient(
        domain="httpbin.org",
        health_check_interval=30,
        health_check_timeout=5,
        health_check_path="/get",
        max_retries=3
    ) as client:
        
        try:
            # 获取健康IP列表
            healthy_ips = await client.get_healthy_ips()
            print(f"健康IP列表: {healthy_ips}")
            
            # 发送GET请求
            print("\n发送异步GET请求...")
            response = await client.get("/get", params={"async": "test"})
            print(f"状态码: {response.status}")
            data = await response.json()
            print(f"响应: {data}")
            
            # 发送POST请求
            print("\n发送异步POST请求...")
            response = await client.post("/post", json={"async": True, "data": "test"})
            print(f"状态码: {response.status}")
            data = await response.json()
            print(f"响应: {data}")
            
            # 并发请求示例
            print("\n发送并发请求...")
            tasks = [
                client.get("/get", params={"task": i}) 
                for i in range(3)
            ]
            responses = await asyncio.gather(*tasks)
            
            for i, response in enumerate(responses):
                data = await response.json()
                print(f"任务 {i} 状态码: {response.status}")
            
        except Exception as e:
            print(f"错误: {e}")


def context_manager_example():
    """上下文管理器示例"""
    print("\n=== 上下文管理器示例 ===")
    
    with OpsGWClient("httpbin.org", health_check_path="/get") as client:
        try:
            response = client.get("/get")
            print(f"状态码: {response.status_code}")
            print("使用上下文管理器自动管理资源")
        except Exception as e:
            print(f"错误: {e}")


if __name__ == "__main__":
    # 运行同步示例
    sync_example()
    
    # 运行异步示例
    asyncio.run(async_example())
    
    # 运行上下文管理器示例
    context_manager_example() 