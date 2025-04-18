import { defineStore } from "pinia";
import { ref, computed, reactive } from 'vue'

export const useCiStore = defineStore(
  "ci",
  () => {
    // 模型列表
    const modelList = ref([])
    const multipleForm = reactive({ filterParams: [] })
    const filterParams = ref([]);
    const filterLists = ref([])
    const ciDataIdNameObj = ref({})
    // 函数
    const setFilterList = (params) => {
      console.log(params)
      filterLists.value = params
      console.log(filterLists.value)
    }
    const saveFilterParams = (params) => {
      console.log(params)
      multipleForm.filterParams = params
    }
    // const getModelRefData = async (model) => {
    //   let res = await proxy.$api.getModelRefCi({
    //     model: model,
    //     page: 1,
    //     page_size: 10000,
    //   });
    //   let tmpObj = {};
    //   // if (res.length === 0) return;
    //   res.data.results.forEach((item) => {
    //     tmpObj[item.id] = item.name;
    //   });
    //   tempList[field.ref_model] = tmpObj;
    //   ciDataIdNameObj
    // };
    // 获取model
    const setModelList = (params) => {
      modelList.value = params
    }

    return {
      setFilterList, saveFilterParams, setModelList
    }
  },
  // 插件外参
  {
    // persist: piniaPersistConfig('tabs', ['tabsMenuList'])
    persist: true

  }


);

export default useCiStore