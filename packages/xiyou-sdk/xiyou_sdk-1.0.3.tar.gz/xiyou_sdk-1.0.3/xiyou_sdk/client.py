"""
Xiyou API客户端
"""

import json
import requests
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin, urlencode

from .auth import XiyouAuth


class XiyouClient:
    """Xiyou API客户端"""

    def __init__(self, client_id: str, client_secret: str, endpoint: str):
        """
        初始化客户端

        Args:
            client_id: 客户端ID
            client_secret: 客户端密钥
            endpoint: API域名（如：https://api.xiyou.com）
        """
        self.endpoint = endpoint.rstrip("/")
        self.auth = XiyouAuth(client_id, client_secret)
        self.session = requests.Session()

    def do(
        self,
        method: str,
        path: str = "",
        body: Optional[Union[Dict[str, Any], str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """
        执行API请求

        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE等)
            path: API路径（如：/v1/asins/traffic）
            body: 请求体，可以是字典或字符串
            params: URL查询参数

        Returns:
            requests.Response对象

        Raises:
            requests.exceptions.RequestException: HTTP请求错误
        """
        # 构建完整URL
        url = urljoin(self.endpoint + "/", path.lstrip("/"))

        # 处理查询参数
        if params:
            url += "?" + urlencode(params)

        # 处理请求体
        request_body = ""
        if body is not None:
            if isinstance(body, dict):
                request_body = json.dumps(
                    body, ensure_ascii=False, separators=(",", ":"), sort_keys=True
                )
            else:
                request_body = str(body)

        # 获取认证头部（只对body进行签名）
        headers = self.auth.get_auth_headers(request_body)

        # 发起请求
        response = self.session.request(
            method=method.upper(),
            url=url,
            headers=headers,
            data=request_body if request_body else None,
        )

        return response
