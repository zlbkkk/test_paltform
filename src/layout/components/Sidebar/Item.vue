<template>
  <div>
    <i v-if="icon" :class="icon" class="sub-el-icon" />
    <span slot="title">{{ title }}</span>
  </div>
</template>

<script>
export default {
  name: 'MenuItem',
  props: {
    icon: {
      type: String,
      default: ''
    },
    title: {
      type: String,
      default: ''
    }
  }
}
</script>
