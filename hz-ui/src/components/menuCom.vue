<template>
  <div style="width: 100%;">
    <h3>菜单授权->{{ row.rowInfo.role }}</h3>
    <el-tree
      ref="menuTreeRef"
      :data="dataSource"
      show-checkbox
      node-key="id"
      default-expand-all
      :expand-on-click-node="false"
    >
      <template #default="{ node, data }">
        <span class="custom-tree-node">
          <span>{{ node.label }}</span>
          <!-- <span>
            <a @click="append(data)"> Append </a>
            <a style="margin-left: 8px" @click="remove(node, data)"> Delete </a>
          </span> -->
        </span>
      </template>
    </el-tree>
    <!-- <el-button @click="getCheckedNodes">get by node</el-button> -->
    <el-button @click="getCheckedKeys">更新</el-button>
    <!-- <el-button @click="setCheckedKeys">set by key</el-button> -->

  </div>


</template>
<script lang="ts" setup>

import { ref,computed,getCurrentInstance,onMounted,watch } from 'vue'
import { ElTree } from 'element-plus'

import type Node from 'element-plus/es/components/tree/src/model/node'
const {proxy} = getCurrentInstance();
const menuTreeRef = ref<InstanceType<typeof ElTree>>()
// 接收父组件的变量
const row = defineProps({
  test:{
    type: String,
  },
  rowInfo:{
    type: Object
  }
})
// 接收事件
const emit = defineEmits(["getdata"])
interface Tree {
  id: number
  label: string
  children?: Tree[]
}
const dataSource = ref([])
const getMenuListFunc = (async() => {
  let res = await proxy.$api.getMenuList()
  console.log(res)
  dataSource.value = res.data.result
})
// 监听
watch(row,(newv,oldv) => {
    setCheckedKeys(newv.rowInfo.menu)
  })

onMounted(()=>{
  getMenuListFunc();
  // setCheckedKeys(row.rowInfo.menu)
})
let id = 1000

const append = (data: Tree) => {
  const newChild = { id: id++, label: 'testtest', children: [] }
  if (!data.children) {
    data.children = []
  }
  data.children.push(newChild)
  dataSource.value = [...dataSource.value]
}

const remove = (node: Node, data: Tree) => {
  const parent = node.parent
  const children: Tree[] = parent.data.children || parent.data
  const index = children.findIndex((d) => d.id === data.id)
  children.splice(index, 1)
  dataSource.value = [...dataSource.value]
}
const getCheckedNodes = () => {
  console.log(menuTreeRef.value!.getCheckedNodes(false, false))
}
const getCheckedKeys = async() => {
  let newMenuList = menuTreeRef.value!.getCheckedKeys(false)
  // 更新对应关系
  let res = await proxy.$api.roleupdate({id:row.rowInfo.id,menu:newMenuList})
  // 重新获取数据
  emit("getdata")

}
const setCheckedKeys = (val) => {
  menuTreeRef.value!.setCheckedKeys(val, false)
}

</script>

<style>
.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
}
</style>
