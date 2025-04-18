<template>
  <el-space direction="vertical" fill>
    <el-input
    v-model="textarea"
    :autosize="{ minRows: 5, maxRows: 10 }"
    style="width: 500px"
    type="textarea"
    placeholder="输入文本"
    clearable
    maxlength="2000"
    show-word-limit
  />
  <a-qrcode :value="textarea" :size="250" />
    </el-space>
  <div>


</div>
 

</template>

<script lang="ts" setup>
import {ref} from 'vue'
const textarea = ref('')
</script>

<style scoped>
/* .demo-tabs > .el-tabs__content {
  padding: 32px;
  color: #6b778c;
  font-size: 32px;
  font-weight: 600;
} */
 .qrCodeClass {
  display: flex;
  width: 100%;
 }
</style>