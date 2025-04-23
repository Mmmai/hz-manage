<template>
  <el-dialog v-model="qCodeDia" title="实例二维码" width="600">
    <div style="display: flex; justify-content: center">
      <a-qrcode :value="JSON.stringify(props.qCodeContext)" :size="500" />
    </div>
  </el-dialog>
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
import { useStore } from "vuex";
const store = useStore();

const qCodeDia = defineModel("showqCodeDia");
const props = defineProps(["qCodeContext"]);
</script>
<style scoped lang="scss">
</style>