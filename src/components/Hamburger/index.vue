<template>
  <el-tooltip
    :content="isActive ? '收起菜单' : '展开菜单'"
    placement="bottom"
    :open-delay="500"
  >
    <div
      class="hamburger-wrapper"
      @click="toggleClick"
    >
      <svg
        :class="{'is-active':isActive}"
        class="hamburger"
        viewBox="0 0 1024 1024"
        xmlns="http://www.w3.org/2000/svg"
        width="64"
        height="64"
      >
        <path d="M408 442h480c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8H408c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8zm-8 204c0 4.4 3.6 8 8 8h480c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8H408c-4.4 0-8 3.6-8 8v56zm504-486H120c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h784c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8z" />
      </svg>
      <div class="hamburger-indicator" :class="{'show': !isActive}"></div>
    </div>
  </el-tooltip>
</template>

<script>
export default {
  name: 'Hamburger',
  props: {
    isActive: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    toggleClick() {
      this.$emit('toggleClick')
    }
  }
}
</script>

<style scoped>
.hamburger-wrapper {
  padding: 0 15px;
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 4px;
}

.hamburger-wrapper:hover {
  background-color: rgba(0, 0, 0, 0.05);
  transform: scale(1.05);
}

.hamburger {
  display: inline-block;
  vertical-align: middle;
  width: 20px;
  height: 20px;
  transition: all 0.3s ease;
  color: #606266;
}

.hamburger:hover {
  color: #409EFF;
}

.hamburger.is-active {
  transform: rotate(90deg);
  color: #409EFF;
}

/* 指示器 - 当侧边栏收缩时显示 */
.hamburger-indicator {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 6px;
  height: 6px;
  background: linear-gradient(45deg, #409EFF, #67C23A);
  border-radius: 50%;
  opacity: 0;
  transform: scale(0);
  transition: all 0.3s ease;
  animation: pulse 2s infinite;
}

.hamburger-indicator.show {
  opacity: 1;
  transform: scale(1);
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.7);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(64, 158, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0);
  }
}
</style>
