import axios from '../utils/request'
import commonFunc from '../utils/common'
// import path from './path'
const path = {
    // cmdb
    cmdbCiModel: "/api/v1/cmdb/models/",
    cmdbCiModelGroup: "/api/v1/cmdb/model_groups/",
    cmdbCiModelField: "/api/v1/cmdb/model_fields/",
    cmdbCiModelFieldGroup: "/api/v1/cmdb/model_field_groups/",
    cmdbValidationRules: "/api/v1/cmdb/validation_rules/",
    cmdbCiModelUnique: "/api/v1/cmdb/unique_constraint/",
    cmdbCiModelInstance: "/api/v1/cmdb/model_instance/",
    cmdbCiDataCol: "/api/v1/cmdb/model_field_preference/",
    cmdbCiDataTree: "/api/v1/cmdb/model_instance_group/",
    cmdbCiDataTreeRelation: "/api/v1/cmdb/model_instance_group_relation/create_relations/",
    cmdbModelRef: "/api/v1/cmdb/model_ref/"
  }
export default {
// cmdb
    // 模型组
    getCiModelGroup(params){
        return axios.request({url:path.cmdbCiModelGroup,method: 'get',params: params})
      },
      deleteCiModelGroup(params){
        return axios.delete(path.cmdbCiModelGroup+params)
      },
      addCiModelGroup(params){
        return axios.request({url:path.cmdbCiModelGroup,method: 'post',data: params})
      }, 
      updateCiModelGroup(params){
        // return axios.put(path.role+params.id+'/',params)
        return axios.request({url:path.cmdbCiModelGroup+params.id,method: 'put',data: params})
      },
      // 模型
      getCiModel(params,obj=null){
        if (obj === null){
          return axios.request({url:path.cmdbCiModel,method: 'get',params: params})
        }else{
          return axios.request({url:path.cmdbCiModel+obj,method: 'get',params: params})
        }
      },
      deleteCiModel(params){
        return axios.delete(path.cmdbCiModel+params+'/')
      },
      addCiModel(params){
        return axios.request({url:path.cmdbCiModel,method: 'post',data: params})
        // return axios.post(path.role)}
      }, 
      updateCiModel(params){
        // return axios.put(path.role+params.id+'/',params)
        return axios.request({url:path.cmdbCiModel+params.id+'/',method: 'patch',data: params})
      },
      // 模型字段组
      getCiModelFieldGroup(params){
        return axios.request({url:path.cmdbCiModelFieldGroup,method: 'get',params: params})
      },
      deleteCiModelFieldGroup(params){
        return axios.delete(path.cmdbCiModelFieldGroup+params)
      },
      addCiModelFieldGroup(params){
        return axios.request({url:path.cmdbCiModelFieldGroup,method: 'post',data: params})
      }, 
      updateCiModelFieldGroup(params){
        return axios.request({url:path.cmdbCiModelFieldGroup+params.id+'/',method: 'put',data: params})
      },
      // 模型字段
      deleteCiModelField(params){
        return axios.delete(path.cmdbCiModelField+params)
      },
      addCiModelField(params){
        return axios.request({url:path.cmdbCiModelField,method: 'post',data: params})
      }, 
      updateCiModelField(params){
        return axios.request({url:path.cmdbCiModelField+params.id+'/',method: 'patch',data: params})
      },
      getCiModelFieldType(params=null){
        return axios.request({url:path.cmdbCiModelField+'/metadata',method: 'get'})
  
      },
      // 字段校验
      getValidationRules(params){
        return axios.request({url:path.cmdbValidationRules,method: 'get',params: params})
      },
      deleteValidationRules(params){
        return axios.delete(path.cmdbValidationRules+params)
      },
      addValidationRules(params){
        return axios.request({url:path.cmdbValidationRules,method: 'post',data: params})
      }, 
      updateValidationRules(params){
        return axios.request({url:path.cmdbValidationRules+params.id+'/',method: 'patch',data: params})
      },
      // 字段唯一性
      getCiModelUnique(params){
        return axios.request({url:path.cmdbCiModelUnique,method: 'get',params: params})
      },
      deleteCiModelUnique(params){
        return axios.delete(path.cmdbCiModelUnique+params)
      },
      addCiModelUnique(params){
        return axios.request({url:path.cmdbCiModelUnique,method: 'post',data: params})
      }, 
      updateCiModelUnique(params){
        return axios.request({url:path.cmdbCiModelUnique+params.id+'/',method: 'patch',data: params})
      },

      // 模型实例
      getCiModelInstance(params){
        return axios.request({url:path.cmdbCiModelInstance,method: 'get',params: params})
      },
      deleteCiModelInstance(params){
        return axios.delete(path.cmdbCiModelInstance+params)
      },
      addCiModelInstance(params){
        return axios.request({url:path.cmdbCiModelInstance,method: 'post',data: params})
      }, 
      updateCiModelInstance(params){
        return axios.request({url:path.cmdbCiModelInstance+params.id+'/',method: 'patch',data: params})
      },
      // 批量更新
      multipleUpdateCiModelInstance(params){
        return axios.request({url:path.cmdbCiModelInstance+'/bulk_update_fields/',method: 'patch',data: params})
      },
      // ci数据显示列
      getCiModelCol(params){
        return axios.request({url:path.cmdbCiDataCol,method: 'get',params: params})
      },
      deleteCiModelCol(params){
        return axios.delete(path.cmdbCiDataCol+params)
      },
      addCiModelCol(params){
        return axios.request({url:path.cmdbCiDataCol,method: 'post',data: params})
      }, 
      updateCiModelCol(params){
        return axios.request({url:path.cmdbCiDataCol+params.id+'/',method: 'patch',data: params})
      },
      // ci tree
      getCiModelTree(params){
        return axios.request({url:path.cmdbCiDataTree,method: 'get',params: params})
      },
      // 从CI树节点查询ci实例
      getCiDataFromModelTree(params){
        return axios.request({url:path.cmdbCiDataTree+params+'/search_instances',method: 'get'})
      },
      deleteCiModelTree(params){
        return axios.delete(path.cmdbCiDataTree+params)
      },
      addCiModelTree(params){
        return axios.request({url:path.cmdbCiDataTree,method: 'post',data: params})
      }, 
      updateCiModelTree(params){
        return axios.request({url:path.cmdbCiDataTree+params.id+'/',method: 'patch',data: params})
      },
      // 实例关联实例树
      setCiDataToTree(params){
        return axios.request({url:path.cmdbCiDataTreeRelation,method: 'post',data: params})
      },
      // 模型引用实例获取
      getModelRefCi(params){
        return axios.request({url:path.cmdbModelRef,method: 'get',params: params})
      },
      // 导入实例的模板下载
      downloadImportTemplate(params){
        commonFunc.downloadFile(path.cmdbCiModelInstance+'export_template/',params)
        // return axios.request({url:path.cmdbCiModelInstance+'export_template/',method: 'get',params: params})

      }

    }