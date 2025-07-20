<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.name"
        placeholder="项目名称"
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
        新建项目
      </el-button>
    </div>

    <div class="table-container">
      <el-table
        :key="tableKey"
        v-loading="listLoading"
        :data="list"
        border
        fit
        highlight-current-row
        style="width: 100%; min-width: 1100px;"
        :row-style="{ height: '48px' }"
        :cell-style="{ padding: '8px 0', 'white-space': 'nowrap' }"
      >
      <el-table-column label="ID" prop="id" sortable="custom" align="center" width="60">
        <template slot-scope="{row}">
          <span>{{ row.id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="项目名称" width="180" show-overflow-tooltip>
        <template slot-scope="{row}">
          <el-tooltip :content="row.name" placement="top" :disabled="!isTextOverflow(row.name, 180)">
            <span class="link-type text-ellipsis" @click="handleUpdate(row)">{{ row.name }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column label="描述" width="220" show-overflow-tooltip>
        <template slot-scope="{row}">
          <el-tooltip :content="row.description" placement="top" :disabled="!isTextOverflow(row.description, 220)">
            <span class="text-ellipsis">{{ row.description }}</span>
          </el-tooltip>
        </template>
      </el-table-column>

      <el-table-column label="状态" class-name="status-col" width="80" align="center">
        <template slot-scope="{row}">
          <el-tag
            :type="row.status | statusFilter"
            :class="{ 'status-changed': row.statusChanged }"
            size="small"
          >
            {{ row.status | statusDisplayFilter }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="创建人" width="100" align="center" show-overflow-tooltip>
        <template slot-scope="{row}">
          <span>{{ row.creator }}</span>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180" align="center" show-overflow-tooltip>
        <template slot-scope="{row}">
          <span>{{ row.created_at | parseTime }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="220" class-name="small-padding fixed-width">
        <template slot-scope="{row,$index}">
          <div class="button-group">
            <el-button type="primary" size="mini" @click="handleUpdate(row)">
              编辑
            </el-button>
            <el-button
              v-if="row.status === 'inactive'"
              size="mini"
              type="success"
              @click="handleModifyStatus(row,'active')"
            >
              激活
            </el-button>
            <el-button
              v-if="row.status === 'active'"
              size="mini"
              type="warning"
              @click="handleModifyStatus(row,'inactive')"
            >
              禁用
            </el-button>
            <el-button v-if="row.status!='deleted'" size="mini" type="danger" @click="handleDelete(row,$index)">
              删除
            </el-button>
          </div>
        </template>
      </el-table-column>
      </el-table>
    </div>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />

    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="100px" style="width: 400px; margin-left:50px;">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="temp.name" />
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input v-model="temp.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="temp.status" class="filter-item" placeholder="请选择">
            <el-option v-for="item in statusOptions" :key="item.key" :label="item.display_name" :value="item.key" />
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          取消
        </el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">
          确认
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import waves from '@/directive/waves' // waves directive
import Pagination from '@/components/Pagination' // secondary package based on el-pagination

export default {
  name: 'ProjectList',
  components: { Pagination },
  directives: { waves },
  filters: {
    statusFilter(status) {
      const statusMap = {
        active: 'success',
        inactive: 'info',
        deleted: 'danger'
      }
      return statusMap[status]
    },
    statusDisplayFilter(status) {
      const statusMap = {
        active: '激活',
        inactive: '禁用',
        deleted: '已删除'
      }
      return statusMap[status]
    },
    parseTime(time) {
      if (!time) return ''
      const date = new Date(time)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      return `${year}-${month}-${day} ${hours}:${minutes}`
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
        status: 'active'
      },
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: '编辑项目',
        create: '创建项目'
      },
      rules: {
        name: [{ required: true, message: '项目名称是必填项', trigger: 'blur' }],
        description: [{ required: true, message: '项目描述是必填项', trigger: 'blur' }]
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    // 检查文本是否超出指定宽度
    isTextOverflow(text, maxWidth) {
      if (!text) return false
      // 简单估算：中文字符约14px，英文字符约8px
      const chineseChars = (text.match(/[\u4e00-\u9fa5]/g) || []).length
      const englishChars = text.length - chineseChars
      const estimatedWidth = chineseChars * 14 + englishChars * 8
      return estimatedWidth > maxWidth - 40 // 减去padding等空间
    },
    getList() {
      this.listLoading = true
      // 模拟数据
      setTimeout(() => {
        this.list = [
          {
            id: 1,
            name: '电商平台测试',
            description: '电商平台的自动化测试项目',
            status: 'active',
            creator: 'admin',
            created_at: new Date('2024-01-10')
          },
          {
            id: 2,
            name: '用户管理系统',
            description: '用户管理系统的测试项目',
            status: 'active',
            creator: 'tester',
            created_at: new Date('2024-01-12')
          },
          {
            id: 3,
            name: '支付系统测试',
            description: '支付系统的接口和UI测试',
            status: 'inactive',
            creator: 'admin',
            created_at: new Date('2024-01-15')
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
    handleModifyStatus(row, status) {
      const statusText = status === 'active' ? '激活' : '禁用'

      this.$confirm(`确认${statusText}项目 "${row.name}"?`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 模拟API调用
        const loading = this.$loading({
          lock: true,
          text: `正在${statusText}项目...`,
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        })

        setTimeout(() => {
          // 更新状态
          row.status = status
          // 添加状态变化标记，用于视觉反馈
          this.$set(row, 'statusChanged', true)

          loading.close()

          this.$notify({
            title: '成功',
            message: `项目已${statusText}`,
            type: 'success',
            duration: 2000
          })

          // 3秒后移除状态变化标记
          setTimeout(() => {
            this.$set(row, 'statusChanged', false)
          }, 3000)
        }, 800)
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消操作'
        })
      })
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        name: '',
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
          this.temp.creator = 'admin'
          this.temp.created_at = new Date()
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
      this.$confirm(`确认删除项目 "${row.name}"?`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const loading = this.$loading({
          lock: true,
          text: '正在删除项目...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        })

        setTimeout(() => {
          this.list.splice(index, 1)
          this.total = this.list.length
          loading.close()

          this.$notify({
            title: '成功',
            message: `项目 "${row.name}" 已删除`,
            type: 'success',
            duration: 2000
          })
        }, 800)
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
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

/* 操作按钮组样式优化 */
.button-group {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
  flex-wrap: nowrap;
  white-space: nowrap;
}

.button-group .el-button {
  margin: 0 !important;
  padding: 4px 8px !important;
  font-size: 12px !important;
  min-width: auto !important;
}

/* 操作按钮布局优化 */
.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: center;
  align-items: center;
}

.action-buttons .el-button {
  margin: 0 !important;
  padding: 5px 8px !important;
  font-size: 12px !important;
  min-width: auto !important;
}

/* 表格整体样式优化 */
.el-table {
  font-size: 13px;
  width: 100% !important;
}

.el-table .cell {
  padding: 0 8px;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.el-table th {
  padding: 8px 0;
  font-size: 13px;
}

.el-table td {
  padding: 8px 0;
}

/* 确保表格占满容器宽度 */
.app-container {
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
}

/* 防止文本换行 */
.el-table .cell {
  white-space: nowrap !important;
}

/* 文本省略号样式 */
.text-ellipsis {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: top;
}

/* 项目名称链接样式 */
.link-type {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
  color: #409EFF;
  transition: color 0.3s;
}

.link-type:hover {
  color: #66b1ff;
}

/* ID列确保不换行 */
.el-table .cell {
  white-space: nowrap !important;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 表格行高度固定 */
.el-table td {
  height: 48px !important;
  padding: 8px 0 !important;
}

/* 确保所有列内容都不换行 */
.el-table .cell {
  line-height: 32px !important;
  height: 32px !important;
  display: flex;
  align-items: center;
}

/* 状态标签优化 */
.el-tag--small {
  padding: 0 6px;
  height: 20px;
  line-height: 18px;
  font-size: 11px;
}

/* 表格容器样式 */
.table-container {
  overflow-x: auto;
  width: 100%;
}

/* 状态变化动画效果 */
.status-changed {
  animation: statusChange 0.6s ease-in-out;
  box-shadow: 0 0 10px rgba(24, 144, 255, 0.5);
}

@keyframes statusChange {
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 rgba(24, 144, 255, 0.5);
  }
  50% {
    transform: scale(1.1);
    box-shadow: 0 0 15px rgba(24, 144, 255, 0.8);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 10px rgba(24, 144, 255, 0.5);
  }
}
</style>
