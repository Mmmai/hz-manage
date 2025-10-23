import { useRouter, useRoute } from 'vue-router'
import { defineStore } from "pinia";
import piniaPersistConfig from "@/utils/persist"
import { ref, computed } from 'vue'
import { parseMinWidth } from 'element-plus/es/components/table/src/util.mjs';
import { useKeepAliveStore } from "./keepAlive";

const keepAliveStore = useKeepAliveStore();
export const useTabsStore = defineStore(
  "tabs",
  () => {

    // 
    const tabsMenuList = ref([]);
    const router = useRouter();
    const currentTitle = ref('')
    const currentBreadcrumb = ref([]);
    const currentMenu = ref('')
    // action
    // const pushTesst = ()=>{
    //   tabsMenuList.value.push(3)
    // }
    // 为了添加详细模型显示“主机、交换机等标签”

    const tabsMenuDict = computed(() => {
      let _temp = {}
      tabsMenuList.value.forEach(item => {
        _temp[item.path] = item
      })
      return _temp
    })

    const updateCurrentTitle = async (params) => {
      currentTitle.value = params.title
      currentMenu.value = params.name.split('_')[0]
      currentBreadcrumb.value = params.menuPath
      // console.log("currentBreadcrumb:", currentBreadcrumb)
    }

    // 添加标签
    const addTabs = (tabItem) => {
      // 实现看单个详情,每次都覆盖之前的详单tabs
      if (tabItem.name === 'logFlowMission_info') {
        // if (tabsMenuList.value.every(item => item.name !== tabItem.name)) {
        //   tabsMenuList.value.push(tabItem);
        // }
        // 判断旧的tabs列表里是否存在这个详单的name，有的话删除，并追加新的
        // 拿到旧的index
        let index = tabsMenuList.value.findIndex(item => item.name === tabItem.name)
        if (index !== -1) {
          tabsMenuList.value.splice(index, 1, tabItem)
        } else {
          tabsMenuList.value.push(tabItem)
        }
        return
      }
      // 详情页在本tab内
      if (tabItem.isInfo) {
        return
      }

      if (tabsMenuList.value.every(item => item.path !== tabItem.path)) {
        tabsMenuList.value.push(tabItem);
      }
      if (!keepAliveStore.keepAliveName.includes(tabItem.name) && tabItem.isKeepAlive) {
        keepAliveStore.addKeepAliveName(tabItem.name);
      }

    }
    const removeTabs = (tabPath: string, isCurrent: boolean = true) => {
      const tabItem = tabsMenuList.value.find(item => item.path === tabPath);
      // console.log(tabItem)
      tabItem?.isKeepAlive && keepAliveStore.removeKeepAliveName(tabItem.name);
      // console.log(tabPath.path)
      if (isCurrent) {
        tabsMenuList.value.forEach((item, index) => {

          if (item.path !== tabPath) return;

          const nextTab = tabsMenuList.value[index + 1] || tabsMenuList.value[index - 1];

          if (!nextTab) return;
          if (nextTab.name === "model_info") {
            router.push(nextTab.fullPath)

          } else {
            router.push(nextTab.path)

          }
          // currentTitle.value = nextTab.title
          // console.log(currentTitle.value)
        });
      }
      // 删除tab菜单

      let _tempList = []
      tabsMenuList.value.filter(item => {
        if (item.path !== tabPath) {
          if (item.fullPath !== tabPath) {
            _tempList.push(item)
          }
        }
      })

      // let _tempList = tabsMenuList.value.filter(item => item.path !== tabPath || item.fullPath !== tabPath)
      tabsMenuList.value = _tempList
      console.log(tabsMenuList.value)

    }
    const setTabs = (params: TabsMenuProps[]) => {
      tabsMenuList.value = params;
    }
    const closeTabsOnSide = (path: string, type: "left" | "right") => {
      const currentIndex = tabsMenuList.value.findIndex(item => item.fullPath === path);
      if (currentIndex !== -1) {
        const range = type === "left" ? [0, currentIndex] : [currentIndex + 1, tabsMenuList.value.length];
        tabsMenuList.value = tabsMenuList.value.filter((item, index) => {
          return index < range[0] || index >= range[1] || item.name == 'home';
        });
      }
      const KeepAliveList = tabsMenuList.value.filter(item => item.isKeepAlive);
      keepAliveStore.setKeepAliveName(KeepAliveList.map(item => item.name));

    }
    // Close MultipleTab
    const closeMultipleTab = (tabsMenuValue?: string) => {
      tabsMenuList.value = tabsMenuList.value.filter(item => {
        return item.path === tabsMenuValue || item.name == 'home';
      });
      const KeepAliveList = tabsMenuList.value.filter(item => item.isKeepAlive);
      keepAliveStore.setKeepAliveName(KeepAliveList.map(item => item.name));
      // router.push(tabsMenuValue)
    }



    return {
      tabsMenuList, closeTabsOnSide, closeMultipleTab,
      addTabs, removeTabs, tabsMenuDict, currentTitle, updateCurrentTitle, currentMenu, setTabs, currentBreadcrumb
    }
  },
  // 插件外参
  {
    // persist: piniaPersistConfig('tabs', ['tabsMenuList'])
    persist: true

  }
  //   state: () => ({
  //     tabsMenuList: []
  //   }),
  //   actions: {
  //     // Add Tabs
  //     async addTabs(tabItem) {
  //       if (tabsMenuList.value.every(item => item.path !== tabItem.path)) {
  //         tabsMenuList.value.push(tabItem);
  //       }

  //     },
  //     // Remove Tabs
  //     async removeTabs(tabPath, isCurrent) {
  //       if (isCurrent) {
  //         tabsMenuList.value.forEach((item, index) => {
  //           if (item.path !== tabPath) return;
  //           const nextTab = tabsMenuList.value[index + 1] || tabsMenuList.value[index - 1];
  //           if (!nextTab) return;
  //           router.push(nextTab.path);
  //         });
  //       }

  //     },
  //   }
  // },


);

export default useTabsStore
