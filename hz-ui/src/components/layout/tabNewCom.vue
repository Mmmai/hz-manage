<template>
  <el-tabs v-model="nowTab" type="card" class="demo-tabs" @tab-click="tabClick" @tab-remove="tabRemove">
    <el-tab-pane v-for="item in tabsMenuList" :key="item.name" :label="item.title" :name="item.path"
      :closable="item.name !== 'home'">
      {{ item.content }}
    </el-tab-pane>
  </el-tabs>
</template>
<script lang="ts" setup>

import { ref, computed, getCurrentInstance, onMounted, watch } from 'vue'
import { ElTree } from 'element-plus'

import type Node from 'element-plus/es/components/tree/src/model/node'
const { proxy } = getCurrentInstance();
import { useRoute, useRouter } from "vue-router";
import Sortable from "sortablejs";
const route = useRoute();
const router = useRouter();
const nowTab = ref(route.fullPath)

import useTabsStore from '@/store/tabs'

const tabsStore = useTabsStore()
// console.log(route)
const tabsMenuList = computed(() => tabsStore.tabsMenuList);
const tabsMenuDict = computed(() => tabsStore.tabsMenuDict)
onMounted(() => {
  tabsDrop()
  initTabs()
})
watch(
  () => route.fullPath,
  () => {
    // if (route.meta.isFull) return;
    nowTab.value = route.path
    // console.log(nowTab.value)

    const tabsParams = {
      icon: route.meta.icon as string,
      title: route.meta.title as string,
      path: route.path,
      name: route.name as string,
      fullPath: route.fullPath
      //   close: !route.meta.isAffix,
      //   isKeepAlive: route.meta.isKeepAlive as boolean
    };
    if (route.meta.isInfo) {
      if (route.path.includes('logFlowMission')) {
        tabsParams.title = route.meta.title + '-详情'
      } else {
        tabsParams.title = route.meta.title + '-' + route.query.verbose_name

      }
    }
    tabsStore.addTabs(tabsParams);
    // 更新当前面包屑
    tabsStore.updateCurrentTitle(tabsParams)
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
    }
  });
};
const initTabs = () => {

  router.getRoutes().forEach(item => {
    // if (item.meta.isAffix && !item.meta.isHide && !item.meta.isFull) {
    if (item.name == 'home') {

      const tabsParams = {
        icon: item.meta.icon,
        title: item.meta.title,
        path: item.path,
        name: item.name,
        fullPath: route.fullPath

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
  // console.log(fullPath)

  tabsStore.removeTabs(fullPath as string, fullPath == route.path);
};

</script>

<style scoped lang="scss">
.demo-tabs>.el-tabs__content {
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
</style>
