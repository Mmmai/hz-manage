import axios from '../utils/request'
// import path from './path'
const path = {
  export: "/api/v1/export/",
  loki: "/api/v1/log/loki/",
  logModule:"/api/v1/log/logModule/",
  logFlow: "/api/v1/log/logFlow/",
  logFlowInfo: "/api/v1/log/logFlow/stepQuery",
  logFlowMission: "/api/v1/log/logFlowMission/",
}
// 导出
export default {
exportXls(params){
  return axios.request({
    url:path.export,
    method: 'post',
    data:params,
    responseType: 'blob',

  })
},
// loki接口
lokiLabelGet(data){
  return axios.request({
    url:path.loki + 'labels',
    method: 'get',
    params:data
  })
},
lokiLabelValueGet(data){
  return axios.request({
    url:path.loki + 'label',
    method: 'get',
    params:data
   })
  },
lokiQuery(data){
  return axios.request({
    url:path.loki + 'query',
    method: 'post',
    data: data,
    // headers:{"Content-Type":"multipart/form-data"}
   })
  },
  lokiNearQuery(data){
    return axios.request({
      url:path.loki + 'queryContext',
      method: 'post',
      data: data,
      // headers:{"Content-Type":"multipart/form-data"}
     })
    },

  // 日志环节
  getLogModule(params){
    return axios.request({
      url:path.logModule,
      method: 'get',
      params: params
    })
    // return axios.post(path.role)}
  },  
  delLogModule(params){
    return axios.delete(path.logModule+params+'/')
  },
  addLogModule(params){
    return axios.request({
      url:path.logModule,
      method: 'post',
      data: params
    })
    // return axios.post(path.role)}
  }, 
  updateLogModule(params){
    // return axios.put(path.role+params.id+'/',params)
    return axios.request({
      url:path.logModule+params.id+'/',
      method: 'patch',
      data: params
    })
  },
  // 日志流程
  getLogFlow(params){
    return axios.request({
      url:path.logFlow,
      method: 'get',
      params: params
    })
    // return axios.post(path.role)}
  },  
  delLogFlow(params){
    return axios.delete(path.logFlow+params+'/')
  },
  addLogFlow(params){
    return axios.request({
      url:path.logFlow,
      method: 'post',
      data: params
    })
    // return axios.post(path.role)}
  }, 
  updateLogFlow(params){
    // return axios.put(path.role+params.id+'/',params)
    return axios.request({
      url:path.logFlow+params.id+'/',
      method: 'patch',
      data: params
    })
  },
  // 流程日志查询
  getFlowLokiLog(params){
    return axios.request({
      url:path.logFlowInfo,
      method: 'post',
      data: params
    })
  },
  // 历史任务
  getLogFlowMission(params){
    if (typeof(params) === 'string'){
      return axios.request({
        url:path.logFlowMission+params,
        method: 'get',
        // params: params
      })
    }else{
    return axios.request({
      url:path.logFlowMission,
      method: 'get',
      params: params
    })
    }
  } 
}