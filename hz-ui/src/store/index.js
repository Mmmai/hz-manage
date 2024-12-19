import {
  createStore
} from "vuex"
import api from '../api/index'

// Vuex的核心作用就是管理组件之间的状态管理
export default createStore({
  state: {
    counter: 0,
    isCollapse: true,
    currentMenu: localStorage.getItem('currentMenu') ? localStorage.getItem('currentMenu')  : '',

    // currentMenu: localStorage.getItem('currentMenu') ? JSON.parse(localStorage.getItem('currentMenu'))  : '',
    token: localStorage.getItem('token') ? localStorage.getItem('token') : '',
    role: localStorage.getItem('role') ? JSON.parse(localStorage.getItem('role')) : '',
    username: localStorage.getItem('username') ? localStorage.getItem('username') : '',
    userinfo: localStorage.getItem('userinfo') ? JSON.parse(localStorage.getItem('userinfo')) : '',

    // 动态菜单
    dynamicCreateRoute: false,
    routeInfo: [],
    // 菜单栏
    menuInfo: [],
    // tagList: []
    tagList: localStorage.getItem('tagList') ? JSON.parse(localStorage.getItem('tagList')) : [],
  },
  getters: {},
  // 更新数据
  mutations: {
    // 左侧菜单收缩
    changeIsCollapse(state) {
      // 取相反值
      state.isCollapse = !state.isCollapse
    },
    // 面包屑,左侧菜单点击会触发tag更新
    selectMenu(state, val) {
      // localStorage.setItem('currentMenu', JSON.stringify(val));
      if (val.name == 'home') {
        // localStorage.setItem('currentMenu', '');

        return 
      } else {
        state.currentMenu = val.label
        localStorage.setItem('currentMenu', val.label);
        console.log(123)
        console.log(val)
        // tab标签判断
        let result = state.tagList.findIndex(item => item.name === val.name)

        // JSON.parse(localStorage.getItem('tagList'))
        if (val.is_info){
          let result = state.tagList.findIndex(item => item.path === val.path)
          if (result == -1){
            state.tagList.push(val)
            localStorage.setItem('tagList', JSON.stringify(state.tagList));
          }
        }else{
          let result = state.tagList.findIndex(item => item.name === val.name)
          if (result == -1){
            state.tagList.push(val)
            localStorage.setItem('tagList', JSON.stringify(state.tagList));
          }
        }
        // state.tagList.forEach(item => {
        //   if (item.is_info){
            
        //   }else{

        //   }
          
        // });

        // result == -1 ? state.tagList.push(val) : ''

      }
    },
    // tag标签点击切换
    updateBreadcrumb(state, val) {
      // localStorage.setItem('currentMenu', JSON.stringify(val));
      state.currentMenu = val.label
      localStorage.setItem('currentMenu', val.label);
      // console.log(localStorage.getItem('currentMenu'))
    },

    // tag标签更新
    updateTagList(state, val) {
      state.tagList = val
      localStorage.setItem('tagList', JSON.stringify(val));
      // state.currentMenu = val.name
      // console.log(val.name)
    },
    updateCurrentUsername(state, val) {
      // state.username = val
      state.username = val;
      localStorage.setItem('username', val)
    },

    // 存储token
    addToken(state, config) {
      // 修改token，并将token存入localStorage
      state.token = config.token;
      localStorage.setItem('token', config.token);
      state.role = config.role;
      localStorage.setItem('role', JSON.stringify(config.role));
      // 存储username信息
      state.userinfo = config.userinfo;
      localStorage.setItem('userinfo', JSON.stringify(config.userinfo));

    },
    updateUsername(state, config) {
      state.username = config
    },
    // 更新动态路由获取flag
    updateDynamicCreateRoute(state, flag) {
      state.dynamicCreateRoute = flag
    },
    setRouteInfo(state, config) {
      state.routeInfo = config
    },
    // 更新菜单列表
    setRoleMenu(state, config) {
      // 禁用的菜单不显示
      state.menuInfo = config.filter(item => item.status )
      // console.log(config)
      // config.forEach(item => {
      //   if (item.name === 'home'){
      //     localStorage.setItem('tagList', JSON.stringify([item]))
      //   }
        
        
      // });
      // state.tagList = config.slice(0, 1)
    }
    // 当前路由地址


  },
  actions: {
    async getRouteInfoAction({
      commit,
      state
    }, config) {
      let res = await api.getRouteInfo(config)
      console.log(res)
      commit("setRouteInfo", res.data.routeInfo)
    },
    async getRoleMenu({
      commit,
      state
    }, config) {
      // let role = JSON.parse(localStorage.getItem('role'))
      let res = await api.getMenuList(config)
      commit("setRoleMenu", res.data.results)
    }

  }

})