<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.name"
        placeholder="用例名称"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-select v-model="listQuery.method" placeholder="请求方法" clearable style="width: 120px" class="filter-item">
        <el-option v-for="item in methodOptions" :key="item" :label="item" :value="item" />
      </el-select>
      <el-select v-model="listQuery.status" placeholder="状态" clearable style="width: 120px" class="filter-item">
        <el-option v-for="item in statusOptions" :key="item.key" :label="item.display_name" :value="item.key" />
      </el-select>
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-plus" @click="handleCreate">
        新建用例
      </el-button>
      <el-button class="filter-item" type="success" icon="el-icon-video-play" @click="handleBatchRun">
        批量执行
      </el-button>
    </div>

    <el-table
      :key="tableKey"
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="ID" prop="id" sortable="custom" align="center" width="60">
        <template slot-scope="{row}">
          <span>{{ row.id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="用例名称" min-width="180px">
        <template slot-scope="{row}">
          <span class="link-type" @click="handleUpdate(row)">{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="请求方法" width="100px" align="center" show-overflow-tooltip>
        <template slot-scope="{row}">
          <el-tag :type="row.method | methodFilter">{{ row.method }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="请求路径" min-width="200px" show-overflow-tooltip>
        <template slot-scope="{row}">
          <span>{{ row.path }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" class-name="status-col" width="80">
        <template slot-scope="{row}">
          <el-tag :type="row.status | statusFilter">
            {{ row.status | statusDisplayFilter }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="最后执行" width="120px" align="center" show-overflow-tooltip>
        <template slot-scope="{row}">
          <span>{{ row.last_run | parseTime }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="280" class-name="small-padding fixed-width" show-overflow-tooltip>
        <template slot-scope="{row,$index}">
          <div class="button-group">
            <el-button type="primary" size="mini" @click="handleUpdate(row)">
              编辑
            </el-button>
            <el-button type="success" size="mini" @click="handleRun(row)">
              执行
            </el-button>
            <el-button type="info" size="mini" @click="handleCopy(row)">
              复制
            </el-button>
            <el-button size="mini" type="danger" @click="handleDelete(row,$index)">
              删除
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />

    <!-- 用例编辑对话框 -->
    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible" width="80%" top="5vh">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用例名称" prop="name">
              <el-input v-model="temp.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="请求方法" prop="method">
              <el-select v-model="temp.method" placeholder="请选择请求方法">
                <el-option v-for="item in methodOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="请求路径" prop="path">
          <el-input v-model="temp.path" placeholder="/api/users" />
        </el-form-item>
        
        <el-form-item label="请求头">
          <json-editor v-model="temp.headers" :options="jsonEditorOptions" />
        </el-form-item>
        
        <el-form-item label="请求参数" v-if="temp.method === 'GET'">
          <json-editor v-model="temp.params" :options="jsonEditorOptions" />
        </el-form-item>
        
        <el-form-item label="请求体" v-if="['POST', 'PUT', 'PATCH'].includes(temp.method)">
          <json-editor v-model="temp.body" :options="jsonEditorOptions" />
        </el-form-item>
        
        <el-form-item label="断言规则">
          <el-card shadow="never">
            <div v-for="(assertion, index) in temp.assertions" :key="index" class="assertion-item">
              <el-row :gutter="10">
                <el-col :span="6">
                  <el-select v-model="assertion.type" placeholder="断言类型">
                    <el-option label="状态码" value="status_code" />
                    <el-option label="响应体包含" value="response_contains" />
                    <el-option label="JSON路径" value="json_path" />
                    <el-option label="响应时间" value="response_time" />
                  </el-select>
                </el-col>
                <el-col :span="6">
                  <el-select v-model="assertion.operator" placeholder="操作符">
                    <el-option label="等于" value="equals" />
                    <el-option label="不等于" value="not_equals" />
                    <el-option label="包含" value="contains" />
                    <el-option label="不包含" value="not_contains" />
                    <el-option label="大于" value="greater_than" />
                    <el-option label="小于" value="less_than" />
                  </el-select>
                </el-col>
                <el-col :span="8">
                  <el-input v-model="assertion.expected" placeholder="期望值" />
                </el-col>
                <el-col :span="4">
                  <el-button type="danger" size="mini" @click="removeAssertion(index)">删除</el-button>
                </el-col>
              </el-row>
            </div>
            <el-button type="primary" size="mini" @click="addAssertion">添加断言</el-button>
          </el-card>
        </el-form-item>
        
        <el-form-item label="用例描述">
          <el-input v-model="temp.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取消</el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">确认</el-button>
      </div>
    </el-dialog>

    <!-- 执行结果对话框 -->
    <el-dialog title="执行结果" :visible.sync="resultDialogVisible" width="70%">
      <el-card v-if="executionResult">
        <div slot="header">
          <span>{{ executionResult.case_name }}</span>
          <el-tag :type="executionResult.status === 'PASS' ? 'success' : 'danger'" style="float: right;">
            {{ executionResult.status }}
          </el-tag>
        </div>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <h4>请求信息</h4>
            <p><strong>方法:</strong> {{ executionResult.request.method }}</p>
            <p><strong>URL:</strong> {{ executionResult.request.url }}</p>
            <p><strong>耗时:</strong> {{ executionResult.response_time }}ms</p>
          </el-col>
          <el-col :span="12">
            <h4>响应信息</h4>
            <p><strong>状态码:</strong> {{ executionResult.response.status_code }}</p>
            <p><strong>响应大小:</strong> {{ executionResult.response.size }}B</p>
          </el-col>
        </el-row>
        
        <el-tabs>
          <el-tab-pane label="响应体" name="response">
            <pre>{{ JSON.stringify(executionResult.response.body, null, 2) }}</pre>
          </el-tab-pane>
          <el-tab-pane label="断言结果" name="assertions">
            <el-table :data="executionResult.assertion_results" border>
              <el-table-column prop="type" label="断言类型" />
              <el-table-column prop="expected" label="期望值" />
              <el-table-column prop="actual" label="实际值" />
              <el-table-column prop="result" label="结果">
                <template slot-scope="scope">
                  <el-tag :type="scope.row.result ? 'success' : 'danger'">
                    {{ scope.row.result ? '通过' : '失败' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </el-dialog>
  </div>
</template>

<script>
import waves from '@/directive/waves'
import Pagination from '@/components/Pagination'
import JsonEditor from '@/components/JsonEditor'

export default {
  name: 'ApiCase',
  components: { Pagination, JsonEditor },
  directives: { waves },
  filters: {
    statusFilter(status) {
      const statusMap = {
        active: 'success',
        inactive: 'info'
      }
      return statusMap[status]
    },
    statusDisplayFilter(status) {
      const statusMap = {
        active: '激活',
        inactive: '禁用'
      }
      return statusMap[status]
    },
    methodFilter(method) {
      const methodMap = {
        GET: 'success',
        POST: 'primary',
        PUT: 'warning',
        DELETE: 'danger',
        PATCH: 'info'
      }
      return methodMap[method]
    }
  },
  data() {
    return {
      tableKey: 0,
      list: null,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20,
        name: undefined,
        method: undefined,
        status: undefined
      },
      methodOptions: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
      statusOptions: [
        { key: 'active', display_name: '激活' },
        { key: 'inactive', display_name: '禁用' }
      ],
      multipleSelection: [],
      temp: {
        id: undefined,
        name: '',
        method: 'GET',
        path: '',
        headers: {},
        params: {},
        body: {},
        assertions: [],
        description: '',
        status: 'active'
      },
      dialogFormVisible: false,
      resultDialogVisible: false,
      dialogStatus: '',
      textMap: {
        update: '编辑用例',
        create: '创建用例'
      },
      rules: {
        name: [{ required: true, message: '用例名称是必填项', trigger: 'blur' }],
        method: [{ required: true, message: '请求方法是必填项', trigger: 'change' }],
        path: [{ required: true, message: '请求路径是必填项', trigger: 'blur' }]
      },
      jsonEditorOptions: {
        mode: 'code',
        modes: ['code', 'tree']
      },
      executionResult: null
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      // 模拟数据
      setTimeout(() => {
        this.list = [
          {
            id: 1,
            name: '用户登录接口',
            method: 'POST',
            path: '/api/auth/login',
            status: 'active',
            last_run: new Date('2024-01-15 10:30:00')
          },
          {
            id: 2,
            name: '获取用户信息',
            method: 'GET',
            path: '/api/user/profile',
            status: 'active',
            last_run: new Date('2024-01-15 09:15:00')
          },
          {
            id: 3,
            name: '创建订单',
            method: 'POST',
            path: '/api/orders',
            status: 'active',
            last_run: new Date('2024-01-14 16:45:00')
          }
        ]
        this.total = this.list.length
        this.listLoading = false
      }, 1000)
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handleSelectionChange(val) {
      this.multipleSelection = val
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        name: '',
        method: 'GET',
        path: '',
        headers: {},
        params: {},
        body: {},
        assertions: [],
        description: '',
        status: 'active'
      }
    },
    handleCreate() {
      this.resetTemp()
      this.dialogStatus = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.temp.id = parseInt(Math.random() * 100) + 1024
          this.temp.last_run = new Date()
          this.list.unshift(this.temp)
          this.dialogFormVisible = false
          this.$notify({
            title: '成功',
            message: '创建成功',
            type: 'success',
            duration: 2000
          })
        }
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row)
      if (!this.temp.headers) this.temp.headers = {}
      if (!this.temp.params) this.temp.params = {}
      if (!this.temp.body) this.temp.body = {}
      if (!this.temp.assertions) this.temp.assertions = []
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.temp)
          const index = this.list.findIndex(v => v.id === this.temp.id)
          this.list.splice(index, 1, tempData)
          this.dialogFormVisible = false
          this.$notify({
            title: '成功',
            message: '更新成功',
            type: 'success',
            duration: 2000
          })
        }
      })
    },
    handleDelete(row, index) {
      this.$confirm('确认删除该用例?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.list.splice(index, 1)
        this.$notify({
          title: '成功',
          message: '删除成功',
          type: 'success',
          duration: 2000
        })
      })
    },
    handleRun(row) {
      // 模拟执行用例
      this.$message({
        message: '正在执行用例...',
        type: 'info'
      })
      
      setTimeout(() => {
        this.executionResult = {
          case_name: row.name,
          status: 'PASS',
          request: {
            method: row.method,
            url: 'https://api.example.com' + row.path
          },
          response: {
            status_code: 200,
            size: 1024,
            body: { success: true, data: { id: 1, name: 'test' } }
          },
          response_time: 156,
          assertion_results: [
            { type: '状态码', expected: '200', actual: '200', result: true },
            { type: '响应体包含', expected: 'success', actual: 'success', result: true }
          ]
        }
        this.resultDialogVisible = true
      }, 2000)
    },
    handleCopy(row) {
      const newRow = Object.assign({}, row)
      newRow.id = parseInt(Math.random() * 100) + 1024
      newRow.name = row.name + '_copy'
      this.list.unshift(newRow)
      this.$message({
        message: '复制成功',
        type: 'success'
      })
    },
    handleBatchRun() {
      if (this.multipleSelection.length === 0) {
        this.$message({
          message: '请先选择要执行的用例',
          type: 'warning'
        })
        return
      }
      this.$message({
        message: `正在批量执行 ${this.multipleSelection.length} 个用例...`,
        type: 'info'
      })
    },
    addAssertion() {
      this.temp.assertions.push({
        type: 'status_code',
        operator: 'equals',
        expected: '200'
      })
    },
    removeAssertion(index) {
      this.temp.assertions.splice(index, 1)
    }
  }
}
</script>

<style scoped>
.link-type {
  color: #409EFF;
  cursor: pointer;
}

.link-type:hover {
  color: #66b1ff;
}

.assertion-item {
  margin-bottom: 10px;
}

pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}

/* 操作按钮组样式优化 */
.button-group {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  flex-wrap: nowrap;  /* 强制不换行 */
  white-space: nowrap;
}

.button-group .el-button {
  margin: 0;
  min-width: 56px;  /* 稍微减小最小宽度 */
  padding: 7px 12px;  /* 调整内边距 */
  font-size: 12px;
}

/* 表格样式优化 */
.el-table th {
  white-space: nowrap;  /* 表头文字不换行 */
  text-overflow: ellipsis;
  overflow: hidden;
}

.el-table td {
  white-space: nowrap;  /* 表格内容不换行 */
}

/* 勾选框对齐优化 */
.el-table .el-table-column--selection .cell {
  text-align: center;
  padding: 0;
}

.el-table .el-checkbox {
  display: inline-block;
  vertical-align: middle;
}

/* 表格布局优化 */
.el-table {
  width: 100% !important;
}

.el-table .cell {
  word-break: break-word;
  line-height: 1.4;
}

/* 用例名称列样式 */
.link-type {
  display: inline-block;
  max-width: 100%;
  word-break: break-word;
  line-height: 1.4;
}

/* 操作按钮组紧凑布局 */
.button-group {
  display: flex;
  gap: 4px;
  justify-content: center;
  flex-wrap: nowrap;
  white-space: nowrap;
}

.button-group .el-button {
  margin: 0 !important;
  padding: 4px 6px !important;
  font-size: 12px !important;
  min-width: auto !important;
}
</style>
