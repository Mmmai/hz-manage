import axios from '../utils/request'
import path from './path'

// 登录
function login(params) {
    return axios.request({
        url: path.login,
        method: 'post',
        data: params
    })
}


function test() {
    return axios.get(path.test)
}
function user(config) {
    return axios.request({
        url: path.user,
        method: 'get',
        params: config
    })

}
function useradd(params) {
    return axios.post(path.user, params)
}
function userupdate(params) {
    return axios.put(path.user + params.id + '/', params)
}
function userdel(params) {
    return axios.delete(path.user + params + '/')
}
function usermuldel(data) {
    // return axios.delete(path.user+'multiple_delete/',data)
    return axios.request({
        url: path.user + 'multiple_delete/',
        method: 'delete',
        data: data
    })
}
function getRole(params) {
    return axios.request({
        url: path.role,
        method: 'get',
        params: params
    })
    // return axios.post(path.role)}
}
function roledel(params) {
    return axios.delete(path.role + params + '/')
}
function roleadd(params) {
    return axios.request({
        url: path.role,
        method: 'post',
        data: params
    })
    // return axios.post(path.role)}
}
function roleupdate(params) {
    // return axios.put(path.role+params.id+'/',params)
    return axios.request({
        url: path.role + params.id + '/',
        method: 'patch',
        data: params
    })
}

export {
    login,
    test,
    user,
    useradd,
    userupdate,
    userdel,
    usermuldel,
    getRole,
    roledel,
    roleadd,
    roleupdate,
}