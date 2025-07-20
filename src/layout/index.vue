<template>
  <div :class="classObj" class="app-wrapper">
    <div v-if="device==='mobile'&&sidebar.opened" class="drawer-bg" @click="handleClickOutside" />
    <sidebar class="sidebar-container" />
    <div class="main-container">
      <div :class="{'fixed-header':fixedHeader}">
        <navbar />
      </div>
      <app-main />
    </div>

    <!-- 首次访问提示 -->
    <el-dialog
      title="💡 使用提示"
      :visible.sync="showTip"
      width="400px"
      :show-close="false"
      :close-on-click-modal="false"
      center
    >
      <div class="tip-content">
        <p>👋 欢迎使用测试平台！</p>
        <p>💡 点击左上角的 <i class="el-icon-s-fold" style="color: #409EFF;"></i> 按钮可以收起/展开左侧菜单</p>
        <p>📱 菜单收起后，点击左侧边栏任意位置即可重新展开</p>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-checkbox v-model="dontShowAgain">不再显示此提示</el-checkbox>
        <el-button type="primary" @click="closeTip" style="margin-left: 20px;">知道了</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { Navbar, Sidebar, AppMain } from './components'
import ResizeMixin from './mixin/ResizeHandler'

export default {
  name: 'Layout',
  components: {
    Navbar,
    Sidebar,
    AppMain
  },
  mixins: [ResizeMixin],
  data() {
    return {
      showTip: false,
      dontShowAgain: false
    }
  },
  computed: {
    sidebar() {
      return this.$store.state.app.sidebar
    },
    device() {
      return this.$store.state.app.device
    },
    fixedHeader() {
      return this.$store.state.settings.fixedHeader
    },
    classObj() {
      return {
        hideSidebar: !this.sidebar.opened,
        openSidebar: this.sidebar.opened,
        withoutAnimation: this.sidebar.withoutAnimation,
        mobile: this.device === 'mobile'
      }
    }
  },
  mounted() {
    // 检查是否需要显示使用提示
    const hasSeenTip = localStorage.getItem('sidebar-tip-seen')
    if (!hasSeenTip) {
      setTimeout(() => {
        this.showTip = true
      }, 1000) // 延迟1秒显示，让用户先熟悉界面
    }
  },
  methods: {
    handleClickOutside() {
      this.$store.dispatch('app/closeSideBar', { withoutAnimation: false })
    },
    closeTip() {
      this.showTip = false
      if (this.dontShowAgain) {
        localStorage.setItem('sidebar-tip-seen', 'true')
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.tip-content {
  text-align: left;
  line-height: 1.8;

  p {
    margin: 12px 0;
    font-size: 14px;
    color: #606266;

    &:first-child {
      font-size: 16px;
      font-weight: 500;
      color: #303133;
    }
  }

  i {
    font-weight: bold;
    font-size: 16px;
  }
}

.dialog-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>

<style lang="scss" scoped>
  @import "~@/styles/mixin.scss";
  @import "~@/styles/variables.scss";

  .app-wrapper {
    @include clearfix;
    position: relative;
    height: 100%;
    width: 100%;
    &.mobile.openSidebar{
      position: fixed;
      top: 0;
    }
  }
  .drawer-bg {
    background: #000;
    opacity: 0.3;
    width: 100%;
    top: 0;
    height: 100%;
    position: absolute;
    z-index: 999;
  }

  .fixed-header {
    position: fixed;
    top: 0;
    right: 0;
    z-index: 9;
    width: calc(100% - #{$sideBarWidth});
    transition: width 0.28s;
  }

  .hideSidebar .fixed-header {
    width: calc(100% - 54px);
  }

  .mobile .fixed-header {
    width: 100%;
  }
</style>
