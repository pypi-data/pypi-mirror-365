"""
Xiyou OpenAPI Python SDK 安装配置
"""

from setuptools import setup, find_packages

with open("README_SDK.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="xiyou_sdk",
    version="1.0.1",
    author="Xiyou SDK Team",
    author_email="support@xiyou.com",
    description="Xiyou OpenAPI Python SDK - 提供完整的API功能（当前包含认证模块）",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xiyou/xiyou-python-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    keywords="xiyou api sdk auth signature hmac authentication amazon asin",
    project_urls={
        "Bug Reports": "https://github.com/xiyou/xiyou-python-sdk/issues",
        "Source": "https://github.com/xiyou/xiyou-python-sdk",
        "Documentation": "https://docs.xiyou.com",
    },
)
