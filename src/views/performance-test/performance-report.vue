<template>
  <div class="performance-report">
    <div class="page-header">
      <h1>📈 性能报告</h1>
      <p>查看和管理历史性能测试报告，对比分析性能趋势</p>
    </div>

    <!-- 报告筛选 -->
    <el-card class="filter-card">
      <div slot="header">
        <span>🔍 报告筛选</span>
      </div>
      
      <el-form :model="filterForm" inline>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="yyyy-MM-dd"
            value-format="yyyy-MM-dd"
          >
          </el-date-picker>
        </el-form-item>
        
        <el-form-item label="测试类型">
          <el-select v-model="filterForm.testType" placeholder="全部类型" clearable>
            <el-option label="监控数据分析" value="monitor"></el-option>
            <el-option label="HTTP压力测试" value="http"></el-option>
            <el-option label="CPU压力测试" value="cpu"></el-option>
            <el-option label="内存压力测试" value="memory"></el-option>
            <el-option label="磁盘I/O测试" value="disk"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="性能评分">
          <el-select v-model="filterForm.scoreRange" placeholder="全部评分" clearable>
            <el-option label="优秀 (85-100)" value="excellent"></el-option>
            <el-option label="良好 (70-84)" value="good"></el-option>
            <el-option label="需要优化 (0-69)" value="poor"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="filterReports">筛选</el-button>
          <el-button @click="resetFilter">重置</el-button>
          <el-button type="success" @click="exportReports">导出报告</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 报告列表 -->
    <el-card class="reports-card">
      <div slot="header">
        <span>📋 报告列表</span>
        <el-button 
          style="float: right; padding: 3px 0" 
          type="text" 
          @click="refreshReports"
        >
          刷新
        </el-button>
      </div>
      
      <el-table 
        :data="filteredReports" 
        style="width: 100%"
        @row-click="viewReport"
        row-class-name="report-row"
      >
        <el-table-column prop="name" label="报告名称" width="200">
          <template slot-scope="scope">
            <div class="report-name">
              <i :class="getReportIcon(scope.row.type)"></i>
              {{ scope.row.name }}
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="type" label="测试类型" width="120">
          <template slot-scope="scope">
            <el-tag :type="getTypeTagType(scope.row.type)" size="small">
              {{ getTypeName(scope.row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="score" label="性能评分" width="100">
          <template slot-scope="scope">
            <div class="score-display" :class="getScoreClass(scope.row.score)">
              {{ scope.row.score }}
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="duration" label="测试时长" width="100">
          <template slot-scope="scope">
            {{ scope.row.duration }}秒
          </template>
        </el-table-column>
        
        <el-table-column prop="createTime" label="创建时间" width="180">
          <template slot-scope="scope">
            {{ formatTime(scope.row.createTime) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="getStatusTagType(scope.row.status)" size="small">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200">
          <template slot-scope="scope">
            <el-button size="mini" @click.stop="viewReport(scope.row)">查看</el-button>
            <el-button size="mini" type="primary" @click.stop="compareReport(scope.row)">对比</el-button>
            <el-button size="mini" type="danger" @click.stop="deleteReport(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-wrapper">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="pagination.currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pagination.pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
        >
        </el-pagination>
      </div>
    </el-card>

    <!-- 报告详情对话框 -->
    <el-dialog 
      title="报告详情" 
      :visible.sync="reportDialogVisible" 
      width="80%"
      :before-close="closeReportDialog"
    >
      <div v-if="selectedReport" class="report-detail">
        <!-- 报告基本信息 -->
        <div class="report-info">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="info-item">
                <label>报告名称:</label>
                <span>{{ selectedReport.name }}</span>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="info-item">
                <label>测试类型:</label>
                <span>{{ getTypeName(selectedReport.type) }}</span>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="info-item">
                <label>性能评分:</label>
                <span class="score" :class="getScoreClass(selectedReport.score)">
                  {{ selectedReport.score }}
                </span>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="info-item">
                <label>创建时间:</label>
                <span>{{ formatTime(selectedReport.createTime) }}</span>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 性能指标摘要 -->
        <div class="metrics-summary">
          <h3>📊 性能指标摘要</h3>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="metric-card">
                <div class="metric-value">{{ selectedReport.metrics.avgCpu }}%</div>
                <div class="metric-label">平均CPU使用率</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-card">
                <div class="metric-value">{{ selectedReport.metrics.avgMemory }}%</div>
                <div class="metric-label">平均内存使用率</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-card">
                <div class="metric-value">{{ selectedReport.metrics.maxLoad }}</div>
                <div class="metric-label">最大系统负载</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-card">
                <div class="metric-value">{{ selectedReport.metrics.bottlenecks }}</div>
                <div class="metric-label">发现瓶颈数</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 性能趋势图 -->
        <div class="trend-charts">
          <h3>📈 性能趋势</h3>
          <div ref="trendChart" class="trend-chart"></div>
        </div>

        <!-- 瓶颈分析 -->
        <div v-if="selectedReport.bottlenecks && selectedReport.bottlenecks.length > 0" class="bottlenecks-analysis">
          <h3>⚠️ 瓶颈分析</h3>
          <div class="bottlenecks-list">
            <div 
              v-for="(bottleneck, index) in selectedReport.bottlenecks" 
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
        </div>

        <!-- 优化建议 -->
        <div v-if="selectedReport.recommendations && selectedReport.recommendations.length > 0" class="recommendations">
          <h3>💡 优化建议</h3>
          <div class="recommendations-list">
            <div 
              v-for="(recommendation, index) in selectedReport.recommendations" 
              :key="index"
              class="recommendation-item"
            >
              <div class="recommendation-number">{{ index + 1 }}</div>
              <div class="recommendation-content">{{ recommendation }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <span slot="footer" class="dialog-footer">
        <el-button @click="reportDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="downloadReport">下载报告</el-button>
      </span>
    </el-dialog>

    <!-- 对比分析对话框 -->
    <el-dialog 
      title="性能对比分析" 
      :visible.sync="compareDialogVisible" 
      width="90%"
    >
      <div class="compare-content">
        <div class="compare-selector">
          <el-select v-model="compareReports" multiple placeholder="选择要对比的报告" style="width: 100%;">
            <el-option
              v-for="report in reports"
              :key="report.id"
              :label="report.name"
              :value="report.id"
            >
            </el-option>
          </el-select>
        </div>
        
        <div v-if="compareReports.length >= 2" class="compare-charts">
          <div ref="compareChart" class="compare-chart"></div>
        </div>
      </div>
      
      <span slot="footer" class="dialog-footer">
        <el-button @click="compareDialogVisible = false">关闭</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'PerformanceReport',
  data() {
    return {
      filterForm: {
        dateRange: [],
        testType: '',
        scoreRange: ''
      },
      reports: [],
      filteredReports: [],
      pagination: {
        currentPage: 1,
        pageSize: 10,
        total: 0
      },
      reportDialogVisible: false,
      compareDialogVisible: false,
      selectedReport: null,
      compareReports: [],
      trendChart: null,
      compareChart: null
    }
  },
  mounted() {
    this.loadReports()
  },
  methods: {
    loadReports() {
      // 模拟加载报告数据
      this.reports = [
        {
          id: 1,
          name: 'Web服务器性能监控_20250720',
          type: 'monitor',
          score: 85,
          duration: 300,
          createTime: new Date('2025-07-20 14:08:12'),
          status: 'completed',
          metrics: {
            avgCpu: 25.3,
            avgMemory: 45.2,
            maxLoad: 1.23,
            bottlenecks: 2
          },
          bottlenecks: [
            {
              severity: 'medium',
              description: 'CPU使用率偶尔超过80%',
              impact: '可能影响响应时间'
            }
          ],
          recommendations: [
            '优化CPU密集型任务',
            '考虑负载均衡'
          ]
        },
        {
          id: 2,
          name: 'API接口压力测试_20250719',
          type: 'http',
          score: 72,
          duration: 600,
          createTime: new Date('2025-07-19 16:30:00'),
          status: 'completed',
          metrics: {
            avgCpu: 65.8,
            avgMemory: 78.5,
            maxLoad: 2.45,
            bottlenecks: 3
          },
          bottlenecks: [
            {
              severity: 'high',
              description: '内存使用率持续过高',
              impact: '系统性能显著下降'
            }
          ],
          recommendations: [
            '增加物理内存',
            '优化内存使用'
          ]
        }
      ]
      
      this.filteredReports = [...this.reports]
      this.pagination.total = this.reports.length
    },

    filterReports() {
      let filtered = [...this.reports]
      
      // 按时间范围筛选
      if (this.filterForm.dateRange && this.filterForm.dateRange.length === 2) {
        const startDate = new Date(this.filterForm.dateRange[0])
        const endDate = new Date(this.filterForm.dateRange[1])
        endDate.setHours(23, 59, 59, 999)
        
        filtered = filtered.filter(report => {
          const reportDate = new Date(report.createTime)
          return reportDate >= startDate && reportDate <= endDate
        })
      }
      
      // 按测试类型筛选
      if (this.filterForm.testType) {
        filtered = filtered.filter(report => report.type === this.filterForm.testType)
      }
      
      // 按性能评分筛选
      if (this.filterForm.scoreRange) {
        filtered = filtered.filter(report => {
          switch (this.filterForm.scoreRange) {
            case 'excellent':
              return report.score >= 85
            case 'good':
              return report.score >= 70 && report.score < 85
            case 'poor':
              return report.score < 70
            default:
              return true
          }
        })
      }
      
      this.filteredReports = filtered
      this.pagination.total = filtered.length
      this.pagination.currentPage = 1
    },

    resetFilter() {
      this.filterForm = {
        dateRange: [],
        testType: '',
        scoreRange: ''
      }
      this.filteredReports = [...this.reports]
      this.pagination.total = this.reports.length
      this.pagination.currentPage = 1
    },

    refreshReports() {
      this.loadReports()
      this.$message.success('报告列表已刷新')
    },

    exportReports() {
      // 模拟导出功能
      this.$message.success('报告导出功能开发中...')
    },

    viewReport(report) {
      this.selectedReport = report
      this.reportDialogVisible = true
      this.$nextTick(() => {
        this.initTrendChart()
      })
    },

    compareReport(report) {
      this.compareReports = [report.id]
      this.compareDialogVisible = true
    },

    deleteReport(report) {
      this.$confirm('确定要删除这个报告吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const index = this.reports.findIndex(r => r.id === report.id)
        if (index > -1) {
          this.reports.splice(index, 1)
          this.filterReports()
          this.$message.success('报告已删除')
        }
      })
    },

    closeReportDialog() {
      this.reportDialogVisible = false
      if (this.trendChart) {
        this.trendChart.dispose()
        this.trendChart = null
      }
    },

    downloadReport() {
      this.$message.success('报告下载功能开发中...')
    },

    handleSizeChange(val) {
      this.pagination.pageSize = val
    },

    handleCurrentChange(val) {
      this.pagination.currentPage = val
    },

    initTrendChart() {
      if (!this.$refs.trendChart) return
      
      this.trendChart = echarts.init(this.$refs.trendChart)
      
      // 模拟趋势数据
      const timeData = []
      const cpuData = []
      const memoryData = []
      
      for (let i = 0; i < 50; i++) {
        timeData.push(`${i * 6}s`)
        cpuData.push(Math.floor(Math.random() * 100))
        memoryData.push(Math.floor(Math.random() * 100))
      }
      
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['CPU使用率', '内存使用率']
        },
        xAxis: {
          type: 'category',
          data: timeData
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
            name: 'CPU使用率',
            type: 'line',
            data: cpuData,
            smooth: true,
            itemStyle: { color: '#409EFF' }
          },
          {
            name: '内存使用率',
            type: 'line',
            data: memoryData,
            smooth: true,
            itemStyle: { color: '#67C23A' }
          }
        ]
      }
      
      this.trendChart.setOption(option)
    },

    getReportIcon(type) {
      const icons = {
        monitor: 'el-icon-monitor',
        http: 'el-icon-connection',
        cpu: 'el-icon-cpu',
        memory: 'el-icon-memory-card',
        disk: 'el-icon-folder'
      }
      return icons[type] || 'el-icon-document'
    },

    getTypeName(type) {
      const names = {
        monitor: '监控分析',
        http: 'HTTP测试',
        cpu: 'CPU测试',
        memory: '内存测试',
        disk: '磁盘测试'
      }
      return names[type] || type
    },

    getTypeTagType(type) {
      const types = {
        monitor: 'primary',
        http: 'success',
        cpu: 'warning',
        memory: 'info',
        disk: 'danger'
      }
      return types[type] || 'info'
    },

    getScoreClass(score) {
      if (score >= 85) return 'score-excellent'
      if (score >= 70) return 'score-good'
      return 'score-poor'
    },

    getStatusTagType(status) {
      const types = {
        completed: 'success',
        running: 'warning',
        failed: 'danger',
        pending: 'info'
      }
      return types[status] || 'info'
    },

    getStatusText(status) {
      const texts = {
        completed: '已完成',
        running: '运行中',
        failed: '失败',
        pending: '待处理'
      }
      return texts[status] || status
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

    formatTime(time) {
      return new Date(time).toLocaleString()
    }
  },

  beforeDestroy() {
    if (this.trendChart) {
      this.trendChart.dispose()
    }
    if (this.compareChart) {
      this.compareChart.dispose()
    }
  }
}
</script>

<style scoped>
.performance-report {
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

.filter-card {
  margin-bottom: 20px;
}

.reports-card {
  margin-bottom: 20px;
}

.report-row {
  cursor: pointer;
}

.report-row:hover {
  background-color: #f5f7fa;
}

.report-name {
  display: flex;
  align-items: center;
}

.report-name i {
  margin-right: 8px;
  color: #409EFF;
}

.score-display {
  font-weight: bold;
  padding: 4px 8px;
  border-radius: 4px;
  text-align: center;
}

.score-excellent {
  background: #f0f9ff;
  color: #67C23A;
}

.score-good {
  background: #fdf6ec;
  color: #E6A23C;
}

.score-poor {
  background: #fef0f0;
  color: #F56C6C;
}

.pagination-wrapper {
  margin-top: 20px;
  text-align: right;
}

.report-detail {
  max-height: 70vh;
  overflow-y: auto;
}

.report-info {
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 5px;
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

.info-item .score {
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 3px;
}

.metrics-summary {
  margin-bottom: 30px;
}

.metrics-summary h3 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.metric-card {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 5px;
  border-left: 4px solid #409EFF;
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

.trend-charts {
  margin-bottom: 30px;
}

.trend-charts h3 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.trend-chart {
  height: 400px;
  width: 100%;
}

.bottlenecks-analysis {
  margin-bottom: 30px;
}

.bottlenecks-analysis h3 {
  color: #2c3e50;
  margin-bottom: 20px;
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

.recommendations {
  margin-bottom: 30px;
}

.recommendations h3 {
  color: #2c3e50;
  margin-bottom: 20px;
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

.compare-content {
  margin-top: 20px;
}

.compare-selector {
  margin-bottom: 20px;
}

.compare-chart {
  height: 400px;
  width: 100%;
}

@media (max-width: 768px) {
  .performance-report {
    padding: 10px;
  }

  .metric-value {
    font-size: 1.5em;
  }

  .trend-chart, .compare-chart {
    height: 300px;
  }
}
</style>
