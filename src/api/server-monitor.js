import request from '@/utils/request'

// 获取服务器列表
export function getServers() {
  return request({
    url: '/api/servers',
    method: 'get'
  })
}

// 保存服务器配置
export function saveServer(data) {
  return request({
    url: data.id ? `/api/servers/${data.id}` : '/api/servers',
    method: data.id ? 'put' : 'post',
    data
  })
}

// 删除服务器
export function deleteServer(serverId) {
  return request({
    url: `/api/servers/${serverId}`,
    method: 'delete'
  })
}

// 测试服务器连接
export function testServerConnection(serverId, serverConfig = null) {
  return request({
    url: serverId ? `/api/servers/${serverId}/test` : '/api/servers/test',
    method: 'post',
    data: serverConfig
  })
}

// 获取服务器监控数据
export function getServerMetrics(serverId, timeRange = '1h') {
  return request({
    url: `/api/servers/${serverId}/metrics`,
    method: 'get',
    params: { timeRange }
  })
}

// 获取服务器实时数据
export function getServerRealtimeMetrics(serverId) {
  return request({
    url: `/api/servers/${serverId}/metrics/realtime`,
    method: 'get'
  })
}

// 获取服务器进程列表
export function getServerProcesses(serverId, limit = 10) {
  return request({
    url: `/api/servers/${serverId}/processes`,
    method: 'get',
    params: { limit }
  })
}

// 获取服务器系统信息
export function getServerSystemInfo(serverId) {
  return request({
    url: `/api/servers/${serverId}/system-info`,
    method: 'get'
  })
}

// 获取服务器历史数据
export function getServerHistoricalData(serverId, startTime, endTime, metrics = ['cpu', 'memory', 'disk', 'network']) {
  return request({
    url: `/api/servers/${serverId}/historical`,
    method: 'get',
    params: {
      startTime,
      endTime,
      metrics: metrics.join(',')
    }
  })
}

// 设置服务器告警规则
export function setServerAlertRules(serverId, rules) {
  return request({
    url: `/api/servers/${serverId}/alert-rules`,
    method: 'post',
    data: { rules }
  })
}

// 获取服务器告警历史
export function getServerAlerts(serverId, limit = 50) {
  return request({
    url: `/api/servers/${serverId}/alerts`,
    method: 'get',
    params: { limit }
  })
}
