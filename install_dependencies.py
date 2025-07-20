#!/usr/bin/env python3
"""
安装服务器监控所需的依赖库
"""

import subprocess
import sys
import os

def install_package(package):
    """安装Python包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_package(package):
    """检查包是否已安装"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def main():
    """主函数"""
    print("🚀 开始安装服务器监控依赖库...")
    print("=" * 50)
    
    # 需要安装的包
    packages = {
        'paramiko': 'SSH连接库',
        'psutil': '系统监控库',
        'cryptography': 'SSH加密库（paramiko依赖）'
    }
    
    success_count = 0
    total_count = len(packages)
    
    for package, description in packages.items():
        print(f"\n📦 检查 {package} ({description})...")
        
        if check_package(package):
            print(f"✅ {package} 已安装")
            success_count += 1
        else:
            print(f"⏳ 正在安装 {package}...")
            if install_package(package):
                print(f"✅ {package} 安装成功")
                success_count += 1
            else:
                print(f"❌ {package} 安装失败")
    
    print("\n" + "=" * 50)
    print(f"📊 安装结果: {success_count}/{total_count} 个包安装成功")
    
    if success_count == total_count:
        print("🎉 所有依赖库安装完成！")
        print("\n📋 功能说明:")
        print("   - paramiko: 支持SSH连接到远程服务器")
        print("   - psutil: 获取本地系统监控数据")
        print("   - cryptography: 提供SSH加密支持")
        
        print("\n🚀 现在可以使用以下功能:")
        print("   ✅ 真实SSH连接测试")
        print("   ✅ 远程服务器监控数据获取")
        print("   ✅ 本地系统监控")
        print("   ✅ 密码和密钥认证")
        
        print("\n💡 使用提示:")
        print("   1. 重启Flask服务器: python simple_server.py")
        print("   2. 在监控界面配置真实服务器")
        print("   3. 测试连接并查看监控数据")
        
    else:
        print("⚠️  部分依赖库安装失败")
        print("\n🔧 手动安装命令:")
        for package in packages:
            if not check_package(package):
                print(f"   pip install {package}")
        
        print("\n📝 常见问题解决:")
        print("   1. 网络问题: 使用国内镜像源")
        print("      pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ paramiko psutil")
        print("   2. 权限问题: 使用管理员权限运行")
        print("   3. Python版本: 确保使用Python 3.6+")

if __name__ == "__main__":
    main()
