import os
import requests
import threading
import time
import random
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

# 配置参数
TEST_FILE_SIZE_MB = 10          # 测试文件大小(MB)
TEST_DURATION = 0               # 测试持续时间(秒)，0表示无限
UPLOAD_ENDPOINT = "http://104.168.64.206/upload"  # 上传端点
DOWNLOAD_ENDPOINT = "http://104.168.64.206/download"  # 下载端点
THREAD_COUNT = 4                # 并发线程数

# 统计变量
total_uploaded = 0
total_downloaded = 0
running = True

def create_test_file(filename, size_mb):
    """创建测试文件"""
    chunk_size = 1024 * 1024  # 1MB
    with open(filename, 'wb') as f:
        for _ in range(size_mb):
            f.write(os.urandom(chunk_size))

def upload_file(filename):
    """模拟文件上传"""
    global total_uploaded
    try:
        with open(filename, 'rb') as f:
            files = {'file': (filename, f)}
            response = requests.post(UPLOAD_ENDPOINT, files=files)
            if response.status_code == 200:
                total_uploaded += os.path.getsize(filename)
    except Exception as e:
        print(f"Upload error: {e}")

def download_file():
    """模拟文件下载"""
    global total_downloaded
    try:
        response = requests.get(DOWNLOAD_ENDPOINT, stream=True)
        if response.status_code == 200:
            content_length = int(response.headers.get('content-length', 0))
            # 实际不保存文件，只计算流量
            for chunk in response.iter_content(chunk_size=8192):
                if not chunk:
                    break
                total_downloaded += len(chunk)
    except Exception as e:
        print(f"Download error: {e}")

def worker():
    """工作线程函数"""
    test_file = f"test_{threading.get_ident()}.bin"
    create_test_file(test_file, TEST_FILE_SIZE_MB)
    
    while running:
        # 随机选择上传或下载
        if random.random() > 0.5:
            upload_file(test_file)
        else:
            download_file()
        
        # 添加随机延迟模拟真实用户行为
        time.sleep(random.uniform(0.1, 1.0))
    
    # 清理测试文件
    if os.path.exists(test_file):
        os.remove(test_file)

def print_stats():
    """打印统计信息"""
    start_time = time.time()
    
    while running:
        elapsed = time.time() - start_time
        up_mb = total_uploaded / (1024 * 1024)
        down_mb = total_downloaded / (1024 * 1024)
        
        print(f"\rUploaded: {up_mb:.2f} MB | Downloaded: {down_mb:.2f} MB | "
              f"Duration: {elapsed:.1f}s | Total: {up_mb + down_mb:.2f} MB", end="")
        sys.stdout.flush()
        time.sleep(1)

def start_local_server():
    """启动本地HTTP服务器用于测试"""
    port = 000
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"Local test server running on port {port}")
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return f"http://localhost:{port}"

def main():
    global running, UPLOAD_ENDPOINT, DOWNLOAD_ENDPOINT
    
    print("Starting network traffic test (simulated upload/download)")
    
    # 如果没有提供端点，启动本地测试服务器
    if UPLOAD_ENDPOINT == "http://104.168.64.206/upload":
        print("No endpoint provided, starting local test server...")
        base_url = start_local_server()
        UPLOAD_ENDPOINT = f"{base_url}/upload"
        DOWNLOAD_ENDPOINT = f"{base_url}/test.bin"
        
        # 创建测试文件
        create_test_file("test.bin", TEST_FILE_SIZE_MB)
    
    # 启动统计线程
    threading.Thread(target=print_stats, daemon=True).start()
    
    # 启动工作线程
    threads = []
    for _ in range(THREAD_COUNT):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)
    
    try:
        # 如果设置了持续时间，等待相应时间
        if TEST_DURATION > 0:
            time.sleep(TEST_DURATION)
            running = False
        else:
            # 无限运行，直到用户中断
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping test...")
        running = False
    
    # 等待所有线程结束
    for t in threads:
        t.join()
    
    print("\nTest completed.")

if __name__ == "__main__":
    main()