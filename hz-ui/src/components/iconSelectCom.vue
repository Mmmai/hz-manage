<template>
  <el-dialog
    v-model="iconDialogVisible"
    title="请选择图标"
    width="80%"
    :before-close="handleClose"
    @open="beforeOpen"
  >
    <el-tabs v-model="activeName" class="demo-tabs">
      <el-tab-pane label="图标1" name="1"></el-tab-pane>
      <el-tab-pane label="图标2" name="2"></el-tab-pane>

      <!-- <el-tab-pane label="图标3" name="3"></el-tab-pane> -->

      <div style="display: flex; flex-wrap: wrap">
        <div
          v-for="(name, index) in iconsObj[activeName]"
          :index="index"
          :key="index"
          style="
            cursor: pointer;
            padding: 5px;
            border: 1px solid rgb(227, 232, 232);
          "
          :class="currentIconName === name ? 'red' : ''"
          @click="selectIcon(name)"
        >
          <Icon :icon="name" style="width: 1.2rem; height: 1.2rem"></Icon>
          <!-- {{ name }} -->
        </div>
      </div>
    </el-tabs>

    <!-- <template #footer>
            <span class="dialog-footer">
                <el-button @click="iconDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="handleOk">确定</el-button>
            </span>
        </template> -->
  </el-dialog>
</template>

<script setup lang="ts">
// import * as ElIcons from "@element-plus/icons-vue";
// import { range } from "lodash-es";
import { reactive, ref, toRefs, watch, onMounted, computed } from "vue";
// import ZondiconsNetwork from "~icons/zondicons/network?width=20px&height=20px";
import ep from "@iconify/json/json/ep.json";
// import zondicons from "@iconify/json/json/zondicons.json";
import clarity from "@iconify/json/json/clarity.json";

import { Icon } from "@iconify/vue";

const iconDialogVisible = defineModel("isShow");
const currentIconName = defineModel("iconName");
const activeName = ref("1");
const iconsObj = ref({});
onMounted(() => {
  getData();
});
const loadIcon = (alias, params, category = []) => {
  // console.log(params);

  let icons = [];
  if ("categories" in params) {
    if (category.length > 0) {
      for (const name in params.categories) {
        if (category.includes(name)) {
          params.categories[name].forEach((item) => {
            icons.push(`${params.prefix}:${item}`);
          });
        }
      }
    } else {
      for (const name in params.icons) {
        icons.push(`${params.prefix}:${name}`);
      }
    }
  } else {
    for (const name in params.icons) {
      icons.push(`${params.prefix}:${name}`);
    }
  }

  // console.log(icons)
  iconsObj.value[alias] = icons;
};
// const icons = ref([])
const getData = () => {
  // console.log(iconsObj.value);
  loadIcon("1", ep);
  // loadIcon("other", zondicons);
  loadIcon("2", clarity, ["Essential", "Technology"]);
};

const handleClose = () => {
  iconDialogVisible.value = false;
};
const beforeOpen = () => {};
const selectIcon = (name) => {
  // console.log(name);
  //   if (typeof name === "string") {
  currentIconName.value = name;
  //   } else if (typeof name === "object") {
  //   currentIconName.value = name.name;
  //   }
  iconDialogVisible.value = false;
};
//   const iconList = reactive({
//     icons: getData(),
//     iconDialogVisible: false,
//     currentIconName: 'Aim'
//   })
//   console.log(iconList)
//   watch(() => props.iconName,(val) => {
//     iconList.currentIconName = val;
//   })
</script>

<style scoped>
.red {
  background-color: var(--el-color-primary);
  color: white;
}
</style>