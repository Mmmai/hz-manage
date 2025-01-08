
import { defineStore } from "pinia";
import piniaPersistConfig from "@/utils/persist"
import { ref, computed } from 'vue'
import { parseMinWidth } from 'element-plus/es/components/table/src/util.mjs';
import { pa } from "element-plus/es/locale/index.mjs";
export const useConfigStore = defineStore(
  "configs",
  () => {
    // 
    const gmCry = ref({});
    const showAllPass = ref(false)
    const showAllPassTime = ref(0 * 1000)
    const setGmCry = (params) => {
      gmCry.value = params
    }
    const updateShowAllPass = (params) => {
      showAllPass.value = params
    }
    const setShowAllPassTime = (params) => {
      showAllPassTime.value = params
    }
    const updateShowAllPassTime = (params) => {
      showAllPassTime.value = params
    }
    return {
      gmCry, setGmCry, showAllPass, updateShowAllPass, setShowAllPassTime, showAllPassTime, updateShowAllPassTime
    }
  },
  // 插件外参
  {
    // persist: piniaPersistConfig('tabs', ['tabsMenuList'])
    persist: true

  }


);

export default useConfigStore;
