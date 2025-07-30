#!/usr/bin/env python3
"""
Xiyou SDK 基本使用示例

本示例演示如何使用XiyouClient进行API请求
"""

from xiyou_sdk import XiyouClient, XiyouAuth


def main():
    """主函数，演示SDK功能的使用"""

    print("=== Xiyou SDK 使用示例 ===\n")

    # 方式1：使用XiyouClient（推荐）
    print("1. 使用XiyouClient进行API调用:")

    client = XiyouClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        endpoint="/v1/asins/traffic",
        base_url="https://api.xiyou.com",
    )

    # 示例：调用ASIN流量得分API
    try:
        response = client.do(
            method="POST",
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

    # 示例：使用完整URI覆盖endpoint
    print("2. 使用完整URI覆盖endpoint:")
    try:
        response = client.do(
            method="POST",
            uri="https://api.xiyou.com/v1/foundation/trendsAvailableDates",
            body={"resourceType": "asin", "cycle": "daily"},
        )

        print(f"状态码: {response.status_code}")

    except Exception as e:
        print(f"请求失败: {e}")

    print()

    # 示例：带查询参数
    print("3. 带查询参数的请求:")
    try:
        response = client.do(method="GET", params={"page": 1, "limit": 10})

        print(f"请求URL包含参数: {response.url}")

    except Exception as e:
        print(f"请求失败: {e}")

    print()

    # 示例：不同endpoint的客户端
    print("4. 创建不同endpoint的客户端:")

    trends_client = XiyouClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        endpoint="/v1/foundation/trendsAvailableDates",
    )

    try:
        response = trends_client.do(
            method="POST", body={"resourceType": "asin", "cycle": "daily"}
        )

        print(f"趋势API状态码: {response.status_code}")

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

    print("\n=== SDK使用示例完成 ===")


if __name__ == "__main__":
    main()
