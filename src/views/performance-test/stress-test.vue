<template>
  <div class="stress-test">
    <div class="page-header">
      <h1>🔧 压力测试工具</h1>
      <p>配置和执行系统压力测试，实时监控性能指标</p>
    </div>

    <el-row :gutter="20">
      <!-- 测试配置 -->
      <el-col :span="8">
        <el-card class="config-card">
          <div slot="header">
            <span>⚙️ 测试配置</span>
          </div>
          
          <el-form :model="testConfig" label-width="100px">
            <el-form-item label="测试类型">
              <el-select v-model="testConfig.type" placeholder="选择测试类型">
                <el-option label="HTTP压力测试" value="http"></el-option>
                <el-option label="CPU压力测试" value="cpu"></el-option>
                <el-option label="内存压力测试" value="memory"></el-option>
                <el-option label="磁盘I/O测试" value="disk"></el-option>
              </el-select>
            </el-form-item>

            <!-- HTTP测试配置 -->
            <div v-if="testConfig.type === 'http'">
              <el-form-item label="目标URL">
                <el-input v-model="testConfig.url" placeholder="http://example.com/api"></el-input>
              </el-form-item>
              <el-form-item label="请求方法">
                <el-select v-model="testConfig.method">
                  <el-option label="GET" value="GET"></el-option>
                  <el-option label="POST" value="POST"></el-option>
                  <el-option label="PUT" value="PUT"></el-option>
                  <el-option label="DELETE" value="DELETE"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="并发用户">
                <el-input-number v-model="testConfig.concurrent" :min="1" :max="1000"></el-input-number>
              </el-form-item>
              <el-form-item label="测试时长">
                <el-input-number v-model="testConfig.duration" :min="10" :max="3600" placeholder="秒"></el-input-number>
              </el-form-item>
            </div>

            <!-- CPU测试配置 -->
            <div v-if="testConfig.type === 'cpu'">
              <el-form-item label="CPU核心数">
                <el-input-number v-model="testConfig.cores" :min="1" :max="16"></el-input-number>
              </el-form-item>
              <el-form-item label="测试时长">
                <el-input-number v-model="testConfig.duration" :min="10" :max="3600" placeholder="秒"></el-input-number>
              </el-form-item>
              <el-form-item label="负载强度">
                <el-slider v-model="testConfig.intensity" :min="10" :max="100" show-stops></el-slider>
              </el-form-item>
            </div>

            <!-- 内存测试配置 -->
            <div v-if="testConfig.type === 'memory'">
              <el-form-item label="内存大小">
                <el-input-number v-model="testConfig.memorySize" :min="100" :max="8192" placeholder="MB"></el-input-number>
              </el-form-item>
              <el-form-item label="测试时长">
                <el-input-number v-model="testConfig.duration" :min="10" :max="3600" placeholder="秒"></el-input-number>
              </el-form-item>
              <el-form-item label="访问模式">
                <el-select v-model="testConfig.pattern">
                  <el-option label="顺序访问" value="sequential"></el-option>
                  <el-option label="随机访问" value="random"></el-option>
                </el-select>
              </el-form-item>
            </div>

            <!-- 磁盘测试配置 -->
            <div v-if="testConfig.type === 'disk'">
              <el-form-item label="文件大小">
                <el-input-number v-model="testConfig.fileSize" :min="10" :max="1024" placeholder="MB"></el-input-number>
              </el-form-item>
              <el-form-item label="测试时长">
                <el-input-number v-model="testConfig.duration" :min="10" :max="3600" placeholder="秒"></el-input-number>
              </el-form-item>
              <el-form-item label="操作类型">
                <el-select v-model="testConfig.operation">
                  <el-option label="读取" value="read"></el-option>
                  <el-option label="写入" value="write"></el-option>
                  <el-option label="读写混合" value="mixed"></el-option>
                </el-select>
              </el-form-item>
            </div>

            <el-form-item>
              <el-button 
                type="primary" 
                @click="startTest" 
                :loading="testing"
                :disabled="!isConfigValid"
              >
                {{ testing ? '测试中...' : '开始测试' }}
              </el-button>
              <el-button @click="stopTest" :disabled="!testing">停止测试</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 测试历史 -->
        <el-card class="history-card" style="margin-top: 20px;">
          <div slot="header">
            <span>📋 测试历史</span>
          </div>
          
          <div class="history-list">
            <div 
              v-for="(test, index) in testHistory" 
              :key="index"
              class="history-item"
              @click="viewTestResult(test)"
            >
              <div class="history-info">
                <div class="history-type">{{ getTestTypeName(test.type) }}</div>
                <div class="history-time">{{ formatTime(test.startTime) }}</div>
              </div>
              <div class="history-status" :class="test.status">
                {{ getStatusText(test.status) }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 实时监控 -->
      <el-col :span="16">
        <el-card class="monitor-card">
          <div slot="header">
            <span>📊 实时监控</span>
            <el-button 
              style="float: right; padding: 3px 0" 
              type="text" 
              @click="toggleMonitoring"
            >
              {{ monitoring ? '停止监控' : '开始监控' }}
            </el-button>
          </div>
          
          <!-- 监控图表 -->
          <div class="monitor-charts">
            <el-row :gutter="20">
              <el-col :span="12">
                <div class="chart-container">
                  <h4>CPU使用率</h4>
                  <div ref="cpuChart" class="chart"></div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="chart-container">
                  <h4>内存使用率</h4>
                  <div ref="memoryChart" class="chart"></div>
                </div>
              </el-col>
            </el-row>
            
            <el-row :gutter="20" style="margin-top: 20px;">
              <el-col :span="12">
                <div class="chart-container">
                  <h4>网络I/O</h4>
                  <div ref="networkChart" class="chart"></div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="chart-container">
                  <h4>磁盘I/O</h4>
                  <div ref="diskChart" class="chart"></div>
                </div>
              </el-col>
            </el-row>
          </div>

          <!-- 实时指标 -->
          <div class="metrics-panel">
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="metric-item">
                  <div class="metric-value">{{ currentMetrics.cpu }}%</div>
                  <div class="metric-label">CPU使用率</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-item">
                  <div class="metric-value">{{ currentMetrics.memory }}%</div>
                  <div class="metric-label">内存使用率</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-item">
                  <div class="metric-value">{{ currentMetrics.network }}</div>
                  <div class="metric-label">网络速度</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-item">
                  <div class="metric-value">{{ currentMetrics.disk }}</div>
                  <div class="metric-label">磁盘I/O</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>

        <!-- 测试结果 -->
        <el-card v-if="testResult" class="result-card" style="margin-top: 20px;">
          <div slot="header">
            <span>📈 测试结果</span>
          </div>
          
          <div class="result-content">
            <el-row :gutter="20">
              <el-col :span="8">
                <div class="result-item">
                  <div class="result-label">测试类型</div>
                  <div class="result-value">{{ getTestTypeName(testResult.type) }}</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="result-item">
                  <div class="result-label">测试时长</div>
                  <div class="result-value">{{ testResult.duration }}秒</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="result-item">
                  <div class="result-label">测试状态</div>
                  <div class="result-value" :class="testResult.status">
                    {{ getStatusText(testResult.status) }}
                  </div>
                </div>
              </el-col>
            </el-row>

            <!-- HTTP测试结果 -->
            <div v-if="testResult.type === 'http'" class="http-results">
              <el-row :gutter="20" style="margin-top: 20px;">
                <el-col :span="6">
                  <div class="result-item">
                    <div class="result-label">总请求数</div>
                    <div class="result-value">{{ testResult.totalRequests }}</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="result-item">
                    <div class="result-label">成功请求</div>
                    <div class="result-value">{{ testResult.successRequests }}</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="result-item">
                    <div class="result-label">平均响应时间</div>
                    <div class="result-value">{{ testResult.avgResponseTime }}ms</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="result-item">
                    <div class="result-label">QPS</div>
                    <div class="result-value">{{ testResult.qps }}</div>
                  </div>
                </el-col>
              </el-row>
            </div>

            <!-- 性能指标图表 -->
            <div class="result-charts" style="margin-top: 20px;">
              <div ref="resultChart" class="chart" style="height: 300px;"></div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'StressTest',
  data() {
    return {
      testConfig: {
        type: 'http',
        url: '',
        method: 'GET',
        concurrent: 10,
        duration: 60,
        cores: 4,
        intensity: 80,
        memorySize: 512,
        pattern: 'sequential',
        fileSize: 100,
        operation: 'mixed'
      },
      testing: false,
      monitoring: false,
      testResult: null,
      testHistory: [],
      currentMetrics: {
        cpu: 0,
        memory: 0,
        network: '0 KB/s',
        disk: '0 KB/s'
      },
      charts: {
        cpu: null,
        memory: null,
        network: null,
        disk: null,
        result: null
      },
      monitoringData: {
        cpu: [],
        memory: [],
        network: [],
        disk: [],
        timestamps: []
      },
      monitoringTimer: null
    }
  },
  computed: {
    isConfigValid() {
      if (this.testConfig.type === 'http') {
        return this.testConfig.url && this.testConfig.concurrent > 0 && this.testConfig.duration > 0
      }
      return this.testConfig.duration > 0
    }
  },
  mounted() {
    this.initCharts()
    this.loadTestHistory()
  },
  methods: {
    async startTest() {
      this.testing = true
      this.testResult = null
      
      try {
        // 模拟测试执行
        const response = await this.executeTest()
        this.testResult = response
        this.addToHistory(response)
        this.$message.success('测试完成')
      } catch (error) {
        this.$message.error('测试失败: ' + error.message)
      } finally {
        this.testing = false
      }
    },

    stopTest() {
      this.testing = false
      this.$message.info('测试已停止')
    },

    async executeTest() {
      // 模拟测试执行过程
      return new Promise((resolve) => {
        setTimeout(() => {
          const result = {
            type: this.testConfig.type,
            duration: this.testConfig.duration,
            status: 'completed',
            startTime: new Date(),
            endTime: new Date(Date.now() + this.testConfig.duration * 1000)
          }

          if (this.testConfig.type === 'http') {
            result.totalRequests = this.testConfig.concurrent * this.testConfig.duration
            result.successRequests = Math.floor(result.totalRequests * 0.95)
            result.avgResponseTime = Math.floor(Math.random() * 200 + 50)
            result.qps = Math.floor(result.totalRequests / this.testConfig.duration)
          }

          resolve(result)
        }, 2000)
      })
    },

    toggleMonitoring() {
      if (this.monitoring) {
        this.stopMonitoring()
      } else {
        this.startMonitoring()
      }
    },

    startMonitoring() {
      this.monitoring = true
      this.monitoringTimer = setInterval(() => {
        this.updateMetrics()
      }, 1000)
    },

    stopMonitoring() {
      this.monitoring = false
      if (this.monitoringTimer) {
        clearInterval(this.monitoringTimer)
        this.monitoringTimer = null
      }
    },

    updateMetrics() {
      // 模拟实时指标数据
      const cpu = Math.floor(Math.random() * 100)
      const memory = Math.floor(Math.random() * 100)
      const network = Math.floor(Math.random() * 1000)
      const disk = Math.floor(Math.random() * 500)

      this.currentMetrics = {
        cpu: cpu,
        memory: memory,
        network: `${network} KB/s`,
        disk: `${disk} KB/s`
      }

      // 更新图表数据
      const now = new Date().toLocaleTimeString()
      this.monitoringData.timestamps.push(now)
      this.monitoringData.cpu.push(cpu)
      this.monitoringData.memory.push(memory)
      this.monitoringData.network.push(network)
      this.monitoringData.disk.push(disk)

      // 保持最近50个数据点
      if (this.monitoringData.timestamps.length > 50) {
        this.monitoringData.timestamps.shift()
        this.monitoringData.cpu.shift()
        this.monitoringData.memory.shift()
        this.monitoringData.network.shift()
        this.monitoringData.disk.shift()
      }

      this.updateCharts()
    },

    initCharts() {
      this.$nextTick(() => {
        if (this.$refs.cpuChart) {
          this.charts.cpu = echarts.init(this.$refs.cpuChart)
        }
        if (this.$refs.memoryChart) {
          this.charts.memory = echarts.init(this.$refs.memoryChart)
        }
        if (this.$refs.networkChart) {
          this.charts.network = echarts.init(this.$refs.networkChart)
        }
        if (this.$refs.diskChart) {
          this.charts.disk = echarts.init(this.$refs.diskChart)
        }
      })
    },

    updateCharts() {
      const baseOption = {
        tooltip: { trigger: 'axis' },
        xAxis: {
          type: 'category',
          data: this.monitoringData.timestamps
        },
        yAxis: { type: 'value' },
        series: [{
          type: 'line',
          smooth: true,
          areaStyle: { opacity: 0.3 }
        }]
      }

      if (this.charts.cpu) {
        this.charts.cpu.setOption({
          ...baseOption,
          series: [{
            ...baseOption.series[0],
            data: this.monitoringData.cpu,
            itemStyle: { color: '#409EFF' }
          }]
        })
      }

      if (this.charts.memory) {
        this.charts.memory.setOption({
          ...baseOption,
          series: [{
            ...baseOption.series[0],
            data: this.monitoringData.memory,
            itemStyle: { color: '#67C23A' }
          }]
        })
      }

      if (this.charts.network) {
        this.charts.network.setOption({
          ...baseOption,
          series: [{
            ...baseOption.series[0],
            data: this.monitoringData.network,
            itemStyle: { color: '#E6A23C' }
          }]
        })
      }

      if (this.charts.disk) {
        this.charts.disk.setOption({
          ...baseOption,
          series: [{
            ...baseOption.series[0],
            data: this.monitoringData.disk,
            itemStyle: { color: '#F56C6C' }
          }]
        })
      }
    },

    getTestTypeName(type) {
      const names = {
        http: 'HTTP压力测试',
        cpu: 'CPU压力测试',
        memory: '内存压力测试',
        disk: '磁盘I/O测试'
      }
      return names[type] || type
    },

    getStatusText(status) {
      const texts = {
        running: '运行中',
        completed: '已完成',
        failed: '失败',
        stopped: '已停止'
      }
      return texts[status] || status
    },

    formatTime(time) {
      return new Date(time).toLocaleString()
    },

    addToHistory(result) {
      this.testHistory.unshift(result)
      if (this.testHistory.length > 10) {
        this.testHistory.pop()
      }
      this.saveTestHistory()
    },

    loadTestHistory() {
      const history = localStorage.getItem('stressTestHistory')
      if (history) {
        this.testHistory = JSON.parse(history)
      }
    },

    saveTestHistory() {
      localStorage.setItem('stressTestHistory', JSON.stringify(this.testHistory))
    },

    viewTestResult(test) {
      this.testResult = test
    }
  },

  beforeDestroy() {
    this.stopMonitoring()
    Object.values(this.charts).forEach(chart => {
      if (chart) {
        chart.dispose()
      }
    })
  }
}
</script>

<style scoped>
.stress-test {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
}

.page-header h1 {
  font-size: 2.5em;
  color: #2c3e50;
  margin-bottom: 10px;
}

.page-header p {
  font-size: 1.1em;
  color: #666;
}

.config-card, .history-card, .monitor-card, .result-card {
  height: fit-content;
}

.history-list {
  max-height: 300px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  margin-bottom: 8px;
  background: #f8f9fa;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.history-item:hover {
  background: #e9ecef;
}

.history-info {
  flex: 1;
}

.history-type {
  font-weight: bold;
  color: #2c3e50;
}

.history-time {
  font-size: 0.9em;
  color: #666;
  margin-top: 5px;
}

.history-status {
  padding: 4px 8px;
  border-radius: 3px;
  font-size: 0.8em;
  font-weight: bold;
}

.history-status.running {
  background: #fff3cd;
  color: #856404;
}

.history-status.completed {
  background: #d4edda;
  color: #155724;
}

.history-status.failed {
  background: #f8d7da;
  color: #721c24;
}

.history-status.stopped {
  background: #e2e3e5;
  color: #383d41;
}

.monitor-charts {
  margin-bottom: 20px;
}

.chart-container {
  text-align: center;
}

.chart-container h4 {
  margin-bottom: 10px;
  color: #2c3e50;
}

.chart {
  height: 200px;
  width: 100%;
}

.metrics-panel {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 5px;
}

.metric-item {
  text-align: center;
}

.metric-value {
  font-size: 2em;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 5px;
}

.metric-label {
  color: #666;
  font-size: 0.9em;
}

.result-content {
  margin-top: 15px;
}

.result-item {
  text-align: center;
  margin-bottom: 15px;
}

.result-label {
  color: #666;
  font-size: 0.9em;
  margin-bottom: 5px;
}

.result-value {
  font-size: 1.5em;
  font-weight: bold;
  color: #2c3e50;
}

.result-value.completed {
  color: #67C23A;
}

.result-value.failed {
  color: #F56C6C;
}

.result-value.running {
  color: #E6A23C;
}

.http-results {
  border-top: 1px solid #e9ecef;
  padding-top: 20px;
}

.result-charts {
  border-top: 1px solid #e9ecef;
  padding-top: 20px;
}

@media (max-width: 768px) {
  .stress-test {
    padding: 10px;
  }

  .chart {
    height: 150px;
  }

  .metric-value {
    font-size: 1.5em;
  }
}
</style>
