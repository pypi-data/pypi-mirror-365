"""
OpsGW SDK 自定义异常类
"""


class OpsGWException(Exception):
    """OpsGW SDK 基础异常类"""
    pass


class NoHealthyIPException(OpsGWException):
    """没有健康的IP可用时抛出的异常"""
    pass


class HealthCheckException(OpsGWException):
    """健康检查失败时抛出的异常"""
    pass


class DNSResolutionException(OpsGWException):
    """DNS解析失败时抛出的异常"""
    pass 