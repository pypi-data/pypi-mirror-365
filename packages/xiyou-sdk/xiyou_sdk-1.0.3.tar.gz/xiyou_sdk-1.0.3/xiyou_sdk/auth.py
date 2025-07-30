"""
Xiyou API认证和加签模块
"""

import hashlib
import time
from typing import Dict, Optional


class XiyouAuth:
    """Xiyou API认证类，负责生成签名和认证头部"""

    def __init__(self, client_id: str, client_secret: str):
        """
        初始化认证对象

        Args:
            client_id: 客户端ID
            client_secret: 客户端密钥
        """
        self.client_id = client_id
        self.client_secret = client_secret

    def _calculate_signature(self, timestamp: int, request_body: str) -> str:
        """
        计算API请求签名

        Args:
            timestamp: 时间戳
            request_body: 请求体内容

        Returns:
            签名字符串
        """
        # 构建签名字符串：client_id + timestamp + client_secret + request_body
        sign_str = self.client_id + str(timestamp) + self.client_secret + request_body
        return hashlib.sha256(sign_str.encode("utf-8")).hexdigest()

    def generate_signature(self, timestamp: int, request_body: str = "") -> str:
        """
        生成API请求签名（兼容旧接口）

        Args:
            timestamp: 时间戳
            request_body: 请求体内容

        Returns:
            签名字符串
        """
        return self._calculate_signature(timestamp, request_body)

    def get_auth_headers(
        self, request_body: str = "", timestamp: Optional[int] = None
    ) -> Dict[str, str]:
        """
        获取认证头部

        Args:
            request_body: 请求体内容
            timestamp: 自定义时间戳，不提供则使用当前时间

        Returns:
            包含认证信息的头部字典
        """
        if timestamp is None:
            timestamp = int(time.time())

        signature = self._calculate_signature(timestamp, request_body)

        return {
            "X-Client-Id": self.client_id,
            "X-Timestamp": str(timestamp),
            "X-Sign": signature,
            "Content-Type": "application/json",
        }
