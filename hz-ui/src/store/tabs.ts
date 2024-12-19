import { useRouter, useRoute } from 'vue-router'
import { defineStore } from "pinia";
import piniaPersistConfig from "@/utils/persist"
import { ref, computed } from 'vue'
import { parseMinWidth } from 'element-plus/es/components/table/src/util.mjs';
export const useTabsStore = defineStore(
  "tabs",
  () => {

    // 
    const tabsMenuList = ref([]);
    const router = useRouter();
    const currentTitle = ref('')
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
    }
    // const updateCurentMenu = async(params) =>{
    //   currentMenu.value = params
    // }
    // const addTabs = async (tabItem) => {
    //   if (tabsMenuList.value.every(item => item.fullPath !== tabItem.fullPath)) {
    //     tabsMenuList.value.push(tabItem);
    //   }
    // }
    // 添加标签
    const addTabs = async (tabItem) => {
      // 实现看单个详情,每次都覆盖之前的详单tabs
      if (tabItem.name === 'logFlowMission_info') {
        console.log('名字一致')
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

      if (tabsMenuList.value.every(item => item.path !== tabItem.path)) {
        tabsMenuList.value.push(tabItem);
      }


    }
    const removeTabs = (tabPath: string, isCurrent: boolean = true) => {
      // console.log(tabPath.path)
      console.log('删除tabs', tabPath)
      if (isCurrent) {
        tabsMenuList.value.forEach((item, index) => {
          console.log('进入')

          if (item.path !== tabPath) return;
          console.log('进入这里')
          const nextTab = tabsMenuList.value[index + 1] || tabsMenuList.value[index - 1];
          if (!nextTab) return;
          console.log(nextTab.path)
          router.push(nextTab.fullPath);
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
      // tabsMenuList.value.forEach((item,index)=>{
      //   if (tabPath != item.path){

      //   }

      // })
    }
    const setTabs = (tabsMenuList: TabsMenuProps[]) => {
      tabsMenuList.value = tabsMenuList;
    }
    return {
      tabsMenuList,
      addTabs, removeTabs, tabsMenuDict, currentTitle, updateCurrentTitle, currentMenu, setTabs
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
  //       if (this.tabsMenuList.every(item => item.path !== tabItem.path)) {
  //         this.tabsMenuList.push(tabItem);
  //       }

  //     },
  //     // Remove Tabs
  //     async removeTabs(tabPath, isCurrent) {
  //       if (isCurrent) {
  //         this.tabsMenuList.forEach((item, index) => {
  //           if (item.path !== tabPath) return;
  //           const nextTab = this.tabsMenuList[index + 1] || this.tabsMenuList[index - 1];
  //           if (!nextTab) return;
  //           router.push(nextTab.path);
  //         });
  //       }

  //     },
  //   }
  // },


);

export default useTabsStore
