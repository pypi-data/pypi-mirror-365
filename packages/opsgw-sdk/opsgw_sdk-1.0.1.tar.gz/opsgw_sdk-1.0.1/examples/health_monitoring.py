#!/usr/bin/env python3
"""
健康监测功能演示
"""

import time
import asyncio
from opsgw_sdk import OpsGWClient, AsyncOpsGWClient


def health_monitoring_demo():
    """健康监测演示"""
    print("=== 健康监测功能演示 ===")
    
    # 创建客户端
    client = OpsGWClient(
        domain="httpbin.org",
        health_check_interval=10,  # 10秒检查一次
        health_check_timeout=3,
        health_check_path="/get",
        max_retries=2
    )
    
    try:
        print("初始化客户端...")
        time.sleep(2)  # 等待初始健康检查完成
        
        # 显示初始状态
        all_ips = client.get_all_ips()
        healthy_ips = client.get_healthy_ips()
        
        print(f"所有IP: {all_ips}")
        print(f"健康IP: {healthy_ips}")
        print(f"健康IP数量: {len(healthy_ips)}/{len(all_ips)}")
        
        # 模拟持续监控
        print("\n开始持续监控（30秒）...")
        start_time = time.time()
        
        while time.time() - start_time < 30:
            healthy_ips = client.get_healthy_ips()
            print(f"[{time.strftime('%H:%M:%S')}] 健康IP: {healthy_ips}")
            time.sleep(5)
        
        # 强制健康检查
        print("\n强制执行健康检查...")
        client.force_health_check()
        healthy_ips = client.get_healthy_ips()
        print(f"强制检查后的健康IP: {healthy_ips}")
        
        # 发送一些请求
        print("\n发送测试请求...")
        for i in range(3):
            try:
                response = client.get("/get", params={"test": i})
                print(f"请求 {i+1} 成功，状态码: {response.status_code}")
            except Exception as e:
                print(f"请求 {i+1} 失败: {e}")
            time.sleep(2)
    
    except Exception as e:
        print(f"错误: {e}")
    
    finally:
        client.close()


async def async_health_monitoring_demo():
    """异步健康监测演示"""
    print("\n=== 异步健康监测功能演示 ===")
    
    async with AsyncOpsGWClient(
        domain="httpbin.org",
        health_check_interval=10,
        health_check_timeout=3,
        health_check_path="/get",
        max_retries=2
    ) as client:
        
        try:
            print("初始化异步客户端...")
            await asyncio.sleep(2)  # 等待初始健康检查完成
            
            # 显示初始状态
            all_ips = await client.get_all_ips()
            healthy_ips = await client.get_healthy_ips()
            
            print(f"所有IP: {all_ips}")
            print(f"健康IP: {healthy_ips}")
            print(f"健康IP数量: {len(healthy_ips)}/{len(all_ips)}")
            
            # 模拟持续监控
            print("\n开始持续监控（20秒）...")
            start_time = time.time()
            
            while time.time() - start_time < 20:
                healthy_ips = await client.get_healthy_ips()
                print(f"[{time.strftime('%H:%M:%S')}] 健康IP: {healthy_ips}")
                await asyncio.sleep(5)
            
            # 强制健康检查
            print("\n强制执行健康检查...")
            await client.force_health_check()
            healthy_ips = await client.get_healthy_ips()
            print(f"强制检查后的健康IP: {healthy_ips}")
            
            # 并发发送请求
            print("\n并发发送测试请求...")
            tasks = [
                client.get("/get", params={"async_test": i}) 
                for i in range(5)
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    print(f"请求 {i+1} 失败: {response}")
                else:
                    print(f"请求 {i+1} 成功，状态码: {response.status}")
        
        except Exception as e:
            print(f"错误: {e}")


def ip_status_demo():
    """IP状态检查演示"""
    print("\n=== IP状态检查演示 ===")
    
    client = OpsGWClient(
        domain="httpbin.org",
        health_check_path="/get"
    )
    
    try:
        all_ips = client.get_all_ips()
        print(f"所有IP: {all_ips}")
        
        for ip in all_ips:
            is_healthy = client.health_checker.is_ip_healthy(ip)
            status = "健康" if is_healthy else "不健康"
            print(f"IP {ip}: {status}")
        
        # 检查特定IP
        if all_ips:
            test_ip = all_ips[0]
            is_healthy = client.health_checker.is_ip_healthy(test_ip)
            print(f"\n测试IP {test_ip} 的健康状态: {'健康' if is_healthy else '不健康'}")
    
    except Exception as e:
        print(f"错误: {e}")
    
    finally:
        client.close()


if __name__ == "__main__":
    # 运行健康监测演示
    health_monitoring_demo()
    
    # 运行异步健康监测演示
    asyncio.run(async_health_monitoring_demo())
    
    # 运行IP状态检查演示
    ip_status_demo() 