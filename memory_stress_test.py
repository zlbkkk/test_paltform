#!/usr/bin/env python3
"""
内存性能测试脚本
用于模拟内存波动，测试前端监控系统的实时显示能力
"""

import time
import gc
import threading
import psutil
from datetime import datetime

class MemoryStressTest:
    def __init__(self):
        self.memory_blocks = []
        self.running = False
        self.test_thread = None
        
    def get_memory_info(self):
        """获取当前内存使用情况"""
        memory = psutil.virtual_memory()
        process = psutil.Process()
        process_memory = process.memory_info()
        
        return {
            'system_total': memory.total / (1024**3),  # GB
            'system_used': memory.used / (1024**3),   # GB
            'system_percent': memory.percent,
            'process_rss': process_memory.rss / (1024**2),  # MB
            'process_vms': process_memory.vms / (1024**2),  # MB
        }
    
    def allocate_memory(self, size_mb):
        """分配指定大小的内存（安全模式，不超过70%）"""
        # 检查分配前的内存使用率
        current_memory = psutil.virtual_memory()
        current_percent = current_memory.percent

        # 预估分配后的内存使用率
        estimated_usage = current_percent + (size_mb * 1024 * 1024 / current_memory.total * 100)

        if estimated_usage > 70:
            print(f"⚠️  安全检查: 分配 {size_mb}MB 会导致内存使用率达到 {estimated_usage:.1f}%，超过70%限制")
            print(f"📊 当前内存使用率: {current_percent:.1f}%")
            return False

        try:
            # 创建一个大的字节数组来占用内存
            size_bytes = size_mb * 1024 * 1024
            memory_block = bytearray(size_bytes)

            # 写入一些数据确保内存真正被使用（减少写入频率以提高性能）
            for i in range(0, size_bytes, 8192):  # 每8KB写入一次
                memory_block[i] = i % 256

            self.memory_blocks.append(memory_block)

            # 再次检查实际内存使用率
            new_memory = psutil.virtual_memory()
            print(f"✅ 安全分配了 {size_mb}MB 内存，内存使用率: {new_memory.percent:.1f}%，总块数: {len(self.memory_blocks)}")

        except MemoryError:
            print(f"❌ 内存分配失败: 无法分配 {size_mb}MB")
            return False
        return True
    
    def release_memory(self, count=1):
        """释放指定数量的内存块"""
        released = 0
        for _ in range(min(count, len(self.memory_blocks))):
            if self.memory_blocks:
                self.memory_blocks.pop()
                released += 1
        
        if released > 0:
            gc.collect()  # 强制垃圾回收
            print(f"🗑️  释放了 {released} 个内存块，剩余: {len(self.memory_blocks)}")
        
        return released

    def emergency_safety_check(self):
        """紧急安全检查，确保内存使用率不超过70%"""
        memory_info = self.get_memory_info()
        if memory_info['system_percent'] > 70:
            print(f"🚨 紧急安全检查触发！当前内存使用率: {memory_info['system_percent']:.1f}%")
            release_count = len(self.memory_blocks) // 2
            if release_count > 0:
                self.release_memory(release_count)
                print(f"🛡️  紧急释放了 {release_count} 个内存块")
                time.sleep(3)
                return True
        return False

    def memory_wave_pattern(self, duration_minutes=None):
        """执行波浪式内存使用模式 - 支持死循环"""
        if duration_minutes:
            print(f"🌊 开始波浪式内存测试，持续 {duration_minutes} 分钟")
            start_time = time.time()
            end_time = start_time + (duration_minutes * 60)
        else:
            print(f"🌊 开始波浪式内存测试，死循环模式 (按 Ctrl+C 停止)")
            end_time = None

        phase = 0
        while self.running and (end_time is None or time.time() < end_time):
            current_time = datetime.now().strftime('%H:%M:%S')
            memory_info = self.get_memory_info()
            
            print(f"\n⏰ {current_time} - 阶段 {phase + 1}")
            print(f"📊 系统内存: {memory_info['system_percent']:.1f}% "
                  f"({memory_info['system_used']:.1f}GB / {memory_info['system_total']:.1f}GB)")
            print(f"🔍 进程内存: RSS={memory_info['process_rss']:.1f}MB, "
                  f"VMS={memory_info['process_vms']:.1f}MB")
            
            # 安全的波浪式内存分配模式（保持在70%以下）
            if phase % 4 == 0:
                # 阶段1: 小量快速分配
                print("📈 小量快速分配阶段")
                for _ in range(3):
                    if not self.allocate_memory(20):  # 每次20MB，更安全
                        break
                    time.sleep(3)

            elif phase % 4 == 1:
                # 阶段2: 持续小量分配
                print("📊 持续小量分配阶段")
                for _ in range(4):
                    if not self.allocate_memory(15):  # 每次15MB
                        break
                    time.sleep(4)

            elif phase % 4 == 2:
                # 阶段3: 部分释放后适量分配
                print("📉 部分释放阶段")
                self.release_memory(2)
                time.sleep(5)
                if self.allocate_memory(25):  # 分配一个中等块
                    time.sleep(5)

            else:
                # 阶段4: 大量释放
                print("🗑️  大量释放阶段")
                release_count = max(1, len(self.memory_blocks) // 3)  # 释放1/3而不是1/2
                self.release_memory(release_count)
                time.sleep(8)

            phase += 1

            # 每个阶段后进行安全检查
            self.emergency_safety_check()

            # 安全检查：如果内存使用率超过65%就主动释放
            if memory_info['system_percent'] > 65:
                print("⚠️  内存使用率超过65%，主动释放内存保持安全")
                self.release_memory(2)
                time.sleep(3)
        
        print(f"\n🏁 波浪式测试完成")
    
    def memory_spike_pattern(self, spike_count=None):
        """执行安全的内存尖峰模式（保持在70%以下）- 支持死循环"""
        if spike_count:
            print(f"⚡ 开始安全内存尖峰测试，{spike_count} 次尖峰")
            max_spikes = spike_count
        else:
            print(f"⚡ 开始安全内存尖峰测试，死循环模式 (按 Ctrl+C 停止)")
            max_spikes = float('inf')

        i = 0
        while i < max_spikes and self.running:
            if not self.running:
                break

            current_time = datetime.now().strftime('%H:%M:%S')
            if spike_count:
                print(f"\n⚡ {current_time} - 尖峰 {i + 1}/{spike_count}")
            else:
                print(f"\n⚡ {current_time} - 尖峰 {i + 1} (死循环模式)")

            # 安全的尖峰大小，从30MB开始，每次增加5MB，循环重置
            spike_size = 30 + ((i % 10) * 5)  # 每10次循环重置大小
            print(f"📈 尝试分配 {spike_size}MB 安全内存尖峰")

            if self.allocate_memory(spike_size):
                # 保持尖峰一段时间
                print(f"✅ 尖峰创建成功，保持8秒")
                time.sleep(8)

                # 快速释放
                print("📉 释放尖峰内存")
                self.release_memory(1)

                # 等待观察期
                time.sleep(10)
            else:
                print("⚠️  尖峰分配被安全机制阻止，等待后继续")
                # 如果分配失败，释放一些现有内存后继续
                if len(self.memory_blocks) > 0:
                    self.release_memory(1)
                time.sleep(8)

            i += 1  # 递增计数器

        print(f"\n🏁 安全尖峰测试完成")
    
    def gradual_increase_pattern(self, duration_minutes=None):
        """执行安全的渐进式内存增长模式（保持在70%以下）- 支持死循环"""
        if duration_minutes:
            print(f"📈 开始安全渐进式内存增长测试，持续 {duration_minutes} 分钟")
            start_time = time.time()
            end_time = start_time + (duration_minutes * 60)
        else:
            print(f"📈 开始安全渐进式内存增长测试，死循环模式 (按 Ctrl+C 停止)")
            end_time = None

        allocation_size = 10  # 更小的起始分配大小
        cycle_count = 0  # 循环计数器

        while self.running and (end_time is None or time.time() < end_time):
            current_time = datetime.now().strftime('%H:%M:%S')
            memory_info = self.get_memory_info()

            cycle_count += 1
            print(f"\n📈 {current_time} - 循环 {cycle_count} - 尝试分配 {allocation_size}MB")
            print(f"📊 当前系统内存使用: {memory_info['system_percent']:.1f}%")

            if self.allocate_memory(allocation_size):
                allocation_size += 5  # 每次只增加5MB，更安全
                time.sleep(20)  # 更长的间隔时间
            else:
                print("⚠️  分配被安全机制阻止，保持当前内存水平")
                # 不增加分配大小，保持当前水平
                time.sleep(15)

            # 安全检查：如果内存使用率超过65%
            if memory_info['system_percent'] > 65:
                if duration_minutes:  # 有时间限制的模式
                    print("⚠️  内存使用率超过65%，停止增长以保持安全")
                    break
                else:  # 死循环模式
                    print("⚠️  内存使用率超过65%，释放内存并重置循环")
                    self.release_memory(len(self.memory_blocks) // 2)
                    allocation_size = 10
                    time.sleep(10)

            # 如果分配大小变得太大，重置为较小值
            if allocation_size > 50:
                print("📉 分配大小过大，重置为较小值")
                allocation_size = 15

        print(f"\n🏁 安全渐进式测试完成")
    
    def start_test(self, test_type='wave', duration=None):
        """开始内存测试 - 默认死循环模式"""
        if self.running:
            print("❌ 测试已在运行中")
            return

        self.running = True

        def test_worker():
            try:
                if duration:
                    print(f"🚀 开始内存性能测试 - 类型: {test_type}, 持续: {duration}分钟")
                else:
                    print(f"� 开始内存性能测试 - 类型: {test_type}, 死循环模式")
                print(f"�💡 提示: 请在前端监控页面观察内存使用率变化")
                print(f"🔄 按 Ctrl+C 停止测试")

                initial_memory = self.get_memory_info()
                print(f"\n📊 初始内存状态:")
                print(f"   系统内存: {initial_memory['system_percent']:.1f}%")
                print(f"   进程内存: {initial_memory['process_rss']:.1f}MB")

                if test_type == 'wave':
                    self.memory_wave_pattern(duration)
                elif test_type == 'spike':
                    self.memory_spike_pattern(duration)
                elif test_type == 'gradual':
                    self.gradual_increase_pattern(duration)
                else:
                    print(f"❌ 未知的测试类型: {test_type}")

            except Exception as e:
                print(f"❌ 测试过程中出错: {e}")
            finally:
                self.cleanup()

        self.test_thread = threading.Thread(target=test_worker)
        self.test_thread.start()
    
    def stop_test(self):
        """停止测试"""
        print("\n🛑 正在停止测试...")
        self.running = False
        if self.test_thread:
            self.test_thread.join()
        self.cleanup()
    
    def cleanup(self):
        """清理所有分配的内存"""
        print(f"\n🧹 清理内存，释放 {len(self.memory_blocks)} 个内存块")
        self.memory_blocks.clear()
        gc.collect()
        
        final_memory = self.get_memory_info()
        print(f"✅ 清理完成")
        print(f"📊 最终内存状态:")
        print(f"   系统内存: {final_memory['system_percent']:.1f}%")
        print(f"   进程内存: {final_memory['process_rss']:.1f}MB")

def main():
    """主函数"""
    print("🧪 安全内存性能测试工具")
    print("=" * 60)
    print("🛡️  安全特性:")
    print("   • 内存使用率严格控制在70%以下")
    print("   • 多重安全检查机制")
    print("   • 自动释放机制防止系统崩溃")
    print("   • 死循环模式，持续运行直到手动停止")
    print("=" * 60)
    print("测试模式:")
    print("1. wave   - 安全波浪式内存使用 (推荐，死循环)")
    print("2. spike  - 安全内存尖峰测试 (死循环)")
    print("3. gradual - 安全渐进式内存增长 (死循环)")
    print("\n💡 所有模式都是死循环，按 Ctrl+C 停止")
    print("=" * 60)
    
    tester = MemoryStressTest()
    
    try:
        # 默认执行波浪式测试，死循环模式
        tester.start_test('wave')  # 不传duration参数，默认死循环

        # 等待测试完成（或用户中断）
        if tester.test_thread:
            tester.test_thread.join()
            
    except KeyboardInterrupt:
        print("\n\n⚠️  收到中断信号")
        tester.stop_test()
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        tester.cleanup()

if __name__ == "__main__":
    main()
