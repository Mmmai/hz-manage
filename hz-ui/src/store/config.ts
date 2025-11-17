
import { defineStore } from "pinia";
import { ref, computed, getCurrentInstance } from 'vue'
import api from '../api/index'

import { ElMessage } from "element-plus";
import { useRouter, useRoute } from "vue-router";

export const useConfigStore = defineStore(
  "configs",
  () => {
    // 
    const dynamicCreateRoute = ref(false);

    // 菜单折叠
    const collapse = ref(false);
    const changeCollapse = () => {
      collapse.value = !collapse.value
    }
    // token
    const token = ref<string>(null)
    // 用户角色
    const userInfo = ref<{}>({})
    const role = ref([])
    // 权限菜单
    const permission = ref<[string]>([])
    const setUserConfig = (params) => {
      token.value = params.token
      userInfo.value = params.userinfo
      permission.value = params.permission
      role.value = params.role
    }
    const setDynamicCreateRoute = (params) => {
      dynamicCreateRoute.value = params
    }

    // 动态菜单
    const menuInfo = ref([])
    const getMenuInfo = async (config) => {
      let res = await api.getMenuList(config)

      if (res.status === 403) {
        // 弹出提示没有认证,清除token等，重新登录
        ElMessage.error(JSON.stringify(res.data))
        setUserConfig({ token: null, userinfo: null, permission: null, role: null })
        // 只有在提供了router实例时才进行跳转
      } else {
        menuInfo.value = res.data.results
      }
    }
    const gmCry = ref({});
    const showAllPass = ref(false)
    const showAllPassTime = ref(0 * 1000)
    // 版本
    const appVersion = ref(null)


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
      let res = await api.getSysConfig({ param_name: "app_version" })
      appVersion.value = res.data[0].param_value
    }
    // 清空配置
    const clearConfig = () => {
      token.value = null
      userInfo.value = null
      role.value = null
      permission.value = null
      menuInfo.value = null
      gmCry.value = null
      showAllPass.value = null
      showAllPassTime.value = null
      appVersion.value = null
    }
    return {
      dynamicCreateRoute, setDynamicCreateRoute, collapse, changeCollapse, token, userInfo, role, permission, setUserConfig, menuInfo, getMenuInfo,
      gmCry, setGmCry, showAllPass, updateShowAllPass, setShowAllPassTime, showAllPassTime, updateShowAllPassTime, appVersion, getAppVersion, clearConfig
    }
  },
  // 插件外参
  {
    // persist: false
    // persist: piniaPersistConfig('tabs', ['tabsMenuList'])
    persist: {
      key: "configs",
      // pick:["dynamicCreateRoute"]
      // 排除
      omit: [
        "dynamicCreateRoute",
      ]
    }
  }


);

export default useConfigStore;
