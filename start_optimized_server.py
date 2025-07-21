#!/usr/bin/env python3
"""
启动优化后的服务器
包含性能监控和缓存状态显示
"""

import subprocess
import time
import requests
import threading
from datetime import datetime

class OptimizedServerManager:
    def __init__(self):
        self.server_process = None
        self.monitoring_thread = None
        self.is_monitoring = False
        
    def start_server(self):
        """启动服务器"""
        print("🚀 启动优化后的服务器...")
        try:
            self.server_process = subprocess.Popen(
                ['python', 'simple_server.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务器启动
            print("⏳ 等待服务器启动...")
            time.sleep(3)
            
            # 检查服务器是否正常运行
            try:
                response = requests.get('http://localhost:5000/api/servers', timeout=5)
                if response.status_code == 200:
                    print("✅ 服务器启动成功！")
                    print("🌐 访问地址: http://localhost:5000")
                    return True
                else:
                    print(f"❌ 服务器响应异常: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ 服务器连接失败: {e}")
                return False
                
        except Exception as e:
            print(f"❌ 启动服务器失败: {e}")
            return False
    
    def start_monitoring(self):
        """启动性能监控"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitor_performance, daemon=True)
        self.monitoring_thread.start()
        print("📊 性能监控已启动")
    
    def _monitor_performance(self):
        """监控性能指标"""
        while self.is_monitoring:
            try:
                # 获取服务器状态
                response = requests.get('http://localhost:5000/api/servers', timeout=5)
                if response.status_code == 200:
                    servers_data = response.json()
                    if servers_data.get('success') and servers_data.get('data'):
                        server_id = servers_data['data'][0]['id']
                        
                        # 测试API响应时间
                        start_time = time.time()
                        metrics_response = requests.get(
                            f'http://localhost:5000/api/servers/{server_id}/metrics',
                            params={'timeRange': '1h'},
                            timeout=10
                        )
                        response_time = (time.time() - start_time) * 1000
                        
                        if metrics_response.status_code == 200:
                            data = metrics_response.json()
                            cache_info = data.get('data', {}).get('cache_info', {})
                            cache_hit = cache_info.get('cache_hit', False)
                            cache_age = cache_info.get('cache_age', 'N/A')
                            
                            status = "🔥 缓存命中" if cache_hit else "🐌 缓存未命中"
                            
                            print(f"📊 [{datetime.now().strftime('%H:%M:%S')}] "
                                  f"响应时间: {response_time:.1f}ms | {status} | 缓存年龄: {cache_age}")
                        else:
                            print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] "
                                  f"API错误: {metrics_response.status_code}")
                
                time.sleep(10)  # 每10秒监控一次
                
            except Exception as e:
                print(f"❌ 监控错误: {e}")
                time.sleep(5)
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
        print("🛑 性能监控已停止")
    
    def stop_server(self):
        """停止服务器"""
        self.stop_monitoring()
        
        if self.server_process:
            print("🛑 正在停止服务器...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
                print("✅ 服务器已停止")
            except subprocess.TimeoutExpired:
                print("⚠️  强制终止服务器进程")
                self.server_process.kill()
    
    def show_optimization_info(self):
        """显示优化信息"""
        print("\n" + "=" * 60)
        print("🚀 性能优化特性")
        print("=" * 60)
        print("✅ 30秒API响应缓存")
        print("✅ 最多返回200个数据点")
        print("✅ 10秒后台数据更新")
        print("✅ 智能数据采样")
        print("✅ 过期缓存自动清理")
        print("=" * 60)
        print("📊 预期性能提升:")
        print("   • 响应时间: 20s -> <500ms (40倍提升)")
        print("   • 缓存命中率: >80%")
        print("   • 数据传输量: 减少80%")
        print("=" * 60)

def main():
    """主函数"""
    print("🌐 优化后的服务器监控系统")
    print("🎯 性能优化版本")
    
    manager = OptimizedServerManager()
    manager.show_optimization_info()
    
    try:
        # 启动服务器
        if manager.start_server():
            # 启动性能监控
            manager.start_monitoring()
            
            print("\n💡 使用说明:")
            print("   • 服务器已启动并开启性能监控")
            print("   • 访问 http://localhost:5000 查看前端")
            print("   • 运行 python test_performance_optimization.py 进行性能测试")
            print("   • 按 Ctrl+C 停止服务器")
            
            # 等待用户中断
            while True:
                time.sleep(1)
        else:
            print("❌ 服务器启动失败")
            
    except KeyboardInterrupt:
        print("\n🛑 收到停止信号...")
        manager.stop_server()
        print("👋 再见！")
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        manager.stop_server()

if __name__ == "__main__":
    main()
