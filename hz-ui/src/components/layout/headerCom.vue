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
              <el-dropdown-item
                v-for="(theme, index) in themeColors"
                :key="index"
                :command="theme.color"
                >{{ theme.themeName }}</el-dropdown-item
              >
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
import useTabsStore from "@/store/tabs";
import { useElementPlusTheme } from "use-element-plus-theme";

const layoutThemeColor = useStorage("layout-theme-color", "#409eff"); // 默认主题色
const { changeTheme } = useElementPlusTheme(layoutThemeColor.value); // 初始化主题色
const tabsStore = useTabsStore();
const currentMenuLabel = computed(() => {
  return tabsStore.currentTitle;
});
const currentBreadcrumb = computed(() => {
  return tabsStore.currentBreadcrumb;
});
import { useDark, useToggle, useStorage } from "@vueuse/core";
const isDark = useDark();
const toggleDark = useToggle(isDark);

const themeColors = [
  { color: "#409eff", themeName: "默认" },
  { color: "#749bc7", themeName: "道奇蓝" },
  { color: "#722ed1", themeName: "深紫罗兰色" },
  { color: "#eb2f96", themeName: "深粉色" },
  { color: "#f5222d", themeName: "猩红色" },
  { color: "#fa541c", themeName: "橙红色" },
  { color: "#13c2c2", themeName: "绿宝石" },
  { color: "#52c41a", themeName: "酸橙绿" },
];

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

const handleThemeChange = (theme) => {
  console.log("切换主题:", theme);
  layoutThemeColor.value = theme;
  changeTheme(theme);
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