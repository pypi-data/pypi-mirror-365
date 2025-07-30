#!/usr/bin/env python3
"""
Xiyou SDK 基本使用示例

本示例演示如何使用XiyouClient进行API请求（同步和异步）
"""

from xiyou_sdk import XiyouClient, XiyouAuth


def main():
    """主函数，演示SDK功能的使用"""

    print("=== Xiyou SDK 使用示例 ===\n")

    # 方式1：使用XiyouClient（推荐）
    print("1. 使用XiyouClient进行同步API调用:")

    client = XiyouClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        endpoint="https://api.xiyou.com",  # 只包含域名
    )

    # 示例：调用ASIN流量得分API
    try:
        response = client.do(
            method="POST",
            path="/v1/asins/traffic",  # API路径
            body={
                "entities": [
                    {"country": "US", "asin": "B09PCSR9SX"},
                    {"country": "US", "asin": "B006HFJA12"},
                ]
            },
        )

        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text[:200]}...")  # 显示前200字符

    except Exception as e:
        print(f"请求失败: {e}")

    print()

    # 示例：调用不同的API路径
    print("2. 调用不同的API路径:")
    try:
        response = client.do(
            method="POST",
            path="/v1/foundation/trendsAvailableDates",
            body={"resourceType": "asin", "cycle": "daily"},
        )

        print(f"状态码: {response.status_code}")

    except Exception as e:
        print(f"请求失败: {e}")

    print()

    # 示例：带查询参数
    print("3. 带查询参数的请求:")
    try:
        response = client.do(
            method="GET", path="/v1/some-endpoint", params={"page": 1, "limit": 10}
        )

        print(f"请求URL包含参数: {response.url}")

    except Exception as e:
        print(f"请求失败: {e}")

    print()

    # 示例：使用不同域名的客户端
    print("4. 使用不同域名的客户端:")

    test_client = XiyouClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        endpoint="https://httpbin.org",  # 测试域名
    )

    try:
        response = test_client.do(method="POST", path="/post", body={"test": "data"})

        print(f"测试API状态码: {response.status_code}")

    except Exception as e:
        print(f"请求失败: {e}")

    print()

    # 方式2：仅使用认证功能
    print("5. 仅使用认证功能:")

    auth = XiyouAuth("your_client_id", "your_client_secret")

    request_body = '{"entities":[{"country":"US","asin":"B09PCSR9SX"}]}'
    headers = auth.get_auth_headers(request_body)

    print("认证头部:")
    for key, value in headers.items():
        print(f"  {key}: {value}")

    print()

    # 说明异步方法
    print("6. 异步方法说明:")
    print("SDK还提供了async_do方法用于异步调用:")
    print(
        "response = await client.async_do(method='POST', path='/v1/asins/traffic', body={...})"
    )
    print("详细异步示例请查看 examples/async_usage.py")

    print("\n=== SDK使用示例完成 ===")


if __name__ == "__main__":
    main()
