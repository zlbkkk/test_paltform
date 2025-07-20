import Vue from 'vue'
import App from './App'
import router from './router'
import store from './store'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import './styles/index.scss'
import './permission'
import { parseTime } from '@/utils'

Vue.config.productionTip = false

Vue.use(ElementUI)

// 注册全局过滤器
Vue.filter('parseTime', parseTime)

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  components: { App },
  template: '<App/>'
})
