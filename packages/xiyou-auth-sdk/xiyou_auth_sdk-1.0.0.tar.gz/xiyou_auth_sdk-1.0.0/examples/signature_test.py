#!/usr/bin/env python3
"""
Xiyou SDK 签名验证测试

本示例用于测试和验证签名生成的正确性
"""

from xiyou_sdk import XiyouAuth


def test_signature_generation():
    """测试签名生成功能"""

    print("=== Xiyou SDK 签名验证测试 ===\n")

    # 使用测试数据
    auth = XiyouAuth(client_id="xiyoutestak00000", secret_key="test_secret_key_12345")

    # 测试用例1: 基本签名测试
    print("测试用例1: 基本签名生成")
    timestamp = "1751272836"
    method = "POST"
    path = "/v1/asins/traffic"
    body = '{"entities":[{"country":"US","asin":"B09PCSR9SX"}]}'

    signature = auth.generate_signature(
        timestamp=timestamp, method=method, path=path, body=body
    )

    print(f"客户端ID: {auth.client_id}")
    print(f"密钥: {auth.secret_key}")
    print(f"时间戳: {timestamp}")
    print(f"方法: {method}")
    print(f"路径: {path}")
    print(f"请求体: {body}")
    print(f"生成的签名: {signature}")
    print()

    # 测试用例2: 空请求体
    print("测试用例2: 空请求体签名")
    signature_empty = auth.generate_signature(
        timestamp=timestamp,
        method="GET",
        path="/v1/foundation/trendsAvailableDates",
        body="",
    )
    print(f"空请求体签名: {signature_empty}")
    print()

    # 测试用例3: 不同HTTP方法
    print("测试用例3: 不同HTTP方法签名")
    for test_method in ["GET", "POST", "PUT", "DELETE"]:
        sig = auth.generate_signature(
            timestamp=timestamp, method=test_method, path="/v1/test", body=""
        )
        print(f"{test_method}方法签名: {sig}")
    print()

    # 测试用例4: 完整认证头部
    print("测试用例4: 完整认证头部生成")
    headers = auth.get_auth_headers(
        method="POST", path="/v1/asins/traffic", body=body, timestamp=timestamp
    )

    print("完整认证头部:")
    for key, value in headers.items():
        print(f"  {key}: {value}")
    print()

    # 验证签名组成部分
    print("签名构建详情:")
    sign_string = f"{auth.client_id}{timestamp}{method.upper()}{path}{body}"
    print(f"签名字符串: {sign_string}")
    print(f"字符串长度: {len(sign_string)}")
    print()

    print("=== 签名验证测试完成 ===")


if __name__ == "__main__":
    test_signature_generation()
