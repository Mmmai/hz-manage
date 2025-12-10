import axios from '../utils/request'
import commonFunc from '../utils/common'
import { add, get, method } from 'lodash'
import { del } from 'vue-demi'
import { de } from 'element-plus/es/locale/index.mjs'
// import path from './path'
const path = {
  nodeTask: "/api/v1/node_mg/nodeTask/",
  nodes: "/api/v1/node_mg/nodes/",
  proxy: "/api/v1/node_mg/proxy/",
  modelConfig: "/api/v1/node_mg/modelConfig/",
  zabbixApi: "/api/v1/node_mg/zabbixApi/",
  // node_mg: "/api/v1/node_mg

}
export default {
  // nodes
  getNodes(params) {
    return axios.request({ url: path.nodes, method: 'get', params: params })
  },
  getNodeDetail(id) {
    return axios.request({ url: path.nodes + id + '/', method: 'get' })

  },
  getNodeInfoTasks(params) {
    return axios.request({ url: path.nodeTask, method: 'get', params: params })
  },
  getNodesArray(params) {
    return axios.request({ url: path.nodes + 'list_all_nodes/', method: 'get', params: params })
  },
  // deleteNodesGroup(params) {
  //   return axios.delete(path.node_mg + params)
  // },
  // addNodes(params) {
  //   return axios.request({ url: path.node_mg, method: 'post', data: params })
  // },
  updateNodes(params) {
    // return axios.put(path.role+params.id+'/',params)
    return axios.request({ url: path.nodes + params.id + '/', method: 'patch', data: params })
  },
  // 批量关联proxy
  batchAssociateProxy(params) {
    // params: { ids:[],proxy_id:''}
    return axios.request({ url: path.nodes + 'associate_proxy/', method: 'post', data: params })
  },
  // 批量解除关联proxy
  batchDissociateProxy(params) {
    // params: { ids:[]}
    return axios.request({ url: path.nodes + 'dissociate_proxy/', method: 'post', data: params })
  },
  // zabbix主机同步状态
  getZabbixStatus(params) {
    return axios.request({ url: path.nodes, params: params, method: 'get' })
  },
  syncZabbixHost(params) {
    return axios.request({ url: path.nodes + 'sync_zabbix/', method: 'post', data: params })
  },
  updateZabbixAvailability(params) {
    return axios.request({ url: path.nodes + 'update_zabbix_availability/', method: 'post', data: params })
  },
  installAgent(params) {
    return axios.request({ url: path.nodes + 'install_agent/', method: 'post', data: params })
  },
  get_inventory(params) {
    return axios.request({ url: path.nodes + 'get_inventory/', method: 'post', data: params })
  },
  // proxy
  getProxy(params) {
    return axios.request({ url: path.proxy, method: 'get', params: params })
  },
  getProxyInfo(id) {
    return axios.request({ url: path.proxy + id + '/', method: 'get' })
  },
  addProxy(params) {
    return axios.request({ url: path.proxy, method: 'post', data: params })
  },
  deleteProxy(params) {
    return axios.request({ url: path.proxy + params + '/', method: 'delete' })
  },
  updateProxy(params) {
    return axios.request({ url: path.proxy + params.id + '/', method: 'patch', data: params })
  },
  getModelConfig(params) {
    return axios.request({ url: path.modelConfig, method: 'get', params: params })
  },
  addModelConfig(params) {
    return axios.request({ url: path.modelConfig, method: 'post', data: params })
  },
  updateModelConfig(params) {
    return axios.request({ url: path.modelConfig + params.id + '/', method: 'patch', data: params })
  },
  deleteModelConfig(params) {
    return axios.request({ url: path.modelConfig + params.id + '/', method: 'delete' })
  },
  // zabbix模板接口
  getZabbixTemplate(params) {
    return axios.request({ url: path.zabbixApi, method: 'get', params: params })
  },
}