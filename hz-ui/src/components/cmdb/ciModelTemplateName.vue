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
      :disabled="true"
      :force-fallback="true"
      :scroll-sensitivity="200"
      ref="el"
      @end="onEnd"
      style="width: 100%; overflow: auto"
    >
      <div v-for="(itemId, index) in checkboxLists" :key="index">
        <div class="listItem">
          <span>{{ modelFieldMap[itemId].verbose_name }}</span>
        </div>
      </div>
    </VueDraggable>
  </div>
</template>

<script lang="ts" setup>
import { ElMessage } from "element-plus";
import {
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
const isEdit = ref(false);
const checkboxLists = ref([]);
const handleCheckAllChange = (val) => {
  console.log(val);
  console.log(checkboxLists.value);
};
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
const commit = async () => {
  let res = await proxy.$api.updateCiModel({
    id: props.modelId,
    instance_name_template: checkboxLists.value,
  });
  if (res.status == "200") {
    ElMessage({ type: "success", message: "更新成功" });
    // 重置表单
    isEdit.value = false;
    // 获取数据源列表
    emits("getCiModel");
  } else {
    ElMessage({
      showClose: true,
      message: "更新失败:" + JSON.stringify(res.data),
      type: "error",
    });
  }
};
// const emits = defineEmits(["getCiModel"]);
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