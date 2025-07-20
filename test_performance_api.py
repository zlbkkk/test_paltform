#!/usr/bin/env python3
"""
测试性能分析API的脚本
"""

import json
import requests

def test_analyze_monitoring_data():
    """测试监控数据分析API"""
    
    # 读取示例监控数据
    try:
        with open('system_monitor_racknerd-2add1ef_20250720_140812.json', 'r', encoding='utf-8') as f:
            monitoring_data = json.load(f)
    except FileNotFoundError:
        print("错误: 找不到监控数据文件")
        return
    
    # 调用API
    url = 'http://localhost:5000/api/analyze-monitoring-data'
    
    try:
        response = requests.post(url, json=monitoring_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                analysis = result['analysis']
                print("✅ API调用成功!")
                print(f"性能评分: {analysis['performance_score']}")
                print(f"发现瓶颈数量: {len(analysis['bottlenecks'])}")
                print(f"优化建议数量: {len(analysis['recommendations'])}")
                
                # 打印瓶颈信息
                if analysis['bottlenecks']:
                    print("\n🔍 发现的性能瓶颈:")
                    for i, bottleneck in enumerate(analysis['bottlenecks'], 1):
                        print(f"  {i}. [{bottleneck['severity'].upper()}] {bottleneck['description']}")
                        print(f"     影响: {bottleneck['impact']}")
                
                # 打印优化建议
                if analysis['recommendations']:
                    print("\n💡 优化建议:")
                    for i, rec in enumerate(analysis['recommendations'], 1):
                        print(f"  {i}. {rec}")
                
                print(f"\nCPU数据点数量: {len(analysis['charts_data']['cpu_timeline'])}")
                print(f"内存数据点数量: {len(analysis['charts_data']['memory_timeline'])}")
                
            else:
                print(f"❌ API返回错误: {result.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")

def test_health_api():
    """测试健康检查API"""
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 健康检查: {result['status']}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")

if __name__ == "__main__":
    print("🚀 开始测试性能分析API...")
    print("-" * 50)
    
    # 测试健康检查
    test_health_api()
    print()
    
    # 测试监控数据分析
    test_analyze_monitoring_data()
    
    print("-" * 50)
    print("✨ 测试完成!")
