import axios from '../utils/request'
// import path from './path'
const path = {
  // audit
  auditLog: "/api/v1/cmdb/audit/logs/",
}
export default {
  // cmdb
  // 模型组
  getAuditLog(params) {
    return axios.request({ url: path.auditLog, method: 'get', params: params })
  },
}