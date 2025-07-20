#!/usr/bin/env python3
"""
简化版Linux系统监控脚本
快速监控5分钟CPU和内存使用情况
"""

import psutil
import time
import json
from datetime import datetime
import os

def collect_system_data(duration=300, interval=1):
    """
    收集系统数据
    :param duration: 监控时长(秒)
    :param interval: 采样间隔(秒)
    """
    print(f"开始监控系统资源 - 时长: {duration}秒 ({duration/60:.1f}分钟)")
    print("按 Ctrl+C 可提前停止监控")
    print("-" * 50)
    
    data = {
        'system_info': {
            'hostname': os.uname().nodename,
            'cpu_count': psutil.cpu_count(),
            'total_memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'start_time': datetime.now().isoformat()
        },
        'samples': []
    }
    
    start_time = time.time()
    sample_count = 0
    
    try:
        while time.time() - start_time < duration:
            # 收集当前时刻的数据
            current_time = datetime.now()
            
            # CPU数据
            cpu_percent = psutil.cpu_percent(interval=None)
            cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
            load_avg = os.getloadavg()
            
            # 内存数据
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            sample = {
                'timestamp': current_time.isoformat(),
                'cpu': {
                    'total_percent': cpu_percent,
                    'per_core_percent': cpu_per_core,
                    'load_1min': load_avg[0],
                    'load_5min': load_avg[1],
                    'load_15min': load_avg[2]
                },
                'memory': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'percent': memory.percent,
                    'cached_gb': round(memory.cached / (1024**3), 2),
                    'buffers_gb': round(memory.buffers / (1024**3), 2)
                },
                'swap': {
                    'total_gb': round(swap.total / (1024**3), 2),
                    'used_gb': round(swap.used / (1024**3), 2),
                    'percent': swap.percent
                }
            }
            
            data['samples'].append(sample)
            sample_count += 1
            
            # 显示进度
            elapsed = time.time() - start_time
            remaining = duration - elapsed
            progress = (elapsed / duration) * 100
            
            print(f"\r进度: {progress:5.1f}% | "
                  f"样本: {sample_count:4d} | "
                  f"CPU: {cpu_percent:5.1f}% | "
                  f"内存: {memory.percent:5.1f}% | "
                  f"剩余: {remaining:3.0f}s", end="")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print(f"\n用户中断监控，已收集 {sample_count} 个样本")
    
    data['system_info']['end_time'] = datetime.now().isoformat()
    data['system_info']['total_samples'] = len(data['samples'])
    
    return data

def save_data(data, filename=None):
    """保存数据到文件"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hostname = data['system_info']['hostname']
        filename = f"system_monitor_{hostname}_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n数据已保存到: {filename}")
    return filename

def print_summary(data):
    """打印监控摘要"""
    if not data['samples']:
        print("没有数据可显示")
        return
    
    print("\n" + "="*50)
    print("监控摘要")
    print("="*50)
    
    # 基本信息
    info = data['system_info']
    print(f"主机: {info['hostname']}")
    print(f"CPU核心: {info['cpu_count']}")
    print(f"总内存: {info['total_memory_gb']}GB")
    print(f"样本数: {info['total_samples']}")
    
    # 统计CPU数据
    cpu_data = [s['cpu']['total_percent'] for s in data['samples']]
    load_data = [s['cpu']['load_1min'] for s in data['samples']]
    
    print(f"\nCPU使用率:")
    print(f"  平均: {sum(cpu_data)/len(cpu_data):6.2f}%")
    print(f"  最大: {max(cpu_data):6.2f}%")
    print(f"  最小: {min(cpu_data):6.2f}%")
    
    print(f"\n系统负载 (1分钟):")
    print(f"  平均: {sum(load_data)/len(load_data):6.2f}")
    print(f"  最大: {max(load_data):6.2f}")
    
    # 统计内存数据
    memory_percent = [s['memory']['percent'] for s in data['samples']]
    memory_used = [s['memory']['used_gb'] for s in data['samples']]
    
    print(f"\n内存使用:")
    print(f"  平均使用率: {sum(memory_percent)/len(memory_percent):6.2f}%")
    print(f"  最大使用率: {max(memory_percent):6.2f}%")
    print(f"  平均使用量: {sum(memory_used)/len(memory_used):6.2f}GB")
    print(f"  最大使用量: {max(memory_used):6.2f}GB")
    
    # 检查交换分区使用
    swap_data = [s['swap']['percent'] for s in data['samples'] if s['swap']['total_gb'] > 0]
    if swap_data:
        avg_swap = sum(swap_data) / len(swap_data)
        max_swap = max(swap_data)
        print(f"\n交换分区:")
        print(f"  平均使用率: {avg_swap:6.2f}%")
        print(f"  最大使用率: {max_swap:6.2f}%")
        if max_swap > 10:
            print("  ⚠️  警告: 交换分区使用率较高，可能存在内存不足")

def analyze_performance(data):
    """简单的性能分析"""
    if not data['samples']:
        return
    
    print("\n" + "="*50)
    print("性能分析")
    print("="*50)
    
    # CPU分析
    cpu_data = [s['cpu']['total_percent'] for s in data['samples']]
    high_cpu_count = sum(1 for cpu in cpu_data if cpu > 80)
    
    if high_cpu_count > 0:
        high_cpu_ratio = high_cpu_count / len(cpu_data) * 100
        print(f"🔥 CPU高使用率 (>80%): {high_cpu_count}次 ({high_cpu_ratio:.1f}%)")
        
        if high_cpu_ratio > 20:
            print("   建议: CPU使用率持续较高，需要检查CPU密集型进程")
    
    # 内存分析
    memory_data = [s['memory']['percent'] for s in data['samples']]
    high_memory_count = sum(1 for mem in memory_data if mem > 85)
    
    if high_memory_count > 0:
        high_memory_ratio = high_memory_count / len(memory_data) * 100
        print(f"💾 内存高使用率 (>85%): {high_memory_count}次 ({high_memory_ratio:.1f}%)")
        
        if high_memory_ratio > 20:
            print("   建议: 内存使用率持续较高，考虑增加内存或优化内存使用")
    
    # 负载分析
    load_data = [s['cpu']['load_1min'] for s in data['samples']]
    cpu_count = data['system_info']['cpu_count']
    high_load_count = sum(1 for load in load_data if load > cpu_count)
    
    if high_load_count > 0:
        high_load_ratio = high_load_count / len(load_data) * 100
        print(f"⚡ 系统负载过高 (>{cpu_count}): {high_load_count}次 ({high_load_ratio:.1f}%)")
        
        if high_load_ratio > 10:
            print("   建议: 系统负载过高，可能存在CPU瓶颈或I/O等待")

def main():
    """主函数"""
    print("Linux系统资源监控工具")
    print("默认监控5分钟，每秒采样一次")
    print()
    
    try:
        # 收集数据 (5分钟 = 300秒)
        data = collect_system_data(duration=300, interval=1)
        
        # 保存数据
        filename = save_data(data)
        
        # 显示摘要
        print_summary(data)
        
        # 性能分析
        analyze_performance(data)
        
        print(f"\n监控完成！数据文件: {filename}")
        
    except KeyboardInterrupt:
        print("\n监控被用户中断")
    except Exception as e:
        print(f"监控过程中发生错误: {e}")

if __name__ == "__main__":
    main()
