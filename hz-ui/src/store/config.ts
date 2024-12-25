
import { defineStore } from "pinia";
import piniaPersistConfig from "@/utils/persist"
import { ref, computed } from 'vue'
import { parseMinWidth } from 'element-plus/es/components/table/src/util.mjs';
export const useConfigStore = defineStore(
  "configs",
  () => {
    // 
    const gmCry = ref({});
    const showAllPass = ref(false)
    const setGmCry = (params) => {
      gmCry.value = params
    }
    const updateShowAllPass = (params) => {
      showAllPass.value = params
    }

    return {
      gmCry, setGmCry, showAllPass, updateShowAllPass
    }
  },
  // 插件外参
  {
    // persist: piniaPersistConfig('tabs', ['tabsMenuList'])
    persist: true

  }


);

export default useConfigStore;
