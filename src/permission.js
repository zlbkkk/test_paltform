import router from './router'
import store from './store'
import { Message } from 'element-ui'
import NProgress from 'nprogress' // progress bar
import 'nprogress/nprogress.css' // progress bar style
import { getToken } from '@/utils/auth' // get token from cookie
import getPageTitle from '@/utils/get-page-title'

NProgress.configure({ showSpinner: false }) // NProgress Configuration

const whiteList = ['/login'] // no redirect whitelist

router.beforeEach(async(to, from, next) => {
  // start progress bar
  NProgress.start()

  // set page title
  document.title = getPageTitle(to.meta.title)

  // 临时绕过登录验证 - 直接设置模拟用户信息
  if (!store.getters.name) {
    // 设置模拟的用户信息
    store.commit('user/SET_TOKEN', 'mock-token-123456')
    store.commit('user/SET_NAME', 'Admin')
    store.commit('user/SET_AVATAR', 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif')
    store.commit('user/SET_ROLES', ['admin'])
  }

  // 如果访问登录页面，直接跳转到首页
  if (to.path === '/login') {
    next({ path: '/' })
    NProgress.done()
    return
  }

  // 其他页面直接放行
  next()
})

router.afterEach(() => {
  // finish progress bar
  NProgress.done()
})
