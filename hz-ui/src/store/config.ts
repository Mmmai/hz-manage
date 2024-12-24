
import { defineStore } from "pinia";
import piniaPersistConfig from "@/utils/persist"
import { ref, computed } from 'vue'
import { parseMinWidth } from 'element-plus/es/components/table/src/util.mjs';
export const useConfigStore = defineStore(
  "configs",
  () => {
    // 
    const gmCry = ref({});
    const setGmCry = (params) => {
      gmCry.value = params
    }
    return {
      gmCry, setGmCry
    }
  },
  // 插件外参
  {
    // persist: piniaPersistConfig('tabs', ['tabsMenuList'])
    persist: true

  }


);

export default useConfigStore;
