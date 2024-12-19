<template>
  <div class="card ci_data_tree">
    <el-row align="middle" justify="start">
      <el-col :span="8">
        <el-text tag="b">实例树</el-text>
      </el-col>
      <el-col :span="14">
        <el-select
          v-model="ciModelId"
          placeholder="Select"
          @change="changeModel()"
        >
          <el-option
            v-for="item in modelist"
            :key="item.id"
            :label="item.verbose_name"
            :value="item.id"
          />
        </el-select>
      </el-col>
    </el-row>

    <el-divider />
    <el-input
      v-model="filterText"
      clearable
      style="max-width: 280px; margin-bottom: 10px"
      size="small"
      placeholder="检索节点"
    />
    <el-tree
      style="max-width: 280px; height: auto"
      :allow-drop="allowDrop"
      :allow-drag="allowDrag"
      :data="treeData"
      :draggable="false"
      default-expand-all
      node-key="id"
      @node-drag-start="handleDragStart"
      @node-drag-enter="handleDragEnter"
      @node-drag-leave="handleDragLeave"
      @node-drag-over="handleDragOver"
      @node-drag-end="handleDragEnd"
      @node-drop="handleDrop"
      :highlight-current="true"
      :current-node-key="currentNodeId"
      :expand-on-click-node="false"
      ref="treeRef"
      @node-click="nodeClick"
      :filter-node-method="filterNode"
      v-loading="loading"
    >
      <!-- <template #default="{ node, data }" class="labelClass"> -->
      <template #default="{ node, data }">
        <div class="custom-tree-node">
          <el-input
            v-if="isEdit === data.id"
            v-model.trim="groupNameInput"
            placeholder="请输入"
            ref="eInputRef"
            @blur="($event) => editSave($event, data)"
            @keyup.enter="$event.target.blur()"
            :autofocus="true"
            maxlength="6"
            type="text"
            size="small"
          >
          </el-input>
          <el-text size="default" v-else
            >{{ node.label
            }}<el-text size="small"
              >({{ data.instance_count }})</el-text
            ></el-text
          >
          <div class="actionClass" :class="{ is_show_action: node.isShowEdit }">
            <!-- <Edit style="width: 1em; height: 1em; margin-right: 8px" @click.stop="editCateName(data)"
            v-if="!data.built_in" /> -->
            <el-space>
              <EditOutlined
                @click.stop="editCateName(data)"
                v-if="!data.built_in"
              />
              <a-dropdown
                :trigger="['click']"
                ref="aDropdownRef"
                @openChange="handleOpen(node)"
              >
                <DownOutlined @click.stop />
                <template #overlay>
                  <a-menu>
                    <a-menu-item
                      key="0"
                      v-if="data.level === 1 ? false : true"
                      @click="appendBroNode(node, data)"
                    >
                      添加同级节点
                    </a-menu-item>
                    <a-menu-item
                      key="1"
                      v-if="canAddChildNone(data)"
                      @click="appendChildNode(node, data)"
                    >
                      添加子节点
                    </a-menu-item>
                    <a-menu-item
                      key="2"
                      v-if="canDeleteNode(data)"
                      @click="deleteNode(node)"
                    >
                      删除节点
                    </a-menu-item>
                  </a-menu>
                </template>
              </a-dropdown>
            </el-space>
          </div>
        </div>
      </template>

      <!-- </template> -->
    </el-tree>
  </div>
  <div class="table-box">
    <ciDataShow
      :ciModelId="ciModelId"
      :treeData="treeData"
      :currentNodeId="currentNodeId"
      ref="ciDataShowRef"
      @getTree="getCiModelTree"
    />
    <!-- 右键菜单 -->
  </div>
</template>

<script lang="ts" setup>
import { ElScrollbar } from "element-plus";
import {
  ref,
  reactive,
  watch,
  getCurrentInstance,
  nextTick,
  onActivated,
  computed,
  onMounted,
} from "vue";
import { ElMessageBox, ElMessage } from "element-plus";
import { EditOutlined, DownOutlined, StarTwoTone } from "@ant-design/icons-vue";
//
import ciDataShow from "../components/cmdb/ciDataShow.vue";
const { proxy } = getCurrentInstance();
import { ElTree } from "element-plus";
import type Node from "element-plus/es/components/tree/src/model/node";
import useCiStore from "@/store/cmdb/ci";
const ciStore = useCiStore();
const modelInfo = ref("");
// const currentIconName = defineModel('iconName')
// const emit = defineEmits(["toChildGetCiData"])
const loading = ref(false);
const test = ref("");

const isShowPopover = ref(false);
const aDropdownRef = ref();
const openChange = () => {
  // isShowPopover.value = true
  isShowEdit.value = !isShowEdit.value;
  // node.isShowEdit = isShowEdit.value

  setTimeout(() => {
    node.isShowEdit = isShowEdit.value;
  }, 350);
};
const treeData = ref([]);
const filterText = ref("");
watch(filterText, (val) => {
  treeRef.value!.filter(val);
});
const filterNode = (value: string, data: Tree) => {
  if (!value) return true;
  return data.label.toLowerCase().includes(value.toLowerCase());
};

// 获取当前实例的树
// watch(() => modelInfo.value, async (n,) => {
//   await getCiModelTree()
// })

// 判断子按钮
const canAddChildNone = (data) => {
  if (data.level > maxLevel.value - 1 || data.label === "空闲池") {
    return false;
  } else {
    return true;
  }
};
const getCiModelTree = async () => {
  loading.value = true;
  let res = await proxy.$api.getCiModelTree({ model: ciModelId.value });
  console.log(res);
  treeData.value = [res.data];
  nextTick(() => {
    // if ()
    if (currentNodeId.value === 1) {
      treeRef.value!.setCurrentKey(res.data.id);
      currentNodeId.value = treeRef.value!.getCurrentKey();
    }
  });
  loading.value = false;
};
// 获取所有模型列表
const modelist = ref([]);
const ciModelId = ref("");

// const defaultCimodelId = ref('id')
const getCiModelList = async () => {
  let res = await proxy.$api.getCiModel();
  modelist.value = res.data.results;
  ciStore.setModelList(modelist.value);
  // 设置默认为host
  modelInfo.value = modelist.value.find((item) => item.name === "hosts");
  ciModelId.value = modelist.value.find((item) => item.name === "hosts").id;
};

const modelInfoObj = computed(() => {
  let tmpObj = {};
  modelist.value.forEach((item) => {
    tmpObj[item.id] = item;
  });
  return tmpObj;
});

// 父组件调用子组件
const ciDataShowRef = ref("");
// 切换模型时
const changeModel = async () => {
  currentNodeId.value = 1;
  await getCiModelTree();
  // modelInfo.value = modelInfoObj.value[ciModelId.value]
  // console.log(modelInfo.value)
  await ciDataShowRef.value!.closeFilter();

  await ciDataShowRef.value!.clearMultipleSelect();

  await ciDataShowRef.value!.setLoading(true);

  await ciDataShowRef.value!.getHasConfigField();
  await ciDataShowRef.value!.getModelField();
  // await ciDataShowRef.value!.getCiData()
  await ciDataShowRef.value!.setLoading(false);
  await ciDataShowRef.value!.initCiDataForm();
  await ciDataShowRef.value!.getCiData({
    model: ciModelId.value,
    model_instance_group: currentNodeId.value,
  });
};
// watch(()=>ciModelId.value,async(n,)=>{
//   await getCiModelTree();
//   console.log(modelist.value)
//   console.log(ciModelId.value)
//   modelInfo.value = modelist.value.find(item=> item.id === ciModelId.value)
//   console.log(modelInfo.value)
// },{deep:true})
onMounted(async () => {
  console.log(123);
  await getCiModelList();
  await getCiModelTree();
  ciDataShowRef.value!.setLoading(true);
  await ciDataShowRef.value!.getHasConfigField();
  await ciDataShowRef.value!.getModelField();
  // await ciDataShowRef.value!.getCiData()
  await ciDataShowRef.value!.setLoading(false);

  await ciDataShowRef.value!.initCiDataForm();
  await ciDataShowRef.value!.getCiData({
    model: ciModelId.value,
    model_instance_group: treeRef.value!.getCurrentKey(),
  });
});

// 节点是否可以删除
const canDeleteNode = (params) => {
  if (!params.built_in) {
    if (!params.children) {
      return true;
    }
    if (params.children.length >>> 0) {
      return false;
    } else {
      return true;
    }
  } else {
    return false;
  }
};
const treeRef = ref<InstanceType<typeof ElTree>>();
const eInputRef = ref();
const currentNodeId = ref(1);
const isShowEdit = ref(false);

const cid = ref(100);
const appendChildNode = (node, data) => {
  isEditAction.value = false;
  let nid = cid.value++;
  treeRef.value!.append(
    {
      id: nid,
      label: "新建子目录",
      level: data.level + 1,
      parent: data.id,
      model: modelInfo.value.id,
    },
    node
  );
  treeRef.value!.setCurrentKey(nid);
  isEdit.value = nid;
  nextTick(() => {
    eInputRef.value.focus();
  });
};
const appendBroNode = (node, data) => {
  let nid = cid.value++;
  isEditAction.value = false;
  treeRef.value!.insertAfter(
    {
      id: nid,
      label: "新建目录",
      level: data.level,
      parent: node.parent.data.id,
      model: modelInfo.value.id,
    },
    node
  );
  treeRef.value!.setCurrentKey(nid);
  isEdit.value = nid;
  nextTick(() => {
    eInputRef.value.focus();
  });
};
const nodeClick = () => {
  // 点击节点后，触发cidata父组件获取数据接口
  currentNodeId.value = treeRef.value!.getCurrentKey();
  ciDataShowRef.value!.clearMultipleSelect();

  // emit('toChildGetCiData',{id:treeRef.value!.getCurrentKey()})
  ciDataShowRef.value!.setLoading(true);
  ciDataShowRef.value!.getCiData({
    model: ciModelId.value,
    model_instance_group: treeRef.value!.getCurrentKey(),
  });
  ciDataShowRef.value!.setLoading(true);
};

const handleOpen = (node) => {
  isShowEdit.value = !isShowEdit.value;
  node.isShowEdit = isShowEdit.value;
};

// 修改节点
const isEdit = ref(99999);
const groupNameInput = ref("");

const isEditAction = ref(true);
// 点击重命名
const editCateName = (data) => {
  // 将当前节点名赋值给groupNameInput
  isEditAction.value = true;
  console.log(data);
  groupNameInput.value = data.label;
  // 将当前节点id赋值给isEdit
  isEdit.value = data.id;
  nextTick(() => {
    eInputRef.value.focus();
  }); // nextTick(()=>{
  //   data.isShowEdit = false

  // })
};

// 失去焦点
const editSave = async (val, data) => {
  // 置为初始值
  isEdit.value = 99999;
  if (!groupNameInput.value) {
    ElMessage.warning("名称不可为空");
    treeRef.value!.remove(data);
  } else {
    // 更新
    if (isEditAction.value) {
      if (groupNameInput.value == data.label) {
        return false;
      } else {
        let res = await proxy.$api.updateCiModelTree({
          id: data.id,
          label: groupNameInput.value,
        });
        if (res.status == "200") {
          ElMessage({ type: "success", message: "更新成功" });
          // 重置表单
          data.label = groupNameInput.value;
          getCiModelTree();
          groupNameInput.value = "";
        } else {
          ElMessage({
            showClose: true,
            message: "更新失败:" + JSON.stringify(res.data),
            type: "error",
          });
        }
        console.log(data);
      }
    } else {
      // 添加请求
      data.label = groupNameInput.value;
      console.log(data);
      let res = await proxy.$api.addCiModelTree(data);
      if (res.status == "201") {
        ElMessage({ type: "success", message: "添加成功" });
        // 重置表单
        getCiModelTree();
        groupNameInput.value = "";
      } else {
        ElMessage({
          showClose: true,
          message: "添加失败:" + JSON.stringify(res.data),
          type: "error",
        });
        treeRef.value!.remove(data);
      }
    }
  }
};

// 删除节点
const deleteNode = (node) => {
  if (node) {
    ElMessageBox.confirm("确定删除该目录吗?", "系统提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    })
      .then(async () => {
        // 请求删除节点的方法  删除节点
        // treeRef.value!.remove(node)
        let res = await proxy.$api.deleteCiModelTree(node.data.id);
        //
        // let res = {status:204}
        if (res.status == 200) {
          ElMessage({
            type: "success",
            message: "删除成功",
          });
          // 重新加载页面数据
          await getCiModelTree();
          // resetForm(modelFieldFormRef.value);
          // modelFieldDrawer.value = false
        } else {
          ElMessage({
            type: "error",
            message: "删除失败",
          });
        }
      })
      .catch(() => {});
  }
};

// 拖拽
const renderContent = (h, { node }) => {
  return h(ElScrollbar, null, node.verbose_name);
};
const dragBeforeNode = ref("");
const handleDragStart = (node: Node, ev: DragEvents) => {
  // console.log('drag start', node)
  dragBeforeNode.value = node;
  console.log(dragBeforeNode.value);
};
const handleDragEnter = (
  draggingNode: Node,
  dropNode: Node,
  ev: DragEvents
) => {
  // console.log('tree drag enter:', dropNode.label)
};
const handleDragLeave = (
  draggingNode: Node,
  dropNode: Node,
  ev: DragEvents
) => {
  // console.log('tree drag leave:', dropNode.label)
};
const handleDragOver = (draggingNode: Node, dropNode: Node, ev: DragEvents) => {
  // console.log('tree drag over:', dropNode.label)
};
// 拖拽结束
const handleDragEnd = async (
  draggingNode: Node,
  dropNode: Node,
  dropType: NodeDropType,
  ev: DragEvents
) => {
  // console.log('进入的节点:',dropNode)
  // console.log('被拖拽的节点:', draggingNode)
  // console.log('111---:',dragBeforeNode.value)
  if (dropNode.data.id === draggingNode.data.id) return;
  // return
  let params = {};
  if (dropType === "inner") {
    params = { id: draggingNode.data.id, parent: dropNode.data.id };
  } else {
    params = { id: draggingNode.data.id, parent: dropNode.parent.data.id };
  }
  let res = await proxy.$api.updateCiModelTree(params);
  if (res.status == "200") {
    ElMessage({ type: "success", message: "更新成功" });
    // 重置表单
    getCiModelTree();
  } else {
    ElMessage({
      showClose: true,
      message: "更新失败:" + JSON.stringify(res.data),
      type: "error",
    });
  }
  // console.log('tree drag end:', dropNode && dropNode.label, dropType)
};
const handleDrop = (
  draggingNode: Node,
  dropNode: Node,
  dropType: NodeDropType,
  ev: DragEvents
) => {
  // console.log('tree drop:', dropNode.label, dropType)
};
// 是否能放进节点
const maxLevel = ref<int>(5);
const allowDrop = (draggingNode: Node, dropNode: Node, type: AllowDropType) => {
  // if (dropNode.data.level === 1 || dropNode.data.label === '空闲池') {
  if (dropNode.data.built_in) {
    return false;
  } else {
    // 当拖拽节点变化后的总层数大于5时，就不能进入这个节点的，以及它的前后
    let _tempLevel = maxLevel.value - draggingNode.data.level;

    if (_tempLevel + dropNode.data.level >= maxLevel.value) {
      if (type === "inner") {
        return false;
      } else {
        return true;
      }
    }
    return true;
  }
};
const allowDrag = (draggingNode: Node) => {
  // 内置目录不能拖拽
  return !draggingNode.data.built_in;
};
</script>

<style scoped lang="scss">
:deep(.tree_rightmenu) {
  position: fixed;
  width: 10%;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.175);
  z-index: 1000;
}

.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
}

.el-dropdown-link {
  cursor: pointer;
  color: var(--el-color-primary);
  display: flex;
  align-items: center;
}

.actionClass {
  display: none;
}

.el-tree-node__content:hover .actionClass {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.is_show_action {
  display: flex;
}

.ci_data_tree {
  // width: 19%;
  // height: $mainHeight - $headerHeight;
  flex: 0 0 $leftTreeWidth;
}

.el-divider--horizontal {
  margin: 8px 0;
}
</style>
