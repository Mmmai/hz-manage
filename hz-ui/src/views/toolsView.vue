<template>
  <div class="card">
    <el-tabs v-model="activeName" class="demo-tabs">
      <el-tab-pane label="二维码" name="qrCode">
        <qrCode />
      </el-tab-pane>
      <el-tab-pane label="JSON转换" name="JsonParse">
        <JsonParse />
      </el-tab-pane>
      <el-tab-pane label="时间格式转换" name="TimeTrans">
        <TimeTrans />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: "tools" });

import { ref } from "vue";
import qrCode from "../components/tools/qrCode.vue";
// import transform from '../components/tools/transform.vue';
import JsonParse from "../components/tools/jsonparse.vue";
import TimeTrans from "../components/tools/timetrans.vue";
import { encrypt_sm4, decrypt_sm4 } from "@/utils/gmCrypto.ts";
// console.log(
// );
const activeName = ref("qrCode");
</script>

<style scoped>
/* .demo-tabs > .el-tabs__content {
  padding: 32px;
  color: #6b778c;
  font-size: 32px;
  font-weight: 600;
} */
</style>