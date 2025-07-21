#!/usr/bin/env python3
from flask import Flask, request, jsonify, render_template_string, render_template
from flask_cors import CORS
import io
import sys
import json
import os
import numpy as np
import sqlite3
import threading
import time
import socket
import re
from datetime import datetime, timedelta
from contextlib import redirect_stdout, redirect_stderr

# 尝试导入paramiko，如果没有安装则提示
try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False
    print("⚠️  警告: paramiko库未安装，SSH连接功能将被禁用")
    print("   安装命令: pip install paramiko")

class HistoricalDataPersistence:
    """历史数据持久化管理类"""

    def __init__(self, data_dir='historical_data'):
        self.data_dir = data_dir
        self.ensure_data_dir()

    def ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"📁 创建历史数据目录: {self.data_dir}")

    def get_file_path(self, server_id, metric_type):
        """获取指定服务器和指标类型的文件路径"""
        filename = f"{server_id}_{metric_type}.txt"
        return os.path.join(self.data_dir, filename)

    def save_historical_data(self, server_id, historical_data):
        """保存历史数据到文件（追加模式）"""
        try:
            # 保存CPU数据
            self._append_metric_data(server_id, 'cpu', historical_data['timestamps'], historical_data['cpu'])

            # 保存内存数据
            self._append_metric_data(server_id, 'memory', historical_data['timestamps'], historical_data['memory'])

            # 保存磁盘IO数据
            self._append_disk_io_data(server_id, historical_data['timestamps'],
                                    historical_data['disk_read'], historical_data['disk_write'])

            # 保存网络数据
            self._append_network_data(server_id, historical_data['timestamps'],
                                    historical_data['network_sent'], historical_data['network_recv'])

            print(f"💾 历史数据已追加保存到文件: {server_id}")

        except Exception as e:
            print(f"❌ 保存历史数据失败: {e}")

    def _append_metric_data(self, server_id, metric_type, timestamps, values):
        """追加单一指标数据（CPU或内存）"""
        file_path = self.get_file_path(server_id, metric_type)

        # 加载现有数据
        existing_data = {'timestamps': [], 'values': []}
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except:
                pass  # 如果文件损坏，从空数据开始

        # 合并数据（避免重复时间戳）
        existing_timestamps = set(existing_data.get('timestamps', []))
        for i, timestamp in enumerate(timestamps):
            if timestamp not in existing_timestamps:
                existing_data['timestamps'].append(timestamp)
                existing_data['values'].append(values[i])

        # 限制数据点数量（保留最新的1000个数据点）
        max_points = 1000
        if len(existing_data['timestamps']) > max_points:
            existing_data['timestamps'] = existing_data['timestamps'][-max_points:]
            existing_data['values'] = existing_data['values'][-max_points:]

        # 保存更新后的数据
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

    def _append_disk_io_data(self, server_id, timestamps, disk_read, disk_write):
        """追加磁盘IO数据"""
        file_path = self.get_file_path(server_id, 'disk_io')

        # 加载现有数据
        existing_data = {'timestamps': [], 'disk_read': [], 'disk_write': []}
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except:
                pass

        # 合并数据
        existing_timestamps = set(existing_data.get('timestamps', []))
        for i, timestamp in enumerate(timestamps):
            if timestamp not in existing_timestamps:
                existing_data['timestamps'].append(timestamp)
                existing_data['disk_read'].append(disk_read[i])
                existing_data['disk_write'].append(disk_write[i])

        # 限制数据点数量
        max_points = 1000
        if len(existing_data['timestamps']) > max_points:
            existing_data['timestamps'] = existing_data['timestamps'][-max_points:]
            existing_data['disk_read'] = existing_data['disk_read'][-max_points:]
            existing_data['disk_write'] = existing_data['disk_write'][-max_points:]

        # 保存更新后的数据
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

    def _append_network_data(self, server_id, timestamps, network_sent, network_recv):
        """追加网络数据"""
        file_path = self.get_file_path(server_id, 'network')

        # 加载现有数据
        existing_data = {'timestamps': [], 'network_sent': [], 'network_recv': []}
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except:
                pass

        # 合并数据
        existing_timestamps = set(existing_data.get('timestamps', []))
        for i, timestamp in enumerate(timestamps):
            if timestamp not in existing_timestamps:
                existing_data['timestamps'].append(timestamp)
                existing_data['network_sent'].append(network_sent[i])
                existing_data['network_recv'].append(network_recv[i])

        # 限制数据点数量
        max_points = 1000
        if len(existing_data['timestamps']) > max_points:
            existing_data['timestamps'] = existing_data['timestamps'][-max_points:]
            existing_data['network_sent'] = existing_data['network_sent'][-max_points:]
            existing_data['network_recv'] = existing_data['network_recv'][-max_points:]

        # 保存更新后的数据
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

    def append_realtime_data(self, server_id, timestamp, cpu, memory, disk_read, disk_write, network_sent, network_recv):
        """追加单个实时数据点"""
        try:
            # 追加CPU数据
            self._append_metric_data(server_id, 'cpu', [timestamp], [cpu])

            # 追加内存数据
            self._append_metric_data(server_id, 'memory', [timestamp], [memory])

            # 追加磁盘IO数据
            self._append_disk_io_data(server_id, [timestamp], [disk_read], [disk_write])

            # 追加网络数据
            self._append_network_data(server_id, [timestamp], [network_sent], [network_recv])

            print(f"📊 实时数据已追加: {server_id} @ {timestamp}")

        except Exception as e:
            print(f"❌ 追加实时数据失败: {e}")

    def load_historical_data(self, server_id):
        """从文件加载历史数据"""
        try:
            result = {
                'timestamps': [],
                'cpu': [],
                'memory': [],
                'disk_read': [],
                'disk_write': [],
                'network_sent': [],
                'network_recv': []
            }

            # 加载CPU数据
            cpu_file = self.get_file_path(server_id, 'cpu')
            if os.path.exists(cpu_file):
                with open(cpu_file, 'r', encoding='utf-8') as f:
                    cpu_data = json.load(f)
                    result['timestamps'] = cpu_data.get('timestamps', [])
                    result['cpu'] = cpu_data.get('values', [])

            # 加载内存数据
            memory_file = self.get_file_path(server_id, 'memory')
            if os.path.exists(memory_file):
                with open(memory_file, 'r', encoding='utf-8') as f:
                    memory_data = json.load(f)
                    if not result['timestamps']:  # 如果CPU数据没有时间戳，使用内存数据的
                        result['timestamps'] = memory_data.get('timestamps', [])
                    result['memory'] = memory_data.get('values', [])

            # 加载磁盘IO数据
            disk_file = self.get_file_path(server_id, 'disk_io')
            if os.path.exists(disk_file):
                with open(disk_file, 'r', encoding='utf-8') as f:
                    disk_data = json.load(f)
                    if not result['timestamps']:
                        result['timestamps'] = disk_data.get('timestamps', [])
                    result['disk_read'] = disk_data.get('disk_read', [])
                    result['disk_write'] = disk_data.get('disk_write', [])

            # 加载网络数据
            network_file = self.get_file_path(server_id, 'network')
            if os.path.exists(network_file):
                with open(network_file, 'r', encoding='utf-8') as f:
                    network_data = json.load(f)
                    if not result['timestamps']:
                        result['timestamps'] = network_data.get('timestamps', [])
                    result['network_sent'] = network_data.get('network_sent', [])
                    result['network_recv'] = network_data.get('network_recv', [])

            if result['timestamps']:
                print(f"📖 从文件加载历史数据: {server_id}, {len(result['timestamps'])}个数据点")
                return result
            else:
                print(f"📖 未找到历史数据文件: {server_id}")
                return None

        except Exception as e:
            print(f"❌ 加载历史数据失败: {e}")
            return None

app = Flask(__name__, static_folder='dist/static', template_folder='dist')
CORS(app)

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/code-executor')
def code_executor():
    """代码执行器页面"""
    return render_template('code_executor.html')

@app.route('/execute-script', methods=['POST'])
def execute_script():
    try:
        data = request.get_json()
        code = data.get('code', '')
        
        if not code.strip():
            return jsonify({'success': False, 'error': '代码内容不能为空'})
        
        # # 简单的安全检查
        # dangerous = ['import os', 'import sys', 'open(', 'file(', 'exec(', 'eval(']
        # for danger in dangerous:
        #     if danger in code.lower():
        #         return jsonify({'success': False, 'error': f'不允许使用: {danger}'})
        
        # 执行代码
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        try:
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                exec(code)
            
            return jsonify({
                'success': True,
                'output': stdout_buffer.getvalue(),
                'error': stderr_buffer.getvalue()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'output': stdout_buffer.getvalue(),
                'error': str(e)
            })
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

# 性能监控数据分析类
class PerformanceAnalyzer:
    def __init__(self):
        self.analysis_patterns = {
            'cpu_high_usage': {'threshold': 80, 'severity': 'high'},
            'cpu_sustained_high': {'threshold': 60, 'duration_ratio': 0.3, 'severity': 'medium'},
            'memory_high_usage': {'threshold': 85, 'severity': 'high'},
            'memory_sustained_high': {'threshold': 70, 'duration_ratio': 0.4, 'severity': 'medium'},
            'load_high': {'severity': 'high'},
            'context_switch_high': {'threshold_per_sec': 10000, 'severity': 'medium'}
        }

    def analyze_monitoring_data(self, data):
        """分析监控数据，识别性能瓶颈"""
        analysis_result = {
            'system_info': data.get('system_info', {}),
            'monitoring_summary': data.get('monitoring_summary', {}),
            'bottlenecks': [],
            'recommendations': [],
            'performance_score': 100,
            'charts_data': self._prepare_charts_data(data)
        }

        cpu_data = data.get('cpu_data', [])
        memory_data = data.get('memory_data', [])

        if cpu_data:
            cpu_analysis = self._analyze_cpu_data(cpu_data, data['system_info'])
            analysis_result['bottlenecks'].extend(cpu_analysis['bottlenecks'])
            analysis_result['recommendations'].extend(cpu_analysis['recommendations'])
            analysis_result['performance_score'] -= cpu_analysis['score_penalty']

        if memory_data:
            memory_analysis = self._analyze_memory_data(memory_data)
            analysis_result['bottlenecks'].extend(memory_analysis['bottlenecks'])
            analysis_result['recommendations'].extend(memory_analysis['recommendations'])
            analysis_result['performance_score'] -= memory_analysis['score_penalty']

        # 确保性能分数不低于0
        analysis_result['performance_score'] = max(0, analysis_result['performance_score'])

        return analysis_result

    def _analyze_cpu_data(self, cpu_data, system_info):
        """分析CPU数据"""
        bottlenecks = []
        recommendations = []
        score_penalty = 0

        cpu_usage = [item['cpu_percent_total'] for item in cpu_data]
        load_avg = [item['load_average_1min'] for item in cpu_data]
        cpu_count = system_info.get('cpu_count_logical', 1)

        # 分析CPU使用率
        avg_cpu = np.mean(cpu_usage)
        max_cpu = np.max(cpu_usage)
        high_cpu_ratio = len([x for x in cpu_usage if x > 80]) / len(cpu_usage)

        if max_cpu > 95:
            bottlenecks.append({
                'type': 'cpu_critical',
                'severity': 'critical',
                'description': f'CPU使用率达到峰值 {max_cpu:.1f}%',
                'impact': '系统响应严重延迟，可能出现服务不可用'
            })
            recommendations.append('立即检查CPU密集型进程，考虑扩容或优化算法')
            score_penalty += 30
        elif avg_cpu > 70:
            bottlenecks.append({
                'type': 'cpu_high_average',
                'severity': 'high',
                'description': f'CPU平均使用率过高 {avg_cpu:.1f}%',
                'impact': '系统整体性能下降，响应时间增加'
            })
            recommendations.append('优化CPU密集型任务，考虑负载均衡或垂直扩容')
            score_penalty += 20

        if high_cpu_ratio > 0.3:
            bottlenecks.append({
                'type': 'cpu_sustained_high',
                'severity': 'medium',
                'description': f'{high_cpu_ratio*100:.1f}%的时间CPU使用率超过80%',
                'impact': '持续高CPU使用率影响系统稳定性'
            })
            recommendations.append('分析高CPU使用时段的进程活动，优化或调度任务')
            score_penalty += 15

        # 分析系统负载
        avg_load = np.mean(load_avg)
        if avg_load > cpu_count * 2:
            bottlenecks.append({
                'type': 'load_critical',
                'severity': 'critical',
                'description': f'系统负载过高 {avg_load:.2f} (CPU核心数: {cpu_count})',
                'impact': '系统严重过载，任务排队等待执行'
            })
            recommendations.append('立即减少并发任务数量或增加CPU资源')
            score_penalty += 25
        elif avg_load > cpu_count:
            bottlenecks.append({
                'type': 'load_high',
                'severity': 'medium',
                'description': f'系统负载较高 {avg_load:.2f} (CPU核心数: {cpu_count})',
                'impact': '系统接近满负荷运行，性能可能下降'
            })
            recommendations.append('监控系统负载趋势，考虑优化或扩容')
            score_penalty += 10

        return {
            'bottlenecks': bottlenecks,
            'recommendations': recommendations,
            'score_penalty': score_penalty
        }

    def _analyze_memory_data(self, memory_data):
        """分析内存数据"""
        bottlenecks = []
        recommendations = []
        score_penalty = 0

        memory_usage = [item['memory_percent'] for item in memory_data]
        swap_usage = [item['swap_percent'] for item in memory_data]

        avg_memory = np.mean(memory_usage)
        max_memory = np.max(memory_usage)
        avg_swap = np.mean(swap_usage)
        max_swap = np.max(swap_usage)

        # 分析内存使用率
        if max_memory > 95:
            bottlenecks.append({
                'type': 'memory_critical',
                'severity': 'critical',
                'description': f'内存使用率达到峰值 {max_memory:.1f}%',
                'impact': '系统可能出现OOM，服务不稳定'
            })
            recommendations.append('立即释放内存或增加物理内存')
            score_penalty += 30
        elif avg_memory > 80:
            bottlenecks.append({
                'type': 'memory_high',
                'severity': 'high',
                'description': f'内存平均使用率过高 {avg_memory:.1f}%',
                'impact': '内存压力大，可能影响性能'
            })
            recommendations.append('优化内存使用，检查内存泄漏，考虑增加内存')
            score_penalty += 20

        # 分析交换分区使用
        if max_swap > 50:
            bottlenecks.append({
                'type': 'swap_critical',
                'severity': 'critical',
                'description': f'交换分区使用率过高 {max_swap:.1f}%',
                'impact': '频繁的磁盘交换严重影响性能'
            })
            recommendations.append('立即增加物理内存或优化内存使用')
            score_penalty += 25
        elif avg_swap > 10:
            bottlenecks.append({
                'type': 'swap_high',
                'severity': 'medium',
                'description': f'交换分区平均使用率 {avg_swap:.1f}%',
                'impact': '存在内存压力，性能可能受影响'
            })
            recommendations.append('监控内存使用趋势，考虑内存优化')
            score_penalty += 10

        return {
            'bottlenecks': bottlenecks,
            'recommendations': recommendations,
            'score_penalty': score_penalty
        }

    def _prepare_charts_data(self, data):
        """准备图表数据"""
        cpu_data = data.get('cpu_data', [])
        memory_data = data.get('memory_data', [])

        charts_data = {
            'cpu_timeline': [],
            'memory_timeline': [],
            'load_timeline': [],
            'cpu_cores': []
        }

        # CPU时间线数据
        for item in cpu_data:
            timestamp = item['timestamp']
            charts_data['cpu_timeline'].append({
                'time': timestamp,
                'cpu_percent': item['cpu_percent_total'],
                'load_1min': item['load_average_1min']
            })

        # 内存时间线数据
        for item in memory_data:
            timestamp = item['timestamp']
            charts_data['memory_timeline'].append({
                'time': timestamp,
                'memory_percent': item['memory_percent'],
                'swap_percent': item['swap_percent'],
                'memory_used_gb': item['memory_used_gb']
            })

        # CPU核心数据（取最后一个样本的数据）
        if cpu_data:
            last_cpu = cpu_data[-1]
            for i, usage in enumerate(last_cpu['cpu_percent_per_core']):
                charts_data['cpu_cores'].append({
                    'core': f'Core {i}',
                    'usage': usage
                })

        return charts_data

# 创建性能分析器实例
analyzer = PerformanceAnalyzer()

# 服务器监控系统
class ServerMonitor:
    def __init__(self):
        self.servers = {}  # 存储服务器配置
        self.connections = {}  # SSH连接池
        self.monitoring_threads = {}  # 监控线程
        self.metrics_data = {}  # 监控数据存储
        self.historical_cache = {}  # 历史数据缓存
        self.last_update_time = {}  # 上次更新时间
        self.persistence = HistoricalDataPersistence()  # 历史数据持久化

        # 🚀 新增：性能优化缓存
        self.performance_cache = {}  # API响应缓存
        self.cache_ttl = 30  # 缓存30秒
        self.max_data_points = 200  # 最多返回200个数据点
        self.background_update_interval = 10  # 后台更新间隔10秒
        self.background_thread = None  # 后台更新线程
        self.is_running = False  # 后台线程运行状态

        self.init_storage()
        self.start_background_update()  # 启动后台更新

    def init_storage(self):
        """初始化数据存储"""
        # 这里简化为内存存储，实际项目中应该使用数据库
        self.servers = {}  # 空的服务器列表，需要用户手动添加
        self.metrics_data = {}

    def start_background_update(self):
        """🚀 启动后台数据更新线程"""
        if self.background_thread and self.background_thread.is_alive():
            return

        self.is_running = True
        self.background_thread = threading.Thread(target=self._background_update_worker, daemon=True)
        self.background_thread.start()
        print("🔄 后台数据更新线程已启动")

    def stop_background_update(self):
        """停止后台数据更新线程"""
        self.is_running = False
        if self.background_thread:
            self.background_thread.join(timeout=5)
        print("🛑 后台数据更新线程已停止")

    def _background_update_worker(self):
        """后台数据更新工作线程"""
        import time

        while self.is_running:
            try:
                current_time = datetime.now()

                # 为每个服务器更新缓存数据
                for server_id in list(self.servers.keys()):
                    try:
                        self._update_server_cache(server_id, current_time)
                    except Exception as e:
                        print(f"❌ 更新服务器 {server_id} 缓存失败: {e}")

                # 清理过期缓存
                self._cleanup_expired_cache(current_time)

                # 等待下次更新
                time.sleep(self.background_update_interval)

            except Exception as e:
                print(f"❌ 后台更新线程错误: {e}")
                time.sleep(5)

    def _update_server_cache(self, server_id, current_time):
        """更新单个服务器的缓存数据"""
        if server_id not in self.servers:
            return

        server_config = self.servers[server_id]

        # 获取实时监控数据
        real_metrics = self.get_real_server_metrics(server_config)
        if not real_metrics:
            return

        # 更新缓存中的实时数据
        cache_key = f"{server_id}_realtime"
        self.performance_cache[cache_key] = {
            'data': real_metrics,
            'timestamp': current_time,
            'ttl': self.cache_ttl
        }

        # 更新历史数据缓存
        for time_range in ['1h', '6h', '24h']:
            cache_key = f"{server_id}_metrics_{time_range}"

            # 检查是否需要更新
            if (cache_key not in self.performance_cache or
                (current_time - self.performance_cache[cache_key]['timestamp']).total_seconds() > self.cache_ttl):

                # 生成历史数据
                historical_data = self._get_cached_historical_data(server_id, time_range, real_metrics)

                self.performance_cache[cache_key] = {
                    'data': historical_data,
                    'timestamp': current_time,
                    'ttl': self.cache_ttl
                }

                print(f"🔄 已更新缓存: {cache_key}")

    def _cleanup_expired_cache(self, current_time):
        """清理过期的缓存数据"""
        expired_keys = []

        for cache_key, cache_data in self.performance_cache.items():
            if (current_time - cache_data['timestamp']).total_seconds() > cache_data['ttl']:
                expired_keys.append(cache_key)

        for key in expired_keys:
            del self.performance_cache[key]

        if expired_keys:
            print(f"🧹 清理了 {len(expired_keys)} 个过期缓存")

    def _get_cached_historical_data(self, server_id, time_range, current_metrics):
        """获取缓存的历史数据（限制数据点数量）"""
        # 优先从文件加载历史数据
        historical_data = self.persistence.load_historical_data(server_id)

        if historical_data and historical_data.get('timestamps'):
            # 限制数据点数量
            timestamps = historical_data['timestamps']
            if len(timestamps) > self.max_data_points:
                # 均匀采样，保留最重要的数据点
                step = len(timestamps) // self.max_data_points
                indices = list(range(0, len(timestamps), step))
                if len(indices) > self.max_data_points:
                    indices = indices[:self.max_data_points]

                # 确保包含最新的数据点
                if indices[-1] != len(timestamps) - 1:
                    indices[-1] = len(timestamps) - 1

                # 重新构建数据
                sampled_data = {
                    'timestamps': [timestamps[i] for i in indices],
                    'cpu_data': [historical_data.get('cpu_data', [])[i] if i < len(historical_data.get('cpu_data', [])) else 0 for i in indices],
                    'memory_data': [historical_data.get('memory_data', [])[i] if i < len(historical_data.get('memory_data', [])) else 0 for i in indices],
                    'disk_read_data': [historical_data.get('disk_read_data', [])[i] if i < len(historical_data.get('disk_read_data', [])) else 0 for i in indices],
                    'disk_write_data': [historical_data.get('disk_write_data', [])[i] if i < len(historical_data.get('disk_write_data', [])) else 0 for i in indices],
                    'network_sent': [historical_data.get('network_sent', [])[i] if i < len(historical_data.get('network_sent', [])) else 0 for i in indices],
                    'network_recv': [historical_data.get('network_recv', [])[i] if i < len(historical_data.get('network_recv', [])) else 0 for i in indices]
                }

                print(f"📊 数据采样: {len(timestamps)} -> {len(sampled_data['timestamps'])} 个数据点")
                return sampled_data
            else:
                return historical_data
        else:
            # 如果没有历史数据，生成新的（但限制数量）
            return self._generate_historical_data(time_range, current_metrics, limit_points=True)

    def add_server(self, server_config):
        """添加服务器配置"""
        server_id = server_config.get('id') or f"server_{len(self.servers) + 1}"
        server_config['id'] = server_id
        self.servers[server_id] = server_config
        return server_id

    def update_server(self, server_id, server_config):
        """更新服务器配置"""
        if server_id in self.servers:
            server_config['id'] = server_id
            self.servers[server_id] = server_config
            return True
        return False

    def delete_server(self, server_id):
        """删除服务器"""
        if server_id in self.servers:
            # 停止监控
            self.stop_monitoring(server_id)
            # 删除配置
            del self.servers[server_id]
            # 清理数据
            if server_id in self.metrics_data:
                del self.metrics_data[server_id]
            return True
        return False

    def test_connection(self, server_config):
        """测试服务器连接"""
        print(f"🔍 开始测试连接: {server_config.get('host')}:{server_config.get('port')}")
        print(f"   用户名: {server_config.get('username')}")
        print(f"   认证方式: {server_config.get('auth_type', 'password')}")

        try:
            host = server_config['host']
            port = server_config['port']
            username = server_config['username']
            auth_type = server_config.get('auth_type', 'password')

            # 验证必要参数
            if not host or not port or not username:
                return False, "缺少必要的连接参数（主机、端口、用户名）"

            # 检查paramiko是否可用
            if not PARAMIKO_AVAILABLE:
                return False, "SSH连接功能不可用，请安装paramiko库: pip install paramiko"

            print(f"📡 正在连接到 {host}:{port}...")

            # 创建SSH客户端
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # 根据认证方式连接
            if auth_type == 'password':
                password = server_config.get('password')
                if not password:
                    return False, "密码认证需要提供密码"

                print(f"🔐 使用密码认证连接...")
                ssh.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    password=password,
                    timeout=30,  # 增加到30秒
                    allow_agent=False,  # 禁用SSH代理
                    look_for_keys=False  # 禁用自动查找密钥
                )
            elif auth_type == 'key':
                private_key_path = server_config.get('private_key_path')
                key_password = server_config.get('key_password')

                if not private_key_path:
                    return False, "密钥认证需要提供私钥文件路径"

                print(f"🔑 使用密钥认证连接: {private_key_path}")

                # 尝试加载私钥
                try:
                    if private_key_path.endswith('.pem') or 'rsa' in private_key_path.lower():
                        private_key = paramiko.RSAKey.from_private_key_file(private_key_path, password=key_password)
                    else:
                        # 尝试自动检测密钥类型
                        private_key = paramiko.RSAKey.from_private_key_file(private_key_path, password=key_password)
                except:
                    try:
                        private_key = paramiko.Ed25519Key.from_private_key_file(private_key_path, password=key_password)
                    except Exception as key_error:
                        print(f"❌ 密钥加载失败: {key_error}")
                        return False, f"无法加载私钥文件: {private_key_path} - {str(key_error)}"

                ssh.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    pkey=private_key,
                    timeout=30,  # 增加到30秒
                    allow_agent=False,
                    look_for_keys=False
                )
            else:
                return False, f"不支持的认证方式: {auth_type}"

            print(f"✅ SSH连接建立成功")

            # 测试执行简单命令
            print(f"🧪 测试命令执行...")
            stdin, stdout, stderr = ssh.exec_command('echo "connection_test_$(date +%s)"', timeout=5)

            # 读取输出和错误
            result = stdout.read().decode().strip()
            error_output = stderr.read().decode().strip()

            print(f"📤 命令输出: '{result}'")
            if error_output:
                print(f"⚠️  错误输出: '{error_output}'")

            # 验证命令执行结果
            if result and "connection_test_" in result:
                print(f"result的结果是: {result}")
                print(f"✅ 命令执行成功")

                # 额外测试：获取系统信息验证权限
                stdin2, stdout2, stderr2 = ssh.exec_command('whoami && uname -s', timeout=5)
                system_info = stdout2.read().decode().strip()
                print(f"🖥️  系统信息: {system_info}")

                ssh.close()
                return True, f"SSH连接测试成功 - 用户: {system_info.split()[0] if system_info else username}"
            else:
                ssh.close()
                return False, f"SSH连接成功但命令执行失败 - 输出: '{result}'"

        except paramiko.AuthenticationException as e:
            print(f"❌ 认证失败: {e}")
            return False, f"SSH认证失败，请检查用户名和密码/密钥 - {str(e)}"
        except paramiko.SSHException as e:
            print(f"❌ SSH错误: {e}")
            return False, f"SSH连接错误: {str(e)}"
        except socket.timeout as e:
            print(f"❌ 连接超时: {e}")
            return False, f"连接超时，请检查主机地址和端口 - {str(e)}"
        except socket.gaierror as e:
            print(f"❌ 域名解析失败: {e}")
            return False, f"无法解析主机名，请检查主机地址 - {str(e)}"
        except ConnectionRefusedError as e:
            print(f"❌ 连接被拒绝: {e}")
            return False, f"连接被拒绝，请检查SSH服务是否运行和端口是否正确 - {str(e)}"
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            return False, f"连接失败: {str(e)}"

    def get_real_server_metrics(self, server_config):
        """获取真实服务器监控数据"""
        if not PARAMIKO_AVAILABLE:
            return None

        try:
            host = server_config['host']
            port = server_config['port']
            username = server_config['username']
            auth_type = server_config.get('auth_type', 'password')

            # 本地服务器使用psutil
            if host in ['localhost', '127.0.0.1'] or auth_type == 'local':
                return self._get_local_metrics()

            # 远程服务器使用SSH
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # 连接服务器
            if auth_type == 'password':
                ssh.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    password=server_config.get('password'),
                    timeout=30  # 增加到30秒
                )
            else:  # key认证
                private_key_path = server_config.get('private_key_path')
                key_password = server_config.get('key_password')

                try:
                    private_key = paramiko.RSAKey.from_private_key_file(private_key_path, password=key_password)
                except:
                    private_key = paramiko.Ed25519Key.from_private_key_file(private_key_path, password=key_password)

                ssh.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    pkey=private_key,
                    timeout=30  # 增加到30秒
                )

            # 获取系统信息
            metrics = {}

            # CPU信息
            stdin, stdout, stderr = ssh.exec_command("top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1")
            cpu_usage = stdout.read().decode().strip()
            try:
                metrics['cpu'] = float(cpu_usage)
            except:
                metrics['cpu'] = 0.0

            # 负载平均值
            stdin, stdout, stderr = ssh.exec_command("uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ','")
            load_avg = stdout.read().decode().strip()
            try:
                metrics['load_avg'] = float(load_avg)
            except:
                metrics['load_avg'] = 0.0

            # 内存信息
            stdin, stdout, stderr = ssh.exec_command("free | grep Mem | awk '{printf \"%.1f %.1f\", $3/$2*100, $2/1024/1024}'")
            memory_info = stdout.read().decode().strip().split()
            try:
                metrics['memory_percent'] = float(memory_info[0])
                metrics['memory_total'] = float(memory_info[1])
                metrics['memory_used'] = metrics['memory_total'] * metrics['memory_percent'] / 100
            except:
                metrics['memory_percent'] = 0.0
                metrics['memory_total'] = 0.0
                metrics['memory_used'] = 0.0

            # 磁盘信息
            stdin, stdout, stderr = ssh.exec_command("df -h / | tail -1 | awk '{print $5}' | tr -d '%'")
            disk_usage = stdout.read().decode().strip()
            try:
                metrics['disk_percent'] = float(disk_usage)
            except:
                metrics['disk_percent'] = 0.0

            stdin, stdout, stderr = ssh.exec_command("df -BG / | tail -1 | awk '{print $4}' | tr -d 'G'")
            disk_free = stdout.read().decode().strip()
            try:
                metrics['disk_free'] = float(disk_free)
            except:
                metrics['disk_free'] = 0.0

            # 磁盘IO信息 - 使用iostat获取读写速度
            stdin, stdout, stderr = ssh.exec_command("iostat -d 1 2 | tail -n +4 | grep -E '(vda|sda|nvme)' | tail -1 | awk '{print $3, $4}'")
            disk_io_info = stdout.read().decode().strip().split()
            try:
                if len(disk_io_info) >= 2:
                    # iostat输出的是kB/s，转换为字节/s
                    metrics['disk_read'] = float(disk_io_info[0]) * 1024  # kB/s -> B/s
                    metrics['disk_write'] = float(disk_io_info[1]) * 1024  # kB/s -> B/s
                else:
                    metrics['disk_read'] = 0.0
                    metrics['disk_write'] = 0.0
            except:
                metrics['disk_read'] = 0.0
                metrics['disk_write'] = 0.0

            # 网络信息（简化版）
            stdin, stdout, stderr = ssh.exec_command("cat /proc/net/dev | grep -E '(eth0|ens|enp)' | head -1 | awk '{print $2, $10}'")
            network_info = stdout.read().decode().strip().split()
            try:
                metrics['network_recv'] = int(network_info[0]) if len(network_info) > 0 else 0
                metrics['network_sent'] = int(network_info[1]) if len(network_info) > 1 else 0
            except:
                metrics['network_recv'] = 0
                metrics['network_sent'] = 0

            ssh.close()
            return metrics

        except Exception as e:
            print(f"获取服务器监控数据失败: {e}")
            return None

    def _get_local_metrics(self):
        """获取本地服务器监控数据"""
        try:
            import psutil

            metrics = {}

            # CPU信息
            metrics['cpu'] = psutil.cpu_percent(interval=1)
            metrics['load_avg'] = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0

            # 内存信息
            memory = psutil.virtual_memory()
            metrics['memory_percent'] = memory.percent
            metrics['memory_total'] = memory.total / (1024**3)  # GB
            metrics['memory_used'] = memory.used / (1024**3)    # GB

            # 磁盘信息
            disk = psutil.disk_usage('/')
            metrics['disk_percent'] = disk.percent
            metrics['disk_free'] = disk.free / (1024**3)  # GB

            # 磁盘IO信息
            disk_io = psutil.disk_io_counters()
            if disk_io:
                # 获取当前时间戳，计算IO速率
                current_time = time.time()
                if hasattr(self, '_last_disk_io') and hasattr(self, '_last_disk_time'):
                    time_diff = current_time - self._last_disk_time
                    if time_diff > 0:
                        read_diff = disk_io.read_bytes - self._last_disk_io.read_bytes
                        write_diff = disk_io.write_bytes - self._last_disk_io.write_bytes
                        metrics['disk_read'] = read_diff / time_diff  # bytes/s
                        metrics['disk_write'] = write_diff / time_diff  # bytes/s
                    else:
                        metrics['disk_read'] = 0.0
                        metrics['disk_write'] = 0.0
                else:
                    metrics['disk_read'] = 0.0
                    metrics['disk_write'] = 0.0

                # 保存当前值用于下次计算
                self._last_disk_io = disk_io
                self._last_disk_time = current_time
            else:
                metrics['disk_read'] = 0.0
                metrics['disk_write'] = 0.0

            # 网络信息
            network = psutil.net_io_counters()
            metrics['network_recv'] = network.bytes_recv
            metrics['network_sent'] = network.bytes_sent

            return metrics

        except ImportError:
            print("psutil库未安装，无法获取本地监控数据")
            return None
        except Exception as e:
            print(f"获取本地监控数据失败: {e}")
            return None

    def get_server_metrics(self, server_id, time_range='1h'):
        """🚀 获取服务器监控数据（使用缓存优化）"""
        if server_id not in self.servers:
            return None

        current_time = datetime.now()
        cache_key = f"{server_id}_metrics_{time_range}"

        print(f"🔍 查找缓存: {cache_key}")
        print(f"📦 当前缓存键: {list(self.performance_cache.keys())}")

        # 🔥 优先从缓存获取数据
        if cache_key in self.performance_cache:
            cache_data = self.performance_cache[cache_key]
            cache_age = (current_time - cache_data['timestamp']).total_seconds()

            if cache_age < self.cache_ttl:
                print(f"⚡ 从缓存获取数据: {server_id} ({cache_age:.1f}s前)")

                # 获取实时数据
                realtime_cache_key = f"{server_id}_realtime"
                current_metrics = None
                if realtime_cache_key in self.performance_cache:
                    current_metrics = self.performance_cache[realtime_cache_key]['data']

                if not current_metrics:
                    # 如果缓存中没有实时数据，快速获取
                    server_config = self.servers[server_id]
                    current_metrics = self.get_real_server_metrics(server_config)

                if not current_metrics:
                    return {
                        'error': '无法连接到服务器或获取监控数据',
                        'suggestion': '请检查服务器连接状态和配置'
                    }

                # 获取进程数据（也可以缓存）
                processes = self._get_real_processes(self.servers[server_id])

                return {
                    'current': current_metrics,
                    'historical': cache_data['data'],
                    'processes': processes,
                    'cache_info': {
                        'cache_hit': True,
                        'cache_age': f"{cache_age:.1f}s",
                        'last_update': current_time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                }

        # 🐌 缓存未命中，获取新数据（这种情况应该很少发生，因为后台线程在更新）
        print(f"🔄 缓存未命中，获取新数据: {server_id}")

        server_config = self.servers[server_id]
        real_metrics = self.get_real_server_metrics(server_config)

        if not real_metrics:
            return {
                'error': '无法连接到服务器或获取监控数据',
                'suggestion': '请检查服务器连接状态和配置'
            }

        # 获取历史数据（限制数据点）
        historical_data = self._get_cached_historical_data(server_id, time_range, real_metrics)

        # 更新缓存
        self.performance_cache[cache_key] = {
            'data': historical_data,
            'timestamp': current_time,
            'ttl': self.cache_ttl
        }

        # 获取进程数据
        processes = self._get_real_processes(server_config)

        return {
            'current': real_metrics,
            'historical': historical_data,
            'processes': processes,
            'cache_info': {
                'cache_hit': False,
                'last_update': current_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        }



    def _generate_historical_data(self, time_range, current_metrics, limit_points=False):
        """生成历史数据（带缓存机制和数据点限制）"""
        current_time = datetime.now()
        server_key = f"default_{time_range}"  # 简化的服务器标识

        # 解析时间范围
        if time_range == '5m':
            duration_minutes = 5
            interval_seconds = 10
        elif time_range == '15m':
            duration_minutes = 15
            interval_seconds = 30
        elif time_range == '1h':
            duration_minutes = 60
            interval_seconds = 60
        elif time_range == '6h':
            duration_minutes = 360
            interval_seconds = 360
        elif time_range == '24h':
            duration_minutes = 1440
            interval_seconds = 1440
        else:
            duration_minutes = 60
            interval_seconds = 60

        points = duration_minutes * 60 // interval_seconds

        # 🚀 限制数据点数量
        if limit_points and points > self.max_data_points:
            points = self.max_data_points
            interval_seconds = (duration_minutes * 60) // points
            print(f"📊 限制数据点: {duration_minutes * 60 // interval_seconds} -> {points} 个点")

        # 检查是否需要更新缓存
        if (server_key not in self.historical_cache or
            server_key not in self.last_update_time or
            (current_time - self.last_update_time[server_key]).total_seconds() > interval_seconds):

            print(f"🔄 更新历史数据缓存: {server_key}")

            # 获取或初始化缓存
            if server_key not in self.historical_cache:
                self.historical_cache[server_key] = {
                    'data_points': [],
                    'max_points': points
                }

            cache = self.historical_cache[server_key]

            # 添加新的数据点（当前实时数据）
            new_data_point = {
                'timestamp': current_time,
                'cpu': current_metrics.get('cpu', 0),
                'memory': current_metrics.get('memory_percent', 0),
                'disk_read': current_metrics.get('disk_read', 0),
                'disk_write': current_metrics.get('disk_write', 0),
                'network_sent': current_metrics.get('network_sent', 0),
                'network_recv': current_metrics.get('network_recv', 0)
            }

            cache['data_points'].append(new_data_point)

            # 保持数据点数量不超过限制
            if len(cache['data_points']) > points:
                cache['data_points'] = cache['data_points'][-points:]

            # 不再填充模拟数据，只使用真实的监控数据
            # 如果数据点不够，就显示现有的真实数据点
            print(f"📊 当前真实数据点数量: {len(cache['data_points'])}, 请求数量: {points}")

            self.last_update_time[server_key] = current_time

        # 从缓存构建返回数据
        cache = self.historical_cache[server_key]
        timestamps = []
        cpu_data = []
        memory_data = []
        disk_read_data = []
        disk_write_data = []
        network_sent_data = []
        network_recv_data = []

        for point in cache['data_points'][-points:]:  # 取最新的points个数据点
            timestamps.append(point['timestamp'].strftime('%H:%M:%S'))
            cpu_data.append(round(point['cpu'], 1))
            memory_data.append(round(point['memory'], 1))
            disk_read_data.append(int(point['disk_read']))
            disk_write_data.append(int(point['disk_write']))
            network_sent_data.append(int(point['network_sent']))
            network_recv_data.append(int(point['network_recv']))

        print(f"📊 返回历史数据: {len(cpu_data)}个数据点, CPU范围: {min(cpu_data):.1f}-{max(cpu_data):.1f}%")

        result = {
            'timestamps': timestamps,
            'cpu': cpu_data,
            'memory': memory_data,
            'disk_read': disk_read_data,
            'disk_write': disk_write_data,
            'network_sent': network_sent_data,
            'network_recv': network_recv_data
        }

        # 保存历史数据到文件
        self.persistence.save_historical_data('default', result)

        return result



    def _get_real_processes(self, server_config):
        """获取真实进程数据"""
        if not PARAMIKO_AVAILABLE:
            return []

        try:
            host = server_config['host']
            port = server_config['port']
            username = server_config['username']
            auth_type = server_config.get('auth_type', 'password')

            # 本地服务器使用psutil
            if host in ['localhost', '127.0.0.1']:
                return self._get_local_processes()

            # 远程服务器使用SSH
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # 连接服务器
            if auth_type == 'password':
                ssh.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    password=server_config.get('password'),
                    timeout=30  # 增加到30秒
                )
            else:  # key认证
                private_key_path = server_config.get('private_key_path')
                key_password = server_config.get('key_password')

                try:
                    private_key = paramiko.RSAKey.from_private_key_file(private_key_path, password=key_password)
                except:
                    private_key = paramiko.Ed25519Key.from_private_key_file(private_key_path, password=key_password)

                ssh.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    pkey=private_key,
                    timeout=30  # 增加到30秒
                )

            # 获取进程信息 - 按CPU使用率排序的前10个进程
            cmd = "ps aux --sort=-%cpu | head -11 | tail -10 | awk '{print $2,$11,$3,$4,$8}'"
            print(f"🔍 执行进程查询命令: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            process_lines = stdout.read().decode().strip().split('\n')
            error_output = stderr.read().decode().strip()

            print(f"📊 进程命令输出行数: {len(process_lines)}")
            print(f"📊 进程原始输出: {process_lines}")
            if error_output:
                print(f"⚠️ 进程命令错误输出: {error_output}")

            processes = []
            for i, line in enumerate(process_lines):
                if line.strip():
                    parts = line.strip().split(None, 4)
                    print(f"📋 解析第{i+1}行: '{line}' -> 分割为 {len(parts)} 部分: {parts}")
                    if len(parts) >= 5:
                        try:
                            process_data = {
                                'pid': int(parts[0]),
                                'name': parts[1].split('/')[-1][:20],  # 只取程序名，限制长度
                                'cpu_percent': float(parts[2]),
                                'memory_percent': float(parts[3]),
                                'memory_mb': round(float(parts[3]) * 8 * 1024 / 100, 1),  # 估算内存MB
                                'status': parts[4] if len(parts) > 4 else 'running',
                                'create_time': 'N/A'
                            }
                            processes.append(process_data)
                            print(f"✅ 成功解析进程: {process_data}")
                        except (ValueError, IndexError) as e:
                            print(f"❌ 解析进程失败: {e}, 行内容: '{line}'")
                            continue

            ssh.close()
            return processes[:10]  # 返回前10个进程

        except Exception as e:
            print(f"获取进程数据失败: {e}")
            return []

    def _get_local_processes(self):
        """获取本地进程数据"""
        print("🔍 开始获取本地进程数据...")
        try:
            import psutil

            processes = []
            all_processes = list(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info', 'status', 'create_time']))
            print(f"📊 系统总进程数: {len(all_processes)}")

            for proc in all_processes:
                try:
                    pinfo = proc.info
                    # 移除CPU使用率>0的限制，获取所有进程
                    if pinfo['cpu_percent'] is not None:
                        process_data = {
                            'pid': pinfo['pid'],
                            'name': pinfo['name'][:20] if pinfo['name'] else 'Unknown',
                            'cpu_percent': round(pinfo['cpu_percent'], 1),
                            'memory_percent': round(pinfo['memory_percent'], 1) if pinfo['memory_percent'] else 0,
                            'memory_mb': round(pinfo['memory_info'].rss / 1024 / 1024, 1) if pinfo['memory_info'] else 0,
                            'status': pinfo['status'] if pinfo['status'] else 'unknown',
                            'create_time': datetime.fromtimestamp(pinfo['create_time']).strftime('%Y-%m-%d %H:%M:%S') if pinfo['create_time'] else 'N/A'
                        }
                        processes.append(process_data)
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    print(f"⚠️ 无法访问进程: {e}")
                    continue

            print(f"📊 成功获取进程数: {len(processes)}")

            # 按CPU使用率排序，返回前10个
            sorted_processes = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:10]
            print(f"📊 返回前10个进程:")
            for i, proc in enumerate(sorted_processes):
                print(f"  {i+1}. PID:{proc['pid']} {proc['name']} CPU:{proc['cpu_percent']}% MEM:{proc['memory_percent']}%")

            return sorted_processes

        except ImportError:
            print("❌ psutil库未安装，无法获取本地进程数据")
            return []
        except Exception as e:
            print(f"❌ 获取本地进程数据失败: {e}")
            return []

# 创建服务器监控实例
server_monitor = ServerMonitor()

# 不添加任何默认服务器配置，只使用用户真实添加的服务器

@app.route('/api/analyze-monitoring-data', methods=['POST'])
def analyze_monitoring_data_api():
    """分析监控数据API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '没有提供数据'})

        # 分析数据
        analysis_result = analyzer.analyze_monitoring_data(data)

        return jsonify({
            'success': True,
            'analysis': analysis_result
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'分析数据时出错: {str(e)}'})

@app.route('/api/upload-monitoring-data', methods=['POST'])
def upload_monitoring_data():
    """上传监控数据文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有上传文件'})

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'})

        if not file.filename.endswith('.json'):
            return jsonify({'success': False, 'error': '只支持JSON格式文件'})

        # 读取文件内容
        file_content = file.read().decode('utf-8')
        monitoring_data = json.loads(file_content)

        # 分析数据
        analysis_result = analyzer.analyze_monitoring_data(monitoring_data)

        # 保存分析结果（可选）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_filename = f"analysis_result_{timestamp}.json"

        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'filename': file.filename
        })

    except json.JSONDecodeError:
        return jsonify({'success': False, 'error': 'JSON文件格式错误'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'处理文件时出错: {str(e)}'})

@app.route('/api/analyze-monitoring-data', methods=['POST'])
def analyze_monitoring_data():
    """分析监控数据（通过JSON数据）"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '没有提供数据'})

        # 分析数据
        analysis_result = analyzer.analyze_monitoring_data(data)

        return jsonify({
            'success': True,
            'analysis': analysis_result
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'分析数据时出错: {str(e)}'})

# 服务器监控API路由
@app.route('/api/servers', methods=['GET'])
def get_servers():
    """获取服务器列表"""
    try:
        servers_list = list(server_monitor.servers.values())
        return jsonify({
            'success': True,
            'data': servers_list
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/servers', methods=['POST'])
def add_server():
    """添加服务器"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '没有提供数据'})

        server_id = server_monitor.add_server(data)
        return jsonify({
            'success': True,
            'data': server_monitor.servers[server_id]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/servers/<server_id>', methods=['PUT'])
def update_server(server_id):
    """更新服务器配置"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '没有提供数据'})

        success = server_monitor.update_server(server_id, data)
        if success:
            return jsonify({
                'success': True,
                'data': server_monitor.servers[server_id]
            })
        else:
            return jsonify({'success': False, 'error': '服务器不存在'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/servers/<server_id>', methods=['DELETE'])
def delete_server(server_id):
    """删除服务器"""
    try:
        success = server_monitor.delete_server(server_id)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': '服务器不存在'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/servers/test', methods=['POST'])
@app.route('/api/servers/<server_id>/test', methods=['POST'])
def test_server_connection(server_id=None):
    """测试服务器连接"""
    try:
        if server_id:
            # 测试已配置的服务器
            if server_id not in server_monitor.servers:
                return jsonify({'success': False, 'error': '服务器不存在'})
            server_config = server_monitor.servers[server_id]
        else:
            # 测试新的服务器配置
            server_config = request.get_json()
            if not server_config:
                return jsonify({'success': False, 'error': '没有提供服务器配置'})

        success, message = server_monitor.test_connection(server_config)
        return jsonify({
            'success': success,
            'message': message,
            'error': message if not success else None
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/servers/<server_id>/metrics', methods=['GET'])
def get_server_metrics_api(server_id):
    """获取服务器监控数据API"""
    try:
        if server_id not in server_monitor.servers:
            return jsonify({'success': False, 'error': '服务器不存在'})

        time_range = request.args.get('timeRange', '1h')
        print(f"🔍 API请求: {server_id}, 时间范围: {time_range}")

        metrics_data = server_monitor.get_server_metrics(server_id, time_range)

        if metrics_data and 'error' not in metrics_data:
            return jsonify({
                'success': True,
                'data': metrics_data
            })
        elif metrics_data and 'error' in metrics_data:
            return jsonify({
                'success': False,
                'error': metrics_data['error'],
                'suggestion': metrics_data.get('suggestion', '')
            })
        else:
            return jsonify({'success': False, 'error': '无法连接到服务器获取监控数据'})
    except Exception as e:
        print(f"❌ API错误: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/servers/<server_id>/metrics/realtime', methods=['GET'])
def get_server_realtime_metrics(server_id):
    """获取服务器实时数据"""
    try:
        if server_id not in server_monitor.servers:
            return jsonify({'success': False, 'error': '服务器不存在'})

        # 获取最新的监控数据
        metrics_data = server_monitor.get_server_metrics(server_id, '5m')

        if metrics_data:
            return jsonify({
                'success': True,
                'data': metrics_data['current'],
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'success': False, 'error': '获取实时数据失败'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/servers/<server_id>/processes', methods=['GET'])
def get_server_processes(server_id):
    """获取服务器进程列表"""
    try:
        if server_id not in server_monitor.servers:
            return jsonify({'success': False, 'error': '服务器不存在'})

        limit = request.args.get('limit', 10, type=int)
        metrics_data = server_monitor.get_server_metrics(server_id, '5m')

        if metrics_data and 'processes' in metrics_data:
            processes = metrics_data['processes'][:limit]
            return jsonify({
                'success': True,
                'data': processes
            })
        else:
            return jsonify({'success': False, 'error': '获取进程数据失败'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/performance-monitor')
def performance_monitor():
    """性能监控页面"""
    html_template = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>性能监控分析</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .upload-section {
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }

        .upload-area {
            border: 3px dashed #007bff;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            background: white;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .upload-area:hover {
            border-color: #0056b3;
            background: #f8f9ff;
        }

        .upload-area.dragover {
            border-color: #28a745;
            background: #f8fff8;
        }

        .upload-icon {
            font-size: 3em;
            color: #007bff;
            margin-bottom: 20px;
        }

        .btn {
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s ease;
            margin: 10px;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,123,255,0.3);
        }

        .analysis-section {
            padding: 30px;
            display: none;
        }

        .system-info {
            background: #e3f2fd;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }

        .performance-score {
            text-align: center;
            margin-bottom: 30px;
        }

        .score-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2em;
            font-weight: bold;
            color: white;
        }

        .score-excellent { background: linear-gradient(135deg, #28a745, #20c997); }
        .score-good { background: linear-gradient(135deg, #ffc107, #fd7e14); }
        .score-poor { background: linear-gradient(135deg, #dc3545, #e83e8c); }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }

        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .chart-title {
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 20px;
            color: #2c3e50;
            text-align: center;
        }

        .bottlenecks-section {
            margin-top: 30px;
        }

        .bottleneck-item {
            background: white;
            border-left: 5px solid;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 0 10px 10px 0;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }

        .bottleneck-critical { border-left-color: #dc3545; }
        .bottleneck-high { border-left-color: #fd7e14; }
        .bottleneck-medium { border-left-color: #ffc107; }

        .bottleneck-title {
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 10px;
        }

        .bottleneck-description {
            color: #666;
            margin-bottom: 10px;
        }

        .bottleneck-impact {
            font-style: italic;
            color: #888;
        }

        .recommendations {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
        }

        .recommendations h3 {
            color: #155724;
            margin-bottom: 15px;
        }

        .recommendation-item {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 4px solid #28a745;
        }

        .loading {
            text-align: center;
            padding: 50px;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #007bff;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 性能监控分析平台</h1>
            <p>上传系统监控数据，获取AI驱动的性能瓶颈分析和优化建议</p>
        </div>

        <div class="upload-section">
            <div class="upload-area" id="uploadArea">
                <div class="upload-icon">📁</div>
                <h3>拖拽监控数据文件到此处</h3>
                <p>或者点击选择文件</p>
                <p style="color: #666; margin-top: 10px;">支持 JSON 格式的监控数据文件</p>
                <input type="file" id="fileInput" accept=".json" style="display: none;">
                <button class="btn" onclick="document.getElementById('fileInput').click()">选择文件</button>
            </div>
        </div>

        <div class="analysis-section" id="analysisSection">
            <!-- 分析结果将在这里显示 -->
        </div>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const analysisSection = document.getElementById('analysisSection');

        // 拖拽上传功能
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });

        function handleFile(file) {
            if (!file.name.endsWith('.json')) {
                showError('请选择JSON格式的监控数据文件');
                return;
            }

            showLoading();

            const formData = new FormData();
            formData.append('file', file);

            fetch('/api/upload-monitoring-data', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayAnalysis(data.analysis);
                } else {
                    showError(data.error);
                }
            })
            .catch(error => {
                showError('上传文件时发生错误: ' + error.message);
            });
        }

        function showLoading() {
            analysisSection.style.display = 'block';
            analysisSection.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <h3>正在分析监控数据...</h3>
                    <p>AI正在识别性能瓶颈和优化机会</p>
                </div>
            `;
        }

        function showError(message) {
            analysisSection.style.display = 'block';
            analysisSection.innerHTML = `
                <div class="error-message">
                    <strong>错误:</strong> ${message}
                </div>
            `;
        }

        function displayAnalysis(analysis) {
            const systemInfo = analysis.system_info;
            const score = analysis.performance_score;
            const bottlenecks = analysis.bottlenecks;
            const recommendations = analysis.recommendations;
            const chartsData = analysis.charts_data;

            let scoreClass = 'score-excellent';
            let scoreText = '优秀';
            if (score < 70) {
                scoreClass = 'score-poor';
                scoreText = '需要优化';
            } else if (score < 85) {
                scoreClass = 'score-good';
                scoreText = '良好';
            }

            analysisSection.innerHTML = `
                <div class="system-info">
                    <h2>📊 系统信息</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 15px;">
                        <div><strong>主机名:</strong> ${systemInfo.hostname}</div>
                        <div><strong>系统:</strong> ${systemInfo.system} ${systemInfo.release}</div>
                        <div><strong>CPU:</strong> ${systemInfo.cpu_model || 'Unknown'}</div>
                        <div><strong>CPU核心:</strong> ${systemInfo.cpu_count_logical}个逻辑核心</div>
                        <div><strong>总内存:</strong> ${systemInfo.total_memory_gb}GB</div>
                        <div><strong>监控时长:</strong> ${analysis.monitoring_summary.duration_seconds}秒</div>
                    </div>
                </div>

                <div class="performance-score">
                    <h2>🎯 性能评分</h2>
                    <div class="score-circle ${scoreClass}">
                        ${score}
                    </div>
                    <h3>${scoreText}</h3>
                </div>

                <div class="charts-grid">
                    <div class="chart-container">
                        <div class="chart-title">CPU使用率趋势</div>
                        <canvas id="cpuChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-title">内存使用率趋势</div>
                        <canvas id="memoryChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-title">系统负载趋势</div>
                        <canvas id="loadChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-title">CPU核心使用率</div>
                        <canvas id="coreChart"></canvas>
                    </div>
                </div>

                <div class="bottlenecks-section">
                    <h2>⚠️ 性能瓶颈分析</h2>
                    ${bottlenecks.length > 0 ?
                        bottlenecks.map(bottleneck => `
                            <div class="bottleneck-item bottleneck-${bottleneck.severity}">
                                <div class="bottleneck-title">${getBottleneckIcon(bottleneck.severity)} ${bottleneck.description}</div>
                                <div class="bottleneck-impact">影响: ${bottleneck.impact}</div>
                            </div>
                        `).join('') :
                        '<div style="text-align: center; padding: 40px; color: #28a745;"><h3>🎉 未发现明显的性能瓶颈</h3><p>系统运行状况良好</p></div>'
                    }
                </div>

                ${recommendations.length > 0 ? `
                    <div class="recommendations">
                        <h3>💡 优化建议</h3>
                        ${recommendations.map((rec, index) => `
                            <div class="recommendation-item">
                                ${index + 1}. ${rec}
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            `;

            // 绘制图表
            setTimeout(() => {
                drawCharts(chartsData);
            }, 100);
        }

        function getBottleneckIcon(severity) {
            switch(severity) {
                case 'critical': return '🔴';
                case 'high': return '🟠';
                case 'medium': return '🟡';
                default: return '🔵';
            }
        }

        function drawCharts(chartsData) {
            // CPU使用率图表
            if (chartsData.cpu_timeline.length > 0) {
                const cpuCtx = document.getElementById('cpuChart').getContext('2d');
                new Chart(cpuCtx, {
                    type: 'line',
                    data: {
                        labels: chartsData.cpu_timeline.map(item => new Date(item.time).toLocaleTimeString()),
                        datasets: [{
                            label: 'CPU使用率 (%)',
                            data: chartsData.cpu_timeline.map(item => item.cpu_percent),
                            borderColor: '#007bff',
                            backgroundColor: 'rgba(0, 123, 255, 0.1)',
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100
                            }
                        }
                    }
                });
            }

            // 内存使用率图表
            if (chartsData.memory_timeline.length > 0) {
                const memoryCtx = document.getElementById('memoryChart').getContext('2d');
                new Chart(memoryCtx, {
                    type: 'line',
                    data: {
                        labels: chartsData.memory_timeline.map(item => new Date(item.time).toLocaleTimeString()),
                        datasets: [{
                            label: '内存使用率 (%)',
                            data: chartsData.memory_timeline.map(item => item.memory_percent),
                            borderColor: '#28a745',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
                            tension: 0.4
                        }, {
                            label: '交换分区使用率 (%)',
                            data: chartsData.memory_timeline.map(item => item.swap_percent),
                            borderColor: '#dc3545',
                            backgroundColor: 'rgba(220, 53, 69, 0.1)',
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100
                            }
                        }
                    }
                });
            }

            // 系统负载图表
            if (chartsData.cpu_timeline.length > 0) {
                const loadCtx = document.getElementById('loadChart').getContext('2d');
                new Chart(loadCtx, {
                    type: 'line',
                    data: {
                        labels: chartsData.cpu_timeline.map(item => new Date(item.time).toLocaleTimeString()),
                        datasets: [{
                            label: '1分钟负载平均值',
                            data: chartsData.cpu_timeline.map(item => item.load_1min),
                            borderColor: '#ffc107',
                            backgroundColor: 'rgba(255, 193, 7, 0.1)',
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            }

            // CPU核心使用率图表
            if (chartsData.cpu_cores.length > 0) {
                const coreCtx = document.getElementById('coreChart').getContext('2d');
                new Chart(coreCtx, {
                    type: 'bar',
                    data: {
                        labels: chartsData.cpu_cores.map(item => item.core),
                        datasets: [{
                            label: 'CPU核心使用率 (%)',
                            data: chartsData.cpu_cores.map(item => item.usage),
                            backgroundColor: chartsData.cpu_cores.map(item =>
                                item.usage > 80 ? '#dc3545' :
                                item.usage > 60 ? '#ffc107' : '#28a745'
                            )
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100
                            }
                        }
                    }
                });
            }
        }
    </script>
</body>
</html>
    '''
    return render_template_string(html_template)

if __name__ == '__main__':
    print('启动Python代码执行服务...')
    print('访问 http://localhost:5000/api/health 检查服务状态')
    print('服务正在启动...')
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f'启动失败: {e}')
