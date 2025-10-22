import axios from '../utils/request'
// import path from './path'
const path = {
  // audit
  auditLog: "/api/v1/audit/logs/",

}
export default {
  // cmdb
  // 模型组
  getAuditLog(params) {
    return axios.request({ url: path.auditLog, method: 'get', params: params })
  },
  getCiAuditLog(params: { target_type: string, object_id: string }) {
    // 请求参数: {target_type: model_instance, object_id: XXXX} 
    return axios.request({ url: path.auditLog + 'history/', method: 'get', params: params })
  },
}