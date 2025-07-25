# Linux系统资源监控工具

这是一个用于监控Linux服务器CPU和内存使用情况的Python工具集，可以监控5分钟内的系统资源数据并生成详细报告。

## 功能特性

- 🖥️ **CPU监控**: 总体使用率、每核心使用率、负载平均值、上下文切换等
- 💾 **内存监控**: 虚拟内存、交换内存、缓存、缓冲区等详细信息
- 📊 **数据记录**: 支持JSON和CSV格式输出
- 📈 **实时显示**: 监控过程中实时显示进度和关键指标
- 📋 **摘要报告**: 自动生成监控摘要和性能分析
- ⚡ **轻量级**: 最小化系统资源占用

## 文件说明

- `linux_system_monitor.py` - 完整版监控工具，功能丰富，支持多种参数
- `simple_monitor.py` - 简化版监控工具，开箱即用
- `install_requirements.sh` - 依赖安装脚本
- `README.md` - 使用说明文档

## 快速开始

### 1. 安装依赖

```bash
# 给安装脚本添加执行权限
chmod +x install_requirements.sh

# 运行安装脚本
./install_requirements.sh
```

或者手动安装：
```bash
pip3 install psutil
```

### 2. 运行监控

#### 简化版（推荐新手使用）
```bash
# 监控5分钟（默认）
python3 simple_monitor.py

# 给脚本添加执行权限后直接运行
chmod +x simple_monitor.py
./simple_monitor.py
```

#### 完整版（高级用户）
```bash
# 基本使用 - 监控5分钟
python3 linux_system_monitor.py

# 自定义监控时长 - 监控10分钟
python3 linux_system_monitor.py --duration 600

# 自定义采样间隔 - 每2秒采样一次
python3 linux_system_monitor.py --interval 2

# 输出CSV格式
python3 linux_system_monitor.py --format csv

# 指定输出目录
python3 linux_system_monitor.py --output-dir /tmp/monitoring

# 不显示摘要报告
python3 linux_system_monitor.py --no-summary
```

## 输出示例

### 监控过程显示
```
开始监控系统资源 - 时长: 300秒 (5.0分钟)
按 Ctrl+C 可提前停止监控
--------------------------------------------------
进度:  50.0% | 样本:  150 | CPU:  25.3% | 内存:  45.2% | 剩余: 150s
```

### 监控摘要报告
```
==================================================
监控摘要
==================================================
主机: web-server-01
CPU核心: 4
总内存: 8.0GB
样本数: 300

CPU使用率:
  平均:  23.45%
  最大:  78.90%
  最小:   5.20%

系统负载 (1分钟):
  平均:   1.23
  最大:   3.45

内存使用:
  平均使用率:  45.67%
  最大使用率:  52.30%
  平均使用量:   3.65GB
  最大使用量:   4.18GB
```

### 性能分析
```
==================================================
性能分析
==================================================
🔥 CPU高使用率 (>80%): 15次 (5.0%)
💾 内存高使用率 (>85%): 0次 (0.0%)
⚡ 系统负载过高 (>4): 8次 (2.7%)
```

## 输出文件格式

### JSON格式示例
```json
{
  "system_info": {
    "hostname": "web-server-01",
    "cpu_count": 4,
    "total_memory_gb": 8.0,
    "start_time": "2024-01-20T10:30:00.123456"
  },
  "samples": [
    {
      "timestamp": "2024-01-20T10:30:01.123456",
      "cpu": {
        "total_percent": 25.3,
        "per_core_percent": [20.1, 30.5, 25.0, 25.6],
        "load_1min": 1.23,
        "load_5min": 1.45,
        "load_15min": 1.67
      },
      "memory": {
        "total_gb": 8.0,
        "used_gb": 3.6,
        "available_gb": 4.4,
        "percent": 45.2,
        "cached_gb": 1.2,
        "buffers_gb": 0.3
      },
      "swap": {
        "total_gb": 2.0,
        "used_gb": 0.1,
        "percent": 5.0
      }
    }
  ]
}
```

## 命令行参数

### 完整版参数
```
--duration, -d    监控时长(秒)，默认300秒(5分钟)
--interval, -i    采样间隔(秒)，默认1秒
--format, -f      输出格式 [json|csv]，默认json
--output-dir, -o  输出目录，默认./monitoring_data
--no-summary      不显示摘要报告
```

## 使用场景

### 1. 性能基线测试
```bash
# 在系统空闲时建立性能基线
python3 simple_monitor.py
```

### 2. 压力测试监控
```bash
# 在压力测试期间监控系统资源
python3 linux_system_monitor.py --duration 1800  # 30分钟
```

### 3. 问题排查
```bash
# 高频采样，详细监控
python3 linux_system_monitor.py --interval 0.5 --duration 600
```

### 4. 定时监控
```bash
# 添加到crontab，每小时监控5分钟
0 * * * * /usr/bin/python3 /path/to/simple_monitor.py
```

## 注意事项

1. **权限要求**: 建议以root权限运行以获取完整的系统信息
2. **资源占用**: 监控工具本身占用很少的系统资源
3. **存储空间**: 5分钟监控大约产生300KB的JSON数据
4. **中断监控**: 可以随时按Ctrl+C中断监控，已收集的数据会被保存

## 故障排除

### 问题1: 权限不足
```bash
# 解决方案：使用sudo运行
sudo python3 simple_monitor.py
```

### 问题2: psutil模块未找到
```bash
# 解决方案：安装psutil
pip3 install psutil
```

### 问题3: 无法创建输出目录
```bash
# 解决方案：检查目录权限或指定其他目录
python3 linux_system_monitor.py --output-dir /tmp/monitoring
```

## 扩展功能

这个工具可以很容易地扩展以支持：
- 磁盘I/O监控
- 网络流量监控
- 进程级别监控
- 实时告警功能
- Web界面展示

## 许可证

MIT License - 可自由使用和修改
#   t e s t _ p l a t f o r m  
 