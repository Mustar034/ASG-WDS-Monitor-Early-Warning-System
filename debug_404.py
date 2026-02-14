#!/usr/bin/env python3
"""
专项调试404错误
"""
import requests
import json

def test_server_paths():
    """测试服务器所有可能的路径"""
    
    base_url = "http://47.108.55.104:5000"
    
    print("=== 服务器路径调试 ===")
    print(f"服务器: {base_url}")
    print()
    
    # 测试路径列表（从最可能到最不可能）
    test_paths = [
        "/",                    # 根路径
        "/api/upload",          # 队友给的路径
        "/api",                 # API根目录
        "/upload",              # 可能没有/api前缀
        "/data",                # 常见的数据路径
        "/sensor/data",         # 我们之前的路径
        "/api/v1/upload",       # 带版本号
        "/api/v2/upload",
        "/status",              # 状态检查
        "/health",              # 健康检查
        "/test",                # 测试路径
        "/hello",               # 可能有的测试页面
        "/index",               # 索引页
        "/admin",               # 管理页面
        "/swagger",             # API文档
        "/docs",                # 文档
    ]
    
    print("测试GET请求:")
    print("-" * 50)
    for path in test_paths:
        url = base_url + path
        try:
            response = requests.get(url, timeout=5)
            print(f"GET {path:20s} → {response.status_code:3d}")
            if response.status_code in [200, 201]:
                print(f"      响应: {response.text[:100]}")
        except Exception as e:
            print(f"GET {path:20s} → 错误: {e}")
    
    print("\n测试POST请求到上传接口:")
    print("-" * 50)
    
    # 测试POST到可能的路径
    post_paths = ["/api/upload", "/upload", "/data", "/api/data"]
    
    test_data = {"test": "data"}
    
    for path in post_paths:
        url = base_url + path
        try:
            response = requests.post(
                url,
                json=test_data,
                timeout=5
            )
            print(f"POST {path:20s} → {response.status_code:3d}")
            if response.text:
                print(f"      响应: {response.text[:100]}")
        except Exception as e:
            print(f"POST {path:20s} → 错误: {e}")
    
    print("\n=== 分析 ===")
    print("如果所有GET都返回404：")
    print("  1. 队友可能没有定义任何GET路由")
    print("  2. 或者服务器运行不正常")
    print()
    print("如果POST /api/upload 返回405：")
    print("  说明路径存在但不接受POST方法")
    print()
    print("如果POST /api/upload 返回401：")
    print("  说明需要认证")
    print()
    print("如果POST /api/upload 返回400：")
    print("  说明数据格式不对")

if __name__ == "__main__":
    test_server_paths()
