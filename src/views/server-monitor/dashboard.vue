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

        <el-button @click="reinitCharts" type="warning" size="small">
          <i class="el-icon-refresh-right"></i> 重新初始化图表
        </el-button>

        <el-button @click="generateTestData" type="success" size="small">
          <i class="el-icon-data-line"></i> 生成测试数据
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
        <h3>欢迎使用服务器监控系统</h3>
        <p>请先配置要监控的服务器</p>
        <div class="setup-steps">
          <div class="step">
            <span class="step-number">1</span>
            <span class="step-text">点击"配置服务器"按钮</span>
          </div>
          <div class="step">
            <span class="step-number">2</span>
            <span class="step-text">填写服务器连接信息</span>
          </div>
          <div class="step">
            <span class="step-number">3</span>
            <span class="step-text">测试连接并保存配置</span>
          </div>
          <div class="step">
            <span class="step-number">4</span>
            <span class="step-text">选择服务器开始监控</span>
          </div>
        </div>
        <el-button type="primary" size="large" @click="showServerConfig = true">
          <i class="el-icon-plus"></i> 配置第一台服务器
        </el-button>
      </div>
    </div>

    <!-- 连接失败提示 -->
    <div v-if="selectedServer && connectionStatus === 'disconnected'" class="connection-failed">
      <div class="error-state">
        <i class="el-icon-warning"></i>
        <h3>无法连接到服务器</h3>
        <p>{{ currentServerInfo.name }} ({{ currentServerInfo.host }})</p>
        <div class="error-details">
          <p>可能的原因：</p>
          <ul>
            <li>服务器未启动或网络不通</li>
            <li>SSH服务未运行或端口被阻拦</li>
            <li>用户名或密码错误</li>
            <li>防火墙阻止连接</li>
          </ul>
        </div>
        <div class="error-actions">
          <el-button @click="testConnection" :loading="loading">
            <i class="el-icon-refresh"></i> 重新连接
          </el-button>
          <el-button type="primary" @click="editCurrentServer">
            <i class="el-icon-edit"></i> 编辑配置
          </el-button>
          <el-button @click="loadServerData">
            <i class="el-icon-connection"></i> 获取数据
          </el-button>
        </div>
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
    // 延迟初始化图表，确保DOM完全渲染
    this.$nextTick(() => {
      setTimeout(() => {
        console.log('🚀 开始初始化图表...')
        this.initCharts()
        // 再次延迟，确保图表完全初始化后再尝试更新
        setTimeout(() => {
          if (this.historicalData && this.historicalData.timestamps && this.historicalData.timestamps.length > 0) {
            console.log('🔄 延迟更新图表数据')
            this.updateCharts()
          }
        }, 500)
      }, 200)
    })
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

        // 不自动选择服务器，让用户手动选择
        if (this.servers.length === 0) {
          this.$message.info('暂无配置的服务器，请先添加服务器配置')
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
        // 确保图表已初始化
        if (!this.charts.cpu || !this.charts.memory || !this.charts.disk || !this.charts.network) {
          console.log('🔄 重新初始化图表...')
          this.initCharts()
          // 等待图表初始化完成
          await this.$nextTick()
        }

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
      if (!this.selectedServer) return

      this.loading = true
      try {
        const response = await getServerMetrics(this.selectedServer, this.timeRange)

        if (response.success) {
          this.currentMetrics = response.data.current
          this.historicalData = response.data.historical
          this.topProcesses = response.data.processes || []

          console.log('📊 获取到历史数据:', {
            timeRange: this.timeRange,
            timestamps: this.historicalData.timestamps ? this.historicalData.timestamps.length : 0,
            cpuData: this.historicalData.cpu ? this.historicalData.cpu.length : 0,
            firstTime: this.historicalData.timestamps ? this.historicalData.timestamps[0] : null,
            lastTime: this.historicalData.timestamps ? this.historicalData.timestamps[this.historicalData.timestamps.length - 1] : null
          })

          // 更新图表
          this.updateCharts()

          // 确保连接状态为已连接
          if (this.connectionStatus !== 'connected') {
            this.connectionStatus = 'connected'
          }
        } else {
          // 数据获取失败，可能是连接问题
          this.connectionStatus = 'disconnected'
          this.$message.error('获取服务器数据失败: ' + response.error)

          if (response.suggestion) {
            this.$message.info(response.suggestion)
          }

          // 清空数据
          this.currentMetrics = {
            cpu: 0, load_avg: 0, memory_percent: 0, memory_used: 0, memory_total: 0,
            disk_percent: 0, disk_free: 0, network_sent: 0, network_recv: 0
          }
          this.historicalData = { timestamps: [], cpu: [], memory: [], disk_read: [], disk_write: [], network_sent: [], network_recv: [] }
          this.topProcesses = []
        }
      } catch (error) {
        this.connectionStatus = 'disconnected'
        this.$message.error('获取服务器数据失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },

    refreshData() {
      this.loadServerData()
    },

    onTimeRangeChange() {
      console.log('🕐 时间范围变化:', this.timeRange)
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
        console.log('🎨 初始化图表...')
        if (this.$refs.cpuChart) {
          this.charts.cpu = echarts.init(this.$refs.cpuChart, 'dark')
          console.log('✅ CPU图表初始化成功')
        } else {
          console.log('❌ CPU图表DOM元素未找到')
        }
        if (this.$refs.memoryChart) {
          this.charts.memory = echarts.init(this.$refs.memoryChart, 'dark')
          console.log('✅ 内存图表初始化成功')
        } else {
          console.log('❌ 内存图表DOM元素未找到')
        }
        if (this.$refs.diskChart) {
          this.charts.disk = echarts.init(this.$refs.diskChart, 'dark')
          console.log('✅ 磁盘图表初始化成功')
        } else {
          console.log('❌ 磁盘图表DOM元素未找到')
        }
        if (this.$refs.networkChart) {
          this.charts.network = echarts.init(this.$refs.networkChart, 'dark')
          console.log('✅ 网络图表初始化成功')
        } else {
          console.log('❌ 网络图表DOM元素未找到')
        }

        // 初始化后立即更新图表（如果有数据）
        if (this.historicalData && this.historicalData.timestamps && this.historicalData.timestamps.length > 0) {
          console.log('🔄 图表初始化后立即更新数据')
          this.updateCharts()
        }
      })
    },

    updateCharts() {
      console.log('📈 更新图表，时间范围:', this.timeRange)
      console.log('📈 历史数据:', this.historicalData)
      this.updateCpuChart()
      this.updateMemoryChart()
      this.updateDiskChart()
      this.updateNetworkChart()
    },

    updateCpuChart() {
      if (!this.charts.cpu) {
        console.log('❌ CPU图表未初始化')
        return
      }

      console.log('📊 更新CPU图表，数据:', {
        timestamps: this.historicalData.timestamps ? this.historicalData.timestamps.length : 0,
        cpu: this.historicalData.cpu ? this.historicalData.cpu.length : 0,
        timestampsData: this.historicalData.timestamps,
        cpuData: this.historicalData.cpu
      })

      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}<br/>CPU使用率: {c}%'
        },
        xAxis: {
          type: 'category',
          data: this.historicalData.timestamps || []
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
          data: this.historicalData.cpu || [],
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
      console.log('✅ CPU图表更新完成')
    },

    updateMemoryChart() {
      if (!this.charts.memory) {
        console.log('❌ 内存图表未初始化')
        return
      }

      console.log('📊 更新内存图表，数据:', {
        timestamps: this.historicalData.timestamps ? this.historicalData.timestamps.length : 0,
        memory: this.historicalData.memory ? this.historicalData.memory.length : 0
      })
      
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
      if (!this.charts.disk) {
        console.log('❌ 磁盘图表未初始化')
        return
      }

      console.log('📊 更新磁盘图表，数据:', {
        timestamps: this.historicalData.timestamps ? this.historicalData.timestamps.length : 0,
        diskRead: this.historicalData.diskRead ? this.historicalData.diskRead.length : 0,
        diskWrite: this.historicalData.diskWrite ? this.historicalData.diskWrite.length : 0
      })
      
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['读取', '写入']
        },
        grid: {
          left: '80px',  // 为Y轴标签留出足够空间
          right: '20px',
          top: '60px',
          bottom: '60px'
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
            data: this.historicalData.diskRead || this.historicalData.disk_read || [],
            type: 'line',
            smooth: true,
            itemStyle: {
              color: '#faad14'
            }
          },
          {
            name: '写入',
            data: this.historicalData.diskWrite || this.historicalData.disk_write || [],
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
      if (!this.charts.network) {
        console.log('❌ 网络图表未初始化')
        return
      }

      console.log('📊 更新网络图表，数据:', {
        timestamps: this.historicalData.timestamps ? this.historicalData.timestamps.length : 0,
        networkIn: this.historicalData.networkIn ? this.historicalData.networkIn.length : 0,
        networkOut: this.historicalData.networkOut ? this.historicalData.networkOut.length : 0
      })
      
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['发送', '接收']
        },
        grid: {
          left: '80px',  // 为Y轴标签留出足够空间
          right: '20px',
          top: '60px',
          bottom: '60px'
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
            data: this.historicalData.networkOut || this.historicalData.network_sent || [],
            type: 'line',
            smooth: true,
            itemStyle: {
              color: '#722ed1'
            }
          },
          {
            name: '接收',
            data: this.historicalData.networkIn || this.historicalData.network_recv || [],
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
    },

    // 强制重新渲染所有图表
    forceResizeCharts() {
      console.log('🔄 强制重新渲染图表...')
      this.$nextTick(() => {
        Object.values(this.charts).forEach(chart => {
          if (chart) {
            chart.resize()
          }
        })
      })
    },

    // 重新初始化图表
    reinitCharts() {
      console.log('🔄 重新初始化图表...')
      this.destroyCharts()
      this.charts = {
        cpu: null,
        memory: null,
        disk: null,
        network: null
      }
      setTimeout(() => {
        this.initCharts()
      }, 100)
    },

    // 生成测试数据
    generateTestData() {
      console.log('🎲 生成测试数据...')

      const now = new Date()
      const timestamps = []
      const cpu = []
      const memory = []
      const diskRead = []
      const diskWrite = []
      const networkIn = []
      const networkOut = []

      // 根据时间范围生成不同数量的数据点
      let dataPoints = 30
      let intervalMinutes = 1

      switch (this.timeRange) {
        case '5m':
          dataPoints = 30
          intervalMinutes = 0.2 // 12秒
          break
        case '15m':
          dataPoints = 30
          intervalMinutes = 0.5 // 30秒
          break
        case '1h':
          dataPoints = 30
          intervalMinutes = 2 // 2分钟
          break
        case '6h':
          dataPoints = 30
          intervalMinutes = 12 // 12分钟
          break
        case '24h':
          dataPoints = 30
          intervalMinutes = 48 // 48分钟
          break
      }

      for (let i = 0; i < dataPoints; i++) {
        const time = new Date(now.getTime() - (dataPoints - i) * intervalMinutes * 60 * 1000)
        timestamps.push(time.toLocaleTimeString())

        // 生成随机但有趋势的数据
        cpu.push(Math.max(0, Math.min(100, 30 + Math.sin(i * 0.3) * 20 + Math.random() * 10)))
        memory.push(Math.max(0, Math.min(100, 40 + Math.sin(i * 0.2) * 15 + Math.random() * 8)))
        diskRead.push(Math.max(0, 50 + Math.sin(i * 0.4) * 30 + Math.random() * 20))
        diskWrite.push(Math.max(0, 30 + Math.sin(i * 0.5) * 20 + Math.random() * 15))
        networkIn.push(Math.max(0, 100 + Math.sin(i * 0.3) * 50 + Math.random() * 30))
        networkOut.push(Math.max(0, 80 + Math.sin(i * 0.4) * 40 + Math.random() * 25))
      }

      this.historicalData = {
        timestamps,
        cpu,
        memory,
        diskRead,
        diskWrite,
        networkIn,
        networkOut
      }

      console.log('✅ 测试数据生成完成:', this.historicalData)

      // 更新图表
      this.updateCharts()

      this.$message.success('测试数据生成成功！')
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

.setup-steps {
  margin: 30px 0;
  text-align: left;
  max-width: 400px;
}

.step {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  padding: 10px;
  background: #262c36;
  border-radius: 6px;
  border-left: 3px solid #52c41a;
}

.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #52c41a;
  color: #ffffff;
  border-radius: 50%;
  font-weight: bold;
  font-size: 12px;
  margin-right: 12px;
  flex-shrink: 0;
}

.step-text {
  color: #d9d9d9;
  font-size: 14px;
}

.error-details {
  text-align: left;
  margin: 20px 0;
  padding: 15px;
  background: #262c36;
  border-radius: 6px;
  border-left: 3px solid #f5222d;
}

.error-details p {
  margin: 0 0 10px 0;
  color: #ffffff;
  font-weight: bold;
}

.error-details ul {
  margin: 0;
  padding-left: 20px;
  color: #8c8c8c;
}

.error-details li {
  margin-bottom: 5px;
}

.error-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
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
