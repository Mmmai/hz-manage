import axios from '../utils/request'
import path from './path'
import userApis from './user';
import cmdbApis from './cmdb';
import lokiApis from './loki'
import nodeApis from './node_mg'
import auditApis from './audit';
import commonFunc from '../utils/common'
import permissionApis from './permission'
import monitorApis from './monitor'
const api = {
  ...userApis,
  ...cmdbApis,
  ...lokiApis,
  ...nodeApis,
  ...auditApis,
  ...permissionApis,
  ...monitorApis,
  getRouteInfo(params) {
    return axios.request({
      url: path.routeInfo,
      method: 'post',
      data: params
    })
  },
  getSecret(params) {
    return axios.request({
      url: path.getSecret,
      method: 'get',
      params: params

    })
  },

  // 查看单个menu信息
  getMenuInfo(params) {
    return axios.request({
      url: path.menu + params.id,
      method: 'get',
      // params: params

    })
  },
  // 门户组
  pgroupGet(params) {
    return axios.request({
      url: path.pgroup,
      method: 'get',
      params: params
    })
  },
  pgroupAdd(params) {
    return axios.request({
      url: path.pgroup,
      method: 'post',
      data: params
    })
  },
  pgroupDel(params) {
    return axios.request({
      url: path.pgroup + params + '/',
      method: 'delete',
    })
  },
  pgroupUpdate(params) {
    // return axios.put(path.role+params.id+'/',params)
    return axios.request({
      url: path.pgroup + params.id + '/',
      method: 'patch',
      data: params
    })
  },
  pgroupMuldel(data) {
    // return axios.delete(path.user+'multiple_delete/',data)
    return axios.request({
      url: path.pgroup + 'multiple_delete/',
      method: 'delete',
      data: data
    })
  },
  // 门户
  portalGet(params) {
    return axios.request({
      url: path.portal,
      method: 'get',
      params: params
    })
  },
  portalAdd(params) {
    return axios.request({
      url: path.portal,
      method: 'post',
      data: params
    })
  },
  portalDelete(params) {
    return axios.request({
      url: path.portal + params + '/',
      method: 'delete',
    })
  },
  portalUpdate(params) {
    // return axios.put(path.role+params.id+'/',params)
    return axios.request({
      url: path.portal + params.id + '/',
      method: 'patch',
      data: params
    })
  },
  portalMuldel(data) {
    // return axios.delete(path.user+'multiple_delete/',data)
    return axios.request({
      url: path.portal + 'multiple_delete/',
      method: 'delete',
      data: data
    })
  },
  portalTemplateExport() {
    commonFunc.downloadFile(path.portal + 'export_template/')
  },
  portalDataExport() {
    commonFunc.downloadFile(path.portal + 'export_portal/')
  },
  importPortalData(params, headers, timeout) {
    return axios.request({ url: path.portal + 'import_portal/', method: 'post', data: params, headers: headers, timeout: timeout })
  },
  // 
  // dataSource
  dataSourceGet(params) {
    if (typeof (params) === 'string') {
      return axios.request({
        url: path.dataSource + params,
        method: 'get',
        // params: params
      })
    } else {
      return axios.request({
        url: path.dataSource,
        method: 'get',
        params: params
      })
    }
  },
  dataSourceAdd(params) {
    return axios.request({
      url: path.dataSource,
      method: 'post',
      data: params
    })
  },
  dataSourceDel(params) {
    return axios.request({
      url: path.dataSource + params + '/',
      method: 'delete',
    })
  },
  dataSourceUpdate(params) {
    // return axios.put(path.role+params.id+'/',params)
    return axios.request({
      url: path.dataSource + params.id + '/',
      method: 'put',
      data: params
    })
  },
  getSysConfig(params) {
    return axios.request({
      url: path.sysConfig,
      method: 'get',
      params: params
    })
  },
  updateSysConfig(params) {
    return axios.request({
      url: path.sysConfig + params.id + '/',
      method: 'patch',
      data: params
    })
  },
  updateZabbixConfig(params) {
    return axios.request({
      url: path.sysConfig + 'update_zabbix_params/',
      method: 'post',
      data: params
    })
  }
}
export default api;