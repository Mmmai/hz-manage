<template>
  <div class="divVertical">
    <div class="card">
      <!-- 基于el-tag的筛选，
      模型： 主机tag 交换机tag
      操作类型： 添加 删除 修改
      时间选择框
      搜索框 
      -->
    </div>
    <div class="card"></div>
  </div>
</template>

<script lang="ts" setup>
import {
  ref,
  computed,
  watch,
  getCurrentInstance,
  onMounted,
  reactive,
  nextTick,
} from "vue";
const { proxy } = getCurrentInstance();
</script>
<style scoped lang="scss">
</style>