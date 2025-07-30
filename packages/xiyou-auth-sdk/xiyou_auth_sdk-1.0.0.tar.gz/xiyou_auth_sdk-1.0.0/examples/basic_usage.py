#!/usr/bin/env python3
"""
Xiyou SDK 基本使用示例

本示例演示如何使用XiyouAuth进行API请求加签认证
"""

import json

# import requests  # 可选：用户可以使用任何HTTP客户端库
from xiyou_sdk import XiyouAuth


def main():
    """主函数，演示认证功能的使用"""

    # 初始化认证对象
    auth = XiyouAuth(
        client_id="your_client_id",  # 替换为您的客户端ID
        secret_key="your_secret_key",  # 替换为您的密钥
    )

    print("=== Xiyou SDK 认证功能演示 ===\n")

    # 示例1: 获取认证头部
    print("1. 获取认证头部:")
    headers = auth.get_auth_headers(
        method="POST",
        path="/v1/asins/traffic",
        body='{"entities":[{"country":"US","asin":"B09PCSR9SX"}]}',
    )

    print("认证头部:")
    for key, value in headers.items():
        print(f"  {key}: {value}")
    print()

    # 示例2: 手动生成签名
    print("2. 手动生成签名:")
    timestamp = "1751272836"
    signature = auth.generate_signature(
        timestamp=timestamp,
        method="POST",
        path="/v1/asins/traffic",
        body='{"entities":[{"country":"US","asin":"B09PCSR9SX"}]}',
    )
    print(f"时间戳: {timestamp}")
    print(f"签名: {signature}")
    print()

    # 示例3: 与HTTP客户端库结合使用
    print("3. 与HTTP客户端库结合使用示例:")
    try:
        # 构建请求数据
        request_data = {
            "entities": [
                {"country": "US", "asin": "B09PCSR9SX"},
                {"country": "US", "asin": "B006HFJA12"},
            ]
        }
        body = json.dumps(request_data, ensure_ascii=False, separators=(",", ":"))

        # 获取认证头部
        headers = auth.get_auth_headers(
            method="POST", path="/v1/asins/traffic", body=body
        )

        # API调用信息
        url = "https://api.xiyou.com/v1/asins/traffic"

        print(f"请求URL: {url}")
        print("请求头部:")
        for key, value in headers.items():
            print(f"  {key}: {value}")
        print(f"请求体: {body}")
        print()

        print("使用requests库示例代码:")
        print("import requests")
        print(f"response = requests.post('{url}', headers={headers}, data='{body}')")
        print()

        print("使用urllib示例代码:")
        print("import urllib.request")
        print("import urllib.parse")
        print(
            f"req = urllib.request.Request('{url}', data='{body}'.encode(), headers={headers})"
        )
        print("response = urllib.request.urlopen(req)")

    except Exception as e:
        print(f"生成认证信息失败: {e}")

    print("\n=== 认证功能演示完成 ===")


if __name__ == "__main__":
    main()
