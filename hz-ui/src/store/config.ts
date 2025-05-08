
import { defineStore } from "pinia";
import piniaPersistConfig from "@/utils/persist"
import { ref, computed, getCurrentInstance } from 'vue'
import { parseMinWidth } from 'element-plus/es/components/table/src/util.mjs';
import { pa } from "element-plus/es/locale/index.mjs";

export const useConfigStore = defineStore(
  "configs",
  () => {
    // 
    const { proxy } = getCurrentInstance();

    const gmCry = ref({});
    const showAllPass = ref(false)
    const showAllPassTime = ref(0 * 1000)
    // 版本
    const appVersion = ref(null)
    // zabbix相关

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
    const getAppVersion = async (params) => {
      let res = await proxy.$api.getSysConfig({ param_name: "app_version" })
      appVersion.value = res.data[0].param_value
    }
    return {
      gmCry, setGmCry, showAllPass, updateShowAllPass, setShowAllPassTime, showAllPassTime, updateShowAllPassTime, appVersion, getAppVersion
    }
  },
  // 插件外参
  {
    // persist: piniaPersistConfig('tabs', ['tabsMenuList'])
    persist: true

  }


);

export default useConfigStore;
