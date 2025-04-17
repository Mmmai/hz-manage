<template>
  <div class="common-layout">
    <el-container>
      <el-aside width="200px" style="height: 100%;">
        <!-- <el-tree
    style="max-width: 200px"
    :allow-drop="allowDrop"
    :allow-drag="allowDrag"
    :data="data"
    draggable
    default-expand-all
    node-key="id"
    @node-drag-start="handleDragStart"
    @node-drag-enter="handleDragEnter"
    @node-drag-leave="handleDragLeave"
    @node-drag-over="handleDragOver"
    @node-drag-end="handleDragEnd"
    @node-drop="handleDrop"
  /> -->11
      </el-aside>
      <el-container>
        <el-main>
          <el-button @click="test">111</el-button>
          
        </el-main>
      </el-container>
    </el-container>
  </div>

  <el-drawer v-model="drawer2" direction="rtl" size="30%">
    <template #header >
      <h4>列表显示属性配置</h4>
    </template>
    <template #default>
      <div style="display: flex;">
        <div style="width: 50%;">
          <!-- <el-menu
        default-active="2"
        class="el-menu-vertical-demo"
        @open="handleOpen"
        @close="handleClose"
      >
        <el-menu-item :index="index" v-for="data,index in hasNoConfigFieldList" :key="index">
          <span>{{ data.verbose_name}}</span>
          <el-icon><icon-menu /></el-icon>

        </el-menu-item>
      
      </el-menu> -->
      
          <!-- <p v-for="data,index in hasNoConfigFieldList" :key="index">{{ data.verbose_name }}</p> -->

        </div>
        <div style="width: 50%;">
          <h4>已选属性</h4>
        </div>
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

<script lang="ts" setup>
import * as ElIcons from '@element-plus/icons-vue'
import type Node from 'element-plus/es/components/tree/src/model/node'
import type { DragEvents } from 'element-plus/es/components/tree/src/model/useDragNode'
import type {
  AllowDropType,
  NodeDropType,
} from 'element-plus/es/components/tree/src/tree.type'
import {ref} from 'vue'
const drawer2 = ref(false)
const test = ()=>{
  drawer2.value = true
}
// const handleDragStart = (node: Node, ev: DragEvents) => {
//   console.log('drag start', node)
// }
// const handleDragEnter = (
//   draggingNode: Node,
//   dropNode: Node,
//   ev: DragEvents
// ) => {
//   console.log('tree drag enter:', dropNode.label)
// }
// const handleDragLeave = (
//   draggingNode: Node,
//   dropNode: Node,
//   ev: DragEvents
// ) => {
//   console.log('tree drag leave:', dropNode.label)
// }
// const handleDragOver = (draggingNode: Node, dropNode: Node, ev: DragEvents) => {
//   console.log('tree drag over:', dropNode.label)
// }
// const handleDragEnd = (
//   draggingNode: Node,
//   dropNode: Node,
//   dropType: NodeDropType,
//   ev: DragEvents
// ) => {
//   // console.log('tree drag end:', dropNode && dropNode.label, dropType)
// }
// const handleDrop = (
//   draggingNode: Node,
//   dropNode: Node,
//   dropType: NodeDropType,
//   ev: DragEvents
// ) => {
//   console.log('tree drop:', dropNode.label, dropType)
// }
// const allowDrop = (draggingNode: Node, dropNode: Node, type: AllowDropType) => {
//   if (dropNode.data.label === 'Level two 3-1') {
//     return type !== 'inner'
//   } else {
//     return true
//   }
// }
// const allowDrag = (draggingNode: Node) => {
//   return !draggingNode.data.label.includes('Level three 3-1-1')
// }

// const data = [
//   {
//     label: 'Level one 1',
//     children: [
//       {
//         label: 'Level two 1-1',
//         children: [
//           {
//             label: 'Level three 1-1-1',
//           },
//         ],
//       },
//     ],
//   },
//   {
//     label: 'Level one 2',
//     children: [
//       {
//         label: 'Level two 2-1',
//         children: [
//           {
//             label: 'Level three 2-1-1',
//           },
//         ],
//       },
//       {
//         label: 'Level two 2-2',
//         children: [
//           {
//             label: 'Level three 2-2-1',
//           },
//         ],
//       },
//     ],
//   },
// ]

// 穿梭框排序
import { Rank } from '@element-plus/icons-vue'

// const allModelField = ref([
//   { key: 0, label: '11' },
//   { key: 1, label: '22' },
//   { key: 2, label: '33' },
//   { key: 3, label: '44' },
//   { key: 4, label: '55' },
//   { key: 5, label: '66' }
// ])


import { ref, reactive, watch, getCurrentInstance, nextTick, onActivated,computed, onMounted } from 'vue'
import { da } from 'element-plus/es/locale/index.mjs';
const { proxy } = getCurrentInstance();

const modelInfo = ref({})
const allModelField = computed(()=>{
  let tempList = []
  modelInfo.value.field_groups.forEach(item=>{
    item.fields.forEach(field => {
      tempList.push(field)
    });
  })
  return tempList
})

const hasConfigField = ref([])

const hasNoConfigFieldList = computed(()=>{
  return allModelField.value.filter(item => {return hasConfigField.value.indexOf(item) == -1})
})


const getModelField = async () => {
  let res = await proxy.$api.getCiModel({} , 'f22c892a-7fbf-459b-b0c5-096726402176/with_fields')
  console.log(res)
  modelInfo.value = res.data
  console.log(hasNoConfigFieldList.value)
  // console.log()
}

onMounted(async() => {
  console.log('field mount')
  await getModelField();
  // getModelField()
})

</script>
<style scoped lang="less">
::v-deep(.el-transfer-panel__item).el-checkbox {
  margin-right: 10px;

  .transferLable {
    display: flex;
    justify-content: space-between !important;
  }
}

.el-transfer ::v-deep(.el-transfer-panel):first-child .sort {
  display: none;
}

.moving {
  border-bottom: 1px solid #409eff;
}

.movingTop {
  border-top: 1px solid #409eff;
}

.movingBottom {
  border-bottom: 1px solid #409eff;
}
</style>