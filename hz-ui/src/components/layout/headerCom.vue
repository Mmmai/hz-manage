<template>
  <el-row style="width: 100%" justify="space-between">
    <el-col :span="12" style="display: flex; align-items: center">
      <!-- <div class="l-content"> -->
      <el-button @click="changeCollapse" size="small" class="collapseClass">
        <!-- <Menu /> -->
        <el-icon v-if="collapse">
          <Fold />
        </el-icon>
        <el-icon v-else>
          <Expand />
        </el-icon>
      </el-button>
      <!-- 面包屑 -->
      <el-breadcrumb :separator-icon="ArrowRight">
        <!-- 可以跳转 -->
        <!-- <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item 
        :to="currentMenu.path"
        v-if="currentMenu"
      >
        {{ currentMenu.name }}
      </el-breadcrumb-item> -->
        <el-breadcrumb-item
          ><el-icon><HomeFilled /></el-icon>
        </el-breadcrumb-item>
        <el-breadcrumb-item v-for="(item, index) in currentBreadcrumb">
          <div class="flexJbetween gap-2">
            <el-icon>
              <iconifyOffline :icon="item.icon" />
            </el-icon>
            <span> {{ item.name }}</span>
          </div>
        </el-breadcrumb-item>
      </el-breadcrumb>
      <!-- </div> -->
      <!-- <div>
    1111
  </div> -->
    </el-col>

    <el-col :span="4">
      <div
        style="
          display: flex;
          justify-content: flex-end;
          align-items: center;
          gap: 10px;
        "
      >
        <el-link type="primary" href="/docs/" target="_blank">指南</el-link>

        <!-- 主题选择器 -->
        <el-dropdown @command="handleThemeChange">
          <el-button circle size="small">
            <el-icon :size="16">
              <Brush />
            </el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="light">明亮</el-dropdown-item>
              <el-dropdown-item command="dark">暗黑</el-dropdown-item>
              <el-dropdown-item divided>自定义主题</el-dropdown-item>
              <el-dropdown-item command="blue">海洋蓝</el-dropdown-item>
              <el-dropdown-item command="green">清新绿</el-dropdown-item>
              <el-dropdown-item command="purple">优雅紫</el-dropdown-item>
              <el-dropdown-item command="pink">浪漫粉</el-dropdown-item>
              <el-dropdown-item command="orange">活力橙</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <el-switch
          v-model="isDark"
          :active-icon="Moon"
          :inactive-icon="Sunny"
          inline-prompt
          @change="toggleDark"
        />
        <el-dropdown trigger="click">
          <span class="el-dropdown-link">
            <el-icon>
              <UserFilled />
            </el-icon>
            {{ currenUsername }}
            <el-icon class="el-icon--right">
              <arrow-down />
            </el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <!-- <el-dropdown-item>个人中心</el-dropdown-item> -->
              <el-dropdown-item @click="handleLogout">退出</el-dropdown-item>
              <!-- <el-dropdown-item>Action 3</el-dropdown-item> -->
              <!-- <el-dropdown-item disabled>Action 4</el-dropdown-item> -->
              <!-- <el-dropdown-item divided>Action 5</el-dropdown-item> -->
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-col>
  </el-row>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { useStore } from "vuex";
import { ArrowRight, Brush } from "@element-plus/icons-vue";
import router from "@/router";
import { ElMessageBox } from "element-plus";
import { Sunny, Moon } from "@element-plus/icons-vue";
import { useDark, useToggle } from "@vueuse/core";
import useTabsStore from "@/store/tabs";

const tabsStore = useTabsStore();
const currentMenuLabel = computed(() => {
  return tabsStore.currentTitle;
});
const currentBreadcrumb = computed(() => {
  return tabsStore.currentBreadcrumb;
});
const isDark = useDark();

const toggleDark = useToggle(isDark);
let store = useStore();
const collapse = ref(true);
const changeCollapse = () => {
  //调用vuex中的
  store.commit("changeIsCollapse");
  collapse.value = store.state.isCollapse;
};
// const currentMenuLabel = computed(() => {
//   // console.log(store.state.currentMenu)
//   return store.state.currentMenu
// })
// const currentMenu = ref('')

const currenUsername = computed(() => {
  return store.state.username;
});
// console.log('所有路由记录:', router.getRoutes())

// console.log(currentMenu)
const handleLogout = (done) => {
  ElMessageBox.confirm("是否退出?")
    .then(() => {
      store.commit("updateDynamicCreateRoute", false);
      // tabsStore.setTabs([]);
      tabsStore.setTabs([]);

      localStorage.clear();
      // 清楚tab打开的菜单列表
      router.push({ name: "login" });
      // window.location.reload()
    })
    .catch((error) => {
      console.log(123);
      // catch error
      console.error("发生错误: " + error);
    });
};

// 主题切换处理
const handleThemeChange = (theme) => {
  const html = document.documentElement;

  // 清除所有自定义主题类
  html.classList.remove(
    "theme-blue",
    "theme-green",
    "theme-purple",
    "theme-pink",
    "theme-orange"
  );

  switch (theme) {
    case "light":
      isDark.value = false;
      resetThemeVariables();
      applyThemeToElements("light");
      break;
    case "dark":
      isDark.value = true;
      resetThemeVariables();
      applyThemeToElements("dark");
      break;
    default:
      isDark.value = false;
      html.classList.add(`theme-${theme}`);
      setCustomThemeCssVariables(theme);
      applyThemeToElements(theme);
      break;
  }
};

// 重置主题变量为默认值
const resetThemeVariables = () => {
  const root = document.documentElement;
  root.style.removeProperty("--el-color-primary");
  root.style.removeProperty("--el-color-primary-light-3");
  root.style.removeProperty("--el-color-primary-light-5");
  root.style.removeProperty("--el-color-primary-light-7");
  root.style.removeProperty("--el-color-primary-light-8");
  root.style.removeProperty("--el-color-primary-light-9");
  root.style.removeProperty("--el-color-primary-dark-2");
  root.style.removeProperty("--color-background");
  root.style.removeProperty("--color-background-soft");
  root.style.removeProperty("--color-background-mute");
  root.style.removeProperty("--el-bg-color");
  root.style.removeProperty("--el-bg-color-page");
  root.style.removeProperty("--el-fill-color");
  root.style.removeProperty("--el-fill-color-light");
  root.style.removeProperty("--el-fill-color-lighter");
  root.style.removeProperty("--el-fill-color-extra-light");
  root.style.removeProperty("--el-fill-color-dark");
  root.style.removeProperty("--el-fill-color-darker");
  root.style.removeProperty("--el-fill-color-blank");
};

// 设置自定义主题CSS变量
const setCustomThemeCssVariables = (theme) => {
  const root = document.documentElement;

  // 清除之前的自定义变量
  resetThemeVariables();

  // 根据主题设置新的变量
  switch (theme) {
    case "blue":
      root.style.setProperty("--el-color-primary", "#1a73e8");
      root.style.setProperty("--el-color-primary-light-3", "#4a90e2");
      root.style.setProperty("--el-color-primary-light-5", "#5d9de8");
      root.style.setProperty("--el-color-primary-light-7", "#8abcf0");
      root.style.setProperty("--el-color-primary-light-8", "#a3ccf5");
      root.style.setProperty("--el-color-primary-light-9", "#beddf9");
      root.style.setProperty("--el-color-primary-dark-2", "#1459b3");
      root.style.setProperty("--color-background", "#f0f8ff");
      root.style.setProperty("--color-background-soft", "#e6f2ff");
      root.style.setProperty("--color-background-mute", "#d9e9ff");
      root.style.setProperty("--el-bg-color", "#f0f8ff");
      root.style.setProperty("--el-bg-color-page", "#e6f2ff");
      root.style.setProperty("--el-fill-color", "#d9e9ff");
      root.style.setProperty("--el-fill-color-light", "#e6f2ff");
      root.style.setProperty("--el-fill-color-lighter", "#f0f8ff");
      root.style.setProperty("--el-fill-color-extra-light", "#fafcff");
      root.style.setProperty("--el-fill-color-dark", "#c9d9ef");
      root.style.setProperty("--el-fill-color-darker", "#c0d0e9");
      root.style.setProperty("--el-fill-color-blank", "#ffffff");
      break;
    case "green":
      root.style.setProperty("--el-color-primary", "#00c471");
      root.style.setProperty("--el-color-primary-light-3", "#33d090");
      root.style.setProperty("--el-color-primary-light-5", "#4dd8a0");
      root.style.setProperty("--el-color-primary-light-7", "#80e3c2");
      root.style.setProperty("--el-color-primary-light-8", "#99ead2");
      root.style.setProperty("--el-color-primary-light-9", "#b3f1e2");
      root.style.setProperty("--el-color-primary-dark-2", "#009d5a");
      root.style.setProperty("--color-background", "#f0fff8");
      root.style.setProperty("--color-background-soft", "#e6fff2");
      root.style.setProperty("--color-background-mute", "#d9ffeb");
      root.style.setProperty("--el-bg-color", "#f0fff8");
      root.style.setProperty("--el-bg-color-page", "#e6fff2");
      root.style.setProperty("--el-fill-color", "#d9ffeb");
      root.style.setProperty("--el-fill-color-light", "#e6fff2");
      root.style.setProperty("--el-fill-color-lighter", "#f0fff8");
      root.style.setProperty("--el-fill-color-extra-light", "#fafcff");
      root.style.setProperty("--el-fill-color-dark", "#c9efe2");
      root.style.setProperty("--el-fill-color-darker", "#c0e9d8");
      root.style.setProperty("--el-fill-color-blank", "#ffffff");
      break;
    case "purple":
      root.style.setProperty("--el-color-primary", "#8e24aa");
      root.style.setProperty("--el-color-primary-light-3", "#a642c2");
      root.style.setProperty("--el-color-primary-light-5", "#b462ce");
      root.style.setProperty("--el-color-primary-light-7", "#ca94dd");
      root.style.setProperty("--el-color-primary-light-8", "#d7afe7");
      root.style.setProperty("--el-color-primary-light-9", "#e4caf1");
      root.style.setProperty("--el-color-primary-dark-2", "#711d88");
      root.style.setProperty("--color-background", "#fcf0ff");
      root.style.setProperty("--color-background-soft", "#f9e6ff");
      root.style.setProperty("--color-background-mute", "#f2d9ff");
      root.style.setProperty("--el-bg-color", "#fcf0ff");
      root.style.setProperty("--el-bg-color-page", "#f9e6ff");
      root.style.setProperty("--el-fill-color", "#f2d9ff");
      root.style.setProperty("--el-fill-color-light", "#f9e6ff");
      root.style.setProperty("--el-fill-color-lighter", "#fcf0ff");
      root.style.setProperty("--el-fill-color-extra-light", "#fdf8ff");
      root.style.setProperty("--el-fill-color-dark", "#e2c9ef");
      root.style.setProperty("--el-fill-color-darker", "#d8c0e9");
      root.style.setProperty("--el-fill-color-blank", "#ffffff");
      break;
    case "pink":
      root.style.setProperty("--el-color-primary", "#e91e63");
      root.style.setProperty("--el-color-primary-light-3", "#ee4c87");
      root.style.setProperty("--el-color-primary-light-5", "#f1699d");
      root.style.setProperty("--el-color-primary-light-7", "#f6a0c3");
      root.style.setProperty("--el-color-primary-light-8", "#f8b7d3");
      root.style.setProperty("--el-color-primary-light-9", "#fbdce9");
      root.style.setProperty("--el-color-primary-dark-2", "#ba184f");
      root.style.setProperty("--color-background", "#fff0f5");
      root.style.setProperty("--color-background-soft", "#ffe6f0");
      root.style.setProperty("--color-background-mute", "#ffd9eb");
      root.style.setProperty("--el-bg-color", "#fff0f5");
      root.style.setProperty("--el-bg-color-page", "#ffe6f0");
      root.style.setProperty("--el-fill-color", "#ffd9eb");
      root.style.setProperty("--el-fill-color-light", "#ffe6f0");
      root.style.setProperty("--el-fill-color-lighter", "#fff0f5");
      root.style.setProperty("--el-fill-color-extra-light", "#fff8fb");
      root.style.setProperty("--el-fill-color-dark", "#efc9d9");
      root.style.setProperty("--el-fill-color-darker", "#e9c0d0");
      root.style.setProperty("--el-fill-color-blank", "#ffffff");
      break;
    case "orange":
      root.style.setProperty("--el-color-primary", "#ff9800");
      root.style.setProperty("--el-color-primary-light-3", "#ffa726");
      root.style.setProperty("--el-color-primary-light-5", "#ffb74d");
      root.style.setProperty("--el-color-primary-light-7", "#ffcc80");
      root.style.setProperty("--el-color-primary-light-8", "#ffd599");
      root.style.setProperty("--el-color-primary-light-9", "#ffebcc");
      root.style.setProperty("--el-color-primary-dark-2", "#cc7a00");
      root.style.setProperty("--color-background", "#fff8f0");
      root.style.setProperty("--color-background-soft", "#fff2e6");
      root.style.setProperty("--color-background-mute", "#ffe9d9");
      root.style.setProperty("--el-bg-color", "#fff8f0");
      root.style.setProperty("--el-bg-color-page", "#fff2e6");
      root.style.setProperty("--el-fill-color", "#ffe9d9");
      root.style.setProperty("--el-fill-color-light", "#fff2e6");
      root.style.setProperty("--el-fill-color-lighter", "#fff8f0");
      root.style.setProperty("--el-fill-color-extra-light", "#fffcf8");
      root.style.setProperty("--el-fill-color-dark", "#efdcc9");
      root.style.setProperty("--el-fill-color-darker", "#e9d3c0");
      root.style.setProperty("--el-fill-color-blank", "#ffffff");
      break;
  }
};

// 应用主题到特定元素
const applyThemeToElements = (theme) => {
  // 获取需要改变背景色的元素
  const headerElement = document.querySelector(".el-header");
  const asideElement = document.querySelector(".el-aside");
  const footerElement = document.querySelector(".el-footer");
  const menuElement = document.querySelector(".el-menu");

  // 根据主题设置背景色
  let backgroundColor = "";
  switch (theme) {
    case "light":
      backgroundColor = "#ffffff";
      break;
    case "dark":
      backgroundColor = "#181818";
      break;
    case "blue":
      backgroundColor = "#f0f8ff";
      break;
    case "green":
      backgroundColor = "#f0fff8";
      break;
    case "purple":
      backgroundColor = "#fcf0ff";
      break;
    case "pink":
      backgroundColor = "#fff0f5";
      break;
    case "orange":
      backgroundColor = "#fff8f0";
      break;
  }

  // 应用背景色
  if (headerElement) {
    headerElement.style.backgroundColor = backgroundColor;
  }
  if (asideElement) {
    asideElement.style.backgroundColor = backgroundColor;
  }
  if (footerElement) {
    footerElement.style.backgroundColor = backgroundColor;
  }
  if (menuElement) {
    menuElement.style.backgroundColor = backgroundColor;
  }

  // 更新所有菜单相关元素的背景色
  const allMenuElements = document.querySelectorAll(
    ".el-menu, .el-menu-item, .el-sub-menu__title, .el-menu--vertical, .el-menu--popup, .el-sub-menu .el-menu"
  );
  allMenuElements.forEach((element) => {
    element.style.backgroundColor = backgroundColor;
  });

  // 更新所有Element Plus组件的背景色
  const allComponentElements = document.querySelectorAll(
    ".el-input__inner, .el-textarea__inner, .el-checkbox__inner, .el-radio__inner, " +
      ".el-select-dropdown, .el-dropdown-menu, .el-transfer-panel, .el-transfer-panel__body, " +
      ".el-transfer-panel__list, .el-tree, .el-tree-node__content, .el-table, .el-table__body, " +
      ".el-table__header, .el-pagination, .el-tabs__nav, .el-tabs__content, .el-card, " +
      ".el-collapse, .el-collapse-item__header, .el-collapse-item__content, .el-alert, " +
      ".el-message-box, .el-dialog, .el-drawer, .el-popover, .el-tooltip__popper, " +
      ".el-dropdown-menu__item, .el-cascader__dropdown, .el-cascader-menu, .el-color-dropdown, " +
      ".el-color-picker__panel, .el-date-picker, .el-date-range-picker, .el-time-panel, " +
      ".el-time-select, .el-picker-panel, .el-upload-dragger, .el-steps, .el-step__head, " +
      ".el-step__main"
  );
  allComponentElements.forEach((element) => {
    element.style.backgroundColor = backgroundColor;
  });

  // 特别处理暗黑模式下的边框颜色
  const allMenuItems = document.querySelectorAll(
    ".el-menu-item, .el-sub-menu__title"
  );
  if (theme === "dark") {
    allMenuItems.forEach((element) => {
      element.style.borderColor = "#4c4d4f";
    });
  } else {
    allMenuItems.forEach((element) => {
      element.style.borderColor = "#ebeef5";
    });
  }
};
</script>
<style scoped>
.l-content {
  display: flex;
  align-items: center;
}

.collapseClass {
  margin-right: 10px;
}

.el-dropdown {
  align-items: center;
}
</style>