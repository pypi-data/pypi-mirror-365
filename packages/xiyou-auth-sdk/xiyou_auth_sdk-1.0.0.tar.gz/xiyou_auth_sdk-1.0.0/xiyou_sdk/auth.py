"""
Xiyou API认证和加签模块
"""

import hashlib
import hmac
import time
from typing import Dict, Optional


class XiyouAuth:
    """Xiyou API认证类，负责生成签名和认证头部"""

    def __init__(self, client_id: str, secret_key: str):
        """
        初始化认证对象

        Args:
            client_id: 客户端ID
            secret_key: 密钥
        """
        self.client_id = client_id
        self.secret_key = secret_key

    def generate_signature(
        self, timestamp: str, method: str = "POST", path: str = "", body: str = ""
    ) -> str:
        """
        生成API请求签名

        Args:
            timestamp: 时间戳字符串
            method: HTTP方法
            path: API路径
            body: 请求体内容

        Returns:
            签名字符串
        """
        # 构建签名字符串
        # 格式：client_id + timestamp + method + path + body
        sign_string = f"{self.client_id}{timestamp}{method.upper()}{path}{body}"

        # 使用HMAC-SHA256生成签名
        signature = hmac.new(
            self.secret_key.encode("utf-8"), sign_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        return signature

    def get_auth_headers(
        self,
        method: str = "POST",
        path: str = "",
        body: str = "",
        timestamp: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        获取认证头部

        Args:
            method: HTTP方法
            path: API路径
            body: 请求体内容
            timestamp: 自定义时间戳，不提供则使用当前时间

        Returns:
            包含认证信息的头部字典
        """
        if timestamp is None:
            timestamp = str(int(time.time()))

        signature = self.generate_signature(timestamp, method, path, body)

        return {
            "X-Client-Id": self.client_id,
            "X-Timestamp": timestamp,
            "X-Sign": signature,
            "Content-Type": "application/json",
        }
