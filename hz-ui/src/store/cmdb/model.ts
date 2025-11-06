
import { defineStore } from "pinia";
import { json } from "stream/consumers";
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
    // 校验规则
    const validationRules = ref([])
    const validationRulesObjectById = computed(() => {
      return validationRules.value.reduce((acc, cur) => {
        acc[cur.id] = cur;
        return acc;
      }, {});
    });
    const validationRulesEnumOptionsObject = computed(() => {
      return validationRules.value
        .filter(item => item.type === 'enum')
        .reduce((acc, item) => {
          try {
            let ruleObj = JSON.parse(item.rule);
            let tmpList = [];
            Object.keys(ruleObj).forEach((ritem) => {
              tmpList.push({ value: ritem, label: ruleObj[ritem] });
            });
            acc[item.id] = tmpList;
          } catch (e) {
            console.warn('Failed to parse rule for item:', item.id, e);
          }
          return acc;
        }, {});
    });

    // 获取校验规则
    const getValidationRules = async (force = false) => {
      if (!force && validationRules.value.length > 0) return;
      let res = await proxy.$api.getValidationRules({ page_size: 2000, page: 1 })
      validationRules.value = res.data.results
    }

    // 提供给外部调用
    return {
      allModels, modelObjectByName, modelObjectById, modelOptions, getModel,
      validationRules, validationRulesObjectById, validationRulesEnumOptionsObject, getValidationRules
    }
  },
  // 插件外参
  {
    // persist: piniaPersistConfig('tabs', ['tabsMenuList'])
    persist: true

  }


);

export default modelConfigStore;
