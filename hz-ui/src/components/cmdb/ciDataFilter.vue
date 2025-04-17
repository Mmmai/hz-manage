<template>
  <el-drawer
    v-model="isShowFilter"
    direction="rtl"
    size="50%"
    :before-close="handleClose"
  >
    <template #header>
      <el-text tag="b">筛选</el-text>
    </template>
    <template #default>
      <div
        style="
          display: flex;
          /* flex-direction: column; */
          justify-content: space-around;
          gap: 20px;
          height: 100%;
        "
      >
        <div
          class="card"
          style="flex: 1; display: flex; flex-direction: column"
        >
          <el-text tag="b">模型字段</el-text>
          <el-divider />
          <el-input
            v-model="filterText"
            style="width: 100%; margin-bottom: 10px"
            placeholder="筛选字段名称"
            clearable
            ref="filterInputRef"
          />

          <div style="width: 100%; overflow: auto">
            <div v-for="(item, index) in filterModelFields" :key="index">
              <div class="listItem">
                <span>{{ item.verbose_name }}</span>
                <el-icon><ArrowRight @click="toRight(item)" /></el-icon>
              </div>
            </div>
          </div>
        </div>
        <div
          class="card"
          style="flex: 1; display: flex; flex-direction: column"
        >
          <el-text tag="b">过滤器</el-text>
          <el-divider />

          <el-form
            ref="filterFormRef"
            :model="filterForm"
            label-width="auto"
            style="width: 100%"
            label-position="top"
          >
            <el-space wrap>
              <el-form-item label="唯一标识" prop="instance_name">
                <el-input
                  v-model="filterForm.instance_name"
                  type="textarea"
                  style="width: 280px"
                />
              </el-form-item>
              <el-form-item
                v-for="(item, index) in filterForm.filterParams"
                :key="item.index"
                :prop="'filterParams.' + index + '.value'"
              >
                <template #label>
                  <span style="margin-right: 5px">{{ item.label }}</span>
                  <el-button
                    :icon="CircleClose"
                    size="small"
                    circle
                    @click.prevent="toLeft(item)"
                  >
                  </el-button>
                </template>
                <el-space>
                  <el-select
                    v-model="item.match"
                    placeholder="匹配方式"
                    style="max-width: 100px; width: 120px"
                  >
                    <el-option
                      v-for="oitem in matchOptions"
                      :key="oitem.value"
                      :label="oitem.label"
                      :value="oitem.value"
                    >
                      <span style="float: left">{{ oitem.label }}</span>
                      <span
                        style="
                          float: right;
                          color: var(--el-text-color-secondary);
                          font-size: 13px;
                        "
                      >
                        {{ oitem.description }}
                      </span>
                    </el-option>
                  </el-select>
                  <div
                    v-if="
                      item.match === 'null' || item.match === 'not:null'
                        ? true
                        : false
                    "
                  ></div>
                  <div v-else>
                    <div
                      v-if="
                        ['enum'].indexOf(
                          props.allModelFieldByNameObj[item.name].type
                        ) >>> -1
                          ? false
                          : true
                      "
                    >
                      <el-select
                        v-model="item.value"
                        placeholder="请选择"
                        style="width: 180px"
                      >
                        <el-option
                          v-for="ritem in props.enumOptionObj[
                            props.allModelFieldByNameObj[item.name]
                              .validation_rule
                          ]"
                          :key="ritem.value"
                          :label="ritem.label"
                          :value="ritem.value"
                        />
                      </el-select>
                    </div>
                    <div
                      v-else-if="
                        ['model_ref'].indexOf(
                          props.allModelFieldByNameObj[item.name].type
                        ) >>> -1
                          ? false
                          : true
                      "
                    >
                      <el-select
                        v-model="item.value"
                        placeholder="请选择"
                        style="width: 180px"
                      >
                        <el-option
                          v-for="ritem in props.modelRefOptions[item.name]"
                          :key="ritem.value"
                          :label="ritem.label"
                          :value="ritem.value"
                        />
                      </el-select>
                    </div>
                    <div
                      v-else-if="
                        ['boolean'].indexOf(
                          props.allModelFieldByNameObj[item.name].type
                        ) >>> -1
                          ? false
                          : true
                      "
                    >
                      <el-switch
                        v-model="item.value"
                        style="
                          --el-switch-on-color: #13ce66;
                          --el-switch-off-color: #ff4949;
                        "
                      />
                    </div>

                    <div v-else>
                      <el-input v-model="item.value" style="width: 180px" />
                    </div>
                  </div>
                </el-space>
              </el-form-item>
            </el-space>
          </el-form>
        </div>
      </div>
    </template>
    <template #footer>
      <div style="flex: auto">
        <el-button @click="resetForm(filterFormRef)">重置</el-button>
        <el-button @click="searchCommit()" type="primary">搜索</el-button>
      </div>
    </template>
  </el-drawer>
</template>
<script setup lang="ts">
import { ArrowRight, CircleClose } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  computed,
  ref,
  watch,
  getCurrentInstance,
  nextTick,
  reactive,
} from "vue";
const props = defineProps([
  "ciModelId",
  "currentNodeId",
  "allModelField",
  "allModelFieldByNameObj",
  "enumOptionObj",
  "validationRulesObj",
  "modelRefOptions",
]);
const isShowFilter = defineModel("showFilter");
// const hasConfigField = defineModel("hasConfigField");
const filterText = ref("");
const filterInputRef = ref("");
const filterModelFields = computed(() => {
  if (filterText.value === "") return notConfigFieldList.value;
  return notConfigFieldList.value.filter((item) =>
    item.verbose_name.includes(filterText.value)
  );
});

const { proxy } = getCurrentInstance();

function handleClose() {
  isShowFilter.value = false;
}

// const list1 = ref([1, 2, 3, 4, 5, 6]);
// const hasConfigFieldList = ref([1, 2, 3]);

const toRight = (params) => {
  filterLists.value.push(params);
};
const toLeft = (params) => {
  let index = filterForm.filterParams.indexOf(params);
  filterLists.value.splice(index, 1);
};

const removeFilterParam = (name, index) => {
  if (name === "instance_name") {
    filterForm.instance_name = "";
    // filterParam;
  } else {
    filterLists.value.splice(index, 1);
  }
  nextTick(() => {
    emit("updateFilterParam", filterParamComputed.value);
  });
};
const notConfigFieldList = computed(() => {
  return props.allModelField.filter(
    (item) => !filterLists.value.includes(item)
  );
});
// const filterParam = defineModel("filterParam");
const filterParam = ref({});
const emit = defineEmits(["getCiData", "updateFilterParam"]);

const filterFormRef = ref("");
const filterForm = reactive({
  filterParams: [],
  instance_name: "",
});
const matchOptions = ref([
  { value: "=", label: "等于", description: "等于" },
  { value: "not:", label: "不等于", description: "不等于" },
  { value: "like:", label: "模糊匹配", description: "模糊匹配" },
  { value: "not:like:", label: "反向模糊", description: "反向模糊匹配" },
  { value: "in:", label: "包含", description: "包含以,分隔" },
  { value: "not:in:", label: "不包含", description: "不包含以,分隔" },
  { value: "regex:", label: "正则", description: "正则表达式" },
  { value: "null", label: "空", description: "正则表达式" },
  { value: "not:null", label: "非空", description: "正则表达式" },
]);
const filterLists = ref([]);
const filterParamComputed = computed(() => {
  let tmpObj = new Object();

  // console.log(filterParams.value);
  filterForm.filterParams.forEach((item) => {
    // 新增空和非空的匹配
    if (item.match === "null" || item.match === "not:null") {
      tmpObj[item.name] = item.match;
      return;
    }
    if (item.value !== "") {
      let _tmpValue = null;
      if (item.value !== null) {
        _tmpValue = item.value;
      } else {
        _tmpValue = "null";
      }
      if (item.match === "=") {
        tmpObj[item.name] = _tmpValue;
      } else {
        tmpObj[item.name] = item.match + _tmpValue;
      }
    }
  });

  // name字段判断有没有过滤值
  if (filterForm.instance_name !== "") {
    tmpObj.instance_name = filterForm.instance_name;
  }
  return tmpObj;
});
// watch(
//   () => filterParamComputed.value,
//   (n) => {
//     console.log(n);
//   },
//   { deep: true }
// );
// const filterLists = computed(() => ciStore.filterLists);
const searchCommit = () => {
  console.log(filterParamComputed.value);

  emit("updateFilterParam", filterParamComputed.value);
  console.log(filterParamComputed.value);
  // 发起查询流程
  nextTick(() => {
    emit("getCiData", {
      model: props.ciModelId,
      model_instance_group: props.currentNodeId,
    });
  });

  isShowFilter.value = false;
};

const filterParamsName = computed(() =>
  filterForm.filterParams?.map((item) => item.name)
);

// 监听右侧的字段过滤，生成过滤表单
watch(
  () => filterLists.value,
  (n) => {
    let _tmpArr = new Array();
    // if (filterLists.value)
    filterLists.value?.forEach((item, index) => {
      if (filterParamsName.value?.indexOf(item.name) >>> -1) {
        _tmpArr.push({
          name: item.name,
          value: "",
          match: "=",
          label: item.verbose_name,
        });
      } else {
        let index = filterForm.filterParams.findIndex(
          (item2) => item2.name === item.name
        );
        _tmpArr.push(filterForm.filterParams[index]);
      }
    });
    filterForm.filterParams = _tmpArr;
  },
  { deep: true }
);

const resetForm = (formEl) => {
  if (!formEl) return;
  formEl.resetFields();
  emit("updateFilterParam", filterParamComputed.value);
  nextTick(() => {
    emit("getCiData", {
      model: props.ciModelId,
      model_instance_group: props.currentNodeId,
    });
  });
};

defineExpose({
  removeFilterParam,
});
</script>
<style scoped lang="scss">
.el-divider--horizontal {
  margin: 20px 0;
}
.el-drawer__header {
  margin-bottom: 0px !important;
}
</style>