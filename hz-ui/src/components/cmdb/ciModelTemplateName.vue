<template>
  <div>
    <!-- <el-radio-group v-model="radio1">
      <el-radio value="1" size="large" border>自定义</el-radio>
      <el-radio value="2" size="large" border>字段组合</el-radio>
    </el-radio-group> -->
  </div>
  <div class="card">
    <el-button type="primary" @click="editAction" v-show="!isEdit"
      >编辑</el-button
    >
    <el-button type="primary" v-throttle @click="updateCiName"
      >更新唯一标识</el-button
    >
    <el-button @click="cancelAction" v-show="isEdit">取消</el-button>
    <el-button type="primary" @click="commit" v-show="isEdit">保存</el-button>
    <el-divider>可选择指标</el-divider>

    <el-checkbox-group
      v-model="checkboxLists"
      @change="handleCheckAllChange"
      :max="5"
      :disabled="!isEdit"
    >
      <el-checkbox
        v-for="(item, key) in checkboxFields"
        :key="key"
        :label="item.verbose_name"
        :value="item.id"
      >
        {{ item.verbose_name }}
      </el-checkbox>
    </el-checkbox-group>
    <el-divider>拖拽调整顺序</el-divider>
    <VueDraggable
      :disabled="!isEdit"
      v-model="checkboxLists"
      :force-fallback="true"
      :scroll-sensitivity="200"
      ref="el"
      @end="onEnd"
      style="width: 100%; overflow: auto"
    >
      <div v-for="(itemId, index) in checkboxLists" :key="index">
        <div class="listItem">
          <span>{{ modelFieldMap[itemId].verbose_name }}</span>
          <!-- {{ itemId }} -->
        </div>
      </div>
    </VueDraggable>
    <el-divider>效果预览</el-divider>
    <div
      style="
        display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: center;
      "
    >
      <h3>
        {{
          checkboxLists
            .map((item) => modelFieldMap[item].verbose_name)
            .join(" - ")
        }}
      </h3>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ElMessage, ElMessageBox, ElNotification } from "element-plus";
import {
  h,
  ref,
  computed,
  watch,
  getCurrentInstance,
  onMounted,
  reactive,
  nextTick,
  onActivated,
} from "vue";
import { VueDraggable } from "vue-draggable-plus";
const { proxy } = getCurrentInstance();
import { useStore } from "vuex";
const store = useStore();
const props = defineProps(["modelId", "modelFieldLists", "ciModelInfo"]);
// const emits = defineEmits(["getCiModel"]);

const isEdit = ref(false);
const checkboxLists = ref([]);
const handleCheckAllChange = (val) => {};
// const checkboxListsId = computed(() => {
//   return checkboxLists.value.map((item) => item.id);
// });
const checkboxFields = computed(() => {
  return props.modelFieldLists.filter((item) =>
    // 只保留部分类型的字段支持用于命名
    ["string", "enum", "model_ref"].includes(item.type)
  );
});
const modelFieldMap = computed(() => {
  let tmpObj = new Object();
  props.modelFieldLists.forEach((item) => {
    tmpObj[item.id] = item;
  });
  return tmpObj;
});
const onEnd = () => {};

const editAction = () => {
  isEdit.value = true;
};
const cancelAction = () => {
  // 后端获取
  isEdit.value = false;
};

const updateCiName = async () => {
  let res = await proxy.$api.updateInstanceName(props.modelId);
  console.log(res);
  if (res.status == "200") {
    ElNotification({
      title: "Success",
      message: "更新任务提交成功",
      type: "success",
    });
  } else {
    ElNotification({
      title: "Error",
      message: `更新任务提交失败${JSON.stringify(res.data)}`,
      type: "error",
    });
  }
};
// 更新任务的task
const taskPercentage = ref(0);
const commit = async () => {
  // console.log(checkboxLists.value);
  let res = await proxy.$api.updateCiModel({
    id: props.modelId,
    instance_name_template: checkboxLists.value,
  });
  if (res.status == "200") {
    ElMessage({ type: "success", message: "更新成功" });
    // 询问是否自动更新实例名
    ElMessageBox.confirm("更新成功，是否自动更新实例唯一标识?", "Warning", {
      confirmButtonText: "确认",
      cancelButtonText: "取消",
      type: "warning",
    })
      .then(() => {
        // 触发唯一标识更新接口
        updateCiName();
      })
      .catch(() => {
        ElMessage({
          type: "info",
          message: "Delete canceled",
        });
      });
    // 重置表单
    isEdit.value = false;
    // 获取数据源列表
    getModel();
  } else {
    ElMessage({
      showClose: true,
      message: "更新失败:" + JSON.stringify(res.data),
      type: "error",
    });
  }
};
const getModel = async () => {
  let res = await proxy.$api.getCiModel(null, props.modelId);
  // console.log(ciModelInfo.value);
  checkboxLists.value = res.data.model.instance_name_template;
};
defineExpose({
  getModel,
});
// onMounted();
// onActivated(() => {
//   // console.log(123);
//   checkboxLists.value = props.ciModelInfo.instance_name_template;
//   console.log(props.ciModelInfo.instance_name_template);
// });
</script>
<style scoped lang="scss">
</style>