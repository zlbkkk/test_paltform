# Python代码执行实现指南

## 概述

本文档详细说明了如何在脚本编辑器中实现真正的Python代码执行功能。

## 当前实现状态

### 前端实现
- ✅ 代码编辑器（CodeMirror）
- ✅ 语法高亮
- ✅ 执行按钮和日志显示
- ✅ 多种执行方案的自动降级

### 执行方案优先级
1. **后端API执行**（推荐）- 功能最完整
2. **浏览器内执行**（Pyodide）- 纯前端方案
3. **模拟执行**（当前）- 仅用于演示

## 方案一：后端API执行（推荐）

### 优点
- 功能完整，支持所有Python库
- 安全性高，可以完全控制执行环境
- 支持Selenium等需要系统资源的库
- 执行性能好

### 实现步骤

#### 1. 后端服务部署
```bash
# 安装依赖
pip install flask flask-cors

# 运行服务
cd backend-example
python python_executor.py
```

#### 2. 前端配置
在`src/utils/request.js`中配置后端地址：
```javascript
const service = axios.create({
  baseURL: 'http://localhost:5000', // 后端服务地址
  timeout: 30000 // 增加超时时间
})
```

#### 3. 安全考虑
- 代码沙箱执行
- 危险函数黑名单
- 执行时间限制
- 输出大小限制
- 网络访问控制

### Docker部署示例
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "python_executor.py"]
```

## 方案二：浏览器内执行（Pyodide）

### 优点
- 纯前端方案，无需后端
- 支持大部分Python标准库
- 支持NumPy、Pandas等科学计算库

### 缺点
- 不支持Selenium等需要系统资源的库
- 首次加载较慢（需要下载Python运行时）
- 功能相对受限

### 实现状态
- ✅ Pyodide执行器已实现
- ✅ 安全检查
- ✅ 错误处理
- ✅ 输出捕获

### 使用方法
```javascript
import pyodideExecutor from '@/utils/pyodide-executor'

// 执行Python代码
const result = await pyodideExecutor.execute(`
print("Hello, World!")
import numpy as np
arr = np.array([1, 2, 3, 4, 5])
print(f"数组: {arr}")
print(f"平均值: {np.mean(arr)}")
`)

console.log(result.output) // 查看输出
```

## 方案三：容器化执行

### 优点
- 最高安全性
- 完全隔离的执行环境
- 支持所有Python功能

### 缺点
- 复杂度最高
- 需要Docker环境
- 资源消耗较大

### 实现思路
```python
import docker

def execute_in_container(code):
    client = docker.from_env()
    
    # 创建临时容器
    container = client.containers.run(
        'python:3.9-alpine',
        command=['python', '-c', code],
        detach=True,
        mem_limit='128m',
        cpu_quota=50000,
        network_disabled=True,
        remove=True
    )
    
    # 获取执行结果
    result = container.wait()
    output = container.logs().decode('utf-8')
    
    return {
        'success': result['StatusCode'] == 0,
        'output': output
    }
```

## Selenium自动化支持

### 后端实现
```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def setup_selenium_driver():
    options = Options()
    options.add_argument('--headless')  # 无头模式
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    return driver

def execute_selenium_code(code):
    # 在代码前添加driver初始化
    full_code = f"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 自动初始化driver
driver = setup_selenium_driver()

try:
{code}
finally:
    driver.quit()
"""
    
    return execute_python_code(full_code)
```

## 测试用例

### 基础Python测试
```python
# 基础语法测试
print("Hello, World!")
for i in range(5):
    print(f"数字: {i}")

# 数据结构测试
data = [1, 2, 3, 4, 5]
result = sum(data)
print(f"总和: {result}")
```

### Selenium测试（需要后端支持）
```python
# 自动化测试示例
driver.get("https://www.baidu.com")
search_box = driver.find_element(By.ID, "kw")
search_box.send_keys("Python")
search_box.submit()

# 等待结果加载
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "content_left"))
)

print("搜索完成")
```

## 部署建议

### 开发环境
1. 使用Pyodide进行快速开发和测试
2. 后端API用于完整功能验证

### 生产环境
1. 推荐使用后端API + Docker容器
2. 配置负载均衡和监控
3. 实施严格的安全策略

## 安全注意事项

1. **代码审查**：检查危险函数调用
2. **资源限制**：CPU、内存、执行时间
3. **网络隔离**：禁止不必要的网络访问
4. **文件系统保护**：限制文件读写权限
5. **日志记录**：记录所有执行活动

## 性能优化

1. **代码缓存**：缓存编译结果
2. **连接池**：复用数据库连接
3. **异步执行**：支持并发执行
4. **资源回收**：及时清理临时资源

## 故障排除

### 常见问题
1. **Pyodide加载失败**：检查网络连接和CDN可用性
2. **后端API超时**：增加超时时间或优化代码
3. **内存不足**：限制代码复杂度或增加资源限制

### 调试技巧
1. 查看浏览器控制台错误
2. 检查网络请求状态
3. 验证后端服务运行状态
