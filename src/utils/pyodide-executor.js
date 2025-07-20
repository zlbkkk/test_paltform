/**
 * Pyodide Python执行器
 * 在浏览器中运行Python代码
 */

class PyodideExecutor {
  constructor() {
    this.pyodide = null
    this.isLoading = false
    this.isReady = false
  }

  /**
   * 初始化Pyodide
   */
  async init() {
    if (this.isReady) return true
    if (this.isLoading) {
      // 等待加载完成
      while (this.isLoading) {
        await new Promise(resolve => setTimeout(resolve, 100))
      }
      return this.isReady
    }

    try {
      this.isLoading = true
      
      // 加载Pyodide
      const pyodideScript = document.createElement('script')
      pyodideScript.src = 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js'
      document.head.appendChild(pyodideScript)

      await new Promise((resolve, reject) => {
        pyodideScript.onload = resolve
        pyodideScript.onerror = reject
      })

      // 初始化Pyodide
      this.pyodide = await window.loadPyodide({
        indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/'
      })

      // 安装常用包
      await this.pyodide.loadPackage(['numpy', 'pandas', 'matplotlib'])
      
      this.isReady = true
      this.isLoading = false
      return true
    } catch (error) {
      this.isLoading = false
      console.error('Pyodide初始化失败:', error)
      return false
    }
  }

  /**
   * 执行Python代码
   */
  async execute(code) {
    try {
      if (!this.isReady) {
        const initSuccess = await this.init()
        if (!initSuccess) {
          return {
            success: false,
            error: 'Python环境初始化失败'
          }
        }
      }

      // 安全检查
      const safetyCheck = this.checkCodeSafety(code)
      if (!safetyCheck.safe) {
        return {
          success: false,
          error: safetyCheck.message
        }
      }

      const startTime = performance.now()
      
      // 捕获输出
      this.pyodide.runPython(`
import sys
from io import StringIO
sys.stdout = StringIO()
sys.stderr = StringIO()
      `)

      // 执行用户代码
      let result
      try {
        result = this.pyodide.runPython(code)
      } catch (error) {
        // 获取错误信息
        const stderr = this.pyodide.runPython('sys.stderr.getvalue()')
        return {
          success: false,
          error: stderr || error.message,
          execution_time: performance.now() - startTime
        }
      }

      // 获取输出
      const stdout = this.pyodide.runPython('sys.stdout.getvalue()')
      const stderr = this.pyodide.runPython('sys.stderr.getvalue()')

      // 重置输出流
      this.pyodide.runPython(`
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__
      `)

      return {
        success: true,
        output: stdout,
        error: stderr,
        result: result,
        execution_time: performance.now() - startTime
      }

    } catch (error) {
      return {
        success: false,
        error: error.message
      }
    }
  }

  /**
   * 检查代码安全性
   */
  checkCodeSafety(code) {
    const dangerousPatterns = [
      /import\s+os/i,
      /import\s+sys/i,
      /import\s+subprocess/i,
      /open\s*\(/i,
      /file\s*\(/i,
      /exec\s*\(/i,
      /eval\s*\(/i,
      /__import__/i,
      /input\s*\(/i,
      /raw_input\s*\(/i
    ]

    for (const pattern of dangerousPatterns) {
      if (pattern.test(code)) {
        return {
          safe: false,
          message: `检测到潜在危险操作: ${pattern.source}`
        }
      }
    }

    return { safe: true }
  }

  /**
   * 安装Python包
   */
  async installPackage(packageName) {
    if (!this.isReady) {
      throw new Error('Pyodide未初始化')
    }

    try {
      await this.pyodide.loadPackage(packageName)
      return true
    } catch (error) {
      console.error(`安装包 ${packageName} 失败:`, error)
      return false
    }
  }

  /**
   * 获取可用的包列表
   */
  getAvailablePackages() {
    if (!this.isReady) return []
    return this.pyodide.loadedPackages
  }
}

// 创建全局实例
const pyodideExecutor = new PyodideExecutor()

export default pyodideExecutor
