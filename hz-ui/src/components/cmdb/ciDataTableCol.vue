<template>
  <el-drawer v-model="isShowTableCol" direction="rtl" size="50%">
    <template #header>
      <el-text tag="b">表格列显示配置</el-text>
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
          <el-text tag="b">已显示字段</el-text>
          <el-divider />

          <VueDraggable
            ref="el"
            v-model="hasConfigFieldList"
            @start="onStart"
            @update="onUpdate"
            @end="onEnd"
            style="width: 100%; overflow: auto"
          >
            <div v-for="(item, index) in hasConfigFieldList" :key="index">
              <div class="listItem">
                <span>{{ item.verbose_name }}</span>
                <el-icon><Close @click="toLeft(item)" /></el-icon>
              </div>
            </div>
          </VueDraggable>
        </div>
      </div>
    </template>
    <template #footer>
      <div style="flex: auto">
        <el-button @click="cancelClick">取消</el-button>
        <el-button type="primary" @click="colCommit">保存</el-button>
      </div>
    </template>
  </el-drawer>
</template>
<script setup lang="ts">
import {
  ArrowRight,
  CircleClose,
  CirclePlus,
  Close,
  Delete,
} from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  computed,
  ref,
  onMounted,
  watch,
  getCurrentInstance,
  nextTick,
} from "vue";
import { VueDraggable } from "vue-draggable-plus";
const props = defineProps(["ciModelId", "allModelFieldInfo", "allModelField"]);
const isShowTableCol = defineModel("isShowTableCol");
// const hasConfigField = defineModel("hasConfigField");
const hasConfigFieldList = defineModel("hasConfigField");

const { proxy } = getCurrentInstance();
// 字段筛选
const filterText = ref("");
const filterInputRef = ref("");
// const handleClose = (done: () => void) => {
//   ElMessageBox.confirm("Are you sure you want to close this?")
//     .then(() => {
//       done();
//     })
//     .catch(() => {
//       // catch error
//     });
// };
const filterModelFields = computed(() => {
  if (filterText.value === "") return notConfigFieldList.value;
  return notConfigFieldList.value.filter((item) =>
    item.verbose_name.includes(filterText.value)
  );
});
//   // filter(val);
//   if (val === "") return (filterModelFields.value = notConfigFieldList.value);
//   filterModelFields.value = notConfigFieldList.value.filter((item) =>
//     item.verbose_name.includes(val)
//   );
// });
function cancelClick() {
  isShowTableCol.value = false;
}
function confirmClick() {
  ElMessageBox.confirm(`Are you confirm to chose ${radio1.value} ?`)
    .then(() => {
      isShowTableCol.value = false;
    })
    .catch(() => {
      // catch error
    });
}

// const list1 = ref([1, 2, 3, 4, 5, 6]);
// const hasConfigFieldList = ref([1, 2, 3]);

const toRight = (params) => {
  hasConfigFieldList.value.push(params);
};
const toLeft = (params) => {
  let index = hasConfigFieldList.value.indexOf(params);
  hasConfigFieldList.value.splice(index, 1);
};

const onStart = (e: DraggableEvent) => {
  console.log("start", e);
};

const onEnd = (e: DraggableEvent) => {
  console.log("onEnd", e);
  console.log(hasConfigFieldList.value);
};

const onUpdate = () => {
  console.log("update");
};

// 获取模型已配置的显示列
const ciModelCol = ref({});
const getHasConfigField = async () => {
  let res = await proxy.$api.getCiModelCol({
    model: props.ciModelId,
  });
  // console.log(typeof res.data.fields_preferred)
  ciModelCol.value = res.data;
  // hasConfigField.value = res.data.fields_preferred;
  let tmpArr = [];
  res.data.fields_preferred.forEach((item) => {
    tmpArr.push(props.allModelFieldInfo[item]);
  });
  hasConfigFieldList.value = tmpArr;
  // console.log(hasConfigFieldList.value);

  // console.log(1111);
};
// 用于更新
const hasConfigFieldIdList = computed(() => {
  return hasConfigFieldList.value.map((item) => item.id);
});
const emits = defineEmits(["reloadTable"]);
watch(
  () => hasConfigFieldList.value,
  (n) => {
    emits("reloadTable");
    // console.log(hasConfigFieldList.value);
  }
);
// watch(
//   () => isShowTableCol.value,
//   (n) => {
//     if (n) {
//       getHasConfigField();
//     }
//   }
// );
const colCommit = async () => {
  // 提交更新
  let res = await proxy.$api.updateCiModelCol({
    id: ciModelCol.value.id,
    fields_preferred: hasConfigFieldIdList.value,
  });
  // hasConfigField.value =
  if (res.status == "200") {
    ElMessage({ type: "success", message: "更新成功" });
    // 重置表单
    nextTick(() => {
      filterInputRef.value!.clear();
      isShowTableCol.value = false;
    });
    // 获取数据源列表
  } else {
    ElMessage({
      showClose: true,
      message: "更新失败:" + JSON.stringify(res.data),
      type: "error",
    });
  }
};
const notConfigFieldList = computed(() => {
  return props.allModelField.filter(
    (item) => !hasConfigFieldList.value.includes(item)
  );
});
defineExpose({
  getHasConfigField,
});
// onMounted(async () => {
//   await getHasConfigField();
// });
</script>
<style scoped lang="scss">
.el-divider--horizontal {
  margin: 20px 0;
}
.el-drawer__header {
  margin-bottom: 0px !important;
}
</style>