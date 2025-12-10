
import { defineStore } from "pinia";
import { json } from "stream/consumers";
import { ref, computed, getCurrentInstance } from 'vue'
import api from "@/api";
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
    // 更新模型列表allModels
    const updateAllModels = (data) => {
      allModels.value = data
    }
    // 获取模型
    const getModel = async (force = false) => {
      if (!force && allModels.value.length > 0) return;
      let res = await proxy.$api.getCiModel()
      allModels.value = res.data.results
    }
    // 校验规则
    const validationRules = ref([])
    const validationRulesOptions = computed(() => {
      return validationRules.value.map((item) => {
        return {
          label: item.verbose_name,
          name: item.name,
          type: item.type,
          value: item.id,
        };
      });
    });
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
    // 更新模型列表allModels
    const updateValidationRules = (data) => {
      validationRules.value = data
    }
    // 获取校验规则
    const getValidationRules = async (force = false) => {
      if (!force && validationRules.value.length > 0) return;
      let res = await proxy.$api.getValidationRules({ page_size: 2000, page: 1 })
      validationRules.value = res.data.results
    }
    // 递归提取所有 instances
    const extractInstances = (node: any): Array<{ id: string; instance_name: string }> => {
      let instances: Array<{ id: string; instance_name: string }> = []

      // 如果当前节点有 instances，则添加到结果中
      if (node.instances && Array.isArray(node.instances)) {
        instances = instances.concat(node.instances)
      }

      // 递归处理子节点
      if (node.children && Array.isArray(node.children)) {
        node.children.forEach((child: any) => {
          instances = instances.concat(extractInstances(child))
        })
      }

      return instances
    }
    const allModelCiDataObj = ref({})

    const allModelCiDataTreeObj = computed(() => {
      let tempObj = {}
      Object.keys(allModelCiDataObj.value).forEach((item) => {
        let temp = allModelCiDataObj.value[item]
        let instances = extractInstances(temp)
        tempObj[item] = instances.map(instance => ({
          value: instance.id,
          label: instance.instance_name
        }))
      })
      return tempObj
    })
    const getModelTreeInstance = async (model) => {
      let res = await api.getCiModelTreeNode({
        model: model,
      });
      allModelCiDataObj.value[model] = res.data[0];
      console.log(allModelCiDataObj.value[model]);
    }


    // 获取所有模型的实例树和实例
    const getAllModelTreeInstances = async (force = false) => {

      if (!force && Object.keys(allModelCiDataObj.value).length > 0) return;
      if (allModels.value.length == 0) {
        await getModel();
      }
      allModels.value.forEach(async (item) => {
        await getModelTreeInstance(item.id);
      });
    }
    // 清空缓存
    const clearModelConfig = () => {
      allModelCiDataObj.value = {};
      validationRules.value = [];
      allModels.value = [];

    }

    // 提供给外部调用
    return {
      allModels, modelObjectByName, modelObjectById, modelOptions, getModel, updateAllModels, allModelCiDataObj, getModelTreeInstance, getAllModelTreeInstances, allModelCiDataTreeObj,
      validationRules, validationRulesObjectById, validationRulesEnumOptionsObject, getValidationRules, updateValidationRules, validationRulesOptions, clearModelConfig
    }
  },
  // 插件外参
  {
    // persist: piniaPersistConfig('tabs', ['tabsMenuList'])
    persist: true

  }


);

export default modelConfigStore;
