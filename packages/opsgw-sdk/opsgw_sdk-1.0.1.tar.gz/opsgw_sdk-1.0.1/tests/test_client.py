#!/usr/bin/env python3
"""
客户端测试
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from opsgw_sdk import OpsGWClient, AsyncOpsGWClient
from opsgw_sdk.exceptions import NoHealthyIPException, OpsGWException


class TestOpsGWClient(unittest.TestCase):
    """同步客户端测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = OpsGWClient(
            domain="test.example.com",
            health_check_interval=1,
            health_check_timeout=1,
            health_check_path="/health"
        )
    
    def tearDown(self):
        """测试后清理"""
        self.client.close()
    
    @patch('opsgw_sdk.health_checker.dns.resolver.resolve')
    def test_dns_resolution(self, mock_resolve):
        """测试DNS解析"""
        # 模拟DNS解析结果
        mock_answer = Mock()
        mock_answer.__str__ = Mock(return_value="192.168.1.1")
        mock_resolve.return_value = [mock_answer]
        
        # 重新初始化客户端以触发DNS解析
        client = OpsGWClient("test.example.com")
        client.close()
        
        # 验证DNS解析被调用
        mock_resolve.assert_called_with("test.example.com", 'A')
    
    @patch('opsgw_sdk.health_checker.requests.get')
    def test_health_check(self, mock_get):
        """测试健康检查"""
        # 模拟健康检查响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # 强制健康检查
        self.client.force_health_check()
        
        # 验证健康检查被调用
        self.assertTrue(mock_get.called)
    
    def test_get_healthy_ips(self):
        """测试获取健康IP列表"""
        ips = self.client.get_healthy_ips()
        self.assertIsInstance(ips, list)
    
    def test_get_all_ips(self):
        """测试获取所有IP列表"""
        ips = self.client.get_all_ips()
        self.assertIsInstance(ips, list)
    
    @patch('opsgw_sdk.client.requests.Session.request')
    def test_make_request(self, mock_request):
        """测试发送请求"""
        # 模拟响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_request.return_value = mock_response
        
        # 发送请求
        response = self.client.get("/test")
        
        # 验证请求被发送
        self.assertTrue(mock_request.called)
        self.assertEqual(response.status_code, 200)
    
    def test_context_manager(self):
        """测试上下文管理器"""
        with OpsGWClient("test.example.com") as client:
            self.assertIsInstance(client, OpsGWClient)


class TestAsyncOpsGWClient(unittest.TestCase):
    """异步客户端测试"""
    
    def setUp(self):
        """测试前准备"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        self.client = AsyncOpsGWClient(
            domain="test.example.com",
            health_check_interval=1,
            health_check_timeout=1,
            health_check_path="/health"
        )
    
    def tearDown(self):
        """测试后清理"""
        self.loop.run_until_complete(self.client.close())
        self.loop.close()
    
    @patch('opsgw_sdk.health_checker.dns.resolver.resolve')
    def test_async_dns_resolution(self, mock_resolve):
        """测试异步DNS解析"""
        # 模拟DNS解析结果
        mock_answer = Mock()
        mock_answer.__str__ = Mock(return_value="192.168.1.1")
        mock_resolve.return_value = [mock_answer]
        
        # 重新初始化客户端以触发DNS解析
        client = AsyncOpsGWClient("test.example.com")
        self.loop.run_until_complete(client.close())
        
        # 验证DNS解析被调用
        mock_resolve.assert_called_with("test.example.com", 'A')
    
    @patch('opsgw_sdk.health_checker.aiohttp.ClientSession.get')
    def test_async_health_check(self, mock_get):
        """测试异步健康检查"""
        # 模拟健康检查响应
        mock_response = Mock()
        mock_response.status = 200
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # 强制健康检查
        self.loop.run_until_complete(self.client.force_health_check())
        
        # 验证健康检查被调用
        self.assertTrue(mock_get.called)
    
    def test_async_get_healthy_ips(self):
        """测试异步获取健康IP列表"""
        ips = self.loop.run_until_complete(self.client.get_healthy_ips())
        self.assertIsInstance(ips, list)
    
    def test_async_get_all_ips(self):
        """测试异步获取所有IP列表"""
        ips = self.loop.run_until_complete(self.client.get_all_ips())
        self.assertIsInstance(ips, list)
    
    @patch('opsgw_sdk.client.aiohttp.ClientSession.request')
    def test_async_make_request(self, mock_request):
        """测试异步发送请求"""
        # 模拟响应
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = asyncio.coroutine(lambda: {"test": "data"})
        mock_request.return_value = mock_response
        
        # 发送请求
        response = self.loop.run_until_complete(self.client.get("/test"))
        
        # 验证请求被发送
        self.assertTrue(mock_request.called)
        self.assertEqual(response.status, 200)
    
    def test_async_context_manager(self):
        """测试异步上下文管理器"""
        async def test_context():
            async with AsyncOpsGWClient("test.example.com") as client:
                self.assertIsInstance(client, AsyncOpsGWClient)
        
        self.loop.run_until_complete(test_context())


class TestExceptions(unittest.TestCase):
    """异常测试"""
    
    def test_no_healthy_ip_exception(self):
        """测试没有健康IP异常"""
        exception = NoHealthyIPException("test")
        self.assertIsInstance(exception, Exception)
        self.assertEqual(str(exception), "test")
    
    def test_opsgw_exception(self):
        """测试OpsGW异常"""
        exception = OpsGWException("test")
        self.assertIsInstance(exception, Exception)
        self.assertEqual(str(exception), "test")


if __name__ == "__main__":
    unittest.main() 