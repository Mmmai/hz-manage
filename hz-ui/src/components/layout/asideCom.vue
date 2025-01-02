<template>
  <el-aside
    :width="$store.state.isCollapse ? '200px' : '64px'"
    style="border: 1px"
    broder="1px"
    class="el-side-n"
  >
    <!-- style="background-color:#3576d89d" -->
    <!-- :background-color="currentColor" -->
    <el-scrollbar>
      <el-menu
        class="el-menu-vertical-demo"
        :default-active="currentMenu"
        :collapse="!$store.state.isCollapse"
        :collapse-transition="false"
      >
        <div v-show="$store.state.isCollapse" class="top-icon">
          <iconfont-svg icon="icon-yunweijiankong" size="38"></iconfont-svg>
          <span> HZ-MANAGE </span>
        </div>
        <div v-show="!$store.state.isCollapse" class="top-icon">
          <iconfont-svg icon="icon-yunweijiankong" size="38"></iconfont-svg>
        </div>
        <!-- <h3 v-show="!$store.state.isCollapse">后台</h3> -->
        <!-- <template v-for="item in menuInfo" :key="item.name">
          <template v-if="item.children.length === 0 ? true:false">
            <el-menu-item 
              :index="item.name" 
              @click="goRouter(item)"
            >
              <el-icon>
                <component :is="item.icon" />
              </el-icon>
              <span>{{ item.label }}</span>
            </el-menu-item>
          </template>
<template v-if="item.children.length === 0 ? false:true">

              <el-sub-menu index="item.name">
                <template #title>
                  <el-icon><User /></el-icon>
                  <span>{{ item.label }}</span>
                </template>
<template v-for="subItem in item.children" :key="subItem.name">
                  <el-menu-item 
                    :index="subItem.name"
                    @click="goRouter(subItem)"
                  >
                    {{ subItem.label }}
                  </el-menu-item>
                </template>
</el-sub-menu>
</template>
</template> -->
        <submenu
          :menu="menu"
          v-for="menu in menuInfo"
          :key="menu.name"
        ></submenu>
      </el-menu>
    </el-scrollbar>
  </el-aside>
</template>

<!-- <script setup> -->
<script setup>
import { computed, onMounted, getCurrentInstance, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { useStore } from "vuex";
import submenu from "./sub-menu.vue";
const currentColor = "#fff";

import useTabsStore from "@/store/tabs";
const tabsStore = useTabsStore();

const currentMenu = computed(() => tabsStore.currentMenu);
watch(
  () => currentMenu.value,
  (n) => {
    // console.log(n)
  }
);
const { proxy } = getCurrentInstance();
let store = useStore();
// const menuInfo = ref([
//   {
//     path: '/',
//     name: 'home',
//     label: '首页',
//     icon:'HomeFilled'
//   },
//   {
//     name: 'usertop',
//     label: '用户菜单',
//     icon: 'User',
//     children: [
//       {
//         path: '/user',
//         name: 'user',
//         label: '用户管理',
//         icon: 'User'
//       },
//       {
//         path: '/role',
//         name: 'role',
//         label: '角色管理',
//         icon: 'Avatar'
//       }
//     ]
//   },
//   {
//     path: '/other',
//     name: 'other',
//     label: '设置',
//     icon: 'Tools'
//   },

//   ])
const menuInfo = computed(() => {
  // 获取当前定义的所有路由信息
  return store.state.menuInfo;
});
const roleMenuInfo = computed(() => {
  return 111;
});
const test = computed(() => {
  // console.log(store.state.currentMenu)
  return store.state.currentMenu;
});
const currentMenIndex = ref("name");
// watch(test,(newv,oldv) => {
//   console.log(newv,oldv)
// })
</script>

<style scoped>
.el-menu {
  /* border-right: 1px; */
  color: var(--el-text-color-regular);
}

h3 {
  line-height: 40px;
  text-align: center;
  color: #fff;
}

.el-menu-vertical-demo {
}

.top-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 56px;

  > span {
    color: var(--el-text-color-regular);
  }
}

/* .el-aside {
  height: auto;
} */
/* .el-side-n {
  background-color: v-bind(currentColor);
} */
/* .el-menu-item {
  --el-menu-hover-bg-color: var(--el-color-primary-light-3);
  --el-menu-text-color: var(--el-text-color-regular);
  --el-menu-active-color: #fff
  
}


.el-menu-item.is-active {
  color: #fff;
  background-color: var(--el-color-primary-light-3);
} */
</style>