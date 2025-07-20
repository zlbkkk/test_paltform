<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.name"
        placeholder="元素名称"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-select v-model="listQuery.page" placeholder="所属页面" clearable style="width: 200px" class="filter-item">
        <el-option v-for="item in pageOptions" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-plus" @click="handleCreate">
        新建元素
      </el-button>
      <el-button class="filter-item" type="success" icon="el-icon-view" @click="handleCapture">
        元素捕获
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
      <el-table-column label="元素名称" min-width="150px">
        <template slot-scope="{row}">
          <span class="link-type" @click="handleUpdate(row)">{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="定位方式" width="120px" align="center">
        <template slot-scope="{row}">
          <el-tag :type="row.locator_type | locatorTypeFilter">{{ row.locator_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="定位表达式" min-width="200px">
        <template slot-scope="{row}">
          <code>{{ row.locator }}</code>
        </template>
      </el-table-column>
      <el-table-column label="所属页面" width="150px">
        <template slot-scope="{row}">
          <span>{{ row.page_name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100px" align="center">
        <template slot-scope="{row}">
          <el-tag :type="row.status === 'valid' ? 'success' : 'danger'">
            {{ row.status === 'valid' ? '有效' : '无效' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="最后验证" width="150px" align="center">
        <template slot-scope="{row}">
          <span>{{ row.last_validated | parseTime }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="300" class-name="small-padding fixed-width">
        <template slot-scope="{row,$index}">
          <div class="button-group">
            <el-button type="primary" size="mini" @click="handleUpdate(row)">
              编辑
            </el-button>
            <el-button type="success" size="mini" @click="handleValidate(row)">
              验证
            </el-button>
            <el-button type="info" size="mini" @click="handleHighlight(row)">
              高亮
            </el-button>
            <el-button size="mini" type="danger" @click="handleDelete(row,$index)">
              删除
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />

    <!-- 元素编辑对话框 -->
    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible" width="70%">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="元素名称" prop="name">
              <el-input v-model="temp.name" placeholder="请输入元素名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属页面" prop="page_id">
              <el-select v-model="temp.page_id" placeholder="请选择页面" style="width: 100%;">
                <el-option v-for="item in pageOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="定位方式" prop="locator_type">
          <el-select v-model="temp.locator_type" @change="onLocatorTypeChange">
            <el-option label="CSS选择器" value="css" />
            <el-option label="XPath" value="xpath" />
            <el-option label="ID" value="id" />
            <el-option label="Name" value="name" />
            <el-option label="Class Name" value="class" />
            <el-option label="Tag Name" value="tag" />
            <el-option label="Link Text" value="link_text" />
            <el-option label="Partial Link Text" value="partial_link_text" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="定位表达式" prop="locator">
          <el-input 
            v-model="temp.locator" 
            type="textarea" 
            :rows="3" 
            :placeholder="locatorPlaceholder"
          />
          <div class="locator-tips">
            <small>{{ locatorTips }}</small>
          </div>
        </el-form-item>
        
        <el-form-item label="元素描述">
          <el-input v-model="temp.description" type="textarea" :rows="2" placeholder="请输入元素描述" />
        </el-form-item>
        
        <el-form-item label="等待策略">
          <el-card shadow="never">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="等待类型" label-width="80px">
                  <el-select v-model="temp.wait_strategy.type">
                    <el-option label="元素可见" value="visible" />
                    <el-option label="元素存在" value="present" />
                    <el-option label="元素可点击" value="clickable" />
                    <el-option label="固定等待" value="sleep" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="超时时间(s)" label-width="80px">
                  <el-input-number v-model="temp.wait_strategy.timeout" :min="1" :max="60" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="轮询间隔(ms)" label-width="80px">
                  <el-input-number v-model="temp.wait_strategy.poll_frequency" :min="100" :max="5000" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-card>
        </el-form-item>
        
        <el-form-item label="验证元素">
          <el-button type="primary" @click="validateElement" :loading="validating">
            <i class="el-icon-search"></i> 验证定位
          </el-button>
          <el-button type="success" @click="highlightElement" :disabled="!temp.locator">
            <i class="el-icon-view"></i> 高亮显示
          </el-button>
          <div v-if="validationResult.message" class="validation-result">
            <el-alert 
              :title="validationResult.message" 
              :type="validationResult.success ? 'success' : 'error'"
              :closable="false"
              show-icon
            />
          </div>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取消</el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">确认</el-button>
      </div>
    </el-dialog>

    <!-- 元素捕获对话框 -->
    <el-dialog title="元素捕获工具" :visible.sync="captureDialogVisible" width="60%">
      <div class="capture-container">
        <el-form :model="captureForm" label-width="100px">
          <el-form-item label="目标页面">
            <el-input v-model="captureForm.url" placeholder="请输入要捕获元素的页面URL" />
          </el-form-item>
          <el-form-item label="浏览器">
            <el-select v-model="captureForm.browser">
              <el-option label="Chrome" value="chrome" />
              <el-option label="Firefox" value="firefox" />
              <el-option label="Safari" value="safari" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="startCapture" :loading="capturing">
              <i class="el-icon-camera"></i> 开始捕获
            </el-button>
            <el-button @click="stopCapture" :disabled="!capturing">
              <i class="el-icon-video-pause"></i> 停止捕获
            </el-button>
          </el-form-item>
        </el-form>
        
        <div v-if="capturedElements.length > 0" class="captured-elements">
          <h4>已捕获的元素</h4>
          <el-table :data="capturedElements" border>
            <el-table-column prop="name" label="元素名称" />
            <el-table-column prop="locator_type" label="定位方式" width="100" />
            <el-table-column prop="locator" label="定位表达式" />
            <el-table-column label="操作" width="120">
              <template slot-scope="scope">
                <el-button type="primary" size="mini" @click="addCapturedElement(scope.row)">添加</el-button>
                <el-button type="danger" size="mini" @click="removeCapturedElement(scope.$index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import waves from '@/directive/waves'
import Pagination from '@/components/Pagination'

export default {
  name: 'UiElement',
  components: { Pagination },
  directives: { waves },
  filters: {
    locatorTypeFilter(type) {
      const typeMap = {
        css: 'primary',
        xpath: 'success',
        id: 'warning',
        name: 'info',
        class: 'danger'
      }
      return typeMap[type] || 'default'
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
        page: undefined
      },
      pageOptions: [
        { value: 1, label: '登录页面' },
        { value: 2, label: '首页' },
        { value: 3, label: '商品列表页' },
        { value: 4, label: '购物车页面' },
        { value: 5, label: '订单页面' }
      ],
      temp: {
        id: undefined,
        name: '',
        page_id: undefined,
        locator_type: 'css',
        locator: '',
        description: '',
        wait_strategy: {
          type: 'visible',
          timeout: 10,
          poll_frequency: 500
        }
      },
      dialogFormVisible: false,
      captureDialogVisible: false,
      dialogStatus: '',
      textMap: {
        update: '编辑元素',
        create: '创建元素'
      },
      rules: {
        name: [{ required: true, message: '元素名称是必填项', trigger: 'blur' }],
        page_id: [{ required: true, message: '所属页面是必填项', trigger: 'change' }],
        locator_type: [{ required: true, message: '定位方式是必填项', trigger: 'change' }],
        locator: [{ required: true, message: '定位表达式是必填项', trigger: 'blur' }]
      },
      validating: false,
      validationResult: {
        success: false,
        message: ''
      },
      captureForm: {
        url: '',
        browser: 'chrome'
      },
      capturing: false,
      capturedElements: []
    }
  },
  computed: {
    locatorPlaceholder() {
      const placeholders = {
        css: '#login-btn, .submit-button, input[type="text"]',
        xpath: '//button[@id="login-btn"], //input[@name="username"]',
        id: 'login-btn',
        name: 'username',
        class: 'submit-button',
        tag: 'button',
        link_text: '登录',
        partial_link_text: '登'
      }
      return placeholders[this.temp.locator_type] || ''
    },
    locatorTips() {
      const tips = {
        css: 'CSS选择器，如：#id, .class, input[type="text"]',
        xpath: 'XPath表达式，如：//button[@id="login"], //input[@name="username"]',
        id: '元素的id属性值',
        name: '元素的name属性值',
        class: '元素的class属性值',
        tag: '元素的标签名',
        link_text: '链接的完整文本内容',
        partial_link_text: '链接的部分文本内容'
      }
      return tips[this.temp.locator_type] || ''
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
            name: '登录按钮',
            locator_type: 'css',
            locator: '#login-btn',
            page_name: '登录页面',
            status: 'valid',
            last_validated: new Date('2024-01-15 10:30:00')
          },
          {
            id: 2,
            name: '用户名输入框',
            locator_type: 'xpath',
            locator: '//input[@name="username"]',
            page_name: '登录页面',
            status: 'valid',
            last_validated: new Date('2024-01-15 09:15:00')
          },
          {
            id: 3,
            name: '搜索按钮',
            locator_type: 'id',
            locator: 'search-btn',
            page_name: '首页',
            status: 'invalid',
            last_validated: new Date('2024-01-14 16:45:00')
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
        page_id: undefined,
        locator_type: 'css',
        locator: '',
        description: '',
        wait_strategy: {
          type: 'visible',
          timeout: 10,
          poll_frequency: 500
        }
      }
      this.validationResult = { success: false, message: '' }
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
          this.temp.id = parseInt(Math.random() * 100) + 1024;
          const foundPage = this.pageOptions.find(p => p.value === this.temp.page_id);
          this.temp.page_name = foundPage ? foundPage.label : '';
          this.temp.status = 'valid'
          this.temp.last_validated = new Date()
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
      const foundPageForUpdate = this.pageOptions.find(p => p.label === row.page_name);
      this.temp.page_id = foundPageForUpdate ? foundPageForUpdate.value : '';
      if (!this.temp.wait_strategy) {
        this.temp.wait_strategy = {
          type: 'visible',
          timeout: 10,
          poll_frequency: 500
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
          const foundPageForTempData = this.pageOptions.find(p => p.value === tempData.page_id);
          tempData.page_name = foundPageForTempData ? foundPageForTempData.label : '';
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
      this.$confirm('确认删除该元素?', '提示', {
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
    handleValidate(row) {
      this.$message({
        message: '正在验证元素定位...',
        type: 'info'
      })
      
      setTimeout(() => {
        row.status = Math.random() > 0.3 ? 'valid' : 'invalid'
        row.last_validated = new Date()
        this.$message({
          message: row.status === 'valid' ? '元素定位有效' : '元素定位无效',
          type: row.status === 'valid' ? 'success' : 'error'
        })
      }, 2000)
    },
    handleHighlight(row) {
      this.$message({
        message: '正在高亮显示元素...',
        type: 'info'
      })
    },
    handleCapture() {
      this.captureDialogVisible = true
    },
    onLocatorTypeChange() {
      this.temp.locator = ''
      this.validationResult = { success: false, message: '' }
    },
    validateElement() {
      if (!this.temp.locator) {
        this.$message.error('请先输入定位表达式')
        return
      }
      
      this.validating = true
      setTimeout(() => {
        const success = Math.random() > 0.3
        this.validationResult = {
          success,
          message: success ? '找到1个匹配的元素' : '未找到匹配的元素，请检查定位表达式'
        }
        this.validating = false
      }, 2000)
    },
    highlightElement() {
      this.$message({
        message: '正在高亮显示元素...',
        type: 'info'
      })
    },
    startCapture() {
      if (!this.captureForm.url) {
        this.$message.error('请输入目标页面URL')
        return
      }
      
      this.capturing = true
      this.$message({
        message: '正在启动浏览器进行元素捕获...',
        type: 'info'
      })
      
      // 模拟捕获过程
      setTimeout(() => {
        this.capturedElements = [
          { name: '登录按钮', locator_type: 'css', locator: '#login-btn' },
          { name: '用户名输入框', locator_type: 'id', locator: 'username' },
          { name: '密码输入框', locator_type: 'id', locator: 'password' }
        ]
        this.$message.success('元素捕获完成')
      }, 3000)
    },
    stopCapture() {
      this.capturing = false
      this.$message({
        message: '已停止元素捕获',
        type: 'info'
      })
    },
    addCapturedElement(element) {
      this.temp = {
        id: undefined,
        name: element.name,
        page_id: undefined,
        locator_type: element.locator_type,
        locator: element.locator,
        description: '',
        wait_strategy: {
          type: 'visible',
          timeout: 10,
          poll_frequency: 500
        }
      }
      this.dialogStatus = 'create'
      this.captureDialogVisible = false
      this.dialogFormVisible = true
    },
    removeCapturedElement(index) {
      this.capturedElements.splice(index, 1)
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

.locator-tips {
  margin-top: 5px;
  color: #909399;
}

.validation-result {
  margin-top: 10px;
}

.capture-container {
  max-height: 600px;
  overflow-y: auto;
}

.captured-elements {
  margin-top: 20px;
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

code {
  background-color: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
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
