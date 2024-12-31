<template>
  <div class="card">
    <el-form :model="formInline" class="demo-form-inline">
      <el-form-item label="密码密钥">
        <span> {{ gmConfig.key }}</span>
        <!-- <el-input
          v-model="formInline.key"
          placeholder="Approved by"
          clearable
        /> -->
      </el-form-item>

      <!-- <el-form-item>
        <el-button type="primary" @click="onSubmit">更新</el-button>
      </el-form-item> -->
    </el-form>
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
import { useStore } from "vuex";
const store = useStore();
import useConfigStore from "@/store/config";
const configStore = useConfigStore();
const gmConfig = computed(() => configStore.gmCry);
const formInline = reactive({
  key: "",
  region: "",
  date: "",
});

const onSubmit = () => {
  console.log("submit!");
};
</script>
<style scoped lang="scss">
</style>