"""
健康检查器模块 - 负责DNS解析和IP健康监测
"""

import asyncio
import socket
import threading
import time
from typing import List, Dict, Optional, Set
from concurrent.futures import ThreadPoolExecutor
import dns.resolver
import requests
import aiohttp
from .exceptions import DNSResolutionException, HealthCheckException


class HealthChecker:
    """同步健康检查器"""
    
    def __init__(
        self,
        domain: str,
        health_check_interval: int = 30,
        health_check_timeout: int = 5,
        health_check_path: str = "/health",
        max_retries: int = 3
    ):
        self.domain = domain
        self.health_check_interval = health_check_interval
        self.health_check_timeout = health_check_timeout
        self.health_check_path = health_check_path
        self.max_retries = max_retries
        
        self.healthy_ips: Set[str] = set()
        self.all_ips: Set[str] = set()
        self.ip_status: Dict[str, bool] = {}
        self.last_check_time = 0
        
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._health_check_thread: Optional[threading.Thread] = None
        
        # 初始化DNS解析
        self._resolve_dns()
        
        # 启动健康检查线程
        self._start_health_check()
    
    def _resolve_dns(self) -> None:
        """解析域名的IP地址"""
        try:
            answers = dns.resolver.resolve(self.domain, 'A')
            new_ips = {str(answer) for answer in answers}
            
            with self._lock:
                # 添加新的IP
                for ip in new_ips:
                    if ip not in self.all_ips:
                        self.all_ips.add(ip)
                        self.ip_status[ip] = True  # 初始状态设为健康
                        self.healthy_ips.add(ip)
                
                # 移除不再存在的IP
                removed_ips = self.all_ips - new_ips
                for ip in removed_ips:
                    self.all_ips.remove(ip)
                    self.healthy_ips.discard(ip)
                    self.ip_status.pop(ip, None)
                    
        except Exception as e:
            raise DNSResolutionException(f"DNS解析失败: {e}")
    
    def _check_ip_health(self, ip: str) -> bool:
        """检查单个IP的健康状态"""
        try:
            # 构建健康检查URL
            protocol = "https" if not self.health_check_path.startswith("http") else ""
            url = f"{protocol}://{ip}{self.health_check_path}"
            
            # 发送健康检查请求
            response = requests.get(
                url,
                timeout=self.health_check_timeout,
                headers={"Host": self.domain},
                verify=False  # 禁用SSL验证
            )
            
            # 检查响应状态码
            return 200 <= response.status_code < 500
            
        except Exception:
            return False
    
    def _health_check_worker(self) -> None:
        """健康检查工作线程"""
        while not self._stop_event.is_set():
            try:
                # 重新解析DNS
                self._resolve_dns()
                
                # 检查所有IP的健康状态
                with ThreadPoolExecutor(max_workers=len(self.all_ips)) as executor:
                    future_to_ip = {
                        executor.submit(self._check_ip_health, ip): ip 
                        for ip in self.all_ips
                    }
                    
                    for future in future_to_ip:
                        ip = future_to_ip[future]
                        try:
                            is_healthy = future.result(timeout=self.health_check_timeout + 1)
                            
                            with self._lock:
                                self.ip_status[ip] = is_healthy
                                if is_healthy:
                                    self.healthy_ips.add(ip)
                                else:
                                    self.healthy_ips.discard(ip)
                                    
                        except Exception:
                            with self._lock:
                                self.ip_status[ip] = False
                                self.healthy_ips.discard(ip)
                
                self.last_check_time = time.time()
                
            except Exception as e:
                print(f"健康检查过程中发生错误: {e}")
            
            # 等待下次检查
            self._stop_event.wait(self.health_check_interval)
    
    def _start_health_check(self) -> None:
        """启动健康检查线程"""
        if self._health_check_thread is None or not self._health_check_thread.is_alive():
            self._health_check_thread = threading.Thread(
                target=self._health_check_worker,
                daemon=True
            )
            self._health_check_thread.start()
    
    def get_healthy_ips(self) -> List[str]:
        """获取健康的IP列表"""
        with self._lock:
            return list(self.healthy_ips)
    
    def get_all_ips(self) -> List[str]:
        """获取所有IP列表"""
        with self._lock:
            return list(self.all_ips)
    
    def is_ip_healthy(self, ip: str) -> bool:
        """检查指定IP是否健康"""
        with self._lock:
            return self.ip_status.get(ip, False)
    
    def force_health_check(self) -> None:
        """强制执行一次健康检查"""
        self._resolve_dns()
        for ip in self.all_ips:
            is_healthy = self._check_ip_health(ip)
            with self._lock:
                self.ip_status[ip] = is_healthy
                if is_healthy:
                    self.healthy_ips.add(ip)
                else:
                    self.healthy_ips.discard(ip)
        self.last_check_time = time.time()
    
    def stop(self) -> None:
        """停止健康检查"""
        self._stop_event.set()
        if self._health_check_thread and self._health_check_thread.is_alive():
            self._health_check_thread.join(timeout=5)


class AsyncHealthChecker:
    """异步健康检查器"""
    
    def __init__(
        self,
        domain: str,
        health_check_interval: int = 30,
        health_check_timeout: int = 5,
        health_check_path: str = "/health",
        max_retries: int = 3
    ):
        self.domain = domain
        self.health_check_interval = health_check_interval
        self.health_check_timeout = health_check_timeout
        self.health_check_path = health_check_path
        self.max_retries = max_retries
        
        self.healthy_ips: Set[str] = set()
        self.all_ips: Set[str] = set()
        self.ip_status: Dict[str, bool] = {}
        self.last_check_time = 0
        
        self._lock = asyncio.Lock()
        self._stop_event = asyncio.Event()
        self._health_check_task: Optional[asyncio.Task] = None
        
        # 初始化DNS解析
        self._resolve_dns()
    
    def _resolve_dns(self) -> None:
        """解析域名的IP地址"""
        try:
            answers = dns.resolver.resolve(self.domain, 'A')
            new_ips = {str(answer) for answer in answers}
            
            # 添加新的IP
            for ip in new_ips:
                if ip not in self.all_ips:
                    self.all_ips.add(ip)
                    self.ip_status[ip] = True  # 初始状态设为健康
                    self.healthy_ips.add(ip)
            
            # 移除不再存在的IP
            removed_ips = self.all_ips - new_ips
            for ip in removed_ips:
                self.all_ips.remove(ip)
                self.healthy_ips.discard(ip)
                self.ip_status.pop(ip, None)
                
        except Exception as e:
            raise DNSResolutionException(f"DNS解析失败: {e}")
    
    async def _check_ip_health(self, ip: str) -> bool:
        """异步检查单个IP的健康状态"""
        try:
            # 构建健康检查URL
            protocol = "https" if not self.health_check_path.startswith("http") else ""
            url = f"{protocol}://{ip}{self.health_check_path}"
            
            # 发送健康检查请求
            timeout = aiohttp.ClientTimeout(total=self.health_check_timeout)
            connector = aiohttp.TCPConnector(verify_ssl=False)
            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                async with session.get(url, headers={"Host": self.domain}) as response:
                    return 200 <= response.status < 500
                    
        except Exception:
            return False
    
    async def _health_check_worker(self) -> None:
        """异步健康检查工作协程"""
        while not self._stop_event.is_set():
            try:
                # 重新解析DNS
                self._resolve_dns()
                
                # 并发检查所有IP的健康状态
                tasks = [self._check_ip_health(ip) for ip in self.all_ips]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                async with self._lock:
                    for ip, result in zip(self.all_ips, results):
                        is_healthy = isinstance(result, bool) and result
                        self.ip_status[ip] = is_healthy
                        if is_healthy:
                            self.healthy_ips.add(ip)
                        else:
                            self.healthy_ips.discard(ip)
                
                self.last_check_time = time.time()
                
            except Exception as e:
                print(f"健康检查过程中发生错误: {e}")
            
            # 等待下次检查
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self.health_check_interval)
            except asyncio.TimeoutError:
                pass
    
    async def start(self) -> None:
        """启动健康检查"""
        if self._health_check_task is None or self._health_check_task.done():
            self._health_check_task = asyncio.create_task(self._health_check_worker())
    
    async def stop(self) -> None:
        """停止健康检查"""
        self._stop_event.set()
        if self._health_check_task and not self._health_check_task.done():
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
    
    async def get_healthy_ips(self) -> List[str]:
        """获取健康的IP列表"""
        async with self._lock:
            return list(self.healthy_ips)
    
    async def get_all_ips(self) -> List[str]:
        """获取所有IP列表"""
        async with self._lock:
            return list(self.all_ips)
    
    async def is_ip_healthy(self, ip: str) -> bool:
        """检查指定IP是否健康"""
        async with self._lock:
            return self.ip_status.get(ip, False)
    
    async def force_health_check(self) -> None:
        """强制执行一次健康检查"""
        self._resolve_dns()
        tasks = [self._check_ip_health(ip) for ip in self.all_ips]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        async with self._lock:
            for ip, result in zip(self.all_ips, results):
                is_healthy = isinstance(result, bool) and result
                self.ip_status[ip] = is_healthy
                if is_healthy:
                    self.healthy_ips.add(ip)
                else:
                    self.healthy_ips.discard(ip)
        self.last_check_time = time.time() 