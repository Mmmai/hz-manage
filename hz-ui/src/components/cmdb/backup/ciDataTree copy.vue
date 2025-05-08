<template>
  <el-tree style="max-width: 200px;height: auto;" :allow-drop="allowDrop" :allow-drag="allowDrag" :data="treeData" draggable
    default-expand-all node-key="id" @node-drag-start="handleDragStart" @node-drag-enter="handleDragEnter"
    @node-drag-leave="handleDragLeave" @node-drag-over="handleDragOver" @node-drag-end="handleDragEnd"
    @node-drop="handleDrop"
    :highlight-current="true"
    :current-node-key="nowNodeKey"
    :expand-on-click-node="false"
    ref="treeRef"
    @node-click="nodeClick"
    >

    <!-- <template #default="{ node, data }" class="labelClass"> -->
    <template #default="{ node, data }">
      <div class="custom-tree-node">

        <el-input
              v-if="isEdit === data.id"
              v-model.trim="groupNameInput"
              placeholder="请输入"
              ref="eInputRef"
              @blur="$event => editSave($event, data)"
              @keyup.enter="$event.target.blur()"
              :autofocus="true"
              maxlength="10"
              type="text"
              size="small"
              > 
            </el-input>
        <span v-else >{{ node.label }}</span>
        <div  class="actionClass" :class="{is_show_action: node.isShowEdit}">
            <Edit style="width: 1em; height: 1em; margin-right: 8px" @click.stop="editCateName(data)" v-if="!data.built_in"/>

          <el-dropdown  ref="dropdown1" @visible-change="handleOpen(node)" trigger="click" >
            <span class="el-dropdown-link">
              <el-icon class="el-icon--right"><arrow-down  /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item :icon="CirclePlusFilled" @click="appendBroNode(node,data)" v-if="data.level === 1 ? false : true">
                  添加同级节点
                </el-dropdown-item>
                <el-dropdown-item :icon="CirclePlus" @click="appendChildNode(node,data)"  v-if=" data.label === '空闲池'||data.level === 4 ? false : true">添加子节点</el-dropdown-item>
                <el-dropdown-item :icon="Delete" @click="deleteNode(node)" :disabled="nodeDelete(data)"  v-if="data.level === 1 || data.label === '空闲池' ? false : true">删除节点</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        <!-- <el-input
              v-if="isEdit === data.id"
              v-model.trim="groupNameInput"
              placeholder="请输入"
              @blur="$event => editSave($event, data)"
              @keyup.enter="$event.target.blur()"
              > 
            </el-input> -->
        <!-- <span else @dblclick.stop="editCateName(data)"  >
              {{data.label}}
            </span> -->
        <!-- <span v-show="data.show">
          
        </span> -->
      </div>

    </template>

    <!-- </template> -->
  </el-tree>

  <!-- 右键菜单 -->
</template>

<script lang="ts" setup>
import { ElScrollbar } from 'element-plus';
import { ref, reactive, watch, getCurrentInstance, nextTick, onActivated, computed, onMounted } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import {
  ArrowDown,
  Check,
  CircleCheck,
  CirclePlus,
  CirclePlusFilled,
  Delete,
  Plus,
} from '@element-plus/icons-vue'
// 
import { ElTree } from 'element-plus'
import type { DropdownInstance } from 'element-plus'
import type Node from 'element-plus/es/components/tree/src/model/node'
import { fa } from 'element-plus/es/locale/index.mjs';
const modelInfo = defineModel('modelInfo')
// const currentIconName = defineModel('iconName')
const treeData = ref([])
// 获取当前实例的树
watch(()=> modelInfo.value,async(n,) =>{
  console.log(333)
  console.log(modelInfo.value)
  await getCiModelTree()
})
const getCiModelTree = async()=>{
  let res =  await proxy.$api.getCiModelTree({model:modelInfo.value.id})
  console.log({model:modelInfo.value.id})
  console.log(res.data)
  treeData.value = [res.data]
  console.log(treeData.value)
}
onMounted(async()=>{
  console.log(2222)
  console.log(modelInfo.value)
  // await getCiModelTree();
})
// 判断树节点是否可编辑
// const canEdit = (params)=>{
//   if params.built_in
// }
const treeData111 = ref([
  {
    id: 1,
    label: '所有',
    children: [
    {
        label: '空闲池',
        id: 2,

      },
      {
        label: 'BD',
        id: 3,
        children: [
          {
            label: 'kafka',
            id: 21
          },
        ],
      },
    ],
  },
])


interface Tree {
  id: number
  label: string
  children?: Tree[]
}
// 节点是否可以删除
const nodeDelete = (params)=>{
  if (!params.children){
    return false
  } 
  if (params.children.length >>> 0){
    return true
  }else{
    return false
  }
}
const treeRef = ref<InstanceType<typeof ElTree>>()
const eInputRef = ref();
const dropdown1 = ref<DropdownInstance>()
const nowNodeKey = ref(1)
const isShowEdit = ref(false)
const openDropdown = ()=>{
  if (!dropdown1.value) return
  dropdown1.value.handleOpen()
}
const cid = ref(100)
const appendChildNode =  (node,data)=>{
  // console.log(node.parent)
  // console.log(data)
  isEditAction.value = false
  let nid = cid.value++
  console.log(nid)
    // isEdit.value = node.id++
    
  console.log(treeRef.value!.getCurrentKey())
  console.log(treeRef.value!.getCurrentNode())
  treeRef.value!.append({id:nid,label:'新建子目录',level:data.level,parent:data.id,model:modelInfo.value.id},node)
  treeRef.value!.setCurrentKey(nid)

  console.log(treeRef.value!.getCurrentKey())
  console.log(treeRef.value!.getCurrentNode())
  isEdit.value = nid;
  nextTick(()=>{
    // groupNameInput.value = '新建子目录'
    eInputRef.value.focus()
  })

}
const appendBroNode = (node,data)=>{
  let nid = cid.value++
  isEditAction.value = false
  treeRef.value!.insertAfter({id:nid,label:'新建目录',level:data.level,parent:data.id,model:modelInfo.value.id},node)
  treeRef.value!.setCurrentKey(nid)
  isEdit.value =  nid;
  nextTick(()=>{
    eInputRef.value.focus()
  })

}
const nodeClick = ()=>{
  console.log(treeRef.value!.getCurrentNode())
}

const handleOpen = (node)=>{
  isShowEdit.value = !isShowEdit.value
  // node.isShowEdit = isShowEdit.value

  setTimeout(() => {
    node.isShowEdit = isShowEdit.value
  }, 350)
}
const handleClose = ()=>{
  isShowEdit.value = false
}
const mouseenter = (data) => {
  data.show = true
}
const mouseleave = (data) => {
  data.show = false
}

// 新增节点
const addNode = () => {
  if (selectedNode.value) {
    // 在这里处理你的数据调取新增方法
  }
};
// 修改节点
const isEdit = ref(99999)
const groupNameInput = ref('')
const editNode = () => {
  if (selectedNode.value) {
    // 在这里处理修改数据然后请求方法

  }
};

const isEditAction = ref(true)
// 点击重命名
const  editCateName = (data) =>{
  // 将当前节点名赋值给groupNameInput
  isEditAction.value = true
  console.log(data)
  groupNameInput.value = data.label;
  // 将当前节点id赋值给isEdit
  isEdit.value = data.id;
  nextTick(()=>{
    eInputRef.value.focus()
  })  // nextTick(()=>{
  //   data.isShowEdit = false

  // })
}

// 失去焦点   
const editSave = async (val, data) =>{
  // 置为初始值
  isEdit.value = 99999;
  if (!groupNameInput.value) {
    ElMessage.warning('名称不可为空');
    return false;
  }else{
    // 更新
    if (isEditAction.value){
      if (groupNameInput.value == data.label){
          return false
        }else{
            let res = await proxy.$api.updateCiModelTree({id:data.id,label:groupNameInput.value})
            if (res.status == "200") {
                ElMessage({ type: 'success', message: '更新成功', });
                // 重置表单
                groupNameInput.value = ''
              } else {

                ElMessage({ showClose: true, message: '更新失败:' + JSON.stringify(res.data), type: 'error', })
              } 
            console.log(data)
        }
    }else{
      // 添加请求
      data.label = groupNameInput.value
      console.log(data)
      let res = await proxy.$api.addCiModelTree(data)
      if (res.status == "201") {
          ElMessage({ type: 'success', message: '添加成功', });
          // 重置表单
          getCiModelTree();
          // 获取数据源列表        
        } else {
          ElMessage({ showClose: true, message: '添加失败:' + JSON.stringify(res.data), type: 'error', })
          treeRef.value!.remove(data)
        }
    }
    
    // 发起更新请求


  }
}

const { proxy } = getCurrentInstance();


// 删除节点
const deleteNode = (node) => {
  if (node) {
    console.log(node)
    ElMessageBox.confirm(
      '确定删除该目录吗?',
      '系统提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    ).then(async() => {
      // 请求删除节点的方法  删除节点
      // treeRef.value!.remove(node)
      let res = await proxy.$api.deleteCiModelTree(node.data.id)
    // 
    // let res = {status:204}
    if (res.status == 204) {
      ElMessage({
        type: 'success',
        message: '删除成功',
      })
      // 重新加载页面数据
      await getCiModelTree();
      // resetForm(modelFieldFormRef.value);
      // modelFieldDrawer.value = false
    } else {
      ElMessage({
        type: 'error',
        message: '删除失败',
      })
    }
  
    }).catch(() => {

    })
  }
};





// 拖拽
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
  // 内置目录不能拖拽
  return !draggingNode.data.built_in
}






</script>

<style scoped>
::v-deep .tree_rightmenu {
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
  display: inline-block;
}
.is_show_action {
  display: inline-block;
}
</style>