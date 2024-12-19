<template>
  <div class="menu-edit">
    <div class="menu-edit-left">
      <el-card class="box-card">

        <h3>菜单树</h3>
        <el-tree
      :data="dataSource"
      draggable
      node-key="id"
      default-expand-all
      :expand-on-click-node="false"
      @node-contextmenu="rightClick"
      @node-drop="test"	
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
      </el-card>

    </div>
    <!-- 右侧视图 -->
    <div class="menu-edit-right" >
      <el-card class="box-card">
      <!-- <template #header>
        <div class="card-header">
          <span>菜单详情</span>
          <el-button class="button"  type="primary" >编辑</el-button>
        </div>
      </template> -->

      </el-card>
    </div>
  </div>
  <!-- 右键菜单 -->
  <div class="rightMenu" v-show="showRightMenu">
      <ul>
        <li @click="addMenu">
          <el-icon>
            <CirclePlus />
          </el-icon> 新建同级
        </li>
        <li @click="addSonMenu">
          <el-icon>
            <CirclePlus />
          </el-icon> 新建子级
        </li>
        <li @click="delMenu">
          <el-icon>
            <CircleClose />
          </el-icon> 删除功能
        </li>
      </ul>
  </div>

</template>
<script lang="ts" setup>

import { ref,computed,reactive,getCurrentInstance,onMounted } from 'vue'
import type Node from 'element-plus/es/components/tree/src/model/node'
const {proxy} = getCurrentInstance();
const menuInfo = reactive({
  menu_name: '',
  icon: '',
  is_menu:true,
  parentid:'',
  url:'',
  code:'',
  sort:'',
  description:''
})
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

onMounted(()=>{
  getMenuListFunc()
})
let id = 1000

// const append = (data: Tree) => {
//   const newChild = { id: id++, label: 'testtest', children: [] }
//   if (!data.children) {
//     data.children = []
//   }
//   data.children.push(newChild)
//   dataSource.value = [...dataSource.value]
// }

// const remove = (node: Node, data: Tree) => {
//   const parent = node.parent
//   const children: Tree[] = parent.data.children || parent.data
//   const index = children.findIndex((d) => d.id === data.id)
//   children.splice(index, 1)
//   dataSource.value = [...dataSource.value]
// }
// 右键
const test = (a,b,c,d) =>{
  console.log(a,b,c,d)
}
const showRightMenu = ref(false)
const rightClick = (event, data, node, json) => {
  showRightMenu.value = false
  let menu = document.querySelector('.rightMenu')
  menu.style.left = event.clientX + 'px'
  menu.style.top = event.clientY + 'px'
  showRightMenu.value = true
  document.addEventListener('click', show)
}
const show = () => {
  showRightMenu.value = false
}

</script>

<style scoped>
.box-card {
  width: 100%;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
}


.menu-edit {
  display: flex;
  justify-content: space-evenly;
}
.menu-edit-left {
  width: 20%;
  margin: 10px;
}
.menu-edit-right {
  width: 70%;
  margin: 10px;

}
.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
}

.rightMenu {
  position: fixed;
  z-index: 99999999;
  cursor: pointer;
  border: 1px solid #eee;
  box-shadow: 0 0.5em 1em 2px rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  color: #1a1a1a;
}
.rightMenu ul {
  list-style: none;
  margin: 0;
  padding: 0;
  border-radius: 6px;
}
.rightMenu ul li {
  padding: 6px 10px;
  background: #fff;
  border-bottom: 1px solid #000;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: space-around;
}
.rightMenu ul li:last-child {
  border: none;
}
.rightMenu ul li:hover {
  transition: all 1s;
  background: #92c9f6;
}
</style>
