#!/usr/bin/env python3
"""
网络流量测试脚本
模拟网络发送和接收流量，用于测试前端监控系统的网络流量显示
"""

import time
import threading
import socket
import requests
import random
import psutil
from datetime import datetime
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NetworkTrafficGenerator:
    def __init__(self):
        self.running = False
        self.threads = []
        self.stats = {
            'bytes_sent': 0,
            'bytes_recv': 0,
            'packets_sent': 0,
            'packets_recv': 0
        }
        
    def get_network_stats(self):
        """获取当前网络统计信息"""
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }
    
    def generate_upload_traffic(self):
        """生成上传流量（发送数据）"""
        print("🔼 启动上传流量生成线程")
        
        # 测试用的HTTP服务器列表
        test_urls = [
            'https://httpbin.org/post',
            'https://jsonplaceholder.typicode.com/posts',
            'https://reqres.in/api/users'
        ]
        
        while self.running:
            try:
                # 随机选择目标URL
                url = random.choice(test_urls)
                
                # 生成随机大小的数据 (1KB - 50KB)
                data_size = random.randint(1024, 51200)
                test_data = {
                    'data': 'x' * data_size,
                    'timestamp': datetime.now().isoformat(),
                    'test_id': random.randint(1000, 9999)
                }
                
                # 发送POST请求
                response = requests.post(
                    url, 
                    json=test_data,
                    timeout=10,
                    verify=False
                )
                
                if response.status_code == 200:
                    print(f"📤 上传成功: {data_size/1024:.1f}KB 到 {url}")
                else:
                    print(f"⚠️  上传响应码: {response.status_code}")
                
                # 随机间隔 (2-8秒)
                time.sleep(random.uniform(2, 8))
                
            except Exception as e:
                print(f"❌ 上传流量生成错误: {e}")
                time.sleep(5)
    
    def generate_download_traffic(self):
        """生成下载流量（接收数据）"""
        print("🔽 启动下载流量生成线程")
        
        # 测试用的下载URL列表
        download_urls = [
            'https://httpbin.org/bytes/{}',  # 随机字节数据
            'https://jsonplaceholder.typicode.com/posts',
            'https://api.github.com/repos/microsoft/vscode/releases',
            'https://httpbin.org/json',
            'https://reqres.in/api/users?page={}'
        ]
        
        while self.running:
            try:
                # 随机选择下载类型
                url_template = random.choice(download_urls)
                
                if 'bytes/{}' in url_template:
                    # 下载随机大小的数据 (5KB - 100KB)
                    size = random.randint(5120, 102400)
                    url = url_template.format(size)
                elif 'page={}' in url_template:
                    # 分页数据
                    page = random.randint(1, 10)
                    url = url_template.format(page)
                else:
                    url = url_template
                
                # 发送GET请求
                response = requests.get(
                    url,
                    timeout=15,
                    verify=False,
                    stream=True  # 流式下载
                )
                
                if response.status_code == 200:
                    # 计算下载的数据大小
                    content_length = len(response.content)
                    print(f"📥 下载成功: {content_length/1024:.1f}KB 从 {url}")
                else:
                    print(f"⚠️  下载响应码: {response.status_code}")
                
                # 随机间隔 (3-10秒)
                time.sleep(random.uniform(3, 10))
                
            except Exception as e:
                print(f"❌ 下载流量生成错误: {e}")
                time.sleep(5)
    
    def generate_bidirectional_traffic(self):
        """生成双向流量（模拟API调用）"""
        print("🔄 启动双向流量生成线程")
        
        api_endpoints = [
            'https://httpbin.org/anything',
            'https://jsonplaceholder.typicode.com/posts/1',
            'https://reqres.in/api/users/2'
        ]
        
        while self.running:
            try:
                url = random.choice(api_endpoints)
                
                # 随机选择请求方法
                methods = ['GET', 'POST', 'PUT']
                method = random.choice(methods)
                
                if method == 'GET':
                    response = requests.get(url, timeout=10, verify=False)
                    action = "查询"
                elif method == 'POST':
                    data = {
                        'title': f'Test Post {random.randint(1, 1000)}',
                        'body': 'x' * random.randint(500, 2000),
                        'userId': random.randint(1, 10)
                    }
                    response = requests.post(url, json=data, timeout=10, verify=False)
                    action = "创建"
                else:  # PUT
                    data = {
                        'id': random.randint(1, 100),
                        'title': f'Updated Post {random.randint(1, 1000)}',
                        'body': 'y' * random.randint(300, 1500)
                    }
                    response = requests.put(url, json=data, timeout=10, verify=False)
                    action = "更新"
                
                if response.status_code in [200, 201]:
                    content_size = len(response.content)
                    print(f"🔄 {action}成功: {method} {content_size/1024:.1f}KB")
                
                # 随机间隔 (4-12秒)
                time.sleep(random.uniform(4, 12))
                
            except Exception as e:
                print(f"❌ 双向流量生成错误: {e}")
                time.sleep(5)
    
    def generate_local_traffic(self):
        """生成本地网络流量（模拟内网通信）"""
        print("🏠 启动本地流量生成线程")
        
        while self.running:
            try:
                # 创建TCP连接模拟内网通信
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                
                # 尝试连接到本地常见端口
                local_ports = [80, 443, 22, 3306, 5432, 6379, 9200]
                port = random.choice(local_ports)
                
                try:
                    sock.connect(('127.0.0.1', port))
                    # 发送一些测试数据
                    test_data = b'x' * random.randint(100, 1000)
                    sock.send(test_data)
                    print(f"🏠 本地连接成功: 端口 {port}, 发送 {len(test_data)} 字节")
                except:
                    # 连接失败是正常的，因为大部分端口没有服务
                    pass
                finally:
                    sock.close()
                
                # 随机间隔 (5-15秒)
                time.sleep(random.uniform(5, 15))
                
            except Exception as e:
                print(f"❌ 本地流量生成错误: {e}")
                time.sleep(5)
    
    def monitor_network_stats(self):
        """监控网络统计信息"""
        print("📊 启动网络统计监控线程")
        
        last_stats = self.get_network_stats()
        
        while self.running:
            try:
                time.sleep(10)  # 每10秒统计一次
                
                current_stats = self.get_network_stats()
                
                # 计算增量
                sent_delta = current_stats['bytes_sent'] - last_stats['bytes_sent']
                recv_delta = current_stats['bytes_recv'] - last_stats['bytes_recv']
                
                if sent_delta > 0 or recv_delta > 0:
                    print(f"\n📈 网络流量统计 ({datetime.now().strftime('%H:%M:%S')}):")
                    print(f"   📤 发送: {sent_delta/1024:.1f} KB/10s ({sent_delta/1024/10:.1f} KB/s)")
                    print(f"   📥 接收: {recv_delta/1024:.1f} KB/10s ({recv_delta/1024/10:.1f} KB/s)")
                    print(f"   🔄 总计: {(sent_delta + recv_delta)/1024:.1f} KB/10s")
                
                last_stats = current_stats
                
            except Exception as e:
                print(f"❌ 网络统计错误: {e}")
                time.sleep(5)
    
    def start_traffic_generation(self):
        """启动所有流量生成线程"""
        if self.running:
            print("❌ 流量生成已在运行中")
            return
        
        self.running = True
        print("🚀 启动网络流量测试")
        print("💡 提示: 请在前端监控页面观察网络流量变化")
        print("🔄 按 Ctrl+C 停止测试")
        
        # 显示初始网络状态
        initial_stats = self.get_network_stats()
        print(f"\n📊 初始网络状态:")
        print(f"   总发送: {initial_stats['bytes_sent']/1024/1024:.1f} MB")
        print(f"   总接收: {initial_stats['bytes_recv']/1024/1024:.1f} MB")
        
        # 启动各种流量生成线程
        self.threads = [
            threading.Thread(target=self.generate_upload_traffic, daemon=True),
            threading.Thread(target=self.generate_download_traffic, daemon=True),
            threading.Thread(target=self.generate_bidirectional_traffic, daemon=True),
            threading.Thread(target=self.generate_local_traffic, daemon=True),
            threading.Thread(target=self.monitor_network_stats, daemon=True)
        ]
        
        for thread in self.threads:
            thread.start()
        
        # 主线程等待
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_traffic_generation()
    
    def stop_traffic_generation(self):
        """停止所有流量生成"""
        print("\n🛑 正在停止网络流量测试...")
        self.running = False
        
        # 等待所有线程结束
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=2)
        
        # 显示最终统计
        final_stats = self.get_network_stats()
        print(f"\n📊 最终网络状态:")
        print(f"   总发送: {final_stats['bytes_sent']/1024/1024:.1f} MB")
        print(f"   总接收: {final_stats['bytes_recv']/1024/1024:.1f} MB")
        print("✅ 网络流量测试已停止")

def main():
    """主函数"""
    print("🌐 网络流量测试工具")
    print("=" * 60)
    print("🎯 功能特性:")
    print("   • 模拟上传流量（HTTP POST请求）")
    print("   • 模拟下载流量（HTTP GET请求）")
    print("   • 模拟双向API调用")
    print("   • 模拟本地网络通信")
    print("   • 实时网络统计监控")
    print("   • 死循环模式，持续运行")
    print("=" * 60)
    print("⚠️  注意: 流量大小已优化，不会打满带宽")
    print("🔄 测试将持续运行，按 Ctrl+C 停止")
    print("=" * 60)
    
    generator = NetworkTrafficGenerator()
    
    try:
        generator.start_traffic_generation()
    except Exception as e:
        print(f"❌ 程序出错: {e}")
        generator.stop_traffic_generation()

if __name__ == "__main__":
    main()
