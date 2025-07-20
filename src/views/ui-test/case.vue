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
      <el-select v-model="listQuery.browser" placeholder="浏览器" clearable style="width: 120px" class="filter-item">
        <el-option v-for="item in browserOptions" :key="item" :label="item" :value="item" />
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
      <el-table-column type="selection" width="55" />
      <el-table-column label="ID" prop="id" sortable="custom" align="center" width="80">
        <template slot-scope="{row}">
          <span>{{ row.id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="用例名称" min-width="150px">
        <template slot-scope="{row}">
          <span class="link-type" @click="handleUpdate(row)">{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="测试页面" min-width="200px">
        <template slot-scope="{row}">
          <span>{{ row.page_url }}</span>
        </template>
      </el-table-column>
      <el-table-column label="浏览器" width="100px" align="center">
        <template slot-scope="{row}">
          <el-tag :type="row.browser | browserFilter">{{ row.browser }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="步骤数" width="80px" align="center">
        <template slot-scope="{row}">
          <span>{{ row.step_count }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" class-name="status-col" width="100">
        <template slot-scope="{row}">
          <el-tag :type="row.status | statusFilter">
            {{ row.status | statusDisplayFilter }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="最后执行" width="150px" align="center">
        <template slot-scope="{row}">
          <span>{{ row.last_run | parseTime }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="300" class-name="small-padding fixed-width">
        <template slot-scope="{row,$index}">
          <div class="button-group">
            <el-button type="primary" size="mini" @click="handleUpdate(row)">
              编辑
            </el-button>
            <el-button type="success" size="mini" @click="handleRun(row)">
              执行
            </el-button>
            <el-button type="info" size="mini" @click="handleRecord(row)">
              录制
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
    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible" width="90%" top="5vh">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="用例名称" prop="name">
              <el-input v-model="temp.name" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="测试页面" prop="page_url">
              <el-input v-model="temp.page_url" placeholder="https://example.com" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="浏览器" prop="browser">
              <el-select v-model="temp.browser" placeholder="请选择浏览器">
                <el-option v-for="item in browserOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="用例描述">
          <el-input v-model="temp.description" type="textarea" :rows="2" />
        </el-form-item>
        
        <el-form-item label="测试步骤">
          <div class="steps-container">
            <div class="steps-header">
              <el-button type="primary" size="mini" @click="addStep">添加步骤</el-button>
              <el-button type="success" size="mini" @click="startRecord">开始录制</el-button>
              <el-button type="warning" size="mini" @click="importSteps">导入步骤</el-button>
            </div>
            
            <el-table :data="temp.steps" border style="margin-top: 10px;">
              <el-table-column type="index" label="序号" width="60" />
              <el-table-column label="操作类型" width="120">
                <template slot-scope="scope">
                  <el-select v-model="scope.row.action" size="mini">
                    <el-option label="点击" value="click" />
                    <el-option label="输入" value="input" />
                    <el-option label="等待" value="wait" />
                    <el-option label="断言" value="assert" />
                    <el-option label="滚动" value="scroll" />
                    <el-option label="悬停" value="hover" />
                    <el-option label="选择" value="select" />
                    <el-option label="上传" value="upload" />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column label="元素定位" width="200">
                <template slot-scope="scope">
                  <el-input v-model="scope.row.locator" size="mini" placeholder="CSS选择器或XPath" />
                </template>
              </el-table-column>
              <el-table-column label="操作值" width="150">
                <template slot-scope="scope">
                  <el-input v-model="scope.row.value" size="mini" placeholder="输入值或期望值" />
                </template>
              </el-table-column>
              <el-table-column label="等待时间(ms)" width="120">
                <template slot-scope="scope">
                  <el-input-number v-model="scope.row.wait_time" size="mini" :min="0" :max="10000" />
                </template>
              </el-table-column>
              <el-table-column label="描述" min-width="150">
                <template slot-scope="scope">
                  <el-input v-model="scope.row.description" size="mini" placeholder="步骤描述" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template slot-scope="scope">
                  <el-button type="primary" size="mini" @click="editElement(scope.row)">元素</el-button>
                  <el-button type="danger" size="mini" @click="removeStep(scope.$index)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-form-item>
        
        <el-form-item label="执行配置">
          <el-card shadow="never">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="窗口大小" label-width="80px">
                  <el-select v-model="temp.config.window_size">
                    <el-option label="1920x1080" value="1920x1080" />
                    <el-option label="1366x768" value="1366x768" />
                    <el-option label="1280x720" value="1280x720" />
                    <el-option label="375x667 (Mobile)" value="375x667" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="超时时间(s)" label-width="80px">
                  <el-input-number v-model="temp.config.timeout" :min="1" :max="300" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="截图模式" label-width="80px">
                  <el-select v-model="temp.config.screenshot">
                    <el-option label="失败时截图" value="on_failure" />
                    <el-option label="每步截图" value="always" />
                    <el-option label="不截图" value="never" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="无头模式" label-width="80px">
              <el-switch v-model="temp.config.headless" />
            </el-form-item>
          </el-card>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取消</el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">确认</el-button>
      </div>
    </el-dialog>

    <!-- 元素编辑对话框 -->
    <el-dialog title="元素定位编辑" :visible.sync="elementDialogVisible" width="60%">
      <el-form :model="currentElement" label-width="100px">
        <el-form-item label="定位方式">
          <el-select v-model="currentElement.locator_type" @change="updateLocator">
            <el-option label="CSS选择器" value="css" />
            <el-option label="XPath" value="xpath" />
            <el-option label="ID" value="id" />
            <el-option label="Name" value="name" />
            <el-option label="Class" value="class" />
            <el-option label="Tag" value="tag" />
            <el-option label="Link Text" value="link_text" />
          </el-select>
        </el-form-item>
        <el-form-item label="定位表达式">
          <el-input v-model="currentElement.locator" placeholder="请输入定位表达式" />
        </el-form-item>
        <el-form-item label="元素名称">
          <el-input v-model="currentElement.name" placeholder="给元素起个名字" />
        </el-form-item>
        <el-form-item label="验证元素">
          <el-button type="primary" @click="validateElement">验证定位</el-button>
          <span v-if="elementValidation.status" :class="elementValidation.success ? 'success-text' : 'error-text'">
            {{ elementValidation.message }}
          </span>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="elementDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveElement">保存</el-button>
      </div>
    </el-dialog>

    <!-- 执行结果对话框 -->
    <el-dialog title="执行结果" :visible.sync="resultDialogVisible" width="80%">
      <div v-if="executionResult">
        <div class="result-header">
          <el-tag :type="executionResult.status === 'PASS' ? 'success' : 'danger'" size="large">
            {{ executionResult.status }}
          </el-tag>
          <span style="margin-left: 20px;">执行时间: {{ executionResult.duration }}s</span>
          <span style="margin-left: 20px;">浏览器: {{ executionResult.browser }}</span>
        </div>
        
        <el-tabs>
          <el-tab-pane label="执行日志" name="log">
            <div class="execution-log">
              <div v-for="(log, index) in executionResult.logs" :key="index" class="log-item">
                <span class="log-time">{{ log.timestamp }}</span>
                <span :class="'log-level-' + log.level">{{ log.level }}</span>
                <span class="log-message">{{ log.message }}</span>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="步骤详情" name="steps">
            <el-table :data="executionResult.step_results" border>
              <el-table-column type="index" label="步骤" width="60" />
              <el-table-column prop="action" label="操作" width="80" />
              <el-table-column prop="locator" label="元素" />
              <el-table-column prop="status" label="状态" width="80">
                <template slot-scope="scope">
                  <el-tag :type="scope.row.status === 'PASS' ? 'success' : 'danger'" size="mini">
                    {{ scope.row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="duration" label="耗时(ms)" width="100" />
              <el-table-column prop="error" label="错误信息" />
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="截图" name="screenshots">
            <div class="screenshots">
              <div v-for="(screenshot, index) in executionResult.screenshots" :key="index" class="screenshot-item">
                <h4>{{ screenshot.step_name }}</h4>
                <img :src="screenshot.url" alt="截图" style="max-width: 100%; border: 1px solid #ddd;" />
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import waves from '@/directive/waves'
import Pagination from '@/components/Pagination'

export default {
  name: 'UiCase',
  components: { Pagination },
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
    browserFilter(browser) {
      const browserMap = {
        Chrome: 'primary',
        Firefox: 'warning',
        Safari: 'success',
        Edge: 'info'
      }
      return browserMap[browser] || 'default'
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
        browser: undefined,
        status: undefined
      },
      browserOptions: ['Chrome', 'Firefox', 'Safari', 'Edge'],
      statusOptions: [
        { key: 'active', display_name: '激活' },
        { key: 'inactive', display_name: '禁用' }
      ],
      multipleSelection: [],
      temp: {
        id: undefined,
        name: '',
        page_url: '',
        browser: 'Chrome',
        description: '',
        steps: [],
        config: {
          window_size: '1920x1080',
          timeout: 30,
          screenshot: 'on_failure',
          headless: false
        },
        status: 'active'
      },
      dialogFormVisible: false,
      elementDialogVisible: false,
      resultDialogVisible: false,
      dialogStatus: '',
      textMap: {
        update: '编辑用例',
        create: '创建用例'
      },
      rules: {
        name: [{ required: true, message: '用例名称是必填项', trigger: 'blur' }],
        page_url: [{ required: true, message: '测试页面是必填项', trigger: 'blur' }],
        browser: [{ required: true, message: '浏览器是必填项', trigger: 'change' }]
      },
      currentElement: {
        locator_type: 'css',
        locator: '',
        name: ''
      },
      elementValidation: {
        status: false,
        success: false,
        message: ''
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
            name: '用户登录流程测试',
            page_url: 'https://example.com/login',
            browser: 'Chrome',
            step_count: 8,
            status: 'active',
            last_run: new Date('2024-01-15 10:30:00')
          },
          {
            id: 2,
            name: '商品搜索功能测试',
            page_url: 'https://example.com/search',
            browser: 'Firefox',
            step_count: 12,
            status: 'active',
            last_run: new Date('2024-01-15 09:15:00')
          },
          {
            id: 3,
            name: '购物车操作测试',
            page_url: 'https://example.com/cart',
            browser: 'Chrome',
            step_count: 15,
            status: 'inactive',
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
        page_url: '',
        browser: 'Chrome',
        description: '',
        steps: [],
        config: {
          window_size: '1920x1080',
          timeout: 30,
          screenshot: 'on_failure',
          headless: false
        },
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
          this.temp.step_count = this.temp.steps.length
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
      if (!this.temp.steps) this.temp.steps = []
      if (!this.temp.config) {
        this.temp.config = {
          window_size: '1920x1080',
          timeout: 30,
          screenshot: 'on_failure',
          headless: false
        }
      }
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
          tempData.step_count = tempData.steps.length
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
      this.$message({
        message: '正在执行UI测试用例...',
        type: 'info'
      })
      
      setTimeout(() => {
        this.executionResult = {
          status: 'PASS',
          duration: 15.6,
          browser: row.browser,
          logs: [
            { timestamp: '10:30:01', level: 'INFO', message: '启动浏览器' },
            { timestamp: '10:30:02', level: 'INFO', message: '导航到页面: ' + row.page_url },
            { timestamp: '10:30:03', level: 'INFO', message: '点击登录按钮' },
            { timestamp: '10:30:04', level: 'INFO', message: '输入用户名' },
            { timestamp: '10:30:05', level: 'INFO', message: '输入密码' },
            { timestamp: '10:30:06', level: 'INFO', message: '点击提交按钮' },
            { timestamp: '10:30:07', level: 'INFO', message: '验证登录成功' },
            { timestamp: '10:30:08', level: 'INFO', message: '测试完成' }
          ],
          step_results: [
            { action: '点击', locator: '#login-btn', status: 'PASS', duration: 156, error: '' },
            { action: '输入', locator: '#username', status: 'PASS', duration: 89, error: '' },
            { action: '输入', locator: '#password', status: 'PASS', duration: 92, error: '' },
            { action: '点击', locator: '#submit-btn', status: 'PASS', duration: 234, error: '' },
            { action: '断言', locator: '.success-msg', status: 'PASS', duration: 45, error: '' }
          ],
          screenshots: [
            { step_name: '登录页面', url: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==' },
            { step_name: '登录成功', url: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==' }
          ]
        }
        this.resultDialogVisible = true
      }, 3000)
    },
    handleRecord(row) {
      this.$message({
        message: '录制功能开发中，将打开浏览器进行操作录制...',
        type: 'info'
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
    addStep() {
      this.temp.steps.push({
        action: 'click',
        locator: '',
        value: '',
        wait_time: 1000,
        description: ''
      })
    },
    removeStep(index) {
      this.temp.steps.splice(index, 1)
    },
    editElement(step) {
      this.currentElement = {
        locator_type: 'css',
        locator: step.locator,
        name: step.description
      }
      this.currentStep = step
      this.elementDialogVisible = true
    },
    updateLocator() {
      // 根据定位方式更新定位表达式的提示
    },
    validateElement() {
      // 模拟元素验证
      this.elementValidation = {
        status: true,
        success: true,
        message: '元素定位成功，找到1个匹配的元素'
      }
    },
    saveElement() {
      if (this.currentStep) {
        this.currentStep.locator = this.currentElement.locator
        this.currentStep.description = this.currentElement.name
      }
      this.elementDialogVisible = false
    },
    startRecord() {
      this.$message({
        message: '开始录制操作，请在新打开的浏览器窗口中进行操作...',
        type: 'info'
      })
    },
    importSteps() {
      this.$message({
        message: '导入步骤功能开发中...',
        type: 'info'
      })
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

.steps-container {
  border: 1px solid #dcdfe6;
  padding: 15px;
  border-radius: 4px;
}

.steps-header {
  margin-bottom: 15px;
}

.result-header {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.execution-log {
  max-height: 400px;
  overflow-y: auto;
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
}

.log-item {
  margin-bottom: 5px;
  font-family: monospace;
}

.log-time {
  color: #909399;
  margin-right: 10px;
}

.log-level-INFO {
  color: #409EFF;
  margin-right: 10px;
  font-weight: bold;
}

.log-level-ERROR {
  color: #F56C6C;
  margin-right: 10px;
  font-weight: bold;
}

.log-level-WARN {
  color: #E6A23C;
  margin-right: 10px;
  font-weight: bold;
}

.log-message {
  color: #303133;
}

.screenshots {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.screenshot-item {
  text-align: center;
}

.success-text {
  color: #67C23A;
  margin-left: 10px;
}

.error-text {
  color: #F56C6C;
  margin-left: 10px;
}

/* 操作按钮组样式优化 */
.button-group {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.button-group .el-button {
  margin: 0;
  min-width: 60px;
}
</style>
