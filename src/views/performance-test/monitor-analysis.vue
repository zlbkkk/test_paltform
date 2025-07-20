<template>
  <div class="monitor-analysis">
    <div class="page-header">
      <h1>📊 性能监控数据分析</h1>
      <p>上传系统监控数据，获取AI驱动的性能瓶颈分析和优化建议</p>
    </div>

    <!-- 文件上传区域 -->
    <el-card class="upload-card" v-if="!analysisResult">
      <div slot="header">
        <span>📁 上传监控数据</span>
      </div>
      
      <el-upload
        class="upload-dragger"
        drag
        action=""
        :before-upload="handleFileUpload"
        :show-file-list="false"
        accept=".json"
      >
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">
          将监控数据文件拖到此处，或<em>点击上传</em>
        </div>
        <div class="el-upload__tip" slot="tip">
          只能上传JSON格式的监控数据文件，且不超过10MB
        </div>
      </el-upload>

      <div class="upload-examples">
        <h4>💡 支持的监控数据格式：</h4>
        <ul>
          <li>Linux系统监控数据 (system_monitor_*.json)</li>
          <li>包含CPU、内存、负载等性能指标</li>
          <li>时间序列数据，支持5分钟到数小时的监控周期</li>
        </ul>
      </div>
    </el-card>

    <!-- 加载状态 -->
    <el-card v-if="loading" class="loading-card">
      <div class="loading-content">
        <el-spinner size="large"></el-spinner>
        <h3>🤖 AI正在分析监控数据...</h3>
        <p>正在识别性能瓶颈和优化机会，请稍候</p>
      </div>
    </el-card>

    <!-- 分析结果 -->
    <div v-if="analysisResult && !loading" class="analysis-results">
      <!-- 系统信息 -->
      <el-card class="system-info-card">
        <div slot="header">
          <span>🖥️ 系统信息</span>
          <el-button 
            style="float: right; padding: 3px 0" 
            type="text" 
            @click="resetAnalysis"
          >
            重新分析
          </el-button>
        </div>
        
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="info-item">
              <label>主机名:</label>
              <span>{{ analysisResult.system_info.hostname }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="info-item">
              <label>系统:</label>
              <span>{{ analysisResult.system_info.system }} {{ analysisResult.system_info.release }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="info-item">
              <label>CPU核心:</label>
              <span>{{ analysisResult.system_info.cpu_count_logical }}个逻辑核心</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="info-item">
              <label>总内存:</label>
              <span>{{ analysisResult.system_info.total_memory_gb }}GB</span>
            </div>
          </el-col>
        </el-row>
        
        <el-row :gutter="20" style="margin-top: 15px;">
          <el-col :span="6">
            <div class="info-item">
              <label>CPU型号:</label>
              <span>{{ analysisResult.system_info.cpu_model || 'Unknown' }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="info-item">
              <label>监控时长:</label>
              <span>{{ analysisResult.monitoring_summary.duration_seconds }}秒</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="info-item">
              <label>数据点数:</label>
              <span>{{ analysisResult.monitoring_summary.cpu_data_points }}个</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="info-item">
              <label>采样间隔:</label>
              <span>{{ analysisResult.monitoring_summary.sample_interval }}秒</span>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 性能评分 -->
      <el-card class="score-card">
        <div slot="header">
          <span>🎯 性能评分</span>
        </div>
        
        <div class="score-display">
          <div class="score-circle" :class="getScoreClass(analysisResult.performance_score)">
            {{ analysisResult.performance_score }}
          </div>
          <div class="score-text">
            <h3>{{ getScoreText(analysisResult.performance_score) }}</h3>
            <p>{{ getScoreDescription(analysisResult.performance_score) }}</p>
          </div>
        </div>
      </el-card>

      <!-- 性能图表 -->
      <el-card class="charts-card">
        <div slot="header">
          <span>📈 性能趋势图表</span>
        </div>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <h4>CPU使用率趋势</h4>
              <div ref="cpuChart" class="chart"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <h4>内存使用率趋势</h4>
              <div ref="memoryChart" class="chart"></div>
            </div>
          </el-col>
        </el-row>
        
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="12">
            <div class="chart-container">
              <h4>系统负载趋势</h4>
              <div ref="loadChart" class="chart"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <h4>CPU核心使用率</h4>
              <div ref="coreChart" class="chart"></div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 性能瓶颈 -->
      <el-card class="bottlenecks-card" v-if="analysisResult.bottlenecks.length > 0">
        <div slot="header">
          <span>⚠️ 性能瓶颈分析</span>
        </div>
        
        <div class="bottlenecks-list">
          <div 
            v-for="(bottleneck, index) in analysisResult.bottlenecks" 
            :key="index"
            class="bottleneck-item"
            :class="`bottleneck-${bottleneck.severity}`"
          >
            <div class="bottleneck-header">
              <span class="bottleneck-icon">{{ getBottleneckIcon(bottleneck.severity) }}</span>
              <span class="bottleneck-title">{{ bottleneck.description }}</span>
              <el-tag :type="getTagType(bottleneck.severity)" size="small">
                {{ getSeverityText(bottleneck.severity) }}
              </el-tag>
            </div>
            <div class="bottleneck-impact">
              <strong>影响:</strong> {{ bottleneck.impact }}
            </div>
          </div>
        </div>
      </el-card>

      <!-- 优化建议 -->
      <el-card class="recommendations-card" v-if="analysisResult.recommendations.length > 0">
        <div slot="header">
          <span>💡 优化建议</span>
        </div>
        
        <div class="recommendations-list">
          <div 
            v-for="(recommendation, index) in analysisResult.recommendations" 
            :key="index"
            class="recommendation-item"
          >
            <div class="recommendation-number">{{ index + 1 }}</div>
            <div class="recommendation-content">{{ recommendation }}</div>
          </div>
        </div>
      </el-card>

      <!-- 无瓶颈提示 -->
      <el-card v-if="analysisResult.bottlenecks.length === 0" class="no-issues-card">
        <div class="no-issues-content">
          <i class="el-icon-success" style="font-size: 48px; color: #67C23A;"></i>
          <h3>🎉 未发现明显的性能瓶颈</h3>
          <p>系统运行状况良好，性能表现优秀</p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { analyzeMonitoringData } from '@/api/performance'

export default {
  name: 'MonitorAnalysis',
  data() {
    return {
      loading: false,
      analysisResult: null,
      charts: {
        cpu: null,
        memory: null,
        load: null,
        core: null
      }
    }
  },
  methods: {
    async handleFileUpload(file) {
      if (file.size > 10 * 1024 * 1024) {
        this.$message.error('文件大小不能超过10MB')
        return false
      }

      this.loading = true
      
      try {
        const fileContent = await this.readFileAsText(file)
        const monitoringData = JSON.parse(fileContent)
        
        // 调用分析API
        const response = await analyzeMonitoringData(monitoringData)
        
        if (response.success) {
          this.analysisResult = response.analysis
          this.$nextTick(() => {
            this.initCharts()
          })
          this.$message.success('监控数据分析完成')
        } else {
          this.$message.error(response.error || '分析失败')
        }
      } catch (error) {
        console.error('分析错误:', error)
        if (error instanceof SyntaxError) {
          this.$message.error('JSON文件格式错误')
        } else {
          this.$message.error('分析过程中发生错误: ' + error.message)
        }
      } finally {
        this.loading = false
      }
      
      return false // 阻止默认上传行为
    },

    readFileAsText(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = e => resolve(e.target.result)
        reader.onerror = reject
        reader.readAsText(file)
      })
    },

    resetAnalysis() {
      this.analysisResult = null
      this.destroyCharts()
    },

    getScoreClass(score) {
      if (score >= 85) return 'score-excellent'
      if (score >= 70) return 'score-good'
      return 'score-poor'
    },

    getScoreText(score) {
      if (score >= 85) return '优秀'
      if (score >= 70) return '良好'
      return '需要优化'
    },

    getScoreDescription(score) {
      if (score >= 85) return '系统性能表现优秀，运行稳定'
      if (score >= 70) return '系统性能良好，有少量优化空间'
      return '系统存在性能问题，建议立即优化'
    },

    getBottleneckIcon(severity) {
      const icons = {
        critical: '🔴',
        high: '🟠',
        medium: '🟡',
        low: '🔵'
      }
      return icons[severity] || '🔵'
    },

    getTagType(severity) {
      const types = {
        critical: 'danger',
        high: 'warning',
        medium: 'info',
        low: 'success'
      }
      return types[severity] || 'info'
    },

    getSeverityText(severity) {
      const texts = {
        critical: '严重',
        high: '高',
        medium: '中',
        low: '低'
      }
      return texts[severity] || '未知'
    },

    initCharts() {
      this.initCpuChart()
      this.initMemoryChart()
      this.initLoadChart()
      this.initCoreChart()
    },

    initCpuChart() {
      if (!this.$refs.cpuChart) return
      
      this.charts.cpu = echarts.init(this.$refs.cpuChart)
      const data = this.analysisResult.charts_data.cpu_timeline
      
      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}<br/>CPU使用率: {c}%'
        },
        xAxis: {
          type: 'category',
          data: data.map(item => new Date(item.time).toLocaleTimeString())
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
          data: data.map(item => item.cpu_percent),
          type: 'line',
          smooth: true,
          itemStyle: {
            color: '#409EFF'
          },
          areaStyle: {
            opacity: 0.3
          }
        }]
      }
      
      this.charts.cpu.setOption(option)
    },

    initMemoryChart() {
      if (!this.$refs.memoryChart) return
      
      this.charts.memory = echarts.init(this.$refs.memoryChart)
      const data = this.analysisResult.charts_data.memory_timeline
      
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['内存使用率', '交换分区使用率']
        },
        xAxis: {
          type: 'category',
          data: data.map(item => new Date(item.time).toLocaleTimeString())
        },
        yAxis: {
          type: 'value',
          min: 0,
          max: 100,
          axisLabel: {
            formatter: '{value}%'
          }
        },
        series: [
          {
            name: '内存使用率',
            data: data.map(item => item.memory_percent),
            type: 'line',
            smooth: true,
            itemStyle: {
              color: '#67C23A'
            }
          },
          {
            name: '交换分区使用率',
            data: data.map(item => item.swap_percent),
            type: 'line',
            smooth: true,
            itemStyle: {
              color: '#F56C6C'
            }
          }
        ]
      }
      
      this.charts.memory.setOption(option)
    },

    initLoadChart() {
      if (!this.$refs.loadChart) return
      
      this.charts.load = echarts.init(this.$refs.loadChart)
      const data = this.analysisResult.charts_data.cpu_timeline
      
      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}<br/>负载: {c}'
        },
        xAxis: {
          type: 'category',
          data: data.map(item => new Date(item.time).toLocaleTimeString())
        },
        yAxis: {
          type: 'value',
          min: 0
        },
        series: [{
          data: data.map(item => item.load_1min),
          type: 'line',
          smooth: true,
          itemStyle: {
            color: '#E6A23C'
          },
          areaStyle: {
            opacity: 0.3
          }
        }]
      }
      
      this.charts.load.setOption(option)
    },

    initCoreChart() {
      if (!this.$refs.coreChart) return
      
      this.charts.core = echarts.init(this.$refs.coreChart)
      const data = this.analysisResult.charts_data.cpu_cores
      
      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}<br/>使用率: {c}%'
        },
        xAxis: {
          type: 'category',
          data: data.map(item => item.core)
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
          data: data.map(item => ({
            value: item.usage,
            itemStyle: {
              color: item.usage > 80 ? '#F56C6C' : 
                     item.usage > 60 ? '#E6A23C' : '#67C23A'
            }
          })),
          type: 'bar'
        }]
      }
      
      this.charts.core.setOption(option)
    },

    destroyCharts() {
      Object.values(this.charts).forEach(chart => {
        if (chart) {
          chart.dispose()
        }
      })
      this.charts = {
        cpu: null,
        memory: null,
        load: null,
        core: null
      }
    }
  },

  beforeDestroy() {
    this.destroyCharts()
  }
}
</script>

<style scoped>
.monitor-analysis {
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

.upload-card {
  margin-bottom: 30px;
}

.upload-dragger {
  width: 100%;
}

.upload-examples {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 5px;
}

.upload-examples h4 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.upload-examples ul {
  margin: 0;
  padding-left: 20px;
}

.upload-examples li {
  margin-bottom: 5px;
  color: #666;
}

.loading-card {
  margin-bottom: 30px;
}

.loading-content {
  text-align: center;
  padding: 40px;
}

.loading-content h3 {
  margin: 20px 0 10px;
  color: #2c3e50;
}

.loading-content p {
  color: #666;
}

.analysis-results {
  margin-top: 30px;
}

.system-info-card {
  margin-bottom: 30px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.info-item label {
  font-weight: bold;
  color: #2c3e50;
  margin-right: 10px;
  min-width: 80px;
}

.info-item span {
  color: #666;
}

.score-card {
  margin-bottom: 30px;
}

.score-display {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5em;
  font-weight: bold;
  color: white;
  margin-right: 30px;
}

.score-excellent {
  background: linear-gradient(135deg, #67C23A, #85CE61);
}

.score-good {
  background: linear-gradient(135deg, #E6A23C, #F7BA2A);
}

.score-poor {
  background: linear-gradient(135deg, #F56C6C, #F78989);
}

.score-text h3 {
  margin: 0 0 10px;
  color: #2c3e50;
}

.score-text p {
  margin: 0;
  color: #666;
}

.charts-card {
  margin-bottom: 30px;
}

.chart-container {
  text-align: center;
}

.chart-container h4 {
  margin-bottom: 15px;
  color: #2c3e50;
}

.chart {
  height: 300px;
  width: 100%;
}

.bottlenecks-card {
  margin-bottom: 30px;
}

.bottlenecks-list {
  margin-top: 15px;
}

.bottleneck-item {
  border-left: 4px solid;
  padding: 15px;
  margin-bottom: 15px;
  background: #f8f9fa;
  border-radius: 0 5px 5px 0;
}

.bottleneck-critical {
  border-left-color: #F56C6C;
}

.bottleneck-high {
  border-left-color: #E6A23C;
}

.bottleneck-medium {
  border-left-color: #409EFF;
}

.bottleneck-low {
  border-left-color: #67C23A;
}

.bottleneck-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.bottleneck-icon {
  font-size: 1.2em;
  margin-right: 10px;
}

.bottleneck-title {
  flex: 1;
  font-weight: bold;
  color: #2c3e50;
}

.bottleneck-impact {
  color: #666;
  font-size: 0.9em;
}

.recommendations-card {
  margin-bottom: 30px;
}

.recommendations-list {
  margin-top: 15px;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  padding: 15px;
  margin-bottom: 10px;
  background: #e8f5e8;
  border-radius: 5px;
  border-left: 4px solid #67C23A;
}

.recommendation-number {
  background: #67C23A;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.9em;
  margin-right: 15px;
  flex-shrink: 0;
}

.recommendation-content {
  color: #2c3e50;
  line-height: 1.6;
}

.no-issues-card {
  margin-bottom: 30px;
}

.no-issues-content {
  text-align: center;
  padding: 40px;
}

.no-issues-content h3 {
  margin: 20px 0 10px;
  color: #67C23A;
}

.no-issues-content p {
  color: #666;
}

@media (max-width: 768px) {
  .score-display {
    flex-direction: column;
    text-align: center;
  }

  .score-circle {
    margin-right: 0;
    margin-bottom: 20px;
  }

  .chart {
    height: 250px;
  }
}
</style>
