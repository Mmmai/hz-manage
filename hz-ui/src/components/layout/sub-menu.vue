<template>
  <el-sub-menu
    :index="pvar.menu.name"
    v-if="pvar.menu.children.length === 0 ? false : true"
  >
    <template #title>
      <!-- <el-icon>
        <component :is="pvar.menu.icon" />
      </el-icon> -->
      <el-icon>
        <!-- <Icon :icon="pvar.menu.icon"></Icon> -->
        <iconifyOffline :icon="pvar.menu.icon" />
      </el-icon>
      <!-- <span>{{ pvar.menu.icon }}</span> -->
      <span>{{ pvar.menu.label }}</span>
    </template>
    <!-- 多级嵌套菜单渲染 -->
    <sub-menu
      :menu="menuItem"
      v-for="menuItem in pvar.menu.children"
      :key="menuItem.name"
    ></sub-menu>
  </el-sub-menu>
  <el-menu-item :index="pvar.menu.name" v-else @click="goRouter(pvar.menu)">
    <el-icon>
      <!-- <Icon :icon="pvar.menu.icon"></Icon> -->
      <iconifyOffline :icon="pvar.menu.icon" />
    </el-icon>

    <template #title>{{ pvar.menu.label }}</template>
  </el-menu-item>
</template>
<script setup>
import { Icon } from "@iconify/vue";

import { getCurrentInstance } from "vue";
import { useRouter } from "vue-router";
// import {useStore} from 'vuex'
const { proxy } = getCurrentInstance();
// let store = useStore()
const router = useRouter();
const goRouter = (item) => {
  // 路由跳转
  if (item.meta.is_iframe) {
    router.push({
      name: item.name,
      query: { url: item.meta.iframePath },
    });
  } else {
    router.push({
      name: item.name,
    });
  }

  // store更新
  // store.commit("selectMenu",item)
};
const pvar = defineProps({
  menu: {
    type: Object,
  },
});
</script>
<style>
/* .el-sub-menu__title {
  color: var(--el-text-color-regular) !important;
} */
/* .el-scrollbar {
  .el-scrollbar__bar.is-horizontal .el-scrollbar__thumb {
    opacity: 1; 
    height: 2px; 
    border-radius: 2px; 
    background-color: rgba(136, 219, 255, 1); 
    box-shadow: 0 0 6px rgba(0, 0, 0, 0.15); 
  }
  .el-scrollbar__bar.is-vertical .el-scrollbar__thumb {
    opacity: 1;
    width: 2px; 
    border-radius: 2px;
    background-color: rgba(136, 219, 255, 1);
    box-shadow: 0 0 6px rgba(0, 0, 0, 0.15);
  }

} */
:root {
  --menu-text-color: #ffffff;
}

.el-menu {
  /* border-right: 1px; */
  /* color: var(--el-text-color-regular); */
  color: var(--menu-text-color) !important;
  background-color: #001529 !important;
}

/* 第一层菜单项（直接子菜单） */
.el-menu > .el-sub-menu > .el-sub-menu__title {
  background-color: #001529 !important;
}

/* 第二层及以下菜单项 */
.el-menu .el-sub-menu .el-sub-menu .el-sub-menu__title {
  background-color: #0f2438 !important;
}

/* 第一层普通菜单项 */
.el-menu > .el-menu-item {
  background-color: #001529 !important;
}

/* 第二层及以下普通菜单项 */
.el-menu .el-sub-menu .el-menu-item {
  background-color: #0f2438 !important;
}

/* 菜单项hover效果 */
.el-menu .el-menu-item:hover {
  background-color: var(--el-color-primary) !important;
  color: var(--menu-text-color) !important;
}

/* 子菜单标题hover效果 */
.el-menu .el-sub-menu__title:hover {
  background-color: var(--el-color-primary) !important;
  color: var(--menu-text-color) !important;
}

/* 激活的菜单项 */
.el-menu .el-menu-item.is-active {
  color: var(--menu-text-color) !important;
  background-color: var(--el-menu-active-color) !important;
}

/* 普通菜单项字体颜色 */
.el-menu .el-menu-item {
  color: var(--menu-text-color) !important;
}

/* 子菜单字体颜色 */
.el-menu .el-sub-menu {
  color: var(--menu-text-color) !important;
}

/* 子菜单标题字体颜色 */
.el-menu .el-sub-menu__title {
  color: var(--menu-text-color) !important;
}
</style>