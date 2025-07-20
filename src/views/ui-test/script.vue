<template>
  <div class="app-container">
    <div class="script-editor-container">
      <el-row :gutter="20">
        <!-- 左侧脚本编辑区 -->
        <el-col :span="16">
          <el-card>
            <div slot="header">
              <span>脚本编辑器</span>
              <div style="float: right;">
                <el-select v-model="currentScript.language" size="mini" style="width: 120px; margin-right: 10px;">
                  <el-option label="Python" value="python" />
                  <el-option label="Java" value="java" />
                  <el-option label="JavaScript" value="javascript" />
                  <el-option label="C#" value="csharp" />
                </el-select>
                <el-button type="primary" size="mini" @click="saveScript">保存</el-button>
                <el-button type="success" size="mini" @click="runScript">运行</el-button>
              </div>
            </div>
            
            <div class="script-editor">
              <codemirror
                ref="codemirror"
                v-model="currentScript.content"
                :options="editorOptions"
                @input="onScriptChange"
              />
            </div>
          </el-card>
        </el-col>
        
        <!-- 右侧工具面板 -->
        <el-col :span="8">
          <el-card>
            <div slot="header">
              <span>工具面板</span>
            </div>
            
            <el-tabs v-model="activeToolTab" type="border-card">
              <!-- 元素库 -->
              <el-tab-pane label="元素库" name="elements">
                <div class="tool-section">
                  <el-input
                    v-model="elementSearch"
                    placeholder="搜索元素"
                    prefix-icon="el-icon-search"
                    size="mini"
                    style="margin-bottom: 10px;"
                  />
                  <div class="element-list">
                    <div
                      v-for="element in filteredElements"
                      :key="element.id"
                      class="element-item"
                      @click="insertElement(element)"
                    >
                      <div class="element-name">{{ element.name }}</div>
                      <div class="element-locator">{{ element.locator }}</div>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
              
              <!-- 代码模板 -->
              <el-tab-pane label="代码模板" name="templates">
                <div class="tool-section">
                  <div class="template-category">
                    <h4>基础操作</h4>
                    <div
                      v-for="template in basicTemplates"
                      :key="template.name"
                      class="template-item"
                      @click="insertTemplate(template)"
                    >
                      <div class="template-name">{{ template.name }}</div>
                      <div class="template-desc">{{ template.description }}</div>
                    </div>
                  </div>
                  
                  <div class="template-category">
                    <h4>断言验证</h4>
                    <div
                      v-for="template in assertTemplates"
                      :key="template.name"
                      class="template-item"
                      @click="insertTemplate(template)"
                    >
                      <div class="template-name">{{ template.name }}</div>
                      <div class="template-desc">{{ template.description }}</div>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
              
              <!-- 运行日志 -->
              <el-tab-pane label="运行日志" name="logs">
                <div class="tool-section">
                  <div class="log-container">
                    <div v-for="(log, index) in executionLogs" :key="index" class="log-item">
                      <span class="log-time">{{ log.timestamp }}</span>
                      <span :class="'log-level-' + log.level">{{ log.level }}</span>
                      <span class="log-message">{{ log.message }}</span>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 底部控制台 -->
      <el-row style="margin-top: 20px;">
        <el-col :span="24">
          <el-card>
            <div slot="header">
              <span>控制台输出</span>
              <div style="float: right;">
                <el-button type="info" size="mini" @click="clearConsole">清空</el-button>
              </div>
            </div>
            
            <div class="console-output">
              <div v-for="(output, index) in consoleOutput" :key="index" class="console-line">
                <span class="console-time">{{ output.timestamp }}</span>
                <span :class="'console-type-' + output.type">{{ output.message }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 脚本管理对话框 -->
    <el-dialog title="脚本管理" :visible.sync="scriptManagerVisible" width="80%">
      <div class="script-manager">
        <div class="script-toolbar">
          <el-button type="primary" @click="createNewScript">新建脚本</el-button>
          <el-button type="success" @click="importScript">导入脚本</el-button>
          <el-button type="warning" @click="exportScript">导出脚本</el-button>
        </div>
        
        <el-table :data="scriptList" border style="margin-top: 20px;">
          <el-table-column prop="name" label="脚本名称" />
          <el-table-column prop="language" label="语言" width="100" />
          <el-table-column prop="description" label="描述" />
          <el-table-column prop="created_at" label="创建时间" width="150">
            <template slot-scope="scope">
              {{ scope.row.created_at | parseTime }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template slot-scope="scope">
              <el-button type="primary" size="mini" @click="loadScript(scope.row)">加载</el-button>
              <el-button type="info" size="mini" @click="duplicateScript(scope.row)">复制</el-button>
              <el-button type="danger" size="mini" @click="deleteScript(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { codemirror } from 'vue-codemirror'
import 'codemirror/lib/codemirror.css'
import 'codemirror/theme/material.css'
import 'codemirror/mode/python/python.js'
import pyodideExecutor from '@/utils/pyodide-executor'
import request from '@/utils/request'
import 'codemirror/mode/javascript/javascript.js'
import 'codemirror/mode/clike/clike.js'
import 'codemirror/addon/edit/closebrackets.js'
import 'codemirror/addon/edit/matchbrackets.js'
import 'codemirror/addon/selection/active-line.js'
import 'codemirror/addon/fold/foldcode.js'
import 'codemirror/addon/fold/foldgutter.js'
import 'codemirror/addon/fold/brace-fold.js'
import 'codemirror/addon/fold/foldgutter.css'

export default {
  name: 'UiScript',
  components: {
    codemirror
  },
  data() {
    return {
      activeToolTab: 'elements',
      currentScript: {
        id: null,
        name: '新建脚本',
        language: 'python',
        content: `# UI自动化测试脚本
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestScript:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
    
    def test_login(self):
        """测试登录功能"""
        # 打开登录页面
        self.driver.get("https://example.com/login")
        
        # 输入用户名
        username_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_input.send_keys("testuser")
        
        # 输入密码
        password_input = self.driver.find_element(By.ID, "password")
        password_input.send_keys("testpass")
        
        # 点击登录按钮
        login_btn = self.driver.find_element(By.ID, "login-btn")
        login_btn.click()
        
        # 验证登录成功
        success_msg = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-msg"))
        )
        assert "登录成功" in success_msg.text
    
    def teardown(self):
        """清理资源"""
        self.driver.quit()

if __name__ == "__main__":
    test = TestScript()
    try:
        test.test_login()
        print("测试通过")
    except Exception as e:
        print(f"测试失败: {e}")
    finally:
        test.teardown()
`,
        description: ''
      },
      editorOptions: {
        tabSize: 4,
        mode: 'python',
        theme: 'material',
        lineNumbers: true,
        line: true,
        foldGutter: true,
        gutters: ['CodeMirror-linenumbers', 'CodeMirror-foldgutter'],
        autoCloseBrackets: true,
        matchBrackets: true,
        styleActiveLine: true,
        scrollbarStyle: 'native',
        lineWrapping: false,
        viewportMargin: 10
      },
      elementSearch: '',
      elements: [
        { id: 1, name: '登录按钮', locator: '#login-btn', page: '登录页面' },
        { id: 2, name: '用户名输入框', locator: '#username', page: '登录页面' },
        { id: 3, name: '密码输入框', locator: '#password', page: '登录页面' },
        { id: 4, name: '搜索按钮', locator: '.search-btn', page: '首页' },
        { id: 5, name: '商品列表', locator: '.product-list', page: '商品页面' }
      ],
      basicTemplates: [
        {
          name: '点击元素',
          description: '点击指定元素',
          code: {
            python: 'element = driver.find_element(By.ID, "element-id")\nelement.click()',
            java: 'WebElement element = driver.findElement(By.id("element-id"));\nelement.click();',
            javascript: 'const element = await driver.findElement(By.id("element-id"));\nawait element.click();',
            csharp: 'IWebElement element = driver.FindElement(By.Id("element-id"));\nelement.Click();'
          }
        },
        {
          name: '输入文本',
          description: '向输入框输入文本',
          code: {
            python: 'element = driver.find_element(By.ID, "input-id")\nelement.send_keys("输入内容")',
            java: 'WebElement element = driver.findElement(By.id("input-id"));\nelement.sendKeys("输入内容");',
            javascript: 'const element = await driver.findElement(By.id("input-id"));\nawait element.sendKeys("输入内容");',
            csharp: 'IWebElement element = driver.FindElement(By.Id("input-id"));\nelement.SendKeys("输入内容");'
          }
        },
        {
          name: '等待元素',
          description: '等待元素出现',
          code: {
            python: 'wait = WebDriverWait(driver, 10)\nelement = wait.until(EC.presence_of_element_located((By.ID, "element-id")))',
            java: 'WebDriverWait wait = new WebDriverWait(driver, 10);\nWebElement element = wait.until(ExpectedConditions.presenceOfElementLocated(By.id("element-id")));',
            javascript: 'const element = await driver.wait(until.elementLocated(By.id("element-id")), 10000);',
            csharp: 'WebDriverWait wait = new WebDriverWait(driver, TimeSpan.FromSeconds(10));\nIWebElement element = wait.Until(ExpectedConditions.ElementIsVisible(By.Id("element-id")));'
          }
        }
      ],
      assertTemplates: [
        {
          name: '断言文本',
          description: '验证元素文本内容',
          code: {
            python: 'element = driver.find_element(By.ID, "element-id")\nassert "期望文本" in element.text',
            java: 'WebElement element = driver.findElement(By.id("element-id"));\nAssert.assertTrue(element.getText().contains("期望文本"));',
            javascript: 'const element = await driver.findElement(By.id("element-id"));\nconst text = await element.getText();\nassert(text.includes("期望文本"));',
            csharp: 'IWebElement element = driver.FindElement(By.Id("element-id"));\nAssert.IsTrue(element.Text.Contains("期望文本"));'
          }
        },
        {
          name: '断言元素存在',
          description: '验证元素是否存在',
          code: {
            python: 'elements = driver.find_elements(By.ID, "element-id")\nassert len(elements) > 0',
            java: 'List<WebElement> elements = driver.findElements(By.id("element-id"));\nAssert.assertTrue(elements.size() > 0);',
            javascript: 'const elements = await driver.findElements(By.id("element-id"));\nassert(elements.length > 0);',
            csharp: 'var elements = driver.FindElements(By.Id("element-id"));\nAssert.IsTrue(elements.Count > 0);'
          }
        }
      ],
      executionLogs: [],
      consoleOutput: [],
      scriptManagerVisible: false,
      scriptList: [
        {
          id: 1,
          name: '登录测试脚本',
          language: 'python',
          description: '用户登录功能测试',
          created_at: new Date('2024-01-15 10:30:00')
        },
        {
          id: 2,
          name: '商品搜索脚本',
          language: 'java',
          description: '商品搜索功能测试',
          created_at: new Date('2024-01-14 15:20:00')
        }
      ]
    }
  },
  computed: {
    filteredElements() {
      if (!this.elementSearch) {
        return this.elements
      }
      return this.elements.filter(element =>
        element.name.toLowerCase().includes(this.elementSearch.toLowerCase()) ||
        element.locator.toLowerCase().includes(this.elementSearch.toLowerCase())
      )
    }
  },
  watch: {
    'currentScript.language'(newLang) {
      this.updateEditorMode(newLang)
    }
  },
  methods: {
    updateEditorMode(language) {
      const modeMap = {
        python: 'python',
        java: 'text/x-java',
        javascript: 'javascript',
        csharp: 'text/x-csharp'
      }
      this.editorOptions.mode = modeMap[language] || 'python'
    },
    onScriptChange() {
      // 脚本内容变化时的处理
    },
    insertElement(element) {
      const cursor = this.$refs.codemirror.codemirror.getCursor()
      const locatorCode = this.generateElementCode(element)
      this.$refs.codemirror.codemirror.replaceRange(locatorCode, cursor)
    },
    generateElementCode(element) {
      const language = this.currentScript.language
      const locator = element.locator
      
      const codeMap = {
        python: `driver.find_element(By.CSS_SELECTOR, "${locator}")`,
        java: `driver.findElement(By.cssSelector("${locator}"))`,
        javascript: `await driver.findElement(By.css("${locator}"))`,
        csharp: `driver.FindElement(By.CssSelector("${locator}"))`
      }
      
      return codeMap[language] || codeMap.python
    },
    insertTemplate(template) {
      const cursor = this.$refs.codemirror.codemirror.getCursor()
      const code = template.code[this.currentScript.language] || template.code.python
      this.$refs.codemirror.codemirror.replaceRange(code, cursor)
    },
    saveScript() {
      this.$message({
        message: '脚本保存成功',
        type: 'success'
      })
    },
    async runScript() {
      this.executionLogs = []
      this.consoleOutput = []

      this.addLog('INFO', '开始执行脚本')
      this.addConsoleOutput('info', '脚本执行开始...')

      try {
        // 检查是否有代码内容
        if (!this.currentScript.content.trim()) {
          this.addLog('ERROR', '脚本内容为空')
          this.addConsoleOutput('error', '请先编写脚本代码')
          return
        }

        // 调用后端API执行代码
        const response = await request({
          url: '/execute-script',
          method: 'post',
          data: {
            code: this.currentScript.content,
            language: this.currentScript.language
          }
        })

        if (response.data.success) {
          this.addLog('INFO', '脚本执行完成')
          this.addConsoleOutput('success', '执行成功')

          // 显示输出结果
          if (response.data.output) {
            this.addConsoleOutput('info', '输出结果:')
            this.addConsoleOutput('info', response.data.output)
          }
        } else {
          this.addLog('ERROR', '脚本执行失败')
          this.addConsoleOutput('error', response.data.error || '执行失败')
        }
      } catch (error) {
        // 如果后端API不可用，尝试使用Pyodide在浏览器中执行
        if (this.currentScript.language === 'python') {
          this.addLog('WARNING', '后端服务不可用，尝试浏览器内执行')
          this.addConsoleOutput('warning', '正在初始化浏览器Python环境...')

          try {
            const result = await pyodideExecutor.execute(this.currentScript.content)

            if (result.success) {
              this.addLog('INFO', '脚本执行完成（浏览器内执行）')
              this.addConsoleOutput('success', '执行成功')

              if (result.output) {
                this.addConsoleOutput('info', '输出结果:')
                this.addConsoleOutput('info', result.output)
              }

              if (result.execution_time) {
                this.addConsoleOutput('info', `执行时间: ${result.execution_time.toFixed(2)}ms`)
              }
            } else {
              this.addLog('ERROR', '脚本执行失败')
              this.addConsoleOutput('error', result.error)
            }
          } catch (pyodideError) {
            // 如果Pyodide也失败，回退到模拟执行
            this.addLog('WARNING', 'Python环境不可用，使用模拟执行')
            this.addConsoleOutput('warning', '注意：这是模拟执行，非真实运行结果')
            this.simulateExecution()
          }
        } else {
          // 非Python语言，直接模拟执行
          this.addLog('WARNING', '后端服务不可用，使用模拟执行')
          this.addConsoleOutput('warning', '注意：这是模拟执行，非真实运行结果')
          this.simulateExecution()
        }
      }
    },

    simulateExecution() {
      // 原来的模拟执行逻辑
      setTimeout(() => {
        this.addLog('INFO', '初始化浏览器驱动')
        this.addConsoleOutput('info', '浏览器启动成功')
      }, 1000)

      setTimeout(() => {
        this.addLog('INFO', '导航到目标页面')
        this.addConsoleOutput('info', '页面加载完成')
      }, 2000)

      setTimeout(() => {
        this.addLog('INFO', '执行测试步骤')
        this.addConsoleOutput('success', '所有测试步骤执行完成')
      }, 3000)

      setTimeout(() => {
        this.addLog('INFO', '脚本执行完成')
        this.addConsoleOutput('success', '脚本执行成功')
      }, 4000)
    },
    addLog(level, message) {
      this.executionLogs.push({
        timestamp: new Date().toLocaleTimeString(),
        level,
        message
      })
    },
    addConsoleOutput(type, message) {
      this.consoleOutput.push({
        timestamp: new Date().toLocaleTimeString(),
        type,
        message
      })
    },
    clearConsole() {
      this.consoleOutput = []
    },
    createNewScript() {
      this.currentScript = {
        id: null,
        name: '新建脚本',
        language: 'python',
        content: '',
        description: ''
      }
      this.scriptManagerVisible = false
    },
    loadScript(script) {
      this.currentScript = Object.assign({}, script)
      this.scriptManagerVisible = false
    },
    duplicateScript(script) {
      const newScript = Object.assign({}, script)
      newScript.id = null
      newScript.name = script.name + '_copy'
      this.scriptList.push(newScript)
      this.$message.success('脚本复制成功')
    },
    deleteScript(script) {
      this.$confirm('确认删除该脚本?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const index = this.scriptList.findIndex(s => s.id === script.id)
        this.scriptList.splice(index, 1)
        this.$message.success('删除成功')
      })
    },
    importScript() {
      this.$message({
        message: '导入脚本功能开发中...',
        type: 'info'
      })
    },
    exportScript() {
      this.$message({
        message: '导出脚本功能开发中...',
        type: 'info'
      })
    }
  },
  mounted() {
    // 确保CodeMirror正确初始化并显示滚动条
    this.$nextTick(() => {
      const codemirrorInstance = this.$refs.codemirror || this.$el.querySelector('.CodeMirror')
      if (codemirrorInstance && codemirrorInstance.CodeMirror) {
        setTimeout(() => {
          codemirrorInstance.CodeMirror.refresh()
        }, 100)
      }
    })
  }
}
</script>

<style scoped>
.script-editor-container {
  height: calc(100vh - 120px);
}

.script-editor {
  height: calc(100vh - 220px);
  min-height: 500px;
}

.script-editor >>> .CodeMirror {
  height: 500px;
  max-height: 500px;
  font-size: 14px;
  line-height: 1.5;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.script-editor >>> .CodeMirror-scroll {
  max-height: 500px;
  overflow: auto !important;
}

/* 强制显示滚动条 */
.script-editor >>> .CodeMirror-scroll::-webkit-scrollbar {
  width: 14px;
  height: 14px;
}

.script-editor >>> .CodeMirror-scroll::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 7px;
}

.script-editor >>> .CodeMirror-scroll::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 7px;
}

.script-editor >>> .CodeMirror-scroll::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.script-editor >>> .CodeMirror-scroll::-webkit-scrollbar-corner {
  background: #f1f1f1;
}

.tool-section {
  max-height: calc(100vh - 300px);
  overflow-y: auto;
}

.element-list {
  max-height: calc(100vh - 400px);
  overflow-y: auto;
}

.element-item {
  padding: 8px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.element-item:hover {
  border-color: #409EFF;
  background-color: #f0f9ff;
}

.element-name {
  font-weight: bold;
  color: #303133;
}

.element-locator {
  font-size: 12px;
  color: #909399;
  font-family: monospace;
}

.template-category {
  margin-bottom: 20px;
}

.template-category h4 {
  margin: 0 0 10px 0;
  color: #303133;
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 5px;
}

.template-item {
  padding: 8px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.template-item:hover {
  border-color: #67C23A;
  background-color: #f0f9ff;
}

.template-name {
  font-weight: bold;
  color: #303133;
}

.template-desc {
  font-size: 12px;
  color: #909399;
}

.log-container {
  max-height: 300px;
  overflow-y: auto;
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
}

.log-item {
  margin-bottom: 5px;
  font-family: monospace;
  font-size: 12px;
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

.log-message {
  color: #303133;
}

.console-output {
  max-height: 200px;
  overflow-y: auto;
  background-color: #2d3748;
  color: #e2e8f0;
  padding: 10px;
  border-radius: 4px;
  font-family: monospace;
}

.console-line {
  margin-bottom: 5px;
}

.console-time {
  color: #a0aec0;
  margin-right: 10px;
}

.console-type-info {
  color: #63b3ed;
}

.console-type-success {
  color: #68d391;
}

.console-type-error {
  color: #fc8181;
}

.console-type-warning {
  color: #f6e05e;
}

.script-manager {
  max-height: 600px;
  overflow-y: auto;
}

.script-toolbar {
  margin-bottom: 20px;
}
</style>
