import axios from '../utils/request'
import commonFunc from '../utils/common'
import { method } from 'lodash'
// import path from './path'
const path = {
  nodes: "/api/v1/node_mg/nodes/",

}
export default {
  // cmdb
  // 模型组
  getNodes(params) {
    return axios.request({ url: path.nodes, method: 'get', params: params })
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
}