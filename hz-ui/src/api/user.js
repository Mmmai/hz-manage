import axios from '../utils/request'
const path = {
  login: "/api/v1/login/",
  test: "/api/v1/test",
  user: "/api/v1/userinfo/",
  userGroup: "/api/v1/userGroup/",
  role: "/api/v1/role/",
  button: "/api/v1/button/",
  routeInfo: "/api/v1/testroute/",
  portal: "/api/v1/portal/",
  pgroup: "/api/v1/pgroup/",
  // datasource
  dataSource: "/api/v1/datasource/",
  getSecret: "/api/v1/getSecret/",
  sysConfig: "/api/v1/sysconfig/",
}
export default {


  // 登录
  login(params) {
    return axios.request({
      url: path.login,
      method: 'post',
      data: params
    })
  },

  user(config) {
    return axios.request({
      url: path.user,
      method: 'get',
      params: config
    })

  },
  useradd(params) {
    return axios.post(path.user, params)
  },
  userupdate(params) {
    return axios.patch(path.user + params.id + '/', params)
  },
  userdel(params) {
    return axios.delete(path.user + params + '/')
  },
  usermuldel(data) {
    // return axios.delete(path.user+'multiple_delete/',data)
    return axios.request({
      url: path.user + 'multiple_delete/',
      method: 'delete',
      data: data
    })
  },
  getRole(params) {
    return axios.request({
      url: path.role,
      method: 'get',
      params: params
    })
    // return axios.post(path.role)}
  },
  getRoleInfo(params) {
    return axios.request({
      url: path.role + params + '/',
      method: 'get',
    })
    // return axios.post(path.role)}
  },
  roledel(params) {
    return axios.delete(path.role + params + '/')
  },
  roleadd(params) {
    return axios.request({
      url: path.role,
      method: 'post',
      data: params
    })
    // return axios.post(path.role)}
  },
  roleupdate(params) {
    // return axios.put(path.role+params.id+'/',params)
    return axios.request({
      url: path.role + params.id + '/',
      method: 'patch',
      data: params
    })
  },
  // // 获取角色关联权限的树状
  // getPermissionToRole(params) {
  //   return axios.request({
  //     url: '/api/v1/permissions/getPermissionToRole/',
  //     method: 'post',
  //     data: params
  //   })
  //   // return axios.post(path.role)}
  // },

  getUserGroup(config) {
    return axios.request({
      url: path.userGroup,
      method: 'get',
      params: config
    })

  },
  addUserGroup(params) {
    return axios.post(path.userGroup, params)
  },
  updateUserGroup(params) {
    return axios.patch(path.userGroup + params.id + '/', params)
  },
  deleteUserGroup(params) {
    return axios.delete(path.userGroup + params + '/')
  },

  updatePortalOrder(params) {
    return axios.request({
      url: path.portal + 'update_user_sort_order/',
      method: 'post',
      data: params
    })
  },
  // 添加收藏
  addFavorite(params) {
    return axios.request({
      url: path.portal + params.id + '/add_to_favorites/',
      method: 'post',
    })
  },
  // 删除收藏
  removeFavorite(params) {
    return axios.request({
      url: path.portal + params.id + '/remove_from_favorites/',
      method: 'delete'
    })
  },
}