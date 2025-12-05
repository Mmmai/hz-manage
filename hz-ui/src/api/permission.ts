import axios from '../utils/request'
// import path from './path'
export default {
  // nodes
  getDataScope(params) {
    return axios.request({ url: '/api/v1/permissions/data_scope/', method: 'get', params: params })
  },
  getDataScopeAll(params) {
    return axios.request({ url: '/api/v1/permissions/data_scope/aggregated_permissions/', method: 'get', params: params })
  },
  setDataScope(params) {
    // {role:xxx,scope_type:xxx,targets:[{}] }
    return axios.request({ url: '/api/v1/permissions/data_scope/', method: 'post', data: params })
  },
}