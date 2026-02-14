#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一体化测试脚本
"""

import sys
import subprocess
import time
from datetime import datetime

def run_test(test_name, script_path, *args):
    """运行单个测试"""
    print(f"\n{'='*60}")
    print(f"  开始测试: {test_name}")
    print(f"{'='*60}")
    
    try:
        cmd = ['python3', script_path] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)
        
        success = result.returncode == 0
        
        if success:
            print(f"✅ {test_name} 通过")
        else:
            print(f"❌ {test_name} 失败")
        
        return success
        
    except Exception as e:
        print(f"❌ 执行测试失败: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("  一体化服务器测试套件")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 测试列表
    tests = [
        ("基本连接测试", "test_get_connection.py"),
        ("数据结构分析", "analyze_server_data.py"),
        ("连续查询测试", "continuous_query.py", "--once"),
    ]
    
    results = []
    
    for test in tests:
        test_name, script = test[0], test[1]
        args = test[2:] if len(test) > 2 else []
        
        success = run_test(test_name, script, *args)
        results.append((test_name, success))
        
        # 测试间暂停
        time.sleep(1)
    
    # 打印总结
    print("\n" + "=" * 60)
    print("  测试总结")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name:20s}: {status}")
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        print("\n下一步建议:")
        print("1. 运行连续监控: python3 continuous_query.py --interval 10")
        print("2. 将数据保存到文件")
        print("3. 实现数据可视化")
    else:
        print("\n⚠️  部分测试失败")
        print("请检查失败原因并修复")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)