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
    // 权限菜单
    const permission = ref<[string]>([])
    const setUserConfig = (params) => {
      token.value = params.token
      userInfo.value = params.userinfo
      permission.value = params.permission
    }
    const setDynamicCreateRoute = (params) => {
      dynamicCreateRoute.value = params
    }

    // 动态菜单
    const menuInfo = ref([])
    const getMenuInfo = async () => {
      try {
        let res = await api.getMenuList()

        if (res.status === 403) {
          // 弹出提示没有认证,清除token等，重新登录
          ElMessage.error("认证失败，请重新登录")
          setUserConfig({ token: null, userinfo: null, permission: null })
          throw new Error('认证失败');
        } else if (res.status >= 500) {
          // 处理服务器错误
          ElMessage.error("服务器错误，请稍后再试")
          throw new Error('服务器错误');
        } else {
          menuInfo.value = res.data.results
        }
      } catch (error) {
        // 处理网络错误或其他异常
        if (error.response?.status === 403) {
          ElMessage.error("认证失败，请重新登录")
          setUserConfig({ token: null, userinfo: null, permission: null })
        } else if (error.response?.status >= 500) {
          ElMessage.error("服务器错误，请稍后再试")
        } else {
          ElMessage.error("获取菜单失败，请检查网络连接")
        }
        throw error;
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
      permission.value = null
      menuInfo.value = null
      gmCry.value = null
      showAllPass.value = null
      showAllPassTime.value = null
      appVersion.value = null
    }
    return {
      dynamicCreateRoute, setDynamicCreateRoute, collapse, changeCollapse, token, userInfo, permission, setUserConfig, menuInfo, getMenuInfo,
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
)
export default useConfigStore
