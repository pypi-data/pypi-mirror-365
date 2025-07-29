#!/usr/bin/env python3
"""
OpsGW HTTP SDK 安装配置
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取requirements文件
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="opsgw-sdk",
    version="1.0.1",
    author="OpsGW Team",
    author_email="team@opsgw.com",
    description="具有健康监测功能的HTTP SDK",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/opsgw/opsgw-sdk-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "pytest-cov>=2.10",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="http client sdk health check dns load balancer",
    project_urls={
        "Bug Reports": "https://github.com/opsgw/opsgw-sdk-python/issues",
        "Source": "https://github.com/opsgw/opsgw-sdk-python",
        "Documentation": "https://github.com/opsgw/opsgw-sdk-python/blob/main/README.md",
    },
) 