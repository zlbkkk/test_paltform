<template>
  <div class="app-container">
    <el-card>
      <div slot="header">
        <span>接口调试工具</span>
      </div>
      
      <el-form :model="requestForm" label-width="100px">
        <!-- 请求基本信息 -->
        <el-row :gutter="20">
          <el-col :span="4">
            <el-form-item label="请求方法">
              <el-select v-model="requestForm.method" style="width: 100%;">
                <el-option v-for="method in methods" :key="method" :label="method" :value="method" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item label="请求URL">
              <el-input v-model="requestForm.url" placeholder="https://api.example.com/users" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label=" ">
              <el-button type="primary" :loading="loading" @click="sendRequest">
                <i class="el-icon-position"></i> 发送请求
              </el-button>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 请求配置选项卡 -->
        <el-tabs v-model="activeTab" type="border-card">
          <!-- 请求参数 -->
          <el-tab-pane label="Query参数" name="params" v-if="requestForm.method === 'GET'">
            <div class="params-container">
              <div v-for="(param, index) in requestForm.params" :key="index" class="param-row">
                <el-row :gutter="10">
                  <el-col :span="1">
                    <el-checkbox v-model="param.enabled" />
                  </el-col>
                  <el-col :span="8">
                    <el-input v-model="param.key" placeholder="参数名" />
                  </el-col>
                  <el-col :span="8">
                    <el-input v-model="param.value" placeholder="参数值" />
                  </el-col>
                  <el-col :span="6">
                    <el-input v-model="param.description" placeholder="描述" />
                  </el-col>
                  <el-col :span="1">
                    <el-button type="danger" size="mini" icon="el-icon-delete" @click="removeParam(index)" />
                  </el-col>
                </el-row>
              </div>
              <el-button type="primary" size="mini" @click="addParam">添加参数</el-button>
            </div>
          </el-tab-pane>

          <!-- 请求头 -->
          <el-tab-pane label="Headers" name="headers">
            <div class="headers-container">
              <div v-for="(header, index) in requestForm.headers" :key="index" class="header-row">
                <el-row :gutter="10">
                  <el-col :span="1">
                    <el-checkbox v-model="header.enabled" />
                  </el-col>
                  <el-col :span="8">
                    <el-input v-model="header.key" placeholder="Header名" />
                  </el-col>
                  <el-col :span="8">
                    <el-input v-model="header.value" placeholder="Header值" />
                  </el-col>
                  <el-col :span="6">
                    <el-input v-model="header.description" placeholder="描述" />
                  </el-col>
                  <el-col :span="1">
                    <el-button type="danger" size="mini" icon="el-icon-delete" @click="removeHeader(index)" />
                  </el-col>
                </el-row>
              </div>
              <el-button type="primary" size="mini" @click="addHeader">添加Header</el-button>
            </div>
          </el-tab-pane>

          <!-- 请求体 -->
          <el-tab-pane label="Body" name="body" v-if="['POST', 'PUT', 'PATCH'].includes(requestForm.method)">
            <el-radio-group v-model="requestForm.bodyType" style="margin-bottom: 20px;">
              <el-radio label="json">JSON</el-radio>
              <el-radio label="form">Form Data</el-radio>
              <el-radio label="raw">Raw</el-radio>
            </el-radio-group>
            
            <div v-if="requestForm.bodyType === 'json'">
              <json-editor v-model="requestForm.jsonBody" :options="jsonEditorOptions" />
            </div>
            
            <div v-else-if="requestForm.bodyType === 'form'">
              <div v-for="(item, index) in requestForm.formData" :key="index" class="form-row">
                <el-row :gutter="10">
                  <el-col :span="1">
                    <el-checkbox v-model="item.enabled" />
                  </el-col>
                  <el-col :span="8">
                    <el-input v-model="item.key" placeholder="字段名" />
                  </el-col>
                  <el-col :span="8">
                    <el-input v-model="item.value" placeholder="字段值" />
                  </el-col>
                  <el-col :span="6">
                    <el-input v-model="item.description" placeholder="描述" />
                  </el-col>
                  <el-col :span="1">
                    <el-button type="danger" size="mini" icon="el-icon-delete" @click="removeFormData(index)" />
                  </el-col>
                </el-row>
              </div>
              <el-button type="primary" size="mini" @click="addFormData">添加字段</el-button>
            </div>
            
            <div v-else-if="requestForm.bodyType === 'raw'">
              <el-input v-model="requestForm.rawBody" type="textarea" :rows="10" placeholder="请输入原始数据" />
            </div>
          </el-tab-pane>

          <!-- 认证 -->
          <el-tab-pane label="Auth" name="auth">
            <el-form-item label="认证类型">
              <el-select v-model="requestForm.authType">
                <el-option label="无认证" value="none" />
                <el-option label="Bearer Token" value="bearer" />
                <el-option label="Basic Auth" value="basic" />
                <el-option label="API Key" value="apikey" />
              </el-select>
            </el-form-item>
            
            <div v-if="requestForm.authType === 'bearer'">
              <el-form-item label="Token">
                <el-input v-model="requestForm.bearerToken" placeholder="请输入Bearer Token" />
              </el-form-item>
            </div>
            
            <div v-if="requestForm.authType === 'basic'">
              <el-form-item label="用户名">
                <el-input v-model="requestForm.basicAuth.username" placeholder="用户名" />
              </el-form-item>
              <el-form-item label="密码">
                <el-input v-model="requestForm.basicAuth.password" type="password" placeholder="密码" />
              </el-form-item>
            </div>
            
            <div v-if="requestForm.authType === 'apikey'">
              <el-form-item label="Key">
                <el-input v-model="requestForm.apiKey.key" placeholder="API Key名称" />
              </el-form-item>
              <el-form-item label="Value">
                <el-input v-model="requestForm.apiKey.value" placeholder="API Key值" />
              </el-form-item>
              <el-form-item label="位置">
                <el-select v-model="requestForm.apiKey.location">
                  <el-option label="Header" value="header" />
                  <el-option label="Query" value="query" />
                </el-select>
              </el-form-item>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-form>
    </el-card>

    <!-- 响应结果 -->
    <el-card v-if="response" style="margin-top: 20px;">
      <div slot="header">
        <span>响应结果</span>
        <div style="float: right;">
          <el-tag :type="response.status >= 200 && response.status < 300 ? 'success' : 'danger'">
            {{ response.status }} {{ response.statusText }}
          </el-tag>
          <span style="margin-left: 10px;">耗时: {{ response.time }}ms</span>
          <span style="margin-left: 10px;">大小: {{ response.size }}B</span>
        </div>
      </div>
      
      <el-tabs>
        <el-tab-pane label="响应体" name="body">
          <div class="response-body">
            <pre>{{ formatResponseBody(response.data) }}</pre>
          </div>
        </el-tab-pane>
        <el-tab-pane label="响应头" name="headers">
          <el-table :data="formatHeaders(response.headers)" border>
            <el-table-column prop="key" label="Header名" />
            <el-table-column prop="value" label="Header值" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="Cookies" name="cookies">
          <el-table :data="response.cookies || []" border>
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="value" label="值" />
            <el-table-column prop="domain" label="域" />
            <el-table-column prop="path" label="路径" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import JsonEditor from '@/components/JsonEditor'

export default {
  name: 'ApiDebug',
  components: {
    JsonEditor
  },
  data() {
    return {
      loading: false,
      activeTab: 'params',
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'],
      requestForm: {
        method: 'GET',
        url: '',
        params: [
          { enabled: true, key: '', value: '', description: '' }
        ],
        headers: [
          { enabled: true, key: 'Content-Type', value: 'application/json', description: '' }
        ],
        bodyType: 'json',
        jsonBody: '{\n  "key": "value"\n}',
        formData: [
          { enabled: true, key: '', value: '', description: '' }
        ],
        rawBody: '',
        authType: 'none',
        bearerToken: '',
        basicAuth: {
          username: '',
          password: ''
        },
        apiKey: {
          key: '',
          value: '',
          location: 'header'
        }
      },
      jsonEditorOptions: {
        mode: 'code',
        modes: ['code', 'tree']
      },
      response: null
    }
  },
  methods: {
    addParam() {
      this.requestForm.params.push({ enabled: true, key: '', value: '', description: '' })
    },
    removeParam(index) {
      this.requestForm.params.splice(index, 1)
    },
    addHeader() {
      this.requestForm.headers.push({ enabled: true, key: '', value: '', description: '' })
    },
    removeHeader(index) {
      this.requestForm.headers.splice(index, 1)
    },
    addFormData() {
      this.requestForm.formData.push({ enabled: true, key: '', value: '', description: '' })
    },
    removeFormData(index) {
      this.requestForm.formData.splice(index, 1)
    },
    async sendRequest() {
      if (!this.requestForm.url) {
        this.$message.error('请输入请求URL')
        return
      }

      this.loading = true
      const startTime = Date.now()

      try {
        // 模拟请求
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        const endTime = Date.now()
        this.response = {
          status: 200,
          statusText: 'OK',
          time: endTime - startTime,
          size: 1024,
          data: {
            success: true,
            message: '请求成功',
            data: {
              id: 1,
              name: 'Test User',
              email: 'test@example.com'
            }
          },
          headers: {
            'Content-Type': 'application/json',
            'Content-Length': '1024',
            'Server': 'nginx/1.18.0'
          },
          cookies: [
            { name: 'session_id', value: 'abc123', domain: '.example.com', path: '/' }
          ]
        }

        this.$message.success('请求发送成功')
      } catch (error) {
        this.response = {
          status: 500,
          statusText: 'Internal Server Error',
          time: Date.now() - startTime,
          size: 0,
          data: { error: error.message },
          headers: {},
          cookies: []
        }
        this.$message.error('请求发送失败')
      } finally {
        this.loading = false
      }
    },
    formatResponseBody(data) {
      if (typeof data === 'object') {
        return JSON.stringify(data, null, 2)
      }
      return data
    },
    formatHeaders(headers) {
      return Object.keys(headers).map(key => ({
        key,
        value: headers[key]
      }))
    }
  }
}
</script>

<style scoped>
.param-row, .header-row, .form-row {
  margin-bottom: 10px;
}

.params-container, .headers-container {
  min-height: 200px;
}

.response-body pre {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  max-height: 400px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
