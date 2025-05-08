<template>
  <el-dialog
    v-model="iconDialogVisible"
    title="请选择图标"
    width="80%"
    :before-close="handleClose"
    @open="beforeOpen"
  >
    <el-tabs v-model="activeName" class="demo-tabs">
      <el-tab-pane label="常用" name="elementIcon"></el-tab-pane>
      <el-tab-pane label="其它" name="other"></el-tab-pane>

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
          <component
            :is="name"
            style="width: 1.2rem; height: 1.2rem"
          ></component>
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

<script setup>
import * as ElIcons from "@element-plus/icons-vue";
import { range } from "lodash-es";
import { reactive, ref, toRefs, watch, onMounted, computed } from "vue";
// import ZondiconsNetwork from "~icons/zondicons/network?width=20px&height=20px";
import { Icon, listIcons } from "@iconify/vue";

const iconDialogVisible = defineModel("isShow");
const currentIconName = defineModel("iconName");
const activeName = ref("elementIcon");
const iconsObj = ref({ other: [] });
onMounted(() => {
  getData();
});
// const icons = ref([])
const getData = () => {
  let icons = [];
  for (const name in ElIcons) {
    icons.push(name);
  }
  // console.log(icons)
  iconsObj.value["elementIcon"] = icons;
  console.log(iconsObj.value);
};
const handleClose = () => {
  iconDialogVisible.value = false;
};
const beforeOpen = () => {};
const selectIcon = (name) => {
  console.log(typeof name);
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