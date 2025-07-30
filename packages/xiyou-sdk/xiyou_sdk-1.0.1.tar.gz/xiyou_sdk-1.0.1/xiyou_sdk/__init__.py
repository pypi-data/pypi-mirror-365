"""
Xiyou OpenAPI Python SDK

提供Xiyou API的Python客户端库，包含完整的加签认证功能
"""

__version__ = "1.0.1"
__author__ = "Xiyou SDK Team"

from .auth import XiyouAuth
from .client import XiyouClient

__all__ = ["XiyouAuth", "XiyouClient"]
