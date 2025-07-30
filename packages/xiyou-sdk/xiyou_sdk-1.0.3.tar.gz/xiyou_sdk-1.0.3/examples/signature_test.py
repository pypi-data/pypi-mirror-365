#!/usr/bin/env python3
"""
Xiyou SDK 签名验证测试

本示例用于测试和验证签名生成的正确性
"""

from xiyou_sdk import XiyouAuth, XiyouClient
import json


def test_signature_generation():
    """测试签名生成功能"""

    print("=== Xiyou SDK 签名验证测试 ===\n")

    # 使用测试数据
    auth = XiyouAuth(
        client_id="xiyoutestak00000", client_secret="test_secret_key_12345"
    )

    # 测试用例1: 基本签名测试
    print("测试用例1: 基本签名生成")
    timestamp = 1751272836
    request_body = '{"entities":[{"country":"US","asin":"B09PCSR9SX"}]}'

    signature = auth.generate_signature(timestamp, request_body)

    print(f"客户端ID: {auth.client_id}")
    print(f"密钥: {auth.client_secret}")
    print(f"时间戳: {timestamp}")
    print(f"请求体: {request_body}")
    print(f"生成的签名: {signature}")
    print()

    # 测试用例2: 空请求体
    print("测试用例2: 空请求体签名")
    signature_empty = auth.generate_signature(timestamp, "")
    print(f"空请求体签名: {signature_empty}")
    print()

    # 测试用例3: JSON排序测试
    print("测试用例3: JSON排序对签名的影响")

    # 测试无序数据
    unordered_data = {
        "z_field": "value1",
        "a_field": "value2",
        "entities": [{"country": "US", "asin": "B09PCSR9SX"}],
    }

    # 手动排序
    ordered_json = json.dumps(
        unordered_data, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    )
    unordered_json = json.dumps(
        unordered_data, ensure_ascii=False, separators=(",", ":"), sort_keys=False
    )

    sig_ordered = auth.generate_signature(timestamp, ordered_json)
    sig_unordered = auth.generate_signature(timestamp, unordered_json)

    print(f"排序JSON: {ordered_json}")
    print(f"排序签名: {sig_ordered}")
    print(f"未排序JSON: {unordered_json}")
    print(f"未排序签名: {sig_unordered}")
    print(f"签名是否相同: {sig_ordered == sig_unordered}")
    print()

    # 测试用例4: 完整认证头部
    print("测试用例4: 完整认证头部生成")
    headers = auth.get_auth_headers(request_body, timestamp)

    print("完整认证头部:")
    for key, value in headers.items():
        print(f"  {key}: {value}")
    print()

    # 测试用例5: Client测试
    print("测试用例5: XiyouClient签名测试")

    client = XiyouClient(
        client_id="xiyoutestak00000",
        client_secret="test_secret_key_12345",
        endpoint="https://httpbin.org",  # 只包含域名
    )

    # 模拟请求（不实际发送）
    test_body = {
        "z_entities": [{"country": "US", "asin": "B09PCSR9SX"}],
        "a_param": "test",
    }

    print(f"测试数据: {test_body}")
    print(f"Endpoint: {client.endpoint}")

    # 验证内部JSON排序
    sorted_body = json.dumps(
        test_body, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    )
    print(f"Client内部排序后: {sorted_body}")

    # 获取认证头部
    test_headers = client.auth.get_auth_headers(sorted_body)
    print("Client生成的认证头部:")
    for key, value in test_headers.items():
        print(f"  {key}: {value}")

    # 测试URL构建
    print(f"测试path='/post'时完整URL: {client.endpoint}/post")

    print()

    # 验证签名组成部分
    print("签名构建详情:")
    sign_string = f"{auth.client_id}{timestamp}{auth.client_secret}{request_body}"
    print(f"签名字符串: {sign_string}")
    print(f"字符串长度: {len(sign_string)}")
    print()

    print("=== 签名验证测试完成 ===")


if __name__ == "__main__":
    test_signature_generation()
