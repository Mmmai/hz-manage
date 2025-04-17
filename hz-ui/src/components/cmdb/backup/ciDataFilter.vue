<template>
  <div class="card filterClass">
    <div class="formTop">
      <el-form
        ref="multipleFormRef"
        :model="multipleForm"
        label-width="auto"
        style="width: 100%"
        label-position="top"
      >
        <el-space wrap>
          <el-form-item
            v-for="(item, index) in multipleForm.filterParams"
            :key="item.index"
            :prop="'filterParams.' + index + '.value'"
          >
            <template #label>
              <span style="margin-right: 5px">{{ item.label }}</span>
              <el-button
                :icon="CircleClose"
                size="small"
                circle
                @click.prevent="removeFilterParams(index)"
              >
              </el-button>
            </template>
            <!--       :rules="modelFieldFormItemRule"
        :rules="setUpdateFormItemRule(props.allModelFieldByNameObj[item.name]?.validation_rule)"
   :rules="setFormItemRule(item.name)"  -->
            <el-space>
              <el-select
                v-model="item.match"
                placeholder="匹配方式"
                style="max-width: 100px; width: 90px"
              >
                <!-- <el-option
                  v-for="oitem in matchOptions"
                  :key="oitem.value"
                  :label="oitem.label"
                  :value="oitem.value"
                /> -->
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
                      props.allModelFieldByNameObj[item.name].validation_rule
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
            </el-space>
          </el-form-item>
        </el-space>
      </el-form>
    </div>

    <!-- 按钮 -->
    <div class="buttonl">
      <el-button @click="drawer = true">过滤条件</el-button>
      <el-button @click="resetForm(multipleFormRef)">重置</el-button>
      <el-button @click="showFilter = false">隐藏</el-button>

      <el-button @click="searchCommit()" type="primary">搜索</el-button>
    </div>

    <el-drawer v-model="drawer" title="勾选过滤字段">
      <el-checkbox-group v-model="filterLists" @change="setFilter">
        <el-checkbox
          :label="item.verbose_name"
          :value="item"
          :key="index"
          v-for="(item, index) in props.allModelField"
        />
      </el-checkbox-group>
    </el-drawer>
  </div>
</template>
<script lang="ts" setup>
import {
  watch,
  ref,
  reactive,
  computed,
  onActivated,
  onMounted,
  nextTick,
} from "vue";
import {
  Check,
  Delete,
  Setting,
  Message,
  Search,
  Star,
  CircleClose,
  Warning,
} from "@element-plus/icons-vue";
const props = defineProps([
  "ciModelId",
  "currentNodeId",
  "allModelField",
  "allModelFieldByNameObj",
  "enumOptionObj",
  "validationRulesObj",
  "modelRefOptions",
]);
// const ciModelId = defineModel("ciModelId");
// const currentNodeId = defineModel("currentNodeId");
// const allModelField = defineModel("allModelField");
const showFilter = defineModel("showFilter");
// const props.allModelFieldByNameObj = defineModel("props.allModelFieldByNameObj");
// const enumOptionObj = defineModel("enumOptionObj");
// const validationRulesObj = defineModel("validationRulesObj");
const filterParam = defineModel("filterParams");
const emit = defineEmits(["getCiData"]);
import useCiStore from "@/store/cmdb/ci";
const ciStore = useCiStore();

const multipleFormRef = ref("");
const drawer = ref(false);
const multipleForm = reactive({
  filterParams: [],
});
const matchOptions = ref([
  { value: "=", label: "=", description: "等于" },
  { value: "not:", label: "!=", description: "不等于" },
  { value: "like:", label: "*=", description: "模糊匹配" },
  { value: "not:like:", label: "!=", description: "反向模糊匹配" },
  { value: "in:", label: "in", description: "包含以,分隔" },
  { value: "not:in:", label: "!in", description: "不包含以,分隔" },
  { value: "regex:", label: "regex", description: "正则表达式" },
]);
const filterLists = ref([]);
// const filterLists = computed(() => ciStore.filterLists);
const searchCommit = () => {
  let tmpObj = {};
  multipleForm.filterParams.forEach((item) => {
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
  console.log(tmpObj);
  filterParam.value = tmpObj;
  // 发起查询流程
  emit("getCiData", {
    model: props.ciModelId,
    model_instance_group: props.currentNodeId,
  });
};
const test = (value) => {
  console.log(value);
};
const filterParamsName = computed(() =>
  multipleForm.filterParams?.map((item) => item.name)
);
// const multipleFormRef =
// 禁用已选择的

const setFilter = (value) => {
  // ciStore.setFilterList(value)
  nextTick(() => {
    console.log(filterLists.value);
  });
};
// const
watch(
  () => filterLists.value,
  (n) => {
    console.log(n);
    let _tmpArr = [];
    filterLists.value?.forEach((item, index) => {
      if (filterParamsName.value.indexOf(item.name) >>> -1) {
        _tmpArr.push({
          name: item.name,
          value: "",
          match: "=",
          label: item.verbose_name,
        });
      } else {
        _tmpArr.push(multipleForm.filterParams[index]);
      }
    });
    multipleForm.filterParams = _tmpArr;
    // ciStore.saveFilterParams(_tmpArr)
  },
  { deep: true }
);

const removeFilterParams = (index) => {
  filterLists.value.splice(index, 1);
};

const resetForm = (formEl) => {
  if (!formEl) return;
  formEl.resetFields();
  filterParam.value = {};
};
const initForm = computed(() => ciStore.multipleForm);
watch(
  () => initForm.value,
  (n) => {
    console.log(123);
    multipleForm.filterParams = initForm.value.filterParams;
  },
  { deep: true }
);
onMounted(() => {
  if (filterLists.value.length === 0) {
    // useCiStore.addFilterList(props.allModelField[0])
    filterLists.value.push(props.allModelField[0]);
  }
});
</script>
<style lang="scss" scoped>
.filterClass {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  flex: 0.3;
  // position: relative;
}

.formTop {
  align-self: flex-start;
  overflow: auto;
  width: 100%;
}

.buttonl {
  display: flex;
  justify-content: flex-end;
  align-self: flex-end;
  width: 100%;
  // position: absolute;
  // bottom: 0;
}
</style>
