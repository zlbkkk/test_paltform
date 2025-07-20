<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.name"
        placeholder="套件名称"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-select v-model="listQuery.status" placeholder="状态" clearable style="width: 120px" class="filter-item">
        <el-option v-for="item in statusOptions" :key="item.key" :label="item.display_name" :value="item.key" />
      </el-select>
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-plus" @click="handleCreate">
        新建套件
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
    >
      <el-table-column label="ID" prop="id" sortable="custom" align="center" width="80">
        <template slot-scope="{row}">
          <span>{{ row.id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="套件名称" min-width="150px">
        <template slot-scope="{row}">
          <span class="link-type" @click="handleUpdate(row)">{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="描述" min-width="200px">
        <template slot-scope="{row}">
          <span>{{ row.description }}</span>
        </template>
      </el-table-column>
      <el-table-column label="用例数量" width="100px" align="center">
        <template slot-scope="{row}">
          <span>{{ row.case_count }}</span>
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
      <el-table-column label="通过率" width="100px" align="center">
        <template slot-scope="{row}">
          <span :style="{ color: row.pass_rate >= 80 ? '#67C23A' : row.pass_rate >= 60 ? '#E6A23C' : '#F56C6C' }">
            {{ row.pass_rate }}%
          </span>
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
            <el-button type="info" size="mini" @click="handleViewReport(row)">
              报告
            </el-button>
            <el-button size="mini" type="danger" @click="handleDelete(row,$index)">
              删除
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />

    <!-- 套件编辑对话框 -->
    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible" width="70%">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="套件名称" prop="name">
              <el-input v-model="temp.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="执行环境" prop="environment">
              <el-select v-model="temp.environment" placeholder="请选择执行环境">
                <el-option label="开发环境" value="dev" />
                <el-option label="测试环境" value="test" />
                <el-option label="预发布环境" value="staging" />
                <el-option label="生产环境" value="prod" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="套件描述" prop="description">
          <el-input v-model="temp.description" type="textarea" :rows="3" />
        </el-form-item>
        
        <el-form-item label="选择用例">
          <div class="case-selection">
            <div class="available-cases">
              <h4>可用用例</h4>
              <el-input
                v-model="caseSearchKeyword"
                placeholder="搜索用例"
                prefix-icon="el-icon-search"
                style="margin-bottom: 10px;"
              />
              <el-tree
                ref="caseTree"
                :data="availableCases"
                :props="treeProps"
                show-checkbox
                node-key="id"
                :default-checked-keys="temp.case_ids"
                @check="handleCaseCheck"
              />
            </div>
            <div class="selected-cases">
              <h4>已选用例 ({{ temp.case_ids.length }})</h4>
              <el-table :data="selectedCaseList" border max-height="300">
                <el-table-column prop="name" label="用例名称" />
                <el-table-column prop="method" label="方法" width="80">
                  <template slot-scope="scope">
                    <el-tag :type="scope.row.method | methodFilter" size="mini">{{ scope.row.method }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="path" label="路径" />
                <el-table-column label="操作" width="80">
                  <template slot-scope="scope">
                    <el-button type="danger" size="mini" @click="removeCaseFromSuite(scope.row.id)">移除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-form-item>
        
        <el-form-item label="执行配置">
          <el-card shadow="never">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="并发数" label-width="80px">
                  <el-input-number v-model="temp.config.parallel" :min="1" :max="10" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="超时时间(s)" label-width="80px">
                  <el-input-number v-model="temp.config.timeout" :min="1" :max="300" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="失败重试" label-width="80px">
                  <el-input-number v-model="temp.config.retry" :min="0" :max="5" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="失败时停止" label-width="80px">
              <el-switch v-model="temp.config.stop_on_failure" />
            </el-form-item>
          </el-card>
        </el-form-item>
        
        <el-form-item label="通知设置">
          <el-card shadow="never">
            <el-checkbox-group v-model="temp.notifications">
              <el-checkbox label="email">邮件通知</el-checkbox>
              <el-checkbox label="dingtalk">钉钉通知</el-checkbox>
              <el-checkbox label="wechat">企业微信</el-checkbox>
            </el-checkbox-group>
          </el-card>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取消</el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">确认</el-button>
      </div>
    </el-dialog>

    <!-- 执行结果对话框 -->
    <el-dialog title="执行结果" :visible.sync="resultDialogVisible" width="80%">
      <div v-if="executionResult">
        <div class="result-summary">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-card>
                <div class="stat-item">
                  <div class="stat-value">{{ executionResult.total }}</div>
                  <div class="stat-label">总用例</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card>
                <div class="stat-item success">
                  <div class="stat-value">{{ executionResult.passed }}</div>
                  <div class="stat-label">通过</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card>
                <div class="stat-item danger">
                  <div class="stat-value">{{ executionResult.failed }}</div>
                  <div class="stat-label">失败</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card>
                <div class="stat-item warning">
                  <div class="stat-value">{{ executionResult.skipped }}</div>
                  <div class="stat-label">跳过</div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
        
        <el-table :data="executionResult.details" border style="margin-top: 20px;">
          <el-table-column prop="case_name" label="用例名称" />
          <el-table-column prop="method" label="方法" width="80">
            <template slot-scope="scope">
              <el-tag :type="scope.row.method | methodFilter" size="mini">{{ scope.row.method }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80">
            <template slot-scope="scope">
              <el-tag :type="scope.row.status === 'PASS' ? 'success' : 'danger'" size="mini">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="response_time" label="耗时(ms)" width="100" />
          <el-table-column prop="error_message" label="错误信息" />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import waves from '@/directive/waves'
import Pagination from '@/components/Pagination'

export default {
  name: 'ApiSuite',
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
        status: undefined
      },
      statusOptions: [
        { key: 'active', display_name: '激活' },
        { key: 'inactive', display_name: '禁用' }
      ],
      temp: {
        id: undefined,
        name: '',
        description: '',
        environment: 'test',
        case_ids: [],
        config: {
          parallel: 1,
          timeout: 30,
          retry: 0,
          stop_on_failure: false
        },
        notifications: [],
        status: 'active'
      },
      dialogFormVisible: false,
      resultDialogVisible: false,
      dialogStatus: '',
      textMap: {
        update: '编辑套件',
        create: '创建套件'
      },
      rules: {
        name: [{ required: true, message: '套件名称是必填项', trigger: 'blur' }],
        description: [{ required: true, message: '套件描述是必填项', trigger: 'blur' }],
        environment: [{ required: true, message: '执行环境是必填项', trigger: 'change' }]
      },
      caseSearchKeyword: '',
      availableCases: [
        {
          id: 1,
          label: '用户管理',
          children: [
            { id: 11, label: '用户登录接口', method: 'POST', path: '/api/auth/login' },
            { id: 12, label: '获取用户信息', method: 'GET', path: '/api/user/profile' },
            { id: 13, label: '更新用户信息', method: 'PUT', path: '/api/user/profile' }
          ]
        },
        {
          id: 2,
          label: '订单管理',
          children: [
            { id: 21, label: '创建订单', method: 'POST', path: '/api/orders' },
            { id: 22, label: '查询订单', method: 'GET', path: '/api/orders' },
            { id: 23, label: '取消订单', method: 'DELETE', path: '/api/orders/{id}' }
          ]
        }
      ],
      treeProps: {
        children: 'children',
        label: 'label'
      },
      executionResult: null
    }
  },
  computed: {
    selectedCaseList() {
      const result = []
      const findCases = (nodes) => {
        nodes.forEach(node => {
          if (node.children) {
            findCases(node.children)
          } else if (this.temp.case_ids.includes(node.id)) {
            result.push({
              id: node.id,
              name: node.label,
              method: node.method,
              path: node.path
            })
          }
        })
      }
      findCases(this.availableCases)
      return result
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
            name: '用户管理测试套件',
            description: '包含用户注册、登录、信息管理等接口测试',
            case_count: 15,
            status: 'active',
            last_run: new Date('2024-01-15 10:30:00'),
            pass_rate: 95
          },
          {
            id: 2,
            name: '订单流程测试套件',
            description: '订单创建、支付、发货、完成等流程测试',
            case_count: 23,
            status: 'active',
            last_run: new Date('2024-01-15 09:15:00'),
            pass_rate: 87
          },
          {
            id: 3,
            name: '支付接口测试套件',
            description: '支付相关接口的完整测试',
            case_count: 8,
            status: 'inactive',
            last_run: new Date('2024-01-14 16:45:00'),
            pass_rate: 62
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
    resetTemp() {
      this.temp = {
        id: undefined,
        name: '',
        description: '',
        environment: 'test',
        case_ids: [],
        config: {
          parallel: 1,
          timeout: 30,
          retry: 0,
          stop_on_failure: false
        },
        notifications: [],
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
          this.temp.case_count = this.temp.case_ids.length
          this.temp.last_run = new Date()
          this.temp.pass_rate = 100
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
      if (!this.temp.case_ids) this.temp.case_ids = []
      if (!this.temp.config) {
        this.temp.config = {
          parallel: 1,
          timeout: 30,
          retry: 0,
          stop_on_failure: false
        }
      }
      if (!this.temp.notifications) this.temp.notifications = []
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
          tempData.case_count = tempData.case_ids.length
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
      this.$confirm('确认删除该套件?', '提示', {
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
        message: '正在执行测试套件...',
        type: 'info'
      })
      
      setTimeout(() => {
        this.executionResult = {
          total: row.case_count,
          passed: Math.floor(row.case_count * 0.8),
          failed: Math.floor(row.case_count * 0.15),
          skipped: Math.floor(row.case_count * 0.05),
          details: [
            { case_name: '用户登录接口', method: 'POST', status: 'PASS', response_time: 156, error_message: '' },
            { case_name: '获取用户信息', method: 'GET', status: 'PASS', response_time: 89, error_message: '' },
            { case_name: '创建订单', method: 'POST', status: 'FAIL', response_time: 2340, error_message: '连接超时' }
          ]
        }
        this.resultDialogVisible = true
      }, 3000)
    },
    handleViewReport(row) {
      this.$message({
        message: '查看测试报告功能开发中...',
        type: 'info'
      })
    },
    handleCaseCheck(data, checked) {
      this.temp.case_ids = checked.checkedKeys
    },
    removeCaseFromSuite(caseId) {
      const index = this.temp.case_ids.indexOf(caseId)
      if (index > -1) {
        this.temp.case_ids.splice(index, 1)
        this.$refs.caseTree.setCheckedKeys(this.temp.case_ids)
      }
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

.case-selection {
  display: flex;
  gap: 20px;
}

.available-cases, .selected-cases {
  flex: 1;
  border: 1px solid #dcdfe6;
  padding: 15px;
  border-radius: 4px;
}

.result-summary {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.stat-item.success .stat-value {
  color: #67C23A;
}

.stat-item.danger .stat-value {
  color: #F56C6C;
}

.stat-item.warning .stat-value {
  color: #E6A23C;
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
