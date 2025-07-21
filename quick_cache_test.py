#!/usr/bin/env python3
"""
快速缓存测试脚本
验证缓存优化效果
"""

import requests
import time
import json

def test_cache_performance():
    """测试缓存性能"""
    base_url = "http://localhost:5000"
    
    print("🚀 快速缓存性能测试")
    print("=" * 50)
    
    # 获取服务器ID
    try:
        response = requests.get(f"{base_url}/api/servers", timeout=5)
        servers_data = response.json()
        if not servers_data.get('success') or not servers_data.get('data'):
            print("❌ 没有找到服务器配置")
            return
        
        server_id = servers_data['data'][0]['id']
        print(f"🖥️  测试服务器: {server_id}")
        
    except Exception as e:
        print(f"❌ 获取服务器列表失败: {e}")
        return
    
    # 测试API端点
    endpoint = f"{base_url}/api/servers/{server_id}/metrics"
    params = {'timeRange': '1h'}
    
    print(f"\n📊 测试API: {endpoint}")
    print(f"📋 参数: {params}")
    print("-" * 50)
    
    # 进行5次测试
    for i in range(5):
        print(f"\n第 {i+1} 次请求:")
        
        start_time = time.time()
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # 毫秒
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    # 检查缓存信息
                    cache_info = data.get('data', {}).get('cache_info', {})
                    cache_hit = cache_info.get('cache_hit', False)
                    cache_age = cache_info.get('cache_age', 'N/A')
                    
                    cache_status = "🔥 缓存命中" if cache_hit else "🐌 缓存未命中"
                    
                    print(f"   ✅ 响应时间: {response_time:.1f}ms")
                    print(f"   📊 状态: {cache_status}")
                    if cache_hit:
                        print(f"   ⏰ 缓存年龄: {cache_age}")
                    
                    # 显示数据大小
                    content_length = len(response.content)
                    print(f"   📦 数据大小: {content_length/1024:.1f}KB")
                    
                    # 检查数据点数量
                    historical_data = data.get('data', {}).get('historical', {})
                    if historical_data and 'timestamps' in historical_data:
                        data_points = len(historical_data['timestamps'])
                        print(f"   📈 数据点数量: {data_points}")
                    
                else:
                    print(f"   ❌ API错误: {data.get('error', '未知错误')}")
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
        
        # 等待一段时间再进行下次测试
        if i < 4:  # 最后一次不需要等待
            print(f"   ⏳ 等待 3 秒...")
            time.sleep(3)
    
    print("\n" + "=" * 50)
    print("🎯 测试完成！")
    print("\n💡 预期结果:")
    print("   • 第1次请求: 较慢 (需要获取真实数据)")
    print("   • 第2-5次请求: 快速 (缓存命中)")
    print("   • 数据点数量: ≤200 (数据限制)")
    print("   • 缓存命中率: >80%")

if __name__ == "__main__":
    test_cache_performance()
