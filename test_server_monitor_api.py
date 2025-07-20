#!/usr/bin/env python3
"""
测试服务器监控API的脚本
"""

import json
import requests
import time

BASE_URL = 'http://localhost:5000'

def test_get_servers():
    """测试获取服务器列表"""
    print("🔍 测试获取服务器列表...")
    
    try:
        response = requests.get(f'{BASE_URL}/api/servers')
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                servers = result['data']
                print(f"✅ 获取服务器列表成功，共 {len(servers)} 台服务器")
                for server in servers:
                    print(f"   - {server['name']} ({server['host']})")
                return servers
            else:
                print(f"❌ API返回错误: {result.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    return []

def test_add_server():
    """测试添加服务器"""
    print("\n➕ 测试添加服务器...")
    
    server_config = {
        'name': '测试服务器',
        'host': '192.168.1.100',
        'port': 22,
        'username': 'admin',
        'auth_type': 'password',
        'password': 'test123',
        'monitor_interval': 30,
        'description': '这是一个测试服务器',
        'enabled': True
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/servers', json=server_config)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                server = result['data']
                print(f"✅ 添加服务器成功: {server['name']} (ID: {server['id']})")
                return server['id']
            else:
                print(f"❌ API返回错误: {result.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    return None

def test_connection(server_id=None, server_config=None):
    """测试服务器连接"""
    print(f"\n🔗 测试服务器连接...")
    
    try:
        if server_id:
            url = f'{BASE_URL}/api/servers/{server_id}/test'
            response = requests.post(url)
        else:
            url = f'{BASE_URL}/api/servers/test'
            response = requests.post(url, json=server_config)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ 连接测试成功: {result.get('message')}")
                return True
            else:
                print(f"❌ 连接测试失败: {result.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    return False

def test_get_metrics(server_id, time_range='1h'):
    """测试获取监控数据"""
    print(f"\n📊 测试获取监控数据 (时间范围: {time_range})...")
    
    try:
        response = requests.get(f'{BASE_URL}/api/servers/{server_id}/metrics', 
                              params={'timeRange': time_range})
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result['data']
                current = data['current']
                historical = data['historical']
                processes = data['processes']
                
                print("✅ 获取监控数据成功")
                print(f"   当前CPU使用率: {current['cpu']}%")
                print(f"   当前内存使用率: {current['memory_percent']}%")
                print(f"   当前磁盘使用率: {current['disk_percent']}%")
                print(f"   历史数据点数: {len(historical['timestamps'])}")
                print(f"   进程数量: {len(processes)}")
                
                # 显示前3个进程
                print("   Top 3 进程:")
                for i, proc in enumerate(processes[:3]):
                    print(f"     {i+1}. {proc['name']} - CPU: {proc['cpu_percent']}%, 内存: {proc['memory_percent']}%")
                
                return data
            else:
                print(f"❌ API返回错误: {result.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    return None

def test_realtime_metrics(server_id):
    """测试获取实时数据"""
    print(f"\n⚡ 测试获取实时数据...")
    
    try:
        response = requests.get(f'{BASE_URL}/api/servers/{server_id}/metrics/realtime')
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result['data']
                timestamp = result['timestamp']
                
                print("✅ 获取实时数据成功")
                print(f"   时间戳: {timestamp}")
                print(f"   CPU: {data['cpu']}%")
                print(f"   内存: {data['memory_percent']}% ({data['memory_used']}GB/{data['memory_total']}GB)")
                print(f"   磁盘: {data['disk_percent']}% (剩余: {data['disk_free']}GB)")
                print(f"   网络: 发送 {format_bytes(data['network_sent'])}/s, 接收 {format_bytes(data['network_recv'])}/s")
                
                return data
            else:
                print(f"❌ API返回错误: {result.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    return None

def test_processes(server_id, limit=5):
    """测试获取进程列表"""
    print(f"\n🔄 测试获取进程列表 (限制: {limit})...")
    
    try:
        response = requests.get(f'{BASE_URL}/api/servers/{server_id}/processes', 
                              params={'limit': limit})
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                processes = result['data']
                
                print(f"✅ 获取进程列表成功，共 {len(processes)} 个进程")
                print("   进程详情:")
                for proc in processes:
                    print(f"     PID: {proc['pid']}, 名称: {proc['name']}, "
                          f"CPU: {proc['cpu_percent']}%, 内存: {proc['memory_percent']}%")
                
                return processes
            else:
                print(f"❌ API返回错误: {result.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    return None

def test_update_server(server_id):
    """测试更新服务器配置"""
    print(f"\n✏️ 测试更新服务器配置...")
    
    update_data = {
        'name': '更新后的测试服务器',
        'description': '这是更新后的描述',
        'monitor_interval': 60
    }
    
    try:
        response = requests.put(f'{BASE_URL}/api/servers/{server_id}', json=update_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                server = result['data']
                print(f"✅ 更新服务器成功: {server['name']}")
                return True
            else:
                print(f"❌ API返回错误: {result.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    return False

def test_delete_server(server_id):
    """测试删除服务器"""
    print(f"\n🗑️ 测试删除服务器...")
    
    try:
        response = requests.delete(f'{BASE_URL}/api/servers/{server_id}')
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ 删除服务器成功")
                return True
            else:
                print(f"❌ API返回错误: {result.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    return False

def format_bytes(bytes_value):
    """格式化字节数"""
    if bytes_value == 0:
        return '0 B'
    
    units = ['B', 'KB', 'MB', 'GB']
    size = bytes_value
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}"

def main():
    """主测试函数"""
    print("🚀 开始测试服务器监控API...")
    print("=" * 60)
    
    # 1. 测试获取服务器列表
    servers = test_get_servers()
    
    # 2. 测试添加服务器
    new_server_id = test_add_server()
    
    # 3. 使用演示服务器进行测试
    demo_server_id = 'demo-server'
    
    # 4. 测试连接
    test_connection(demo_server_id)
    
    # 5. 测试获取监控数据
    test_get_metrics(demo_server_id, '1h')
    
    # 6. 测试获取实时数据
    test_realtime_metrics(demo_server_id)
    
    # 7. 测试获取进程列表
    test_processes(demo_server_id, 5)
    
    # 8. 如果添加了新服务器，测试更新和删除
    if new_server_id:
        test_update_server(new_server_id)
        time.sleep(1)
        test_delete_server(new_server_id)
    
    print("\n" + "=" * 60)
    print("✨ 服务器监控API测试完成!")

if __name__ == "__main__":
    main()
