<template>
  <div class="tabs-box">
    <div class="tabs-menu">
      <el-tabs
        v-model="nowTab"
        type="card"
        @tab-click="tabClick"
        @tab-remove="tabRemove"
      >
        <el-tab-pane
          v-for="(item, index) in tabsMenuList"
          :key="item.name"
          :label="item.title"
          :name="item.path"
          :closable="item.name !== 'home'"
        >
        </el-tab-pane>
      </el-tabs>
      <el-dropdown trigger="click" placement="bottom-start">
        <div class="more-button">
          <el-icon :size="20"><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="refresh">
              <el-icon><Refresh /></el-icon>刷新
            </el-dropdown-item>
            <el-dropdown-item divided @click="closeCurrentTab">
              <el-icon><Remove /></el-icon>关闭当前
            </el-dropdown-item>
            <el-dropdown-item
              @click="tabsStore.closeTabsOnSide(route.fullPath, 'left')"
            >
              <el-icon><DArrowLeft /></el-icon>关闭左侧
            </el-dropdown-item>
            <el-dropdown-item
              @click="tabsStore.closeTabsOnSide(route.fullPath, 'right')"
            >
              <el-icon><DArrowRight /></el-icon>关闭右侧
            </el-dropdown-item>
            <el-dropdown-item
              divided
              @click="tabsStore.closeMultipleTab(route.fullPath)"
            >
              <el-icon><CircleClose /></el-icon>关闭其它
            </el-dropdown-item>
            <el-dropdown-item @click="closeAllTab">
              <el-icon><FolderDelete /></el-icon>关闭所有
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>
<script lang="ts" setup>
import {
  ref,
  computed,
  getCurrentInstance,
  onMounted,
  watch,
  inject,
} from "vue";
import { ElTree } from "element-plus";
import {
  ContextMenu,
  ContextMenuGroup,
  ContextMenuSeparator,
  ContextMenuItem,
} from "@imengyu/vue3-context-menu";

import type Node from "element-plus/es/components/tree/src/model/node";
const { proxy } = getCurrentInstance();
import { useRoute, useRouter } from "vue-router";
import Sortable from "sortablejs";
const route = useRoute();
const router = useRouter();
const nowTab = ref(route.fullPath);

import useTabsStore from "@/store/tabs";
import { ArrowDown, Refresh } from "@element-plus/icons-vue";
import { nextTick } from "vue";
import { useKeepAliveStore } from "@/store/keepAlive";
const keepAliveStore = useKeepAliveStore();
const tabsStore = useTabsStore();
// console.log(route)
const tabsMenuList = computed(() => tabsStore.tabsMenuList);
const tabsMenuDict = computed(() => tabsStore.tabsMenuDict);
onMounted(() => {
  tabsDrop();
  initTabs();
});
watch(
  () => route.fullPath,
  () => {
    // if (route.meta.isFull) return;
    nowTab.value = route.path;
    // console.log(nowTab.value)

    const tabsParams = {
      icon: route.meta.icon as string,
      title: route.meta.title as string,
      path: route.path,
      name: route.name as string,
      fullPath: route.fullPath,
      isKeepAlive: route.meta.isKeepAlive,
      //   close: !route.meta.isAffix,
      //   isKeepAlive: route.meta.isKeepAlive as boolean
    };
    if (route.meta.isInfo) {
      if (route.path.includes("logFlowMission")) {
        tabsParams.title = route.meta.title + "-详情";
      } else {
        tabsParams.title = route.meta.title + "-" + route.query.verbose_name;
      }
    }
    tabsStore.addTabs(tabsParams);
    // 更新当前面包屑
    tabsStore.updateCurrentTitle(tabsParams);
  },
  { immediate: true }
);
const tabsDrop = () => {
  Sortable.create(document.querySelector(".el-tabs__nav") as HTMLElement, {
    draggable: ".el-tabs__item",
    animation: 300,
    onEnd({ newIndex, oldIndex }) {
      const tabsList = [...tabsStore.tabsMenuList];
      const currRow = tabsList.splice(oldIndex as number, 1)[0];
      tabsList.splice(newIndex as number, 0, currRow);
      tabsStore.setTabs(tabsList);
    },
  });
};
const initTabs = () => {
  router.getRoutes().forEach((item) => {
    // if (item.meta.isAffix && !item.meta.isHide && !item.meta.isFull) {
    if (item.name == "home") {
      const tabsParams = {
        icon: item.meta.icon,
        title: item.meta.title,
        path: item.path,
        name: item.name,
        fullPath: route.fullPath,

        // close: !item.meta.isAffix,
        // isKeepAlive: item.meta.isKeepAlive
      };
      tabsStore.addTabs(tabsParams);
    }
  });
};

// Tab Click
const tabClick = (tabItem: TabsPaneContext) => {
  // const fullPath = tabItem.props.name as string;
  //   console.log(tabItem)
  router.push(tabsMenuDict.value[tabItem.props.name].fullPath);
};

// Remove Tab
const tabRemove = (fullPath: TabPaneName) => {
  tabsStore.removeTabs(fullPath as string, fullPath == route.path);
};

// 右键菜单
const contextMenuX = ref(0);
const contextMenuY = ref(0);
const showContextMenu = ref(false);
//For component
const optionsComponent = ref({
  zIndex: 3,
  minWidth: 80,
  x: 0,
  y: 0,
});
// 右键显示
const handleContextMenu = (index, event) => {
  showContextMenu.value = true;
  optionsComponent.value.x = event.clientX;
  optionsComponent.value.y = event.clientY;
};
const closeCurrentTab = () => {
  tabsStore.removeTabs(nowTab.value, true);
};

const closeOtherTabs = () => {
  const tabsList = [...tabsStore.tabsMenuList];
  tabsStore.setTabs(
    tabsList.filter((tab) => tab.path === nowTab.value || tab.path === "/home")
  );
  showContextMenu.value = false;
};
const closeAllTab = () => {
  tabsStore.closeMultipleTab();
  router.push("/home");
};
// 刷新
// 刷新当前页
const refreshCurrentPage: Function = inject("refresh") as Function;
const refresh = () => {
  setTimeout(() => {
    route.meta.isKeepAlive &&
      keepAliveStore.removeKeepAliveName(route.fullPath as string);
    refreshCurrentPage(false);
    nextTick(() => {
      route.meta.isKeepAlive &&
        keepAliveStore.addKeepAliveName(route.fullPath as string);
      refreshCurrentPage(true);
    });
  }, 0);
};
</script>

<style scoped lang="scss">
.demo-tabs > .el-tabs__content {
  padding: 32px;
  color: #6b778c;
  font-size: 32px;
  font-weight: 600;
}

:deep {
  .el-tabs__header {
    margin: 0;
  }
}
@import "./tabs.scss";
</style>
