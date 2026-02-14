"""
智能测试脚本 - 修复版
"""
import requests
import json
import time
import sys
from datetime import datetime

class SmartServerTester:
    def __init__(self):
        self.server_ip = "47.108.55.104"
        self.port = 5000
        self.base_url = f"http://{self.server_ip}:{self.port}"
        
    def find_upload_endpoint(self):
        """自动发现上传接口"""
        print("🔍 自动发现上传接口...")
        
        # 可能的端点路径
        possible_endpoints = [
            "/api/upload",          # 队友给的
            "/upload",              # 简化版
            "/api/data",            # 你刚刚发现的！
            "/data",                # 更简化
            "/api/sensor/data",     # 我们之前的
            "/api/v1/upload",       # 带版本
            "/api/v2/upload",
            "/api/v1/data",
        ]
        
        for endpoint in possible_endpoints:
            url = self.base_url + endpoint
            print(f"  测试 {endpoint}...")
            
            try:
                # 先用GET测试是否存在（可能返回405）
                response = requests.get(url, timeout=3)
                
                if response.status_code in [200, 405]:
                    print(f"    ✓ 发现接口: {endpoint}")
                    return endpoint
                    
            except Exception:
                pass
        
        print("    ✗ 未找到已知的上传接口")
        return None
    
    def find_auth_method(self, endpoint):
        """发现认证方式"""
        print("\n🔐 发现认证方式...")
        
        url = self.base_url + endpoint
        test_data = {"test": "auth_check"}
        
        # 尝试无认证
        print("  尝试无认证...")
        try:
            response = requests.post(url, json=test_data, timeout=5)
            
            if response.status_code == 200:
                print("    ✓ 不需要认证")
                return {}  # 返回空字典，表示不需要认证头
            elif response.status_code == 401:
                print("    ⚠️  需要认证 (返回401)")
                
                # 尝试我们之前的API密钥
                headers = {"Authorization": "Bearer oKgpm6SpsnmdnaXu0O1bbeb4VKbzzU"}
                response = requests.post(url, json=test_data, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    print("    ✓ 使用旧API密钥成功")
                    return headers
                else:
                    print("    ✗ 旧API密钥无效")
                    # 返回特殊标记，表示需要认证但没有有效密钥
                    return {"need_key": True}
            else:
                print(f"    ⚠️  返回状态码: {response.status_code}")
                return {}
        except Exception as e:
            print(f"    ✗ 认证测试失败: {e}")
            return {}
    
    def test_with_discovered_config(self, endpoint, auth_headers=None):
        """用发现的配置测试上传"""
        print("\n🚀 测试数据上传...")
        
        url = self.base_url + endpoint
        
        # 准备测试数据
        test_data = {
            'device_id': 'raspberry-pi-001',
            'data': {
                'timestamp': datetime.now().isoformat(),
                'sensors': {
                    'temperature': {'value': 25.5, 'unit': 'C'},
                    'humidity': {'value': 60.0, 'unit': 'percent'}
                }
            }
        }
        
        # 确保auth_headers是字典
        if auth_headers is None:
            auth_headers = {}
        
        # 如果auth_headers中有need_key标记，说明需要认证但没有密钥
        if auth_headers.get("need_key"):
            print("  ⚠️  需要认证但没有有效密钥，尝试无认证上传...")
            # 移除need_key标记
            auth_headers = {}
        
        # 添加Content-Type头
        headers = auth_headers.copy()
        headers['Content-Type'] = 'application/json'
        
        print(f"  请求URL: {url}")
        print(f"  认证头: {headers.get('Authorization', '无')}")
        
        try:
            response = requests.post(url, json=test_data, headers=headers, timeout=10)
            
            print(f"  状态码: {response.status_code}")
            
            if response.text:
                # 尝试解析JSON，如果不是JSON则显示纯文本
                try:
                    response_json = response.json()
                    print(f"  响应JSON: {json.dumps(response_json, indent=2)[:200]}")
                except:
                    print(f"  响应文本: {response.text[:200]}")
            
            if response.status_code == 200:
                print("  ✅ 上传成功！")
                return True
            else:
                print("  ❌ 上传失败")
                return False
                
        except Exception as e:
            print(f"  💥 错误: {e}")
            return False
    
    def run(self):
        """运行完整测试流程"""
        print("=" * 60)
        print("  智能服务器测试")
        print("=" * 60)
        
        # 1. 发现端点
        endpoint = self.find_upload_endpoint()
        if not endpoint:
            print("\n❌ 无法找到上传接口，请手动联系队友确认URL")
            return False
        
        # 2. 发现认证方式
        auth_headers = self.find_auth_method(endpoint)
        
        # 3. 测试上传
        success = self.test_with_discovered_config(endpoint, auth_headers)
        
        print("\n" + "=" * 60)
        if success:
            print("✅ 测试成功！")
            print(f"   端点: {endpoint}")
            auth_info = auth_headers.get('Authorization', '无认证') if isinstance(auth_headers, dict) else '未知'
            print(f"   认证: {auth_info}")
            
            # 生成建议的配置
            print("\n💡 建议的config.py配置:")
            print(f"SERVER_HOST = \"{self.server_ip}\"")
            print(f"HTTP_PORT = {self.port}")
            print(f"HTTP_ENDPOINT = \"{endpoint}\"")
            if 'Authorization' in auth_headers:
                print(f"API_KEY = \"{auth_headers['Authorization'].replace('Bearer ', '')}\"")
        else:
            print("❌ 测试失败")
            print("\n🔧 可能的问题：")
            print("   1. 数据格式不对（需要联系队友确认格式）")
            print("   2. 认证方式不对（需要新API密钥）")
            print("   3. 服务器内部错误")
            print("\n📞 联系队友时请提供：")
            print(f"   - 测试的端点: {endpoint}")
            print(f"   - 返回的状态码")
            print(f"   - 完整的错误响应")
        
        print("=" * 60)
        return success

if __name__ == "__main__":
    tester = SmartServerTester()
    success = tester.run()
    sys.exit(0 if success else 1)