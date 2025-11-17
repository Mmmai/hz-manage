import axios from 'axios'
import querystring from "querystring"
const instance = axios.create({
  timeout: 120 * 1000
})

axios.defaults.withCredentials = true;
const errorHandle = (status, info) => {
  switch (status) {
    // case 400:
    //   console.log("语义有误");
    // break;
    case 401:
      console.log("服务器认证失败");
      break;
    case 403:
      console.log("服务器拒绝访问");
      break;
    case 404:
      console.log("地址错误");
      break;
    case 500:
      console.log("服务器遇到意外");
      break;
    case 502:
      console.log("服务器无响应");
      break;
    default:
      console.log(info)
      break;
  }
}


// 拦截器
// 发送数据之前
instance.interceptors.request.use(
  // config: 包含网络请求的所有信息
  (config) => {
    // if(config.method === "post"){
    //   console.log(config.data)
    //   config.data = querystring.stringify(config.data)
    //   console.log(config.data)
    config.startTime = Date.now();
    // }
    let token = JSON.parse(localStorage.getItem('configs'))?.token
    if (token) {
      config.headers.token = token
      // console.log(localStorage.getItem('token'))
    }
    return config;
  },
  (error) => {

    return Promise.reject(error)
  })
// 获取数据之前
instance.interceptors.response.use(
  (response) => {
    const endTime = Date.now();
    const costTime = endTime - response.config.startTime;
    response.costTime = costTime
    // return response.data.staus == 200 ? Promise.resolve(response) : Promise.reject(response)
    // 检查响应数据中是否有token过期的相关信息
    if (response.data && response.data.status === 403) {
      // token过期，清除本地存储并跳转到登录页
      alert.error('登录已过期，请重新登录')
      localStorage.clear()

      // 延迟跳转以确保消息能被看到
      setTimeout(() => {
        // 如果使用Vue Router，可以这样跳转
        if (window.location.hash) {
          window.location.hash = '#/login'
        } else {
          window.location.href = '/#/login'
        }
      }, 1500)

      return Promise.reject(response)
    }
    return Promise.resolve(response)
  },
  (error) => {
    if (error.code === 'ECONNABORTED') {
      // 超时处理，返回一个Promise，可以返回一个自定义的结果对象
      return Promise.resolve({
        timeout: true,
        message: '请求超时',
      });
    }
    const { response } = error;

    // errorHandle(response.status,response.data)
    return response
  }
)


export default instance;