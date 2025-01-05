import axios from '../utils/request'
import path from './path'
export default {
   

// 登录
login(params){
    return axios.request({
      url:path.login,
      method:'post',
      data:params
    })
  },


  test(){
    return axios.get(path.test)
  },
  user(config){
    return axios.request({
      url:path.user,
      method: 'get',
      params:config
    })

  },
  useradd(params){
    return axios.post(path.user,params)
  },
  userupdate(params){
    return axios.patch(path.user+params.id+'/',params)
  },
  userdel(params){
    return axios.delete(path.user+params+'/')
  },
  usermuldel(data){
    // return axios.delete(path.user+'multiple_delete/',data)
    return axios.request({
      url:path.user+'multiple_delete/',
      method:'delete',
      data:data
    })
  },
  getRole(params){
    return axios.request({
      url:path.role,
      method: 'get',
      params: params
    })
    // return axios.post(path.role)}
  },  
  roledel(params){
    return axios.delete(path.role+params+'/')
  },
  roleadd(params){
    return axios.request({
      url:path.role,
      method: 'post',
      data: params
    })
    // return axios.post(path.role)}
  }, 
  roleupdate(params){
    // return axios.put(path.role+params.id+'/',params)
    return axios.request({
      url:path.role+params.id+'/',
      method: 'patch',
      data: params
    })
  },
  // 获取角色关联权限的树状
  getPermissionToRole(params){
    return axios.request({
      url:'/api/v1/getPermissionToRole/',
      method: 'post',
      data: params
    })
    // return axios.post(path.role)}
  }, 

  getUserGroup(config){
    return axios.request({
      url:path.userGroup,
      method: 'get',
      params:config
    })

  },
  addUserGroup(params){
    return axios.post(path.userGroup,params)
  },
  updateUserGroup(params){
    return axios.patch(path.userGroup+params.id+'/',params)
  },
  deleteUserGroup(params){
    return axios.delete(path.userGroup+params+'/')
  },

}