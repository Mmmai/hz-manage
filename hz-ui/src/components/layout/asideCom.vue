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
          <el-text size="large" style="margin-left: 5px" tag="b"
            >智维
            <el-text size="small" style="margin-left: 5px" tag="sub">{{
              appVersion
            }}</el-text>
          </el-text>
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

import useTabsStore from "@/store/tabs";
const tabsStore = useTabsStore();
const appVersion = import.meta.env.APP_VERSION;
const currentMenu = computed(() => tabsStore.currentMenu);
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
}
.el-aside {
  /* background-color: var(--el-color-primary-light-5) !important; */
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