<template>
  <div class="card">
    <el-tabs v-model="activeName" class="demo-tabs" @tab-click="handleClick">
      <el-tab-pane label="zabbix配置" name="zabbix">
        <zabbixConfig />
      </el-tab-pane>
      <el-tab-pane label="安全参数" name="security">
        <securityConfig />
      </el-tab-pane>
      <!-- <el-tab-pane label="Config" name="second">Config</el-tab-pane>
      <el-tab-pane label="Role" name="third">Role</el-tab-pane>
      <el-tab-pane label="Task" name="fourth">Task</el-tab-pane> -->
    </el-tabs>
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
import securityConfig from "@/components/sysconfig/securityConfig.vue";
import zabbixConfig from "@/components/sysconfig/zabbixConfig.vue";
defineOptions({ name: "sysconfig" });

const store = useStore();

import type { TabsPaneContext } from "element-plus";

const activeName = ref("zabbix");

const handleClick = (tab: TabsPaneContext, event: Event) => {
  console.log(tab, event);
};
</script>
<style scoped lang="scss">
</style>