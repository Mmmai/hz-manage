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
          <!-- <iconfont-svg icon="icon-yunweijiankong" size="38"></iconfont-svg> -->
          <!-- <Icon icon="devicon:godot" width="32" height="32" style="margin-right: 5px;" /> -->
          <iconifyOffline icon="devicon:godot" width="32" height="32" />

          <!-- <h5>HZ-MANAGE</h5> -->
          <!-- <h4 style="margin-left: 10px">智维</h4> -->
          <el-text size="large" style="margin-left: 5px" tag="b">智维 </el-text>
          <el-text size="small" style="margin-left: 5px" tag="sub">{{
            appVersion
          }}</el-text>
        </div>
        <div v-show="!$store.state.isCollapse" class="top-icon">
          <!-- <iconfont-svg icon="icon-yunweijiankong" size="38"></iconfont-svg> -->
          <!-- <Icon icon="devicon:godot" /> -->
          <iconifyOffline icon="devicon:godot" />
        </div>
        <submenu
          :menu="menu"
          v-for="menu in showMenu"
          :key="menu.name"
        ></submenu>
      </el-menu>
    </el-scrollbar>
  </el-aside>
</template>

<!-- <script setup> -->
<script setup>
import { Icon } from "@iconify/vue/dist/iconify.js";
import { computed, onMounted, getCurrentInstance, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { useStore } from "vuex";
import submenu from "./sub-menu.vue";
const currentColor = "#fff";
import { storeToRefs } from "pinia";

import useTabsStore from "@/store/tabs";
const tabsStore = useTabsStore();
const APP_VERSION = import.meta.env.APP_VERSION;
const currentMenu = computed(() => tabsStore.currentMenu);
import useConfigStore from "@/store/config";
const configStore = useConfigStore();
const { appVersion } = storeToRefs(configStore);
watch(
  () => currentMenu.value,
  (n) => {
    // console.log(n)
  }
);
const { proxy } = getCurrentInstance();
let store = useStore();
const menuInfo = computed(() => {
  // 获取当前定义的所有路由信息
  return store.state.menuInfo;
});

const dealMenu = (data) => {
  let tmpArr = [];

  for (let item of data) {
    if (!item.status) continue;
    let tmpObj = {
      name: item.name,
      label: item.label,
      icon: item.icon,
      is_iframe: item.is_iframe,
      meta: item.meta,
      children: [],
    };
    if (item.children && item.children.length > 0) {
      tmpObj.children = dealMenu(item.children);
    }
    tmpArr.push(tmpObj);
  }
  return tmpArr;
};

// 禁用status为false的
const showMenu = computed(() => {
  return dealMenu(menuInfo.value);
});
watch(
  () => showMenu.value,
  (n) => {
    console.log(n);
  }
);
console.log(showMenu.value);
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
/* .el-sub-menu__title {
  color: #fff !important;
} */
.el-menu {
  /* border-right: 1px; */
  /* color: var(--el-text-color-regular); */
  /* background-color: var(--el-color-primary-light-5) !important; */
  background-color: var(--color-background, #ffffff) !important;
}
.el-aside {
  /* background-color: var(--el-color-primary-light-5) !important; */
  background-color: var(--color-background, #ffffff) !important;
  border-right: solid 1px var(--el-border-color, #dcdfe6) !important;
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

<style>
/* 确保子菜单也能正确应用主题背景色 */
.el-menu--vertical,
.el-menu--popup,
.el-sub-menu .el-menu {
  background-color: var(--color-background, #ffffff) !important;
}

.el-menu--vertical .el-menu-item,
.el-menu--popup .el-menu-item,
.el-sub-menu .el-menu-item {
  background-color: var(--color-background, #ffffff) !important;
}

.el-menu--vertical .el-menu-item:hover,
.el-menu--popup .el-menu-item:hover,
.el-sub-menu .el-menu-item:hover {
  background-color: var(--el-fill-color-light, #f5f7fa) !important;
}

.el-menu--vertical .el-sub-menu__title,
.el-menu--popup .el-sub-menu__title,
.el-sub-menu .el-sub-menu__title {
  background-color: var(--color-background, #ffffff) !important;
}

.el-menu--vertical .el-sub-menu__title:hover,
.el-menu--popup .el-sub-menu__title:hover,
.el-sub-menu .el-sub-menu__title:hover {
  background-color: var(--el-fill-color-light, #f5f7fa) !important;
}

/* 暗黑模式下的特殊处理 */
html.dark .el-menu--vertical,
html.dark .el-menu--popup,
html.dark .el-sub-menu .el-menu,
html.dark .el-menu--vertical .el-menu-item,
html.dark .el-menu--popup .el-menu-item,
html.dark .el-sub-menu .el-menu-item,
html.dark .el-menu--vertical .el-sub-menu__title,
html.dark .el-menu--popup .el-sub-menu__title,
html.dark .el-sub-menu .el-sub-menu__title,
html.dark .el-menu,
html.dark .el-aside {
  background-color: var(--color-background, #181818) !important;
}

/* 自定义主题处理 */
html.theme-blue .el-menu--vertical,
html.theme-blue .el-menu--popup,
html.theme-blue .el-sub-menu .el-menu,
html.theme-blue .el-menu--vertical .el-menu-item,
html.theme-blue .el-menu--popup .el-menu-item,
html.theme-blue .el-sub-menu .el-menu-item,
html.theme-blue .el-menu--vertical .el-sub-menu__title,
html.theme-blue .el-menu--popup .el-sub-menu__title,
html.theme-blue .el-sub-menu .el-sub-menu__title,
html.theme-blue .el-menu,
html.theme-blue .el-aside {
  background-color: var(--color-background, #f0f8ff) !important;
}

html.theme-green .el-menu--vertical,
html.theme-green .el-menu--popup,
html.theme-green .el-sub-menu .el-menu,
html.theme-green .el-menu--vertical .el-menu-item,
html.theme-green .el-menu--popup .el-menu-item,
html.theme-green .el-sub-menu .el-menu-item,
html.theme-green .el-menu--vertical .el-sub-menu__title,
html.theme-green .el-menu--popup .el-sub-menu__title,
html.theme-green .el-sub-menu .el-sub-menu__title,
html.theme-green .el-menu,
html.theme-green .el-aside {
  background-color: var(--color-background, #f0fff8) !important;
}

html.theme-purple .el-menu--vertical,
html.theme-purple .el-menu--popup,
html.theme-purple .el-sub-menu .el-menu,
html.theme-purple .el-menu--vertical .el-menu-item,
html.theme-purple .el-menu--popup .el-menu-item,
html.theme-purple .el-sub-menu .el-menu-item,
html.theme-purple .el-menu--vertical .el-sub-menu__title,
html.theme-purple .el-menu--popup .el-sub-menu__title,
html.theme-purple .el-sub-menu .el-sub-menu__title,
html.theme-purple .el-menu,
html.theme-purple .el-aside {
  background-color: var(--color-background, #fcf0ff) !important;
}

html.theme-pink .el-menu--vertical,
html.theme-pink .el-menu--popup,
html.theme-pink .el-sub-menu .el-menu,
html.theme-pink .el-menu--vertical .el-menu-item,
html.theme-pink .el-menu--popup .el-menu-item,
html.theme-pink .el-sub-menu .el-menu-item,
html.theme-pink .el-menu--vertical .el-sub-menu__title,
html.theme-pink .el-menu--popup .el-sub-menu__title,
html.theme-pink .el-sub-menu .el-sub-menu__title,
html.theme-pink .el-menu,
html.theme-pink .el-aside {
  background-color: var(--color-background, #fff0f5) !important;
}

html.theme-orange .el-menu--vertical,
html.theme-orange .el-menu--popup,
html.theme-orange .el-sub-menu .el-menu,
html.theme-orange .el-menu--vertical .el-menu-item,
html.theme-orange .el-menu--popup .el-menu-item,
html.theme-orange .el-sub-menu .el-menu-item,
html.theme-orange .el-menu--vertical .el-sub-menu__title,
html.theme-orange .el-menu--popup .el-sub-menu__title,
html.theme-orange .el-sub-menu .el-sub-menu__title,
html.theme-orange .el-menu,
html.theme-orange .el-aside {
  background-color: var(--color-background, #fff8f0) !important;
}
</style>