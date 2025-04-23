<template>
  <el-tree style="max-width: 200px" :allow-drop="allowDrop" :allow-drag="allowDrag" :data="data" draggable
    default-expand-all node-key="id" @node-drag-start="handleDragStart" @node-drag-enter="handleDragEnter"
    @node-drag-leave="handleDragLeave" @node-drag-over="handleDragOver" @node-drag-end="handleDragEnd"
    @node-drop="handleDrop" @node-contextmenu="openMenu" >

    <template #default="{ node, data }">
      <div>
            <el-input
              v-if="isEdit === data.id"
              v-model.trim="groupNameInput"
              placeholder="请输入"
              @blur="$event => editSave($event, data)"
              @keyup.enter="$event.target.blur()"
              > 
            </el-input>
            <span v-else @dblclick.stop="editCateName(data)">
              {{data.label}}
            </span>
          </div>
      </template>
    </el-tree>

  <!-- 右键菜单 -->
  <el-popover ref="popover" v-model:visible="contextMenuVisible" placement="bottom-start" :width="30"

    :popper-style="{ left: `${menuPosition.x}px`, top: `${menuPosition.y}px`, position: 'absolute' ,'min-width':'80px'}" trigger="manual">
    <div style="width: 60px;">
      <div @click="editNode" >修改节点</div>
      <div @click="addNode" >新增节点</div>
      <div @click="deleteNode">删除节点</div>
    </div>
  </el-popover>
</template>

<script lang="ts" setup>
import { ElScrollbar } from 'element-plus';
import { ref, reactive, watch, getCurrentInstance, nextTick, onActivated, computed, onMounted } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'

const renderContent = (h, { node }) => {
  return h(ElScrollbar, null, node.verbose_name);
};
const handleDragStart = (node: Node, ev: DragEvents) => {
  console.log('drag start', node)
}
const handleDragEnter = (
  draggingNode: Node,
  dropNode: Node,
  ev: DragEvents
) => {
  console.log('tree drag enter:', dropNode.label)
}
const handleDragLeave = (
  draggingNode: Node,
  dropNode: Node,
  ev: DragEvents
) => {
  console.log('tree drag leave:', dropNode.label)
}
const handleDragOver = (draggingNode: Node, dropNode: Node, ev: DragEvents) => {
  console.log('tree drag over:', dropNode.label)
}
const handleDragEnd = (
  draggingNode: Node,
  dropNode: Node,
  dropType: NodeDropType,
  ev: DragEvents
) => {
  // console.log('tree drag end:', dropNode && dropNode.label, dropType)
}
const handleDrop = (
  draggingNode: Node,
  dropNode: Node,
  dropType: NodeDropType,
  ev: DragEvents
) => {
  console.log('tree drop:', dropNode.label, dropType)
}
const allowDrop = (draggingNode: Node, dropNode: Node, type: AllowDropType) => {
  if (dropNode.data.label === 'Level two 3-1') {
    return type !== 'inner'
  } else {
    return true
  }
}
const allowDrag = (draggingNode: Node) => {
  return !draggingNode.data.label.includes('Level three 3-1-1')
}

const data = [
  {
    id:1,
    label: '所有',
    children: [
      {
        label: '资源池',
        id:2,
        children: [
          {
            label: '空闲池',
            id:3
          },
        ],
      },
    ],
  },
]



// 菜单相关
const contextMenuVisible = ref(false);
const menuPosition = ref({ x: 0, y: 0 });
const selectedNode = ref<any>(null);
// 处理右键点击事件
const openMenu = (event: MouseEvent, node: any, treeNode: any) => {
  event.preventDefault();
  selectedNode.value = node;
  menuPosition.value = { x: event.clientX, y: event.clientY }; // 获取鼠标点击的位置
  contextMenuVisible.value = true;
};
// 新增节点
const addNode = () => {
  contextMenuVisible.value = false;
  if (selectedNode.value) {
    // 在这里处理你的数据调取新增方法
  }
};
// 修改节点
const isEdit = ref(99999)
const groupNameInput = ref('')
const editNode = () => {
  contextMenuVisible.value = false;
  if (selectedNode.value) {
    // 在这里处理修改数据然后请求方法

  }
};


// 双击重命名
function editCateName(data) {
// 将当前节点名赋值给groupNameInput
console.log(data)
  groupNameInput.value = data.name;
// 将当前节点id赋值给isEdit
  isEdit.value = data.id;
}

// 失去焦点   
function editSave(val, data) {
// 置为初始值
  isEdit.value = 9999;
  if (!groupNameInput.value) {
    ElMessage.warning('材料名称不可为空');
    return false;
  }
}

const { proxy } = getCurrentInstance();


// 删除节点
const deleteNode = () => {
  contextMenuVisible.value = false;
  if (selectedNode.value) {
    ElMessageBox.confirm(
      '确定删除该条信息数据吗?',
      '系统提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    ).then(() => {
      // 请求删除节点的方法  删除节点
    }).catch(() => {

    })
  }
};

</script>

<style scoped>
::v-deep .tree_rightmenu {
  position: fixed;
  width: 10%;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.175);
  z-index: 1000;
}
</style>