<template>
  <div class="app-container">
    <el-card>
      <div slot="header">
        <span>创建新项目</span>
      </div>
      
      <el-form ref="projectForm" :model="projectForm" :rules="rules" label-width="120px" style="max-width: 600px;">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="projectForm.name" placeholder="请输入项目名称" />
        </el-form-item>
        
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="projectForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入项目描述"
          />
        </el-form-item>
        
        <el-form-item label="项目类型" prop="type">
          <el-select v-model="projectForm.type" placeholder="请选择项目类型" style="width: 100%;">
            <el-option label="接口测试" value="api" />
            <el-option label="UI测试" value="ui" />
            <el-option label="混合测试" value="mixed" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="测试环境" prop="environment">
          <el-checkbox-group v-model="projectForm.environment">
            <el-checkbox label="dev">开发环境</el-checkbox>
            <el-checkbox label="test">测试环境</el-checkbox>
            <el-checkbox label="staging">预发布环境</el-checkbox>
            <el-checkbox label="prod">生产环境</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="项目成员" prop="members">
          <el-select
            v-model="projectForm.members"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="请选择或输入项目成员"
            style="width: 100%;"
          >
            <el-option
              v-for="item in memberOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="基础URL" prop="baseUrl">
          <el-input v-model="projectForm.baseUrl" placeholder="请输入项目基础URL，如：https://api.example.com" />
        </el-form-item>
        
        <el-form-item label="数据库配置">
          <el-card shadow="never" style="background-color: #f5f7fa;">
            <el-form-item label="数据库类型" prop="database.type" label-width="100px">
              <el-select v-model="projectForm.database.type" placeholder="请选择数据库类型">
                <el-option label="MySQL" value="mysql" />
                <el-option label="PostgreSQL" value="postgresql" />
                <el-option label="MongoDB" value="mongodb" />
                <el-option label="Redis" value="redis" />
              </el-select>
            </el-form-item>
            <el-form-item label="连接地址" prop="database.host" label-width="100px">
              <el-input v-model="projectForm.database.host" placeholder="数据库连接地址" />
            </el-form-item>
            <el-form-item label="端口" prop="database.port" label-width="100px">
              <el-input v-model="projectForm.database.port" placeholder="端口号" />
            </el-form-item>
            <el-form-item label="数据库名" prop="database.name" label-width="100px">
              <el-input v-model="projectForm.database.name" placeholder="数据库名称" />
            </el-form-item>
          </el-card>
        </el-form-item>
        
        <el-form-item label="通知设置">
          <el-card shadow="never" style="background-color: #f5f7fa;">
            <el-form-item label="邮件通知" label-width="100px">
              <el-switch v-model="projectForm.notification.email" />
            </el-form-item>
            <el-form-item label="钉钉通知" label-width="100px">
              <el-switch v-model="projectForm.notification.dingtalk" />
            </el-form-item>
            <el-form-item label="企业微信" label-width="100px">
              <el-switch v-model="projectForm.notification.wechat" />
            </el-form-item>
          </el-card>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitForm">创建项目</el-button>
          <el-button @click="resetForm">重置</el-button>
          <el-button @click="$router.go(-1)">返回</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'ProjectCreate',
  data() {
    return {
      projectForm: {
        name: '',
        description: '',
        type: '',
        environment: [],
        members: [],
        baseUrl: '',
        database: {
          type: '',
          host: '',
          port: '',
          name: ''
        },
        notification: {
          email: false,
          dingtalk: false,
          wechat: false
        }
      },
      memberOptions: [
        { value: 'admin', label: '管理员' },
        { value: 'tester1', label: '测试员1' },
        { value: 'tester2', label: '测试员2' },
        { value: 'developer1', label: '开发员1' },
        { value: 'developer2', label: '开发员2' }
      ],
      rules: {
        name: [
          { required: true, message: '请输入项目名称', trigger: 'blur' },
          { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
        ],
        description: [
          { required: true, message: '请输入项目描述', trigger: 'blur' },
          { min: 10, max: 200, message: '长度在 10 到 200 个字符', trigger: 'blur' }
        ],
        type: [
          { required: true, message: '请选择项目类型', trigger: 'change' }
        ],
        environment: [
          { type: 'array', required: true, message: '请至少选择一个测试环境', trigger: 'change' }
        ],
        baseUrl: [
          { required: true, message: '请输入基础URL', trigger: 'blur' },
          { type: 'url', message: '请输入正确的URL格式', trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    submitForm() {
      this.$refs.projectForm.validate((valid) => {
        if (valid) {
          // 这里应该调用API创建项目
          console.log('创建项目:', this.projectForm)
          
          this.$notify({
            title: '成功',
            message: '项目创建成功',
            type: 'success',
            duration: 2000
          })
          
          // 创建成功后跳转到项目列表
          setTimeout(() => {
            this.$router.push('/project/list')
          }, 1000)
        } else {
          this.$message.error('请检查表单填写是否正确')
          return false
        }
      })
    },
    resetForm() {
      this.$refs.projectForm.resetFields()
      this.projectForm.database = {
        type: '',
        host: '',
        port: '',
        name: ''
      }
      this.projectForm.notification = {
        email: false,
        dingtalk: false,
        wechat: false
      }
    }
  }
}
</script>

<style scoped>
.app-container {
  padding: 20px;
}
</style>
