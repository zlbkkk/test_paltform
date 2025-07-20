#!/usr/bin/env python3
"""
Python代码执行后端API示例
支持安全执行用户提交的Python代码
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import tempfile
import os
import time
import signal
import threading
import sys
import io
from contextlib import redirect_stdout, redirect_stderr

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 安全配置
EXECUTION_TIMEOUT = 30  # 执行超时时间（秒）
MAX_OUTPUT_SIZE = 10000  # 最大输出大小（字符）

# 危险关键词黑名单
DANGEROUS_KEYWORDS = [
    'import os', 'import sys', 'import subprocess', 'import shutil',
    'open(', 'file(', 'exec(', 'eval(', '__import__',
    'input(', 'raw_input(', 'compile(', 'reload(',
    'exit(', 'quit(', 'help(', 'dir(',
    'globals(', 'locals(', 'vars(', 'delattr(',
    'setattr(', 'getattr(', 'hasattr(',
]

def is_safe_code(code):
    """检查代码是否安全"""
    code_lower = code.lower()
    
    # 检查危险关键词
    for keyword in DANGEROUS_KEYWORDS:
        if keyword.lower() in code_lower:
            return False, f"不允许使用: {keyword}"
    
    # 检查文件操作
    if any(word in code_lower for word in ['open(', 'file(', 'write(', 'read(']):
        return False, "不允许文件操作"
    
    # 检查网络操作
    if any(word in code_lower for word in ['socket', 'urllib', 'requests', 'http']):
        return False, "不允许网络操作"
    
    return True, "代码安全"

def execute_python_code(code, timeout=EXECUTION_TIMEOUT):
    """在受限环境中执行Python代码"""
    try:
        # 创建字符串缓冲区捕获输出
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        # 受限的全局环境
        restricted_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'sum': sum,
                'max': max,
                'min': min,
                'abs': abs,
                'round': round,
                'sorted': sorted,
                'reversed': reversed,
                'type': type,
                'isinstance': isinstance,
                'issubclass': issubclass,
            }
        }
        
        start_time = time.time()
        
        # 重定向输出
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            # 使用exec执行代码
            exec(code, restricted_globals)
        
        execution_time = time.time() - start_time
        
        stdout_content = stdout_buffer.getvalue()
        stderr_content = stderr_buffer.getvalue()
        
        # 限制输出大小
        if len(stdout_content) > MAX_OUTPUT_SIZE:
            stdout_content = stdout_content[:MAX_OUTPUT_SIZE] + "\n... (输出被截断)"
        
        return {
            'success': True,
            'output': stdout_content,
            'error': stderr_content,
            'execution_time': round(execution_time, 3)
        }
        
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': str(e),
            'execution_time': 0
        }

def execute_selenium_code(code):
    """执行Selenium自动化代码（需要特殊处理）"""
    # 这里可以添加Selenium特定的执行逻辑
    # 比如启动无头浏览器等
    return execute_python_code(code)

@app.route('/api/execute-script', methods=['POST'])
def execute_script():
    """执行脚本API端点"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code.strip():
            return jsonify({
                'success': False,
                'error': '代码内容不能为空'
            })
        
        # 安全检查
        is_safe, message = is_safe_code(code)
        if not is_safe:
            return jsonify({
                'success': False,
                'error': f'安全检查失败: {message}'
            })
        
        # 根据语言类型执行
        if language == 'python':
            # 检查是否是Selenium代码
            if 'selenium' in code.lower() or 'webdriver' in code.lower():
                result = execute_selenium_code(code)
            else:
                result = execute_python_code(code)
        else:
            return jsonify({
                'success': False,
                'error': f'暂不支持 {language} 语言'
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        })

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'message': 'Python执行服务运行正常'
    })

if __name__ == '__main__':
    print("启动Python代码执行服务...")
    print("访问 http://localhost:5000/api/health 检查服务状态")
    app.run(host='0.0.0.0', port=5000, debug=True)
