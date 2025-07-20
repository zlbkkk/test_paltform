# 性能测试功能使用指南

## 🎯 功能概述

本平台新增了完整的性能测试功能模块，包括：

1. **📊 监控数据分析** - 上传系统监控数据，获取AI驱动的性能瓶颈分析
2. **🔧 压力测试工具** - 配置和执行各种类型的压力测试
3. **📈 性能报告** - 查看和管理历史性能测试报告

## 🚀 快速开始

### 1. 启动服务

#### 后端服务 (Flask)
```bash
python simple_server.py
```
服务将在 `http://localhost:5000` 启动

#### 前端服务 (Vue.js)
```bash
npm install  # 首次运行需要安装依赖
npm start    # 或 npm run dev
```
前端将在 `http://localhost:8080` 启动

### 2. 访问性能测试功能

在浏览器中打开 `http://localhost:8080`，在左侧菜单中找到 **"性能测试"** 菜单，包含三个子菜单：

- **监控数据分析** - `/performance-test/monitor-analysis`
- **压力测试工具** - `/performance-test/stress-test`  
- **性能报告** - `/performance-test/performance-report`

## 📊 监控数据分析功能

### 功能特点
- 🤖 **AI智能分析** - 自动识别性能瓶颈和异常模式
- 📈 **可视化图表** - CPU、内存、负载等趋势图表
- ⚠️ **瓶颈识别** - 自动标记高、中、低严重性问题
- 💡 **优化建议** - 提供具体的性能优化建议
- 🎯 **性能评分** - 0-100分的综合性能评分

### 使用步骤

1. **准备监控数据**
   - 使用提供的 `linux_system_monitor.py` 或 `simple_monitor.py` 收集系统监控数据
   - 确保数据文件为JSON格式，包含CPU、内存、负载等指标

2. **上传数据文件**
   - 在监控数据分析页面，拖拽JSON文件到上传区域
   - 或点击选择文件按钮选择文件

3. **查看分析结果**
   - AI会自动分析数据并生成报告
   - 查看系统信息、性能评分、趋势图表
   - 重点关注瓶颈分析和优化建议

### 支持的数据格式

```json
{
  "system_info": {
    "hostname": "server-name",
    "cpu_count_logical": 4,
    "total_memory_gb": 8.0,
    "cpu_model": "Intel Xeon CPU"
  },
  "cpu_data": [
    {
      "timestamp": "2025-07-20T14:03:11.862821",
      "cpu_percent_total": 25.3,
      "cpu_percent_per_core": [20.1, 30.5, 25.0, 25.6],
      "load_average_1min": 1.23
    }
  ],
  "memory_data": [
    {
      "timestamp": "2025-07-20T14:03:11.864997",
      "memory_percent": 53.3,
      "swap_percent": 6.4
    }
  ]
}
```

## 🔧 压力测试工具

### 支持的测试类型

1. **HTTP压力测试**
   - 配置目标URL、请求方法、并发用户数
   - 实时监控QPS、响应时间、成功率

2. **CPU压力测试**
   - 指定CPU核心数和负载强度
   - 监控CPU使用率变化

3. **内存压力测试**
   - 配置内存大小和访问模式
   - 监控内存使用情况

4. **磁盘I/O测试**
   - 配置文件大小和操作类型
   - 监控磁盘读写性能

### 实时监控

- 📊 **实时图表** - CPU、内存、网络、磁盘I/O趋势
- 📈 **关键指标** - 当前使用率和速度
- 📋 **测试历史** - 保存最近的测试记录

## 📈 性能报告管理

### 功能特点

- 📋 **报告列表** - 查看所有历史测试报告
- 🔍 **智能筛选** - 按时间、类型、评分筛选
- 📊 **详细分析** - 查看完整的性能分析报告
- 📈 **对比分析** - 对比多个报告的性能差异
- 📤 **导出功能** - 导出报告为文件

### 报告内容

每个性能报告包含：
- 基本信息（测试类型、时长、评分）
- 性能指标摘要
- 趋势图表
- 瓶颈分析
- 优化建议

## 🛠️ API接口

### 主要接口

```javascript
// 分析监控数据
POST /api/analyze-monitoring-data
Content-Type: application/json

// 上传监控数据文件
POST /api/upload-monitoring-data
Content-Type: multipart/form-data

// 健康检查
GET /api/health
```

### 使用示例

```javascript
// 分析监控数据
import { analyzeMonitoringData } from '@/api/performance'

const result = await analyzeMonitoringData(monitoringData)
if (result.success) {
  console.log('性能评分:', result.analysis.performance_score)
  console.log('瓶颈数量:', result.analysis.bottlenecks.length)
}
```

## 🔧 技术架构

### 前端技术栈
- **Vue.js 2.6** - 前端框架
- **Element UI** - UI组件库
- **ECharts 5.4** - 图表库
- **Axios** - HTTP客户端

### 后端技术栈
- **Flask** - Web框架
- **NumPy** - 数据分析
- **Python 3.x** - 运行环境

### AI分析引擎
- **异常检测** - 基于统计方法和机器学习
- **瓶颈识别** - 多维度性能指标分析
- **智能评分** - 综合性能评估算法

## 📝 示例数据

项目中包含示例监控数据文件：
- `system_monitor_racknerd-2add1ef_20250720_140812.json`

可以直接使用此文件测试监控数据分析功能。

## 🐛 故障排除

### 常见问题

1. **上传文件失败**
   - 检查文件格式是否为JSON
   - 确保文件大小不超过10MB
   - 验证JSON格式是否正确

2. **API调用失败**
   - 确认后端服务已启动 (http://localhost:5000)
   - 检查网络连接
   - 查看浏览器控制台错误信息

3. **图表不显示**
   - 确认ECharts库已正确加载
   - 检查数据格式是否正确
   - 查看浏览器控制台错误

### 测试API

使用提供的测试脚本验证API功能：

```bash
python test_performance_api.py
```

## 🎉 总结

性能测试功能已成功集成到平台中，提供了完整的性能监控、分析和报告功能。通过AI驱动的分析引擎，可以快速识别系统性能瓶颈并获得优化建议，大大提升了性能测试的效率和准确性。
