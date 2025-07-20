<template>
  <div class="app-container dashboard-container">
    <div class="dashboard-header">
      <h1 class="dashboard-title">欢迎使用测试平台</h1>
      <p class="dashboard-subtitle">这是一个功能完整的自动化测试平台，支持接口测试和UI测试</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="24" class="stats-row">
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-icon project">
              <i class="el-icon-folder"></i>
            </div>
            <div class="stats-info">
              <div class="stats-number">{{ stats.projects }}</div>
              <div class="stats-label">项目总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-icon api">
              <i class="el-icon-connection"></i>
            </div>
            <div class="stats-info">
              <div class="stats-number">{{ stats.apiCases }}</div>
              <div class="stats-label">接口用例</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-icon ui">
              <i class="el-icon-monitor"></i>
            </div>
            <div class="stats-info">
              <div class="stats-number">{{ stats.uiCases }}</div>
              <div class="stats-label">UI用例</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-icon report">
              <i class="el-icon-document"></i>
            </div>
            <div class="stats-info">
              <div class="stats-number">{{ stats.reports }}</div>
              <div class="stats-label">测试报告</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <div slot="header">
            <span>最近7天测试执行趋势</span>
          </div>
          <div id="execution-chart" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div slot="header">
            <span>用例通过率统计</span>
          </div>
          <div id="pass-rate-chart" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近活动 -->
    <el-row :gutter="20" class="activity-row">
      <el-col :span="24">
        <el-card>
          <div slot="header">
            <span>最近活动</span>
          </div>
          <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in recentActivities"
              :key="index"
              :timestamp="activity.timestamp"
              placement="top"
            >
              <el-card>
                <h4>{{ activity.title }}</h4>
                <p>{{ activity.description }}</p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'Dashboard',
  data() {
    return {
      stats: {
        projects: 12,
        apiCases: 156,
        uiCases: 89,
        reports: 234
      },
      recentActivities: [
        {
          title: '新建项目',
          description: '用户 admin 创建了项目 "电商平台测试"',
          timestamp: '2024-01-15 14:30'
        },
        {
          title: '执行测试',
          description: '接口测试套件 "用户管理" 执行完成，通过率 95%',
          timestamp: '2024-01-15 13:45'
        },
        {
          title: '更新用例',
          description: '用户 tester 更新了 UI 测试用例 "登录流程"',
          timestamp: '2024-01-15 11:20'
        },
        {
          title: '生成报告',
          description: '自动生成测试报告 "每日回归测试报告"',
          timestamp: '2024-01-15 09:00'
        }
      ]
    }
  },
  mounted() {
    this.initCharts()
  },
  methods: {
    initCharts() {
      this.initExecutionChart()
      this.initPassRateChart()
    },
    initExecutionChart() {
      const chart = echarts.init(document.getElementById('execution-chart'))
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['接口测试', 'UI测试']
        },
        xAxis: {
          type: 'category',
          data: ['1/9', '1/10', '1/11', '1/12', '1/13', '1/14', '1/15']
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '接口测试',
            type: 'line',
            data: [12, 15, 18, 22, 25, 28, 30]
          },
          {
            name: 'UI测试',
            type: 'line',
            data: [8, 10, 12, 15, 18, 20, 22]
          }
        ]
      }
      chart.setOption(option)
    },
    initPassRateChart() {
      const chart = echarts.init(document.getElementById('pass-rate-chart'))
      const option = {
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        series: [
          {
            name: '通过率',
            type: 'pie',
            radius: '50%',
            data: [
              { value: 85, name: '通过' },
              { value: 10, name: '失败' },
              { value: 5, name: '跳过' }
            ],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      }
      chart.setOption(option)
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard-container {
  padding: 16px 20px;
}

.dashboard-header {
  text-align: center;
  padding: 16px 0 20px 0;
  margin-bottom: 16px;

  .dashboard-title {
    font-size: 24px;
    font-weight: 500;
    color: #303133;
    margin: 0 0 8px 0;
    line-height: 1.4;
  }

  .dashboard-subtitle {
    font-size: 14px;
    color: #606266;
    margin: 0;
    line-height: 1.5;
  }
}

.dashboard-text {
  margin-bottom: 30px;
  text-align: center;

  h1 {
    color: #303133;
    margin-bottom: 10px;
  }

  p {
    color: #606266;
    font-size: 16px;
  }
}

.stats-row {
  margin-bottom: 16px;
}

.stats-card {
  .stats-content {
    display: flex;
    align-items: center;
    
    .stats-icon {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 20px;
      
      i {
        font-size: 24px;
        color: white;
      }
      
      &.project {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }
      
      &.api {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      }
      
      &.ui {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      }
      
      &.report {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
      }
    }
    
    .stats-info {
      .stats-number {
        font-size: 28px;
        font-weight: bold;
        color: #303133;
        line-height: 1;
      }
      
      .stats-label {
        font-size: 14px;
        color: #909399;
        margin-top: 5px;
      }
    }
  }
}

.charts-row {
  margin-bottom: 16px;
}

.activity-row {
  margin-bottom: 16px;
}
</style>
