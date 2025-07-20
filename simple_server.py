#!/usr/bin/env python3
from flask import Flask, request, jsonify, render_template_string, render_template
from flask_cors import CORS
import io
import sys
import json
import os
import numpy as np
import sqlite3
import paramiko
import threading
import time
from datetime import datetime, timedelta
from contextlib import redirect_stdout, redirect_stderr

app = Flask(__name__)
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
        self.init_storage()

    def init_storage(self):
        """初始化数据存储"""
        # 这里简化为内存存储，实际项目中应该使用数据库
        self.servers = {
            'demo-server': {
                'id': 'demo-server',
                'name': '演示服务器',
                'host': 'localhost',
                'port': 22,
                'username': 'demo',
                'auth_type': 'password',
                'password': 'demo123',
                'enabled': True,
                'monitor_interval': 30,
                'description': '本地演示服务器'
            }
        }
        self.metrics_data = {}

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
        try:
            if server_config['host'] == 'localhost':
                # 本地服务器模拟
                return True, "连接成功"

            # 实际SSH连接测试（需要paramiko库）
            # ssh = paramiko.SSHClient()
            # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # ssh.connect(
            #     hostname=server_config['host'],
            #     port=server_config['port'],
            #     username=server_config['username'],
            #     password=server_config.get('password'),
            #     key_filename=server_config.get('private_key_path'),
            #     timeout=10
            # )
            # ssh.close()

            # 模拟连接测试
            return True, "连接成功"

        except Exception as e:
            return False, str(e)

    def get_server_metrics(self, server_id, time_range='1h'):
        """获取服务器监控数据"""
        if server_id not in self.servers:
            return None

        # 生成模拟数据
        current_time = datetime.now()

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

        # 生成时间序列
        timestamps = []
        cpu_data = []
        memory_data = []
        disk_read_data = []
        disk_write_data = []
        network_sent_data = []
        network_recv_data = []

        points = duration_minutes * 60 // interval_seconds

        for i in range(points):
            timestamp = current_time - timedelta(seconds=(points - i - 1) * interval_seconds)
            timestamps.append(timestamp.strftime('%H:%M:%S'))

            # 生成模拟数据（带一些波动）
            base_cpu = 30 + 20 * np.sin(i * 0.1) + np.random.normal(0, 5)
            cpu_data.append(max(0, min(100, base_cpu)))

            base_memory = 60 + 10 * np.sin(i * 0.05) + np.random.normal(0, 3)
            memory_data.append(max(0, min(100, base_memory)))

            disk_read_data.append(max(0, 1024 * 1024 * (5 + np.random.normal(0, 2))))
            disk_write_data.append(max(0, 1024 * 1024 * (3 + np.random.normal(0, 1))))

            network_sent_data.append(max(0, 1024 * (100 + np.random.normal(0, 20))))
            network_recv_data.append(max(0, 1024 * (150 + np.random.normal(0, 30))))

        # 当前指标
        current_metrics = {
            'cpu': round(cpu_data[-1], 1) if cpu_data else 0,
            'load_avg': round(cpu_data[-1] / 100 * 4, 2) if cpu_data else 0,
            'memory_percent': round(memory_data[-1], 1) if memory_data else 0,
            'memory_used': round(memory_data[-1] / 100 * 8, 1) if memory_data else 0,
            'memory_total': 8.0,
            'disk_percent': round(np.random.uniform(40, 60), 1),
            'disk_free': round(np.random.uniform(100, 200), 1),
            'network_sent': int(network_sent_data[-1]) if network_sent_data else 0,
            'network_recv': int(network_recv_data[-1]) if network_recv_data else 0
        }

        # 历史数据
        historical_data = {
            'timestamps': timestamps,
            'cpu': [round(x, 1) for x in cpu_data],
            'memory': [round(x, 1) for x in memory_data],
            'disk_read': [int(x) for x in disk_read_data],
            'disk_write': [int(x) for x in disk_write_data],
            'network_sent': [int(x) for x in network_sent_data],
            'network_recv': [int(x) for x in network_recv_data]
        }

        # 进程数据
        processes = self._generate_mock_processes()

        return {
            'current': current_metrics,
            'historical': historical_data,
            'processes': processes
        }

    def _generate_mock_processes(self):
        """生成模拟进程数据"""
        processes = [
            {
                'pid': 1234,
                'name': 'python3',
                'cpu_percent': round(np.random.uniform(5, 25), 1),
                'memory_percent': round(np.random.uniform(2, 8), 1),
                'memory_mb': round(np.random.uniform(100, 500), 1),
                'status': 'running',
                'create_time': '2025-07-20 10:30:15'
            },
            {
                'pid': 5678,
                'name': 'nginx',
                'cpu_percent': round(np.random.uniform(1, 5), 1),
                'memory_percent': round(np.random.uniform(1, 3), 1),
                'memory_mb': round(np.random.uniform(50, 150), 1),
                'status': 'running',
                'create_time': '2025-07-20 09:15:30'
            },
            {
                'pid': 9012,
                'name': 'mysql',
                'cpu_percent': round(np.random.uniform(2, 15), 1),
                'memory_percent': round(np.random.uniform(5, 15), 1),
                'memory_mb': round(np.random.uniform(200, 800), 1),
                'status': 'running',
                'create_time': '2025-07-20 08:45:00'
            },
            {
                'pid': 3456,
                'name': 'redis-server',
                'cpu_percent': round(np.random.uniform(0.5, 3), 1),
                'memory_percent': round(np.random.uniform(1, 5), 1),
                'memory_mb': round(np.random.uniform(30, 100), 1),
                'status': 'running',
                'create_time': '2025-07-20 08:30:45'
            },
            {
                'pid': 7890,
                'name': 'java',
                'cpu_percent': round(np.random.uniform(10, 30), 1),
                'memory_percent': round(np.random.uniform(8, 20), 1),
                'memory_mb': round(np.random.uniform(500, 1500), 1),
                'status': 'running',
                'create_time': '2025-07-20 09:00:20'
            }
        ]

        return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)

# 创建服务器监控实例
server_monitor = ServerMonitor()

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
def get_server_metrics(server_id):
    """获取服务器监控数据"""
    try:
        if server_id not in server_monitor.servers:
            return jsonify({'success': False, 'error': '服务器不存在'})

        time_range = request.args.get('timeRange', '1h')
        metrics_data = server_monitor.get_server_metrics(server_id, time_range)

        if metrics_data:
            return jsonify({
                'success': True,
                'data': metrics_data
            })
        else:
            return jsonify({'success': False, 'error': '获取监控数据失败'})
    except Exception as e:
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
