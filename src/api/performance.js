import request from '@/utils/request'

// 分析监控数据
export function analyzeMonitoringData(data) {
  return request({
    url: '/api/analyze-monitoring-data',
    method: 'post',
    data
  })
}

// 上传监控数据文件
export function uploadMonitoringData(formData) {
  return request({
    url: '/api/upload-monitoring-data',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 启动压力测试
export function startStressTest(config) {
  return request({
    url: '/api/stress-test/start',
    method: 'post',
    data: config
  })
}

// 停止压力测试
export function stopStressTest(testId) {
  return request({
    url: `/api/stress-test/stop/${testId}`,
    method: 'post'
  })
}

// 获取压力测试状态
export function getStressTestStatus(testId) {
  return request({
    url: `/api/stress-test/status/${testId}`,
    method: 'get'
  })
}

// 获取实时监控数据
export function getRealtimeMetrics() {
  return request({
    url: '/api/monitoring/realtime',
    method: 'get'
  })
}

// 获取性能报告列表
export function getPerformanceReports(params) {
  return request({
    url: '/api/performance-reports',
    method: 'get',
    params
  })
}

// 获取性能报告详情
export function getPerformanceReportDetail(reportId) {
  return request({
    url: `/api/performance-reports/${reportId}`,
    method: 'get'
  })
}

// 删除性能报告
export function deletePerformanceReport(reportId) {
  return request({
    url: `/api/performance-reports/${reportId}`,
    method: 'delete'
  })
}

// 导出性能报告
export function exportPerformanceReport(reportIds) {
  return request({
    url: '/api/performance-reports/export',
    method: 'post',
    data: { reportIds },
    responseType: 'blob'
  })
}

// 对比性能报告
export function comparePerformanceReports(reportIds) {
  return request({
    url: '/api/performance-reports/compare',
    method: 'post',
    data: { reportIds }
  })
}
