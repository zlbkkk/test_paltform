<template>
  <div class="server-monitor">
    <!-- 顶部控制栏 -->
    <div class="monitor-header">
      <div class="server-selector">
        <el-select v-model="selectedServer" placeholder="选择服务器" @change="onServerChange">
          <el-option
            v-for="server in servers"
            :key="server.id"
            :label="`${server.name} (${server.host})`"
            :value="server.id"
          >
          </el-option>
        </el-select>
        <el-button type="primary" @click="showServerConfig = true">配置服务器</el-button>
      </div>
      
      <div class="time-controls">
        <el-select v-model="timeRange" @change="onTimeRangeChange">
          <el-option label="最近5分钟" value="5m"></el-option>
          <el-option label="最近15分钟" value="15m"></el-option>
          <el-option label="最近1小时" value="1h"></el-option>
          <el-option label="最近6小时" value="6h"></el-option>
          <el-option label="最近24小时" value="24h"></el-option>
        </el-select>
        
        <el-button @click="refreshData" :loading="loading">
          <i class="el-icon-refresh"></i> 刷新
        </el-button>
        
        <el-switch
          v-model="autoRefresh"
          active-text="自动刷新"
          @change="toggleAutoRefresh"
        ></el-switch>
      </div>
    </div>

    <!-- 服务器状态概览 -->
    <div v-if="selectedServer" class="server-overview">
      <div class="server-info">
        <h2>{{ currentServerInfo.name }}</h2>
        <div class="server-details">
          <span>{{ currentServerInfo.host }}:{{ currentServerInfo.port }}</span>
          <el-tag :type="connectionStatus === 'connected' ? 'success' : 'danger'" size="small">
            {{ connectionStatus === 'connected' ? '已连接' : '连接失败' }}
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 关键指标卡片 -->
    <div v-if="selectedServer && connectionStatus === 'connected'" class="metrics-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="metric-card cpu">
            <div class="metric-icon">
              <i class="el-icon-cpu"></i>
            </div>
            <div class="metric-content">
              <div class="metric-value" :class="getCpuStatusClass(currentMetrics.cpu)">
                {{ currentMetrics.cpu }}%
              </div>
              <div class="metric-label">CPU使用率</div>
              <div class="metric-detail">
                负载: {{ currentMetrics.load_avg }}
              </div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="metric-card memory">
            <div class="metric-icon">
              <i class="el-icon-memory-card"></i>
            </div>
            <div class="metric-content">
              <div class="metric-value" :class="getMemoryStatusClass(currentMetrics.memory_percent)">
                {{ currentMetrics.memory_percent }}%
              </div>
              <div class="metric-label">内存使用率</div>
              <div class="metric-detail">
                {{ currentMetrics.memory_used }}GB / {{ currentMetrics.memory_total }}GB
              </div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="metric-card disk">
            <div class="metric-icon">
              <i class="el-icon-folder"></i>
            </div>
            <div class="metric-content">
              <div class="metric-value" :class="getDiskStatusClass(currentMetrics.disk_percent)">
                {{ currentMetrics.disk_percent }}%
              </div>
              <div class="metric-label">磁盘使用率</div>
              <div class="metric-detail">
                剩余: {{ currentMetrics.disk_free }}GB
              </div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="metric-card network">
            <div class="metric-icon">
              <i class="el-icon-connection"></i>
            </div>
            <div class="metric-content">
              <div class="metric-value">
                {{ formatBytes(currentMetrics.network_sent) }}/s
              </div>
              <div class="metric-label">网络发送</div>
              <div class="metric-detail">
                接收: {{ formatBytes(currentMetrics.network_recv) }}/s
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 图表区域 -->
    <div v-if="selectedServer && connectionStatus === 'connected'" class="charts-section">
      <el-row :gutter="20">
        <el-col :span="12">
          <div class="chart-panel">
            <div class="panel-header">
              <h3>CPU使用率趋势</h3>
              <div class="panel-controls">
                <el-button size="mini" @click="toggleChartFullscreen('cpu')">
                  <i class="el-icon-full-screen"></i>
                </el-button>
              </div>
            </div>
            <div ref="cpuChart" class="chart-container"></div>
          </div>
        </el-col>
        
        <el-col :span="12">
          <div class="chart-panel">
            <div class="panel-header">
              <h3>内存使用趋势</h3>
              <div class="panel-controls">
                <el-button size="mini" @click="toggleChartFullscreen('memory')">
                  <i class="el-icon-full-screen"></i>
                </el-button>
              </div>
            </div>
            <div ref="memoryChart" class="chart-container"></div>
          </div>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <div class="chart-panel">
            <div class="panel-header">
              <h3>磁盘I/O</h3>
              <div class="panel-controls">
                <el-button size="mini" @click="toggleChartFullscreen('disk')">
                  <i class="el-icon-full-screen"></i>
                </el-button>
              </div>
            </div>
            <div ref="diskChart" class="chart-container"></div>
          </div>
        </el-col>
        
        <el-col :span="12">
          <div class="chart-panel">
            <div class="panel-header">
              <h3>网络流量</h3>
              <div class="panel-controls">
                <el-button size="mini" @click="toggleChartFullscreen('network')">
                  <i class="el-icon-full-screen"></i>
                </el-button>
              </div>
            </div>
            <div ref="networkChart" class="chart-container"></div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 进程监控 -->
    <div v-if="selectedServer && connectionStatus === 'connected'" class="process-section">
      <div class="section-header">
        <h3>进程监控</h3>
        <el-button size="mini" @click="refreshProcesses">刷新进程</el-button>
      </div>
      
      <el-table :data="topProcesses" style="width: 100%">
        <el-table-column prop="pid" label="PID" width="80"></el-table-column>
        <el-table-column prop="name" label="进程名" width="200"></el-table-column>
        <el-table-column prop="cpu_percent" label="CPU%" width="100">
          <template slot-scope="scope">
            <span :class="getCpuStatusClass(scope.row.cpu_percent)">
              {{ scope.row.cpu_percent }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="memory_percent" label="内存%" width="100">
          <template slot-scope="scope">
            <span :class="getMemoryStatusClass(scope.row.memory_percent)">
              {{ scope.row.memory_percent }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="memory_mb" label="内存(MB)" width="120"></el-table-column>
        <el-table-column prop="status" label="状态" width="100"></el-table-column>
        <el-table-column prop="create_time" label="启动时间"></el-table-column>
      </el-table>
    </div>

    <!-- 无服务器选择提示 -->
    <div v-if="!selectedServer" class="no-server-selected">
      <div class="empty-state">
        <i class="el-icon-monitor"></i>
        <h3>请选择要监控的服务器</h3>
        <p>点击上方"配置服务器"按钮添加服务器</p>
        <el-button type="primary" @click="showServerConfig = true">配置服务器</el-button>
      </div>
    </div>

    <!-- 连接失败提示 -->
    <div v-if="selectedServer && connectionStatus === 'disconnected'" class="connection-failed">
      <div class="error-state">
        <i class="el-icon-warning"></i>
        <h3>无法连接到服务器</h3>
        <p>请检查服务器配置和网络连接</p>
        <el-button @click="testConnection">重新连接</el-button>
        <el-button type="primary" @click="editCurrentServer">编辑配置</el-button>
      </div>
    </div>

    <!-- 服务器配置对话框 -->
    <server-config-dialog
      :visible.sync="showServerConfig"
      :server="editingServer"
      @save="onServerSaved"
      @delete="onServerDeleted"
    ></server-config-dialog>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import ServerConfigDialog from './components/ServerConfigDialog.vue'
import { getServers, getServerMetrics, testServerConnection } from '@/api/server-monitor'

export default {
  name: 'ServerMonitorDashboard',
  components: {
    ServerConfigDialog
  },
  data() {
    return {
      servers: [],
      selectedServer: null,
      currentServerInfo: {},
      connectionStatus: 'disconnected', // connected, disconnected, connecting
      timeRange: '1h',
      autoRefresh: true,
      loading: false,
      showServerConfig: false,
      editingServer: null,
      
      // 当前指标
      currentMetrics: {
        cpu: 0,
        load_avg: 0,
        memory_percent: 0,
        memory_used: 0,
        memory_total: 0,
        disk_percent: 0,
        disk_free: 0,
        network_sent: 0,
        network_recv: 0
      },
      
      // 历史数据
      historicalData: {
        timestamps: [],
        cpu: [],
        memory: [],
        disk_read: [],
        disk_write: [],
        network_sent: [],
        network_recv: []
      },
      
      // 进程数据
      topProcesses: [],
      
      // 图表实例
      charts: {
        cpu: null,
        memory: null,
        disk: null,
        network: null
      },
      
      // 自动刷新定时器
      refreshTimer: null
    }
  },
  mounted() {
    this.loadServers()
    this.initCharts()
  },
  beforeDestroy() {
    this.stopAutoRefresh()
    this.destroyCharts()
  },
  methods: {
    async loadServers() {
      try {
        const response = await getServers()
        this.servers = response.data || []
        
        // 如果有服务器且没有选中的，自动选择第一个
        if (this.servers.length > 0 && !this.selectedServer) {
          this.selectedServer = this.servers[0].id
          this.onServerChange()
        }
      } catch (error) {
        this.$message.error('加载服务器列表失败: ' + error.message)
      }
    },

    async onServerChange() {
      if (!this.selectedServer) return
      
      this.currentServerInfo = this.servers.find(s => s.id === this.selectedServer) || {}
      this.connectionStatus = 'connecting'
      
      // 测试连接
      await this.testConnection()
      
      if (this.connectionStatus === 'connected') {
        // 加载数据
        await this.loadServerData()
        
        // 启动自动刷新
        if (this.autoRefresh) {
          this.startAutoRefresh()
        }
      }
    },

    async testConnection() {
      try {
        const response = await testServerConnection(this.selectedServer)
        this.connectionStatus = response.success ? 'connected' : 'disconnected'
        
        if (!response.success) {
          this.$message.error('服务器连接失败: ' + response.error)
        }
      } catch (error) {
        this.connectionStatus = 'disconnected'
        this.$message.error('连接测试失败: ' + error.message)
      }
    },

    async loadServerData() {
      if (!this.selectedServer || this.connectionStatus !== 'connected') return
      
      this.loading = true
      try {
        const response = await getServerMetrics(this.selectedServer, this.timeRange)
        
        if (response.success) {
          this.currentMetrics = response.data.current
          this.historicalData = response.data.historical
          this.topProcesses = response.data.processes || []
          
          // 更新图表
          this.updateCharts()
        } else {
          this.$message.error('获取服务器数据失败: ' + response.error)
        }
      } catch (error) {
        this.$message.error('获取服务器数据失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },

    refreshData() {
      this.loadServerData()
    },

    onTimeRangeChange() {
      this.loadServerData()
    },

    toggleAutoRefresh() {
      if (this.autoRefresh) {
        this.startAutoRefresh()
      } else {
        this.stopAutoRefresh()
      }
    },

    startAutoRefresh() {
      this.stopAutoRefresh()
      this.refreshTimer = setInterval(() => {
        this.loadServerData()
      }, 30000) // 30秒刷新一次
    },

    stopAutoRefresh() {
      if (this.refreshTimer) {
        clearInterval(this.refreshTimer)
        this.refreshTimer = null
      }
    },

    refreshProcesses() {
      this.loadServerData()
    },

    editCurrentServer() {
      this.editingServer = this.currentServerInfo
      this.showServerConfig = true
    },

    onServerSaved(server) {
      this.loadServers()
      this.showServerConfig = false
      
      if (server.id === this.selectedServer) {
        this.onServerChange()
      }
    },

    onServerDeleted(serverId) {
      this.loadServers()
      this.showServerConfig = false
      
      if (serverId === this.selectedServer) {
        this.selectedServer = null
        this.connectionStatus = 'disconnected'
        this.stopAutoRefresh()
      }
    },

    // 状态样式
    getCpuStatusClass(value) {
      if (value >= 80) return 'status-critical'
      if (value >= 60) return 'status-warning'
      return 'status-normal'
    },

    getMemoryStatusClass(value) {
      if (value >= 85) return 'status-critical'
      if (value >= 70) return 'status-warning'
      return 'status-normal'
    },

    getDiskStatusClass(value) {
      if (value >= 90) return 'status-critical'
      if (value >= 80) return 'status-warning'
      return 'status-normal'
    },

    formatBytes(bytes) {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
    },

    // 图表相关方法
    initCharts() {
      this.$nextTick(() => {
        if (this.$refs.cpuChart) {
          this.charts.cpu = echarts.init(this.$refs.cpuChart, 'dark')
        }
        if (this.$refs.memoryChart) {
          this.charts.memory = echarts.init(this.$refs.memoryChart, 'dark')
        }
        if (this.$refs.diskChart) {
          this.charts.disk = echarts.init(this.$refs.diskChart, 'dark')
        }
        if (this.$refs.networkChart) {
          this.charts.network = echarts.init(this.$refs.networkChart, 'dark')
        }
      })
    },

    updateCharts() {
      this.updateCpuChart()
      this.updateMemoryChart()
      this.updateDiskChart()
      this.updateNetworkChart()
    },

    updateCpuChart() {
      if (!this.charts.cpu) return
      
      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}<br/>CPU使用率: {c}%'
        },
        xAxis: {
          type: 'category',
          data: this.historicalData.timestamps
        },
        yAxis: {
          type: 'value',
          min: 0,
          max: 100,
          axisLabel: {
            formatter: '{value}%'
          }
        },
        series: [{
          data: this.historicalData.cpu,
          type: 'line',
          smooth: true,
          itemStyle: {
            color: '#52c41a'
          },
          areaStyle: {
            opacity: 0.3
          }
        }]
      }
      
      this.charts.cpu.setOption(option)
    },

    updateMemoryChart() {
      if (!this.charts.memory) return
      
      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}<br/>内存使用率: {c}%'
        },
        xAxis: {
          type: 'category',
          data: this.historicalData.timestamps
        },
        yAxis: {
          type: 'value',
          min: 0,
          max: 100,
          axisLabel: {
            formatter: '{value}%'
          }
        },
        series: [{
          data: this.historicalData.memory,
          type: 'line',
          smooth: true,
          itemStyle: {
            color: '#1890ff'
          },
          areaStyle: {
            opacity: 0.3
          }
        }]
      }
      
      this.charts.memory.setOption(option)
    },

    updateDiskChart() {
      if (!this.charts.disk) return
      
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['读取', '写入']
        },
        xAxis: {
          type: 'category',
          data: this.historicalData.timestamps
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: value => this.formatBytes(value) + '/s'
          }
        },
        series: [
          {
            name: '读取',
            data: this.historicalData.disk_read,
            type: 'line',
            smooth: true,
            itemStyle: {
              color: '#faad14'
            }
          },
          {
            name: '写入',
            data: this.historicalData.disk_write,
            type: 'line',
            smooth: true,
            itemStyle: {
              color: '#f5222d'
            }
          }
        ]
      }
      
      this.charts.disk.setOption(option)
    },

    updateNetworkChart() {
      if (!this.charts.network) return
      
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['发送', '接收']
        },
        xAxis: {
          type: 'category',
          data: this.historicalData.timestamps
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: value => this.formatBytes(value) + '/s'
          }
        },
        series: [
          {
            name: '发送',
            data: this.historicalData.network_sent,
            type: 'line',
            smooth: true,
            itemStyle: {
              color: '#722ed1'
            }
          },
          {
            name: '接收',
            data: this.historicalData.network_recv,
            type: 'line',
            smooth: true,
            itemStyle: {
              color: '#13c2c2'
            }
          }
        ]
      }
      
      this.charts.network.setOption(option)
    },

    toggleChartFullscreen(chartType) {
      // 图表全屏功能，可以后续实现
      this.$message.info('全屏功能开发中...')
    },

    destroyCharts() {
      Object.values(this.charts).forEach(chart => {
        if (chart) {
          chart.dispose()
        }
      })
    }
  }
}
</script>

<style scoped>
.server-monitor {
  background: #0f1419;
  color: #d9d9d9;
  min-height: 100vh;
  padding: 20px;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: #1f2329;
  border-radius: 8px;
  border: 1px solid #2f3349;
}

.server-selector {
  display: flex;
  align-items: center;
  gap: 15px;
}

.time-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.server-overview {
  margin-bottom: 30px;
  padding: 20px;
  background: #1f2329;
  border-radius: 8px;
  border: 1px solid #2f3349;
}

.server-info h2 {
  margin: 0 0 10px 0;
  color: #ffffff;
}

.server-details {
  display: flex;
  align-items: center;
  gap: 15px;
  color: #8c8c8c;
}

.metrics-cards {
  margin-bottom: 30px;
}

.metric-card {
  background: #1f2329;
  border: 1px solid #2f3349;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}

.metric-card:hover {
  border-color: #52c41a;
  box-shadow: 0 4px 12px rgba(82, 196, 26, 0.15);
}

.metric-icon {
  font-size: 2.5em;
  margin-right: 20px;
  opacity: 0.8;
}

.metric-card.cpu .metric-icon {
  color: #52c41a;
}

.metric-card.memory .metric-icon {
  color: #1890ff;
}

.metric-card.disk .metric-icon {
  color: #faad14;
}

.metric-card.network .metric-icon {
  color: #722ed1;
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 2.2em;
  font-weight: bold;
  margin-bottom: 5px;
}

.metric-label {
  font-size: 1em;
  color: #8c8c8c;
  margin-bottom: 5px;
}

.metric-detail {
  font-size: 0.9em;
  color: #595959;
}

.status-normal {
  color: #52c41a;
}

.status-warning {
  color: #faad14;
}

.status-critical {
  color: #f5222d;
}

.charts-section {
  margin-bottom: 30px;
}

.chart-panel {
  background: #1f2329;
  border: 1px solid #2f3349;
  border-radius: 8px;
  overflow: hidden;
}

.panel-header {
  padding: 15px 20px;
  border-bottom: 1px solid #2f3349;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #262c36;
}

.panel-header h3 {
  margin: 0;
  color: #ffffff;
  font-size: 1.1em;
}

.panel-controls {
  display: flex;
  gap: 10px;
}

.chart-container {
  height: 300px;
  width: 100%;
}

.process-section {
  background: #1f2329;
  border: 1px solid #2f3349;
  border-radius: 8px;
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  color: #ffffff;
}

.no-server-selected,
.connection-failed {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.empty-state,
.error-state {
  text-align: center;
  color: #8c8c8c;
}

.empty-state i,
.error-state i {
  font-size: 4em;
  margin-bottom: 20px;
  color: #595959;
}

.empty-state h3,
.error-state h3 {
  margin: 0 0 10px 0;
  color: #ffffff;
}

.empty-state p,
.error-state p {
  margin: 0 0 20px 0;
}

/* Element UI 样式覆盖 */
.server-monitor .el-select {
  width: 300px;
}

.server-monitor .el-table {
  background: transparent;
  color: #d9d9d9;
}

.server-monitor .el-table th {
  background: #262c36;
  color: #ffffff;
  border-bottom: 1px solid #2f3349;
}

.server-monitor .el-table td {
  border-bottom: 1px solid #2f3349;
}

.server-monitor .el-table tr {
  background: transparent;
}

.server-monitor .el-table tr:hover {
  background: #262c36;
}

.server-monitor .el-button {
  border-color: #2f3349;
}

.server-monitor .el-button:hover {
  border-color: #52c41a;
  color: #52c41a;
}

.server-monitor .el-button--primary {
  background: #52c41a;
  border-color: #52c41a;
}

.server-monitor .el-button--primary:hover {
  background: #73d13d;
  border-color: #73d13d;
}

.server-monitor .el-tag--success {
  background: rgba(82, 196, 26, 0.2);
  border-color: #52c41a;
  color: #52c41a;
}

.server-monitor .el-tag--danger {
  background: rgba(245, 34, 45, 0.2);
  border-color: #f5222d;
  color: #f5222d;
}

@media (max-width: 768px) {
  .server-monitor {
    padding: 10px;
  }

  .monitor-header {
    flex-direction: column;
    gap: 20px;
  }

  .server-selector,
  .time-controls {
    width: 100%;
    justify-content: center;
  }

  .metric-card {
    margin-bottom: 15px;
  }

  .chart-container {
    height: 250px;
  }
}
</style>
