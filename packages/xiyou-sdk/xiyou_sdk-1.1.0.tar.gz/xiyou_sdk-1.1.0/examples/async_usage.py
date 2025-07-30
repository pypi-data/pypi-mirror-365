#!/usr/bin/env python3
"""
Xiyou SDK 异步使用示例

本示例演示如何使用XiyouClient的async_do方法进行异步API请求
"""

import asyncio
from xiyou_sdk import XiyouClient


async def main():
    """主函数，演示异步功能的使用"""

    print("=== Xiyou SDK 异步使用示例 ===\n")

    # 创建客户端
    client = XiyouClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        endpoint="https://api.xiyou.com",  # 只包含域名
    )

    # 示例1：异步调用ASIN流量得分API
    print("1. 异步调用ASIN流量得分API:")
    try:
        response = await client.async_do(
            method="POST",
            path="/v1/asins/traffic",
            body={
                "entities": [
                    {"country": "US", "asin": "B09PCSR9SX"},
                    {"country": "US", "asin": "B006HFJA12"},
                ]
            },
        )

        print(f"状态码: {response.status}")
        print(f"响应头: {dict(response.headers)}")

        # 读取响应内容
        response_text = await response.text()
        print(f"响应内容: {response_text[:200]}...")  # 显示前200字符

    except Exception as e:
        print(f"异步请求失败: {e}")

    print()

    # 示例2：并发调用多个API
    print("2. 并发调用多个API:")
    try:
        # 创建多个并发任务
        tasks = [
            client.async_do(
                method="POST",
                path="/v1/asins/traffic",
                body={"entities": [{"country": "US", "asin": "B09PCSR9SX"}]},
            ),
            client.async_do(
                method="POST",
                path="/v1/foundation/trendsAvailableDates",
                body={"resourceType": "asin", "cycle": "daily"},
            ),
            client.async_do(
                method="GET", path="/v1/some-endpoint", params={"page": 1, "limit": 10}
            ),
        ]

        # 并发执行所有任务
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for i, response in enumerate(responses, 1):
            if isinstance(response, Exception):
                print(f"任务{i}失败: {response}")
            else:
                print(f"任务{i}成功: 状态码 {response.status}")

    except Exception as e:
        print(f"并发请求失败: {e}")

    print()

    # 示例3：使用httpbin测试异步调用
    print("3. 使用httpbin测试异步调用:")

    test_client = XiyouClient(
        client_id="test_client_id",
        client_secret="test_client_secret",
        endpoint="https://httpbin.org",
    )

    try:
        response = await test_client.async_do(
            method="POST",
            path="/post",
            body={"test": "async_data", "timestamp": "123456"},
        )

        print(f"测试状态码: {response.status}")
        response_text = await response.text()
        print(f"响应内容长度: {len(response_text)}")

    except Exception as e:
        print(f"测试请求失败: {e}")

    print()

    # 示例4：对比同步和异步调用
    print("4. 同步vs异步性能对比:")

    import time

    # 同步调用计时
    sync_start = time.time()
    try:
        sync_response = client.do(
            method="GET", path="/", params={"test": "sync"}  # 测试首页
        )
        sync_time = time.time() - sync_start
        print(f"同步调用耗时: {sync_time:.3f}秒, 状态码: {sync_response.status_code}")
    except Exception as e:
        sync_time = time.time() - sync_start
        print(f"同步调用失败: {e}, 耗时: {sync_time:.3f}秒")

    # 异步调用计时
    async_start = time.time()
    try:
        async_response = await client.async_do(
            method="GET", path="/", params={"test": "async"}  # 测试首页
        )
        async_time = time.time() - async_start
        print(f"异步调用耗时: {async_time:.3f}秒, 状态码: {async_response.status}")
    except Exception as e:
        async_time = time.time() - async_start
        print(f"异步调用失败: {e}, 耗时: {async_time:.3f}秒")

    print("\n=== 异步使用示例完成 ===")


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
