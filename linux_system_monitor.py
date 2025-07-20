#!/usr/bin/env python3
"""
Linux服务器CPU和内存监控工具
监控5分钟内的系统资源使用情况并记录数据
"""

import psutil
import time
import json
import csv
import threading
from datetime import datetime, timedelta
import os
import sys

class LinuxSystemMonitor:
    def __init__(self, monitor_duration=300, sample_interval=1):
        """
        初始化监控器
        :param monitor_duration: 监控时长(秒)，默认300秒(5分钟)
        :param sample_interval: 采样间隔(秒)，默认1秒
        """
        self.monitor_duration = monitor_duration
        self.sample_interval = sample_interval
        self.is_monitoring = False
        
        # 数据存储
        self.cpu_data = []
        self.memory_data = []
        self.system_info = {}
        
        # 获取系统基本信息
        self._collect_system_info()
    
    def _collect_system_info(self):
        """收集系统基本信息"""
        try:
            self.system_info = {
                'hostname': os.uname().nodename,
                'system': os.uname().sysname,
                'release': os.uname().release,
                'version': os.uname().version,
                'machine': os.uname().machine,
                'cpu_count_logical': psutil.cpu_count(logical=True),
                'cpu_count_physical': psutil.cpu_count(logical=False),
                'total_memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                'monitoring_start_time': datetime.now().isoformat()
            }
            
            # 获取CPU信息
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                if 'model name' in cpuinfo:
                    cpu_model = cpuinfo.split('model name')[1].split(':')[1].split('\n')[0].strip()
                    self.system_info['cpu_model'] = cpu_model
                    
        except Exception as e:
            print(f"获取系统信息时出错: {e}")
    
    def _monitor_cpu(self):
        """监控CPU使用情况"""
        print("开始监控CPU...")
        
        while self.is_monitoring:
            try:
                # 获取总体CPU使用率
                cpu_percent = psutil.cpu_percent(interval=None)
                
                # 获取每个核心的CPU使用率
                cpu_percent_per_core = psutil.cpu_percent(interval=None, percpu=True)
                
                # 获取CPU频率
                cpu_freq = psutil.cpu_freq()
                
                # 获取负载平均值
                load_avg = os.getloadavg()
                
                # 获取CPU统计信息
                cpu_stats = psutil.cpu_stats()
                
                cpu_data_point = {
                    'timestamp': datetime.now().isoformat(),
                    'cpu_percent_total': cpu_percent,
                    'cpu_percent_per_core': cpu_percent_per_core,
                    'cpu_frequency_current': cpu_freq.current if cpu_freq else None,
                    'cpu_frequency_min': cpu_freq.min if cpu_freq else None,
                    'cpu_frequency_max': cpu_freq.max if cpu_freq else None,
                    'load_average_1min': load_avg[0],
                    'load_average_5min': load_avg[1],
                    'load_average_15min': load_avg[2],
                    'context_switches': cpu_stats.ctx_switches,
                    'interrupts': cpu_stats.interrupts,
                    'soft_interrupts': cpu_stats.soft_interrupts,
                    'system_calls': cpu_stats.syscalls
                }
                
                self.cpu_data.append(cpu_data_point)
                
            except Exception as e:
                print(f"CPU监控错误: {e}")
            
            time.sleep(self.sample_interval)
    
    def _monitor_memory(self):
        """监控内存使用情况"""
        print("开始监控内存...")
        
        while self.is_monitoring:
            try:
                # 获取虚拟内存信息
                virtual_memory = psutil.virtual_memory()
                
                # 获取交换内存信息
                swap_memory = psutil.swap_memory()
                
                memory_data_point = {
                    'timestamp': datetime.now().isoformat(),
                    # 虚拟内存
                    'memory_total_gb': round(virtual_memory.total / (1024**3), 2),
                    'memory_available_gb': round(virtual_memory.available / (1024**3), 2),
                    'memory_used_gb': round(virtual_memory.used / (1024**3), 2),
                    'memory_free_gb': round(virtual_memory.free / (1024**3), 2),
                    'memory_percent': virtual_memory.percent,
                    'memory_buffers_gb': round(virtual_memory.buffers / (1024**3), 2),
                    'memory_cached_gb': round(virtual_memory.cached / (1024**3), 2),
                    'memory_shared_gb': round(virtual_memory.shared / (1024**3), 2),
                    # 交换内存
                    'swap_total_gb': round(swap_memory.total / (1024**3), 2),
                    'swap_used_gb': round(swap_memory.used / (1024**3), 2),
                    'swap_free_gb': round(swap_memory.free / (1024**3), 2),
                    'swap_percent': swap_memory.percent,
                    'swap_sin_mb': round(swap_memory.sin / (1024**2), 2),
                    'swap_sout_mb': round(swap_memory.sout / (1024**2), 2)
                }
                
                self.memory_data.append(memory_data_point)
                
            except Exception as e:
                print(f"内存监控错误: {e}")
            
            time.sleep(self.sample_interval)
    
    def start_monitoring(self):
        """开始监控"""
        print(f"开始监控系统资源，时长: {self.monitor_duration}秒 ({self.monitor_duration/60:.1f}分钟)")
        print(f"采样间隔: {self.sample_interval}秒")
        print(f"预计采集数据点: {self.monitor_duration // self.sample_interval}个")
        print("-" * 60)
        
        self.is_monitoring = True
        
        # 启动监控线程
        cpu_thread = threading.Thread(target=self._monitor_cpu, daemon=True)
        memory_thread = threading.Thread(target=self._monitor_memory, daemon=True)
        
        cpu_thread.start()
        memory_thread.start()
        
        # 显示进度
        start_time = time.time()
        try:
            while time.time() - start_time < self.monitor_duration:
                elapsed = time.time() - start_time
                remaining = self.monitor_duration - elapsed
                progress = (elapsed / self.monitor_duration) * 100
                
                print(f"\r监控进度: {progress:.1f}% | "
                      f"已用时: {elapsed:.0f}s | "
                      f"剩余: {remaining:.0f}s | "
                      f"CPU数据点: {len(self.cpu_data)} | "
                      f"内存数据点: {len(self.memory_data)}", end="")
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n用户中断监控...")
        
        self.is_monitoring = False
        print(f"\n监控完成！共收集 CPU数据点: {len(self.cpu_data)}, 内存数据点: {len(self.memory_data)}")
    
    def save_data(self, output_format='json', output_dir='./monitoring_data'):
        """保存监控数据"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hostname = self.system_info.get('hostname', 'unknown')
        
        # 准备完整数据
        complete_data = {
            'system_info': self.system_info,
            'monitoring_summary': {
                'duration_seconds': self.monitor_duration,
                'sample_interval': self.sample_interval,
                'cpu_data_points': len(self.cpu_data),
                'memory_data_points': len(self.memory_data),
                'start_time': self.system_info.get('monitoring_start_time'),
                'end_time': datetime.now().isoformat()
            },
            'cpu_data': self.cpu_data,
            'memory_data': self.memory_data
        }
        
        if output_format.lower() == 'json':
            # 保存为JSON格式
            json_file = os.path.join(output_dir, f'system_monitor_{hostname}_{timestamp}.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(complete_data, f, indent=2, ensure_ascii=False)
            print(f"数据已保存到JSON文件: {json_file}")
            
        elif output_format.lower() == 'csv':
            # 保存CPU数据为CSV
            cpu_csv_file = os.path.join(output_dir, f'cpu_monitor_{hostname}_{timestamp}.csv')
            if self.cpu_data:
                with open(cpu_csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.cpu_data[0].keys())
                    writer.writeheader()
                    writer.writerows(self.cpu_data)
                print(f"CPU数据已保存到CSV文件: {cpu_csv_file}")
            
            # 保存内存数据为CSV
            memory_csv_file = os.path.join(output_dir, f'memory_monitor_{hostname}_{timestamp}.csv')
            if self.memory_data:
                with open(memory_csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.memory_data[0].keys())
                    writer.writeheader()
                    writer.writerows(self.memory_data)
                print(f"内存数据已保存到CSV文件: {memory_csv_file}")
        
        return complete_data
    
    def print_summary(self):
        """打印监控摘要"""
        if not self.cpu_data or not self.memory_data:
            print("没有监控数据可显示")
            return
        
        print("\n" + "="*60)
        print("监控摘要报告")
        print("="*60)
        
        # 系统信息
        print(f"主机名: {self.system_info.get('hostname')}")
        print(f"系统: {self.system_info.get('system')} {self.system_info.get('release')}")
        print(f"CPU: {self.system_info.get('cpu_model', 'Unknown')}")
        print(f"CPU核心数: {self.system_info.get('cpu_count_physical')}物理/{self.system_info.get('cpu_count_logical')}逻辑")
        print(f"总内存: {self.system_info.get('total_memory_gb')}GB")
        
        # CPU统计
        cpu_usage = [data['cpu_percent_total'] for data in self.cpu_data]
        print(f"\nCPU使用率统计:")
        print(f"  平均: {sum(cpu_usage)/len(cpu_usage):.2f}%")
        print(f"  最大: {max(cpu_usage):.2f}%")
        print(f"  最小: {min(cpu_usage):.2f}%")
        
        # 内存统计
        memory_usage = [data['memory_percent'] for data in self.memory_data]
        memory_used = [data['memory_used_gb'] for data in self.memory_data]
        print(f"\n内存使用率统计:")
        print(f"  平均使用率: {sum(memory_usage)/len(memory_usage):.2f}%")
        print(f"  最大使用率: {max(memory_usage):.2f}%")
        print(f"  平均使用量: {sum(memory_used)/len(memory_used):.2f}GB")
        print(f"  最大使用量: {max(memory_used):.2f}GB")
        
        # 负载平均值
        load_1min = [data['load_average_1min'] for data in self.cpu_data]
        print(f"\n系统负载 (1分钟平均):")
        print(f"  平均: {sum(load_1min)/len(load_1min):.2f}")
        print(f"  最大: {max(load_1min):.2f}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Linux系统资源监控工具')
    parser.add_argument('--duration', '-d', type=int, default=300, 
                       help='监控时长(秒)，默认300秒(5分钟)')
    parser.add_argument('--interval', '-i', type=float, default=1.0,
                       help='采样间隔(秒)，默认1秒')
    parser.add_argument('--format', '-f', choices=['json', 'csv'], default='json',
                       help='输出格式，默认json')
    parser.add_argument('--output-dir', '-o', default='./monitoring_data',
                       help='输出目录，默认./monitoring_data')
    parser.add_argument('--no-summary', action='store_true',
                       help='不显示摘要报告')
    
    args = parser.parse_args()
    
    # 检查权限
    if os.geteuid() != 0:
        print("警告: 建议以root权限运行以获取完整的系统信息")
    
    # 创建监控器
    monitor = LinuxSystemMonitor(
        monitor_duration=args.duration,
        sample_interval=args.interval
    )
    
    try:
        # 开始监控
        monitor.start_monitoring()
        
        # 保存数据
        monitor.save_data(output_format=args.format, output_dir=args.output_dir)
        
        # 显示摘要
        if not args.no_summary:
            monitor.print_summary()
            
    except Exception as e:
        print(f"监控过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
