import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

/* Layout */
import Layout from '@/layout'

/**
 * Note: sub-menu only appear when route children.length >= 1
 * Detail see: https://panjiachen.github.io/vue-element-admin-site/guide/essentials/router-and-nav.html
 *
 * hidden: true                   if set true, item will not show in the sidebar(default is false)
 * alwaysShow: true               if set true, will always show the root menu
 *                                if not set alwaysShow, when item has more than one children route,
 *                                it will becomes nested mode, otherwise not show the root menu
 * redirect: noRedirect           if set noRedirect will no redirect in the breadcrumb
 * name:'router-name'             the name is used by <keep-alive> (must set!!!)
 * meta : {
    roles: ['admin','editor']    control the page roles (you can set multiple roles)
    title: 'title'               the name show in sidebar and breadcrumb (recommend set)
    icon: 'svg-name'/'el-icon-x' the icon show in the sidebar
    breadcrumb: false            if set false, the item will hidden in breadcrumb(default is true)
    activeMenu: '/example/list'  if set path, the sidebar will highlight the path you set
  }
 */

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all roles can be accessed
 */
export const constantRoutes = [
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true
  },

  {
    path: '/404',
    component: () => import('@/views/404'),
    hidden: true
  },

  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [{
      path: 'dashboard',
      name: 'Dashboard',
      component: () => import('@/views/dashboard/index'),
      meta: { title: '首页', icon: 'el-icon-s-home' }
    }]
  },

  {
    path: '/project',
    component: Layout,
    redirect: '/project/list',
    name: 'Project',
    meta: { title: '项目管理', icon: 'el-icon-folder' },
    children: [
      {
        path: 'list',
        name: 'ProjectList',
        component: () => import('@/views/project/list'),
        meta: { title: '项目列表', icon: 'el-icon-document' }
      },
      {
        path: 'create',
        name: 'ProjectCreate',
        component: () => import('@/views/project/create'),
        meta: { title: '创建项目', icon: 'el-icon-plus' }
      }
    ]
  },

  {
    path: '/api-test',
    component: Layout,
    redirect: '/api-test/case',
    name: 'ApiTest',
    meta: { title: '接口测试', icon: 'el-icon-connection' },
    children: [
      {
        path: 'case',
        name: 'ApiCase',
        component: () => import('@/views/api-test/case'),
        meta: { title: '测试用例', icon: 'el-icon-document' }
      },
      {
        path: 'debug',
        name: 'ApiDebug',
        component: () => import('@/views/api-test/debug'),
        meta: { title: '接口调试', icon: 'el-icon-cpu' }
      },
      {
        path: 'suite',
        name: 'ApiSuite',
        component: () => import('@/views/api-test/suite'),
        meta: { title: '测试套件', icon: 'el-icon-collection' }
      }
    ]
  },

  {
    path: '/ui-test',
    component: Layout,
    redirect: '/ui-test/case',
    name: 'UiTest',
    meta: { title: 'UI测试', icon: 'el-icon-monitor' },
    children: [
      {
        path: 'case',
        name: 'UiCase',
        component: () => import('@/views/ui-test/case'),
        meta: { title: '测试用例', icon: 'el-icon-document' }
      },
      {
        path: 'element',
        name: 'UiElement',
        component: () => import('@/views/ui-test/element'),
        meta: { title: '元素管理', icon: 'el-icon-aim' }
      },
      {
        path: 'script',
        name: 'UiScript',
        component: () => import('@/views/ui-test/script'),
        meta: { title: '脚本编写', icon: 'el-icon-edit' }
      }
    ]
  },

  {
    path: '/performance-test',
    component: Layout,
    redirect: '/performance-test/monitor-analysis',
    name: 'PerformanceTest',
    meta: { title: '性能测试', icon: 'el-icon-cpu' },
    children: [
      {
        path: 'monitor-analysis',
        name: 'MonitorAnalysis',
        component: () => import('@/views/performance-test/monitor-analysis'),
        meta: { title: '监控数据分析', icon: 'el-icon-data-analysis' }
      },
      {
        path: 'stress-test',
        name: 'StressTest',
        component: () => import('@/views/performance-test/stress-test'),
        meta: { title: '压力测试工具', icon: 'el-icon-cpu' }
      },
      {
        path: 'performance-report',
        name: 'PerformanceReport',
        component: () => import('@/views/performance-test/performance-report'),
        meta: { title: '性能报告', icon: 'el-icon-data-line' }
      }
    ]
  },

  {
    path: '/server-monitor',
    component: Layout,
    redirect: '/server-monitor/dashboard',
    name: 'ServerMonitor',
    meta: { title: '服务器监控', icon: 'el-icon-monitor' },
    children: [
      {
        path: 'dashboard',
        name: 'ServerMonitorDashboard',
        component: () => import('@/views/server-monitor/dashboard'),
        meta: { title: '监控面板', icon: 'el-icon-monitor' }
      }
    ]
  },

  // 404 page must be placed at the end !!!
  { path: '*', redirect: '/404', hidden: true }
]

const createRouter = () => new Router({
  // mode: 'history', // require service support
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

// Detail see: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // reset router
}

export default router
