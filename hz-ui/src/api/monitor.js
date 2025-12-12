import axios from '../utils/request'
// import path from './path'
const path = {
  zabbixApi: "/api/v1/monitor/zabbix_api/",
  // node_mg: "/api/v1/node_mg
}
export default {
  // zabbix模板接口
  getZabbixTemplate(params) {
    return axios.request({ url: path.zabbixApi, method: 'get', params: params })
  },
  getZabbixHistory(params) {
    return axios.request({ url: path.zabbixApi, method: 'post', data: params })
  },
}