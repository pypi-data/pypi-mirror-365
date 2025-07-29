"""
HTTP客户端模块 - 集成健康检查功能的HTTP客户端
"""

import random
import asyncio
from typing import Dict, Any, Optional, Union, List
import requests
import aiohttp
from .health_checker import HealthChecker, AsyncHealthChecker
from .exceptions import NoHealthyIPException, OpsGWException


class OpsGWClient:
    """同步HTTP客户端，具有健康监测功能"""
    
    def __init__(
        self,
        domain: str,
        health_check_interval: int = 30,
        health_check_timeout: int = 5,
        health_check_path: str = "/health",
        max_retries: int = 3,
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None,
        verify_ssl: bool = True
    ):
        self.domain = domain
        self.timeout = timeout
        self.headers = headers or {}
        self.verify_ssl = verify_ssl
        self.max_retries = max_retries
        
        # 初始化健康检查器
        self.health_checker = HealthChecker(
            domain=domain,
            health_check_interval=health_check_interval,
            health_check_timeout=health_check_timeout,
            health_check_path=health_check_path,
            max_retries=max_retries
        )
        
        # 创建requests session
        self.session = requests.Session()
        if not verify_ssl:
            self.session.verify = False
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def _get_healthy_ip(self) -> str:
        """获取一个健康的IP地址"""
        healthy_ips = self.health_checker.get_healthy_ips()
        if not healthy_ips:
            # 如果没有健康IP，强制检查一次
            self.health_checker.force_health_check()
            healthy_ips = self.health_checker.get_healthy_ips()
            
        if not healthy_ips:
            raise NoHealthyIPException(f"域名 {self.domain} 没有健康的IP可用")
        
        # 随机选择一个健康IP
        return random.choice(healthy_ips)
    
    def _make_request(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> requests.Response:
        """发送HTTP请求"""
        healthy_ip = self._get_healthy_ip()
        
        # 构建URL
        protocol = "https" if self.verify_ssl else "http"
        url = f"{protocol}://{healthy_ip}{path}"
        
        # 设置请求头
        headers = self.headers.copy()
        headers.update(kwargs.get('headers', {}))
        headers['Host'] = self.domain
        
        # 设置超时
        timeout = kwargs.get('timeout', self.timeout)
        
        # 发送请求
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=timeout,
                    **{k: v for k, v in kwargs.items() if k not in ['headers', 'timeout']}
                )
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries:
                    raise OpsGWException(f"请求失败，已重试 {self.max_retries} 次: {e}")
                
                # 标记当前IP为不健康
                self.health_checker.ip_status[healthy_ip] = False
                self.health_checker.healthy_ips.discard(healthy_ip)
                
                # 获取新的健康IP
                try:
                    healthy_ip = self._get_healthy_ip()
                    protocol = "https" if self.verify_ssl else "http"
                    url = f"{protocol}://{healthy_ip}{path}"
                except NoHealthyIPException:
                    raise OpsGWException(f"所有IP都不健康，无法完成请求: {e}")
    
    def get(self, path: str, **kwargs) -> requests.Response:
        """发送GET请求"""
        return self._make_request('GET', path, **kwargs)
    
    def post(self, path: str, **kwargs) -> requests.Response:
        """发送POST请求"""
        return self._make_request('POST', path, **kwargs)
    
    def put(self, path: str, **kwargs) -> requests.Response:
        """发送PUT请求"""
        return self._make_request('PUT', path, **kwargs)
    
    def delete(self, path: str, **kwargs) -> requests.Response:
        """发送DELETE请求"""
        return self._make_request('DELETE', path, **kwargs)
    
    def patch(self, path: str, **kwargs) -> requests.Response:
        """发送PATCH请求"""
        return self._make_request('PATCH', path, **kwargs)
    
    def head(self, path: str, **kwargs) -> requests.Response:
        """发送HEAD请求"""
        return self._make_request('HEAD', path, **kwargs)
    
    def options(self, path: str, **kwargs) -> requests.Response:
        """发送OPTIONS请求"""
        return self._make_request('OPTIONS', path, **kwargs)
    
    def get_healthy_ips(self) -> List[str]:
        """获取健康的IP列表"""
        return self.health_checker.get_healthy_ips()
    
    def get_all_ips(self) -> List[str]:
        """获取所有IP列表"""
        return self.health_checker.get_all_ips()
    
    def force_health_check(self) -> None:
        """强制执行健康检查"""
        self.health_checker.force_health_check()
    
    def close(self) -> None:
        """关闭客户端"""
        self.health_checker.stop()
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AsyncOpsGWClient:
    """异步HTTP客户端，具有健康监测功能"""
    
    def __init__(
        self,
        domain: str,
        health_check_interval: int = 30,
        health_check_timeout: int = 5,
        health_check_path: str = "/health",
        max_retries: int = 3,
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None,
        verify_ssl: bool = True
    ):
        self.domain = domain
        self.timeout = timeout
        self.headers = headers or {}
        self.verify_ssl = verify_ssl
        self.max_retries = max_retries
        
        # 初始化健康检查器
        self.health_checker = AsyncHealthChecker(
            domain=domain,
            health_check_interval=health_check_interval,
            health_check_timeout=health_check_timeout,
            health_check_path=health_check_path,
            max_retries=max_retries
        )
        
        # 创建aiohttp session
        self.session: Optional[aiohttp.ClientSession] = None
        self._connector = aiohttp.TCPConnector(verify_ssl=verify_ssl)
    
    async def _ensure_session(self) -> None:
        """确保session已创建"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=self._connector
            )
    
    async def _get_healthy_ip(self) -> str:
        """获取一个健康的IP地址"""
        healthy_ips = await self.health_checker.get_healthy_ips()
        if not healthy_ips:
            # 如果没有健康IP，强制检查一次
            await self.health_checker.force_health_check()
            healthy_ips = await self.health_checker.get_healthy_ips()
            
        if not healthy_ips:
            raise NoHealthyIPException(f"域名 {self.domain} 没有健康的IP可用")
        
        # 随机选择一个健康IP
        return random.choice(healthy_ips)
    
    async def _make_request(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """发送异步HTTP请求"""
        await self._ensure_session()
        healthy_ip = await self._get_healthy_ip()
        
        # 构建URL
        protocol = "https" if self.verify_ssl else "http"
        url = f"{protocol}://{healthy_ip}{path}"
        
        # 设置请求头
        headers = self.headers.copy()
        headers.update(kwargs.get('headers', {}))
        headers['Host'] = self.domain
        
        # 发送请求
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    **{k: v for k, v in kwargs.items() if k != 'headers'}
                )
                return response
                
            except Exception as e:
                if attempt == self.max_retries:
                    raise OpsGWException(f"请求失败，已重试 {self.max_retries} 次: {e}")
                
                # 标记当前IP为不健康
                self.health_checker.ip_status[healthy_ip] = False
                self.health_checker.healthy_ips.discard(healthy_ip)
                
                # 获取新的健康IP
                try:
                    healthy_ip = await self._get_healthy_ip()
                    protocol = "https" if self.verify_ssl else "http"
                    url = f"{protocol}://{healthy_ip}{path}"
                except NoHealthyIPException:
                    raise OpsGWException(f"所有IP都不健康，无法完成请求: {e}")
    
    async def get(self, path: str, **kwargs) -> aiohttp.ClientResponse:
        """发送GET请求"""
        return await self._make_request('GET', path, **kwargs)
    
    async def post(self, path: str, **kwargs) -> aiohttp.ClientResponse:
        """发送POST请求"""
        return await self._make_request('POST', path, **kwargs)
    
    async def put(self, path: str, **kwargs) -> aiohttp.ClientResponse:
        """发送PUT请求"""
        return await self._make_request('PUT', path, **kwargs)
    
    async def delete(self, path: str, **kwargs) -> aiohttp.ClientResponse:
        """发送DELETE请求"""
        return await self._make_request('DELETE', path, **kwargs)
    
    async def patch(self, path: str, **kwargs) -> aiohttp.ClientResponse:
        """发送PATCH请求"""
        return await self._make_request('PATCH', path, **kwargs)
    
    async def head(self, path: str, **kwargs) -> aiohttp.ClientResponse:
        """发送HEAD请求"""
        return await self._make_request('HEAD', path, **kwargs)
    
    async def options(self, path: str, **kwargs) -> aiohttp.ClientResponse:
        """发送OPTIONS请求"""
        return await self._make_request('OPTIONS', path, **kwargs)
    
    async def get_healthy_ips(self) -> List[str]:
        """获取健康的IP列表"""
        return await self.health_checker.get_healthy_ips()
    
    async def get_all_ips(self) -> List[str]:
        """获取所有IP列表"""
        return await self.health_checker.get_all_ips()
    
    async def force_health_check(self) -> None:
        """强制执行健康检查"""
        await self.health_checker.force_health_check()
    
    async def start(self) -> None:
        """启动客户端"""
        await self.health_checker.start()
    
    async def close(self) -> None:
        """关闭客户端"""
        await self.health_checker.stop()
        if self.session and not self.session.closed:
            await self.session.close()
        await self._connector.close()
    
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close() 