
import { defineStore } from "pinia";
import { ref, computed, getCurrentInstance } from 'vue'

export const modelConfigStore = defineStore(
  "modelConfigs",
  () => {
    // 
    const { proxy } = getCurrentInstance();
    const allModels = ref([])
    const modelObjectByName = computed(() => {
      return allModels.value.reduce((acc, cur) => {
        acc[cur.name] = cur;
        return acc;
      }, {});
    });
    const modelObjectById = computed(() => {
      return allModels.value.reduce((acc, cur) => {
        acc[cur.id] = cur;
        return acc;
      }, {});
    });
    const modelOptions = computed(() => {
      return allModels.value.map((item) => {
        return {
          label: item.verbose_name,
          value: item.id,
        };
      });
    });
    const getModel = async (force = false) => {
      if (!force && allModels.value.length > 0) return;
      let res = await proxy.$api.getCiModel()
      allModels.value = res.data.results
    }
    return {
      allModels, modelObjectByName, modelObjectById, modelOptions, getModel
    }
  },
  // 插件外参
  {
    // persist: piniaPersistConfig('tabs', ['tabsMenuList'])
    persist: true

  }


);

export default modelConfigStore;
