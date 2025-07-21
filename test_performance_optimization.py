#!/usr/bin/env python3
"""
性能优化测试脚本
测试缓存优化后的API响应时间
"""

import requests
import time
import json
from datetime import datetime
import statistics

class PerformanceTest:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = []
        
    def test_api_response_time(self, endpoint, params=None, iterations=10):
        """测试API响应时间"""
        print(f"\n🧪 测试API: {endpoint}")
        print(f"📊 测试次数: {iterations}")
        print("-" * 50)
        
        response_times = []
        cache_hits = 0
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                response = requests.get(f"{self.base_url}{endpoint}", params=params, timeout=30)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # 转换为毫秒
                response_times.append(response_time)
                
                # 检查是否命中缓存
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('data', {}).get('cache_info', {}).get('cache_hit'):
                        cache_hits += 1
                        cache_status = "🔥 缓存命中"
                    else:
                        cache_status = "🐌 缓存未命中"
                else:
                    cache_status = f"❌ 错误 {response.status_code}"
                
                print(f"第{i+1:2d}次: {response_time:6.1f}ms - {cache_status}")
                
                # 第一次请求后稍微等待，让缓存生效
                if i == 0:
                    time.sleep(1)
                else:
                    time.sleep(0.5)  # 避免请求过于频繁
                    
            except Exception as e:
                print(f"第{i+1:2d}次: 请求失败 - {e}")
                response_times.append(30000)  # 30秒超时
        
        # 统计结果
        if response_times:
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            median_time = statistics.median(response_times)
            
            print(f"\n📈 性能统计:")
            print(f"   平均响应时间: {avg_time:.1f}ms")
            print(f"   最快响应时间: {min_time:.1f}ms")
            print(f"   最慢响应时间: {max_time:.1f}ms")
            print(f"   中位数响应时间: {median_time:.1f}ms")
            print(f"   缓存命中率: {cache_hits}/{iterations} ({cache_hits/iterations*100:.1f}%)")
            
            # 性能评级
            if avg_time < 100:
                grade = "🚀 优秀"
            elif avg_time < 500:
                grade = "✅ 良好"
            elif avg_time < 2000:
                grade = "⚠️  一般"
            else:
                grade = "❌ 需要优化"
            
            print(f"   性能评级: {grade}")
            
            return {
                'endpoint': endpoint,
                'avg_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'median_time': median_time,
                'cache_hit_rate': cache_hits / iterations,
                'grade': grade
            }
        
        return None
    
    def test_concurrent_requests(self, endpoint, params=None, concurrent_users=5, requests_per_user=3):
        """测试并发请求性能"""
        print(f"\n🔄 并发测试: {endpoint}")
        print(f"👥 并发用户数: {concurrent_users}")
        print(f"📊 每用户请求数: {requests_per_user}")
        print("-" * 50)
        
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def worker():
            """工作线程"""
            for _ in range(requests_per_user):
                start_time = time.time()
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", params=params, timeout=30)
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    results_queue.put(('success', response_time))
                except Exception as e:
                    results_queue.put(('error', str(e)))
                time.sleep(0.1)  # 避免过于频繁
        
        # 启动并发线程
        threads = []
        start_time = time.time()
        
        for i in range(concurrent_users):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # 收集结果
        response_times = []
        errors = 0
        
        while not results_queue.empty():
            result_type, result_data = results_queue.get()
            if result_type == 'success':
                response_times.append(result_data)
            else:
                errors += 1
        
        total_requests = concurrent_users * requests_per_user
        success_requests = len(response_times)
        
        print(f"📊 并发测试结果:")
        print(f"   总请求数: {total_requests}")
        print(f"   成功请求: {success_requests}")
        print(f"   失败请求: {errors}")
        print(f"   总耗时: {total_time:.1f}s")
        print(f"   吞吐量: {success_requests/total_time:.1f} 请求/秒")
        
        if response_times:
            avg_time = statistics.mean(response_times)
            print(f"   平均响应时间: {avg_time:.1f}ms")
        
        return {
            'total_requests': total_requests,
            'success_requests': success_requests,
            'errors': errors,
            'total_time': total_time,
            'throughput': success_requests / total_time if total_time > 0 else 0,
            'avg_response_time': statistics.mean(response_times) if response_times else 0
        }
    
    def run_comprehensive_test(self):
        """运行综合性能测试"""
        print("🚀 开始性能优化测试")
        print("=" * 60)
        
        # 检查服务器是否运行
        try:
            response = requests.get(f"{self.base_url}/api/servers", timeout=5)
            if response.status_code != 200:
                print("❌ 服务器未正常运行，请先启动 simple_server.py")
                return
        except Exception as e:
            print(f"❌ 无法连接到服务器: {e}")
            print("   请确保 simple_server.py 正在运行")
            return
        
        # 获取服务器列表
        try:
            servers_response = requests.get(f"{self.base_url}/api/servers")
            servers_data = servers_response.json()
            
            if not servers_data.get('success') or not servers_data.get('data'):
                print("⚠️  没有找到配置的服务器，请先添加服务器配置")
                return
            
            server_id = servers_data['data'][0]['id']
            print(f"🖥️  测试服务器: {server_id}")
            
        except Exception as e:
            print(f"❌ 获取服务器列表失败: {e}")
            return
        
        # 测试不同时间范围的监控数据API
        test_cases = [
            {'endpoint': f'/api/servers/{server_id}/metrics', 'params': {'timeRange': '1h'}, 'name': '1小时监控数据'},
            {'endpoint': f'/api/servers/{server_id}/metrics', 'params': {'timeRange': '6h'}, 'name': '6小时监控数据'},
            {'endpoint': f'/api/servers/{server_id}/metrics', 'params': {'timeRange': '24h'}, 'name': '24小时监控数据'},
        ]
        
        results = []
        
        for test_case in test_cases:
            print(f"\n🧪 测试: {test_case['name']}")
            result = self.test_api_response_time(
                test_case['endpoint'], 
                test_case['params'], 
                iterations=8
            )
            if result:
                result['name'] = test_case['name']
                results.append(result)
        
        # 并发测试
        print(f"\n🔄 并发性能测试")
        concurrent_result = self.test_concurrent_requests(
            f'/api/servers/{server_id}/metrics',
            {'timeRange': '1h'},
            concurrent_users=3,
            requests_per_user=2
        )
        
        # 生成测试报告
        self.generate_report(results, concurrent_result)
    
    def generate_report(self, results, concurrent_result):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 性能优化测试报告")
        print("=" * 60)
        
        print(f"🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 优化目标: 响应时间 < 500ms，缓存命中率 > 80%")
        
        print(f"\n📈 API响应时间测试:")
        for result in results:
            status = "✅" if result['avg_time'] < 500 else "❌"
            cache_status = "✅" if result['cache_hit_rate'] > 0.8 else "❌"
            print(f"   {status} {result['name']}: {result['avg_time']:.1f}ms (缓存命中率: {result['cache_hit_rate']*100:.1f}% {cache_status})")
        
        print(f"\n🔄 并发性能测试:")
        if concurrent_result:
            throughput_status = "✅" if concurrent_result['throughput'] > 5 else "❌"
            print(f"   {throughput_status} 吞吐量: {concurrent_result['throughput']:.1f} 请求/秒")
            print(f"   📊 成功率: {concurrent_result['success_requests']}/{concurrent_result['total_requests']} ({concurrent_result['success_requests']/concurrent_result['total_requests']*100:.1f}%)")
        
        # 总体评估
        avg_response_time = statistics.mean([r['avg_time'] for r in results]) if results else 0
        avg_cache_hit_rate = statistics.mean([r['cache_hit_rate'] for r in results]) if results else 0
        
        print(f"\n🎯 总体评估:")
        print(f"   平均响应时间: {avg_response_time:.1f}ms")
        print(f"   平均缓存命中率: {avg_cache_hit_rate*100:.1f}%")
        
        if avg_response_time < 500 and avg_cache_hit_rate > 0.8:
            print(f"   🚀 优化效果: 优秀！性能目标已达成")
        elif avg_response_time < 1000:
            print(f"   ✅ 优化效果: 良好，还有提升空间")
        else:
            print(f"   ⚠️  优化效果: 需要进一步优化")
        
        print("=" * 60)

def main():
    """主函数"""
    print("🌐 服务器监控系统性能测试工具")
    print("🎯 测试缓存优化效果")
    
    tester = PerformanceTest()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
