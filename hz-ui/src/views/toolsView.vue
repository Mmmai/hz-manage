<template>
  <div class="card">
    <el-tabs v-model="activeName" class="demo-tabs">
      <el-tab-pane label="二维码" name="qrCode">
        <qrCode />
      </el-tab-pane>
      <el-tab-pane label="常用转换" name="transform">
        <transform />
      </el-tab-pane>
    </el-tabs>

  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import qrCode from '../components/tools/qrCode.vue';
import transform from '../components/tools/transform.vue';

const textarea = ref('')
const activeName = ref('qrCode')
</script>

<style scoped>
/* .demo-tabs > .el-tabs__content {
  padding: 32px;
  color: #6b778c;
  font-size: 32px;
  font-weight: 600;
} */
</style>