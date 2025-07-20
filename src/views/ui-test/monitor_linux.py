import psutil
import subprocess
import json
import re
from datetime import datetime

class JavaProcessMonitor:
    def __init__(self):
        self.target_process = None
        self.java_processes = []
    
    def discover_java_processes(self):
        """发现所有Java进程"""
        java_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                if proc.info['name'] and 'java' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    
                    # 提取更多Java进程信息
                    java_info = self._extract_java_info(proc, cmdline)
                    java_processes.append(java_info)
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        self.java_processes = java_processes
        return java_processes
    
    def _extract_java_info(self, proc, cmdline):
        """提取Java进程详细信息"""
        java_info = {
            'pid': proc.pid,
            'cmdline': cmdline,
            'create_time': datetime.fromtimestamp(proc.create_time()).isoformat(),
            'memory_info': proc.memory_info()._asdict(),
            'cpu_percent': proc.cpu_percent(),
        }
        
        # 提取应用名称
        app_name = self._extract_app_name(cmdline)
        java_info['app_name'] = app_name
        
        # 提取JVM参数
        jvm_args = self._extract_jvm_args(cmdline)
        java_info['jvm_args'] = jvm_args
        
        # 提取端口信息
        ports = self._extract_ports(proc)
        java_info['ports'] = ports
        
        return java_info
    
    def _extract_app_name(self, cmdline):
        """从命令行提取应用名称"""
        # 常见的应用名称模式
        patterns = [
            r'-jar\s+([^/\s]+\.jar)',  # jar文件名
            r'spring\.application\.name=([^\s]+)',  # Spring应用名
            r'-Dapp\.name=([^\s]+)',  # 自定义应用名
            r'([^/\s]+)\.jar',  # jar文件名（备选）
        ]
        
        for pattern in patterns:
            match = re.search(pattern, cmdline)
            if match:
                return match.group(1)
        
        return "Unknown Java App"
    
    def _extract_jvm_args(self, cmdline):
        """提取JVM参数"""
        jvm_args = {}
        
        # 堆内存设置
        heap_match = re.search(r'-Xmx(\d+[kmgKMG]?)', cmdline)
        if heap_match:
            jvm_args['max_heap'] = heap_match.group(1)
        
        # GC设置
        gc_match = re.search(r'-XX:\+Use(\w+GC)', cmdline)
        if gc_match:
            jvm_args['gc_type'] = gc_match.group(1)
        
        # 其他重要参数
        if '-server' in cmdline:
            jvm_args['mode'] = 'server'
        elif '-client' in cmdline:
            jvm_args['mode'] = 'client'
        
        return jvm_args
    
    def _extract_ports(self, proc):
        """提取进程监听的端口"""
        ports = []
        try:
            connections = proc.connections()
            for conn in connections:
                if conn.status == 'LISTEN':
                    ports.append(conn.laddr.port)
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
        
        return list(set(ports))  # 去重
    
    def select_process_by_criteria(self, **criteria):
        """根据条件选择进程"""
        if not self.java_processes:
            self.discover_java_processes()
        
        candidates = self.java_processes.copy()
        
        # 按PID筛选
        if 'pid' in criteria:
            candidates = [p for p in candidates if p['pid'] == criteria['pid']]
        
        # 按应用名筛选
        if 'app_name' in criteria:
            candidates = [p for p in candidates if criteria['app_name'].lower() in p['app_name'].lower()]
        
        # 按端口筛选
        if 'port' in criteria:
            candidates = [p for p in candidates if criteria['port'] in p['ports']]
        
        # 按jar文件名筛选
        if 'jar_name' in criteria:
            candidates = [p for p in candidates if criteria['jar_name'] in p['cmdline']]
        
        if len(candidates) == 1:
            self.target_process = candidates[0]
            return candidates[0]
        elif len(candidates) > 1:
            # 如果有多个匹配，返回CPU使用率最高的
            self.target_process = max(candidates, key=lambda x: x['cpu_percent'])
            return self.target_process
        else:
            return None
    
    def interactive_process_selection(self):
        """交互式进程选择"""
        processes = self.discover_java_processes()
        
        if not processes:
            print("未发现Java进程")
            return None
        
        print("\n发现的Java进程:")
        print("-" * 100)
        print(f"{'序号':<4} {'PID':<8} {'应用名':<20} {'端口':<15} {'内存(MB)':<10} {'CPU%':<8}")
        print("-" * 100)
        
        for i, proc in enumerate(processes):
            memory_mb = proc['memory_info']['rss'] / 1024 / 1024
            ports_str = ','.join(map(str, proc['ports'][:3]))  # 只显示前3个端口
            if len(proc['ports']) > 3:
                ports_str += '...'
            
            print(f"{i+1:<4} {proc['pid']:<8} {proc['app_name']:<20} {ports_str:<15} {memory_mb:<10.1f} {proc['cpu_percent']:<8.1f}")
        
        while True:
            try:
                choice = input(f"\n请选择要监控的进程 (1-{len(processes)}): ")
                index = int(choice) - 1
                if 0 <= index < len(processes):
                    self.target_process = processes[index]
                    return self.target_process
                else:
                    print("无效选择，请重新输入")
            except ValueError:
                print("请输入有效数字")