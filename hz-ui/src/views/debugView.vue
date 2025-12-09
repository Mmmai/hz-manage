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

    <!-- <ZtTreeTransfer
      :default-props="transferProps"
      :default-selection-keys="toData"
      :left-data="fromData"
      node-key="id"
      default-expand-all
      is-select-all-nodes
      is-sort
      @check-val="checkVal"
      >111111</ZtTreeTransfer
    > -->
    <div class="example-container">
      <TreeTransfer
        v-model="selectedKeys"
        :data="treeData"
        :titles="['可选节点', '已选节点']"
        :leaf-only="true"
        :check-strictly="false"
        @change="handleChange"
      />
    </div>
  </div>
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
import { computed, ref, onMounted, watch, getCurrentInstance } from "vue";
import { VueDraggable } from "vue-draggable-plus";
import ZtTreeTransfer from "../components/common/treeToTree.vue";
import TreeTransfer from "../components/common/treeTransfer.vue";
const { proxy } = getCurrentInstance();

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

const fromData = ref([
  {
    id: 1,
    label: "1Level one 1",
    children: [
      {
        id: 4,
        label: "1-1",
        children: [
          {
            id: 9,
            label: "1-1-1",
          },
          {
            id: 10,
            label: "1-1-2",
          },
        ],
      },
    ],
  },
  {
    id: 2,
    label: "2Level one 2",
    children: [
      {
        id: 5,
        label: "2-1",
      },
      {
        id: 6,
        label: "2-2",
      },
    ],
  },
  {
    id: 3,
    label: "3Level one 31111111",
    children: [
      {
        id: 7,
        label: "3-111111111111111111",
        disabled: true,
      },
      {
        id: 8,
        label: "Level two 3-21111111",
        disabled: true,
        children: [
          {
            id: 11,
            label: "4-111111111111111111111",
          },
          {
            id: 12,
            label: "4-211111111111111111111",
          },
        ],
      },
    ],
  },
]); // 树形数据
const toData = ref([9, 10]); // 选中的ids数据
const transferProps = ref({
  label: "label",
  children: "children",
  disabled: "disabled",
});

const checkVal = (val: any) => {
  console.log(val);
};
const treeData = ref([]);

const selectedKeys = ref([]);
function convertToTreeFormat(treeData) {
  /**
   * 递归转换节点
   * @param {Object} node - 原始节点
   * @returns {Object|null} 转换后的节点，如果应该被剔除则返回null
   */
  function convertNode(node) {
    const newNode = {
      id: node.id,
      label: node.label,
    };

    // 处理子节点
    let validChildren = [];
    if (node.children && node.children.length > 0) {
      validChildren = node.children
        .map(convertNode)
        .filter((child) => child !== null);
    }

    // 处理实例
    let instanceNodes = [];
    if (node.instances && node.instances.length > 0) {
      // 将instances转换为叶子节点
      instanceNodes = node.instances.map((instance) => ({
        id: instance.id,
        label: instance.instance_name,
      }));
    }

    // 合并子节点和实例节点
    const allChildren = [...validChildren, ...instanceNodes];

    if (allChildren.length > 0) {
      newNode.children = allChildren;
    } else if (
      (!node.instances || node.instances.length === 0) &&
      (!node.children || node.children.length === 0)
    ) {
      // 如果既没有子节点也没有实例，则剔除此节点
      return null;
    }

    return newNode;
  }

  // 处理根节点数组并过滤掉null节点
  const result = treeData.map(convertNode).filter((node) => node !== null);
  return result;
}

// 获取主机模型
const hostModel = ref(null);
const getCiModel = async () => {
  let res = await proxy.$api.getCiModel({
    name: "hosts",
  });
  hostModel.value = res.data.results[0];
};

// 获取主机树数据
const getHostTreeData = async () => {
  console.log(hostModel.value);
  let res = await proxy.$api.getCiModelTreeNode({
    model: hostModel.value?.id,
  });
  treeData.value = convertToTreeFormat(res.data);
  console.log(treeData.value);
};

onMounted(async () => {
  await getCiModel();
  await getHostTreeData();
});
//
const handleChange = (newVal, direction, movedKeys) => {
  console.log("值变化:", newVal);
  console.log("移动方向:", direction);
  console.log("移动的keys:", movedKeys);
};
</script>