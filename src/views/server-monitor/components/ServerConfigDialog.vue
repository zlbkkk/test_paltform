<template>
  <el-dialog
    :title="isEdit ? '编辑服务器' : '添加服务器'"
    :visible.sync="dialogVisible"
    width="600px"
    :before-close="handleClose"
    class="server-config-dialog"
  >
    <el-form
      ref="serverForm"
      :model="formData"
      :rules="formRules"
      label-width="120px"
    >
      <el-form-item label="服务器名称" prop="name">
        <el-input
          v-model="formData.name"
          placeholder="请输入服务器名称"
          maxlength="50"
        ></el-input>
      </el-form-item>
      
      <el-form-item label="主机地址" prop="host">
        <el-input
          v-model="formData.host"
          placeholder="IP地址或域名，如: 192.168.1.100"
        ></el-input>
      </el-form-item>
      
      <el-form-item label="SSH端口" prop="port">
        <el-input-number
          v-model="formData.port"
          :min="1"
          :max="65535"
          placeholder="SSH端口号"
          style="width: 100%"
        ></el-input-number>
      </el-form-item>
      
      <el-form-item label="认证方式" prop="auth_type">
        <el-radio-group v-model="formData.auth_type">
          <el-radio label="password">密码认证</el-radio>
          <el-radio label="key">密钥认证</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="用户名" prop="username">
        <el-input
          v-model="formData.username"
          placeholder="SSH登录用户名"
        ></el-input>
      </el-form-item>
      
      <el-form-item 
        v-if="formData.auth_type === 'password'" 
        label="密码" 
        prop="password"
      >
        <el-input
          v-model="formData.password"
          type="password"
          placeholder="SSH登录密码"
          show-password
        ></el-input>
      </el-form-item>
      
      <el-form-item 
        v-if="formData.auth_type === 'key'" 
        label="私钥文件" 
        prop="private_key_path"
      >
        <el-input
          v-model="formData.private_key_path"
          placeholder="私钥文件路径，如: ~/.ssh/id_rsa"
        ></el-input>
      </el-form-item>
      
      <el-form-item 
        v-if="formData.auth_type === 'key'" 
        label="私钥密码" 
        prop="key_password"
      >
        <el-input
          v-model="formData.key_password"
          type="password"
          placeholder="私钥密码（如果有）"
          show-password
        ></el-input>
      </el-form-item>
      
      <el-form-item label="监控间隔">
        <el-select v-model="formData.monitor_interval" style="width: 100%">
          <el-option label="10秒" :value="10"></el-option>
          <el-option label="30秒" :value="30"></el-option>
          <el-option label="1分钟" :value="60"></el-option>
          <el-option label="5分钟" :value="300"></el-option>
        </el-select>
        <div class="form-tip">数据采集间隔时间</div>
      </el-form-item>
      
      <el-form-item label="描述">
        <el-input
          v-model="formData.description"
          type="textarea"
          :rows="3"
          placeholder="服务器描述信息（可选）"
          maxlength="200"
        ></el-input>
      </el-form-item>
      
      <el-form-item label="启用监控">
        <el-switch v-model="formData.enabled"></el-switch>
        <div class="form-tip">是否启用对此服务器的监控</div>
      </el-form-item>
    </el-form>
    
    <div class="test-connection">
      <el-button 
        @click="testConnection" 
        :loading="testing"
        icon="el-icon-connection"
      >
        测试连接
      </el-button>
      <span v-if="testResult" :class="testResult.success ? 'test-success' : 'test-error'">
        {{ testResult.message }}
      </span>
    </div>
    
    <span slot="footer" class="dialog-footer">
      <el-button @click="handleClose">取消</el-button>
      <el-button 
        v-if="isEdit" 
        type="danger" 
        @click="handleDelete"
        :loading="deleting"
      >
        删除
      </el-button>
      <el-button 
        type="primary" 
        @click="handleSave"
        :loading="saving"
      >
        保存
      </el-button>
    </span>
  </el-dialog>
</template>

<script>
import { saveServer, deleteServer, testServerConnection } from '@/api/server-monitor'

export default {
  name: 'ServerConfigDialog',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    server: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      dialogVisible: false,
      saving: false,
      deleting: false,
      testing: false,
      testResult: null,
      
      formData: {
        id: null,
        name: '',
        host: '',
        port: 22,
        auth_type: 'password',
        username: 'root',
        password: '',
        private_key_path: '',
        key_password: '',
        monitor_interval: 30,
        description: '',
        enabled: true
      },
      
      formRules: {
        name: [
          { required: true, message: '请输入服务器名称', trigger: 'blur' },
          { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
        ],
        host: [
          { required: true, message: '请输入主机地址', trigger: 'blur' },
          { 
            pattern: /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$|^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$/,
            message: '请输入有效的IP地址或域名',
            trigger: 'blur'
          }
        ],
        port: [
          { required: true, message: '请输入端口号', trigger: 'blur' },
          { type: 'number', min: 1, max: 65535, message: '端口号范围 1-65535', trigger: 'blur' }
        ],
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        password: [
          { 
            validator: (rule, value, callback) => {
              if (this.formData.auth_type === 'password' && !value) {
                callback(new Error('请输入密码'))
              } else {
                callback()
              }
            }, 
            trigger: 'blur' 
          }
        ],
        private_key_path: [
          { 
            validator: (rule, value, callback) => {
              if (this.formData.auth_type === 'key' && !value) {
                callback(new Error('请输入私钥文件路径'))
              } else {
                callback()
              }
            }, 
            trigger: 'blur' 
          }
        ]
      }
    }
  },
  computed: {
    isEdit() {
      return this.server && this.server.id
    }
  },
  watch: {
    visible(val) {
      this.dialogVisible = val
      if (val) {
        this.initForm()
        this.testResult = null
      }
    },
    dialogVisible(val) {
      this.$emit('update:visible', val)
    }
  },
  methods: {
    initForm() {
      if (this.server) {
        // 编辑模式
        this.formData = {
          ...this.formData,
          ...this.server
        }
      } else {
        // 新增模式
        this.formData = {
          id: null,
          name: '',
          host: '',
          port: 22,
          auth_type: 'password',
          username: 'root',
          password: '',
          private_key_path: '',
          key_password: '',
          monitor_interval: 30,
          description: '',
          enabled: true
        }
      }
      
      // 清除验证结果
      this.$nextTick(() => {
        if (this.$refs.serverForm) {
          this.$refs.serverForm.clearValidate()
        }
      })
    },
    
    async testConnection() {
      // 先验证必填字段
      try {
        await this.$refs.serverForm.validateField(['name', 'host', 'port', 'username'])
      } catch (error) {
        this.$message.warning('请先填写完整的连接信息')
        return
      }
      
      this.testing = true
      this.testResult = null
      
      try {
        const response = await testServerConnection(null, this.formData)
        
        this.testResult = {
          success: response.success,
          message: response.success ? '连接成功！' : response.error
        }
        
        if (response.success) {
          this.$message.success('服务器连接测试成功')
        } else {
          this.$message.error('连接失败: ' + response.error)
        }
      } catch (error) {
        this.testResult = {
          success: false,
          message: '连接测试失败: ' + error.message
        }
        this.$message.error('连接测试失败: ' + error.message)
      } finally {
        this.testing = false
      }
    },
    
    async handleSave() {
      try {
        await this.$refs.serverForm.validate()
      } catch (error) {
        return
      }
      
      this.saving = true
      
      try {
        const response = await saveServer(this.formData)
        
        if (response.success) {
          this.$message.success(this.isEdit ? '服务器更新成功' : '服务器添加成功')
          this.$emit('save', response.data)
        } else {
          this.$message.error(response.error || '保存失败')
        }
      } catch (error) {
        this.$message.error('保存失败: ' + error.message)
      } finally {
        this.saving = false
      }
    },
    
    async handleDelete() {
      if (!this.isEdit) return
      
      try {
        await this.$confirm('确定要删除这个服务器配置吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
      } catch (error) {
        return
      }
      
      this.deleting = true
      
      try {
        const response = await deleteServer(this.formData.id)
        
        if (response.success) {
          this.$message.success('服务器删除成功')
          this.$emit('delete', this.formData.id)
        } else {
          this.$message.error(response.error || '删除失败')
        }
      } catch (error) {
        this.$message.error('删除失败: ' + error.message)
      } finally {
        this.deleting = false
      }
    },
    
    handleClose() {
      this.dialogVisible = false
    }
  }
}
</script>

<style scoped>
.server-config-dialog {
  color: #d9d9d9;
}

.form-tip {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 5px;
}

.test-connection {
  margin: 20px 0;
  padding: 15px;
  background: #1f2329;
  border-radius: 4px;
  border: 1px solid #2f3349;
  display: flex;
  align-items: center;
  gap: 15px;
}

.test-success {
  color: #52c41a;
  font-weight: bold;
}

.test-error {
  color: #f5222d;
  font-weight: bold;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* Element UI 样式覆盖 */
.server-config-dialog .el-dialog {
  background: #1f2329;
  border: 1px solid #2f3349;
}

.server-config-dialog .el-dialog__header {
  background: #262c36;
  border-bottom: 1px solid #2f3349;
}

.server-config-dialog .el-dialog__title {
  color: #ffffff;
}

.server-config-dialog .el-form-item__label {
  color: #d9d9d9;
}

.server-config-dialog .el-input__inner {
  background: #262c36;
  border-color: #2f3349;
  color: #d9d9d9;
}

.server-config-dialog .el-input__inner:focus {
  border-color: #52c41a;
}

.server-config-dialog .el-textarea__inner {
  background: #262c36;
  border-color: #2f3349;
  color: #d9d9d9;
}

.server-config-dialog .el-textarea__inner:focus {
  border-color: #52c41a;
}

.server-config-dialog .el-radio__label {
  color: #d9d9d9;
}

.server-config-dialog .el-radio__input.is-checked .el-radio__inner {
  background: #52c41a;
  border-color: #52c41a;
}

.server-config-dialog .el-select .el-input__inner {
  background: #262c36;
  border-color: #2f3349;
  color: #d9d9d9;
}
</style>
