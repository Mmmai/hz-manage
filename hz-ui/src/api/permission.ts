import axios from '../utils/request'
// import path from './path'
const path = {
  access: '/api/v1/access/',
  menu: '/api/v1/access/menu/',
  button: '/api/v1/access/button/'
}
export default {
  // 菜单按钮
  // 查看单个menu信息
  getMenuTree(params) {
    return axios.request({
      url: path.menu + 'get_menu_tree/',
      method: 'get',
    })
  },
  getMenuList(params) {
    return axios.request({
      url: path.access + 'getMenu/',
      method: 'post',
      data: params

    })
  },
  menuUpdate(params) {
    return axios.request({
      url: path.menu + params.id + '/',
      method: 'patch',
      data: params
    })
  },
  menuAdd(params) {
    // return axios.put(path.role+params.id+'/',params)
    return axios.request({
      url: path.menu,
      method: 'post',
      data: params
    })
  },
  menuDel(params) {
    return axios.delete(path.menu + params + '/')
  },
  // 按钮
  getButton(params) {
    return axios.request({
      url: path.button,
      method: 'get',
      params: params

    })
  },
  updateButton(params) {
    return axios.request({
      url: path.button + params.id + '/',
      method: 'patch',
      data: params
    })
  },
  addButton(params) {
    // return axios.put(path.role+params.id+'/',params)
    return axios.request({
      url: path.button,
      method: 'post',
      data: params
    })
  },
  deleteButton(params) {
    return axios.delete(path.button + params + '/')
  },
  // nodes
  getDataScope(params) {
    return axios.request({ url: path.access + 'data_scope/', method: 'get', params: params })
  },
  getDataScopeAll(params) {
    return axios.request({ url: path.access + 'data_scope/aggregated_permissions/', method: 'get', params: params })
  },
  setDataScope(params) {
    // {role:xxx,scope_type:xxx,targets:[{}] }
    return axios.request({ url: path.access + 'data_scope/', method: 'post', data: params })
  },
  // 获取用户、用户组、角色权限列表
  getPermissionHas(params) {
    // user_id,user_group_id,role_id
    return axios.request({
      url: path.access + 'get_permission/',
      method: 'get',
      params: params
    })
  },
  // 添加按钮菜单权限
  addObjectPermissions(params) {
    // user_id,user_group_id,role_id
    // {"role_id":1,"button_ids":[]}
    return axios.request({
      url: path.access + 'permission/add_permissions/',
      method: 'post',
      data: params
    })
  },
  // 删除按钮菜单权限
  removeObjectPermissions(params) {
    // user_id,user_group_id,role_id
    // {"role_id":1,"button_ids":[]}
    return axios.request({
      url: path.access + 'permission/remove_permissions/',
      method: 'post',
      data: params
    })
  },
}