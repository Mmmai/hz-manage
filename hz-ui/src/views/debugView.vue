<template>
  <div
    class="card"
    style="
      /* display: flex; */
      flex-direction: column;
      justify-content: space-between;
    "
  >
    <el-button @click="drawer2 = true">打开</el-button>
    <el-drawer v-model="drawer2" direction="rtl" size="50%">
      <template #header>
        <h4>set title by slot</h4>
      </template>
      <template #default>
        <div
          style="
            display: flex;
            /* flex-direction: column; */
            justify-content: space-around;
            gap: 10px;
            height: 100%;
          "
        >
          <el-card class="card" style="flex: 0.4">
            <template #header>
              <div class="card-header">
                <span>模型字段</span>
              </div>
            </template>

            <div style="width: 100%; overflow: auto">
              <p v-for="(item, index) in listl" :key="index">{{ item }}</p>
              <!-- <div style="display: flex; justify-content: space-between">
                <span>{{ item }}</span>
                <el-icon><ArrowRight @click="toRight(item)" /></el-icon>
              </div> -->
            </div>
          </el-card>
          <el-card class="card" style="flex: 0.4">
            <template #header>
              <div class="card-header">
                <span>已显示字段</span>
              </div>
            </template>
            <VueDraggable
              ref="el"
              v-model="listr"
              @start="onStart"
              @update="onUpdate"
              @end="onEnd"
            >
              <div v-for="(item, index) in listr" :key="index">
                <div style="display: flex; justify-content: space-between">
                  <span>{{ item }}</span>
                  <el-icon><Close @click="toLeft(item)" /></el-icon>
                </div>
              </div>
            </VueDraggable>
          </el-card>
        </div>
      </template>
      <template #footer>
        <div style="flex: auto">
          <el-button @click="cancelClick">cancel</el-button>
          <el-button type="primary" @click="confirmClick">confirm</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>
<script setup lang="ts">
import {
  ArrowRight,
  CircleClose,
  CirclePlus,
  Close,
  Delete,
} from "@element-plus/icons-vue";
import { ElMessageBox } from "element-plus";
import { computed, ref, onMounted, watch } from "vue";
import { VueDraggable } from "vue-draggable-plus";

const drawer2 = ref(false);

const radio1 = ref("Option 1");
const handleClose = (done: () => void) => {
  ElMessageBox.confirm("Are you sure you want to close this?")
    .then(() => {
      done();
    })
    .catch(() => {
      // catch error
    });
};
function cancelClick() {
  drawer2.value = false;
}
function confirmClick() {
  ElMessageBox.confirm(`Are you confirm to chose ${radio1.value} ?`)
    .then(() => {
      drawer2.value = false;
    })
    .catch(() => {
      // catch error
    });
}

const list1 = ref([
  1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22,
  23, 24, 25, 26,
]);
const listr = ref([1, 2, 3]);
const listl = computed(() => {
  return list1.value.filter((item) => !listr.value.includes(item));
});
const toRight = (params) => {
  listr.value.push(params);
};
const toLeft = (params) => {
  let index = listr.value.indexOf(params);
  listr.value.splice(index, 1);
};

const onStart = (e: DraggableEvent) => {
  console.log("start", e);
};

const onEnd = (e: DraggableEvent) => {
  console.log("onEnd", e);
  console.log(listr.value);
};

const onUpdate = () => {
  console.log("update");
};
const hasConfigField = ref([]);

const modelInfo = ref({});
const allModelFieldInfo = computed<any>(() => {
  let tempList = {};
  modelInfo.value?.field_groups?.forEach((item) => {
    item.fields.forEach((field) => {
      tempList[field.id] = field;
    });
  });
  return tempList;
});
const allModelFieldByNameObj = computed<any>(() => {
  let tempList = {};
  modelInfo.value?.field_groups?.forEach((item) => {
    item.fields.forEach((field) => {
      tempList[field.name] = field;
    });
  });
  return tempList;
});
// 获取模型已配置的显示列
const ciModelCol = ref({});
const getHasConfigField = async () => {
  let res = await proxy.$api.getCiModelCol({
    model: "a8406612-738f-4b8f-93cc-e3f8fbe217ee",
  });
  // console.log(typeof res.data.fields_preferred)
  ciModelCol.value = res.data;
  hasConfigField.value = res.data.fields_preferred;
};
onMounted(async () => {
  await getHasConfigField();
});
</script>