<template>
  <div class="card">
    <el-form :model="formInline" class="demo-form-inline">
      <el-form-item label="密码密钥">
        <span style="margin-right: 20px">
          {{ gmConfig.key }}
          <el-icon><CopyDocument v-copy="gmConfig.key" /></el-icon
        ></span>

        <el-tooltip
          class="box-item"
          effect="dark"
          content="更新密钥"
          placement="top"
        >
          <el-button
            size="small"
            @click="updateKey"
            type="warning"
            :icon="RefreshRight"
            circle
          ></el-button>
        </el-tooltip>

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
import { RefreshRight } from "@element-plus/icons-vue";
import {
  ref,
  computed,
  watch,
  getCurrentInstance,
  onMounted,
  reactive,
  nextTick,
} from "vue";
import { v1 as uuidv1, v4 as uuidv4 } from "uuid";
const { proxy } = getCurrentInstance();
import { useStore } from "vuex";
import { ElLoading, ElNotification } from "element-plus";

const store = useStore();
import useConfigStore from "@/store/config";
const configStore = useConfigStore();
const gmConfig = computed(() => configStore.gmCry);
const formInline = reactive({
  key: "",
  region: "",
  date: "",
});
const nowKey = ref({});
const getKey = async () => {
  let res = await proxy.$api.getSysConfig({ param_name: "secret_key" });
  nowKey.value = res.data.results[0];
  // console.log(nowKey.value);
};

// const updateKeyResTip = ref("");
const updateKey = async () => {
  // console.log(uuidv1());
  // updateKeyResTip.value = "密钥更新中";
  let newKey = uuidv4().replace(/-/g, "").slice(0, 16);
  // console.log();
  const loading = ElLoading.service({
    lock: true,
    text: "更新中...",
    background: "rgba(0, 0, 0, 0.7)",
  });
  let res = await proxy.$api.updateSysConfig({
    id: nowKey.value.id,
    param_name: "secret_key",
    param_value: newKey,
  });
  if (res.status == "200") {
    console.log(
      `旧密钥：${gmConfig.value.key};新密钥：${res.data.param_value}`
    );

    let res1 = await proxy.$api.reEncrypt({}, 300000);
    if (res1.status == "204" || res1.status == "200") {
      ElNotification({
        title: "Success",
        message: "数据重新加密成功~",
        type: "success",
        duration: 3000,
      });
    } else {
      ElNotification({
        title: "Error",
        message: "数据重新加密失败！",
        type: "error",
      });
      console.log("数据重新加密失败");
    }
    // 更新内存中的key
    let gmRes = await proxy.$api.getSysConfig({ params: "gm" });
    configStore.setGmCry(gmRes.data);
  } else {
    ElNotification({
      title: "Error",
      message: "密钥更新失败！",
      type: "error",
      duration: 3000,
    });
    console.log("更新密钥失败");
  }
  setTimeout(() => {
    loading.close();
    window.location.reload();
  }, 2000);
};
const onSubmit = () => {
  console.log("submit!");
};
onMounted(() => {
  getKey();
});
</script>
<style scoped lang="scss">
</style>