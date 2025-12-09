import axios from '../utils/request'
const path = {
  login: "/api/v1/login/",
  test: "/api/v1/test",
  user: "/api/v1/userinfo/",
  userGroup: "/api/v1/userGroup/",

  role: "/api/v1/role/",
  menuInfo: "/api/v1/menuinfo/",
  menuList: "/api/v1/getMenu/",
  menu: "/api/v1/menu/",
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


  test() {
    return axios.get(path.test)
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
  // 获取角色关联权限的树状
  getPermissionToRole(params) {
    return axios.request({
      url: '/api/v1/getPermissionToRole/',
      method: 'post',
      data: params
    })
    // return axios.post(path.role)}
  },

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
  // 获取用户、用户组、角色权限列表
  getPermissionHas(params) {
    // user_id,user_group_id,role_id
    return axios.request({
      url: '/api/v1/permission/get_permission/',
      method: 'get',
      params: params
    })
  },
  // 添加按钮菜单权限
  addObjectPermissions(params) {
    // user_id,user_group_id,role_id
    // {"role_id":1,"button_ids":[]}
    return axios.request({
      url: '/api/v1/permission/add_permissions/',
      method: 'post',
      data: params
    })
  },
  // 删除按钮菜单权限
  removeObjectPermissions(params) {
    // user_id,user_group_id,role_id
    // {"role_id":1,"button_ids":[]}
    return axios.request({
      url: '/api/v1/permission/remove_permissions/',
      method: 'post',
      data: params
    })
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