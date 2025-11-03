import { createRouter, createWebHashHistory } from 'vue-router'
//createWebHashHistory
import dealWithRoute from './dynamicRoute'
// const store = useStore()
import store from '../store/index'

// 路由和vue视图的对应关系
const publicRoute = [
  {
    path: '/login',
    name: 'login',
    // redirect:'/',
    component: () => import('../views/loginView.vue'),
  },
  {
    path: '/cmdb_only',
    name: 'cmdb_only',
    component: () => import('../views/cmdbForUops.vue'),
    children: []
  },
  {
    // path: '/:error*', // /:error -> 匹配 /, /one, /one/two, /one/two/three, 等
    path: '/:catchAll(.*)',
    // name: '404',
    component: () => import('@/views/404.vue')
  },
  {
    name: 'main',
    path: '/',
    redirect: '/home',
    component: () => import('../views/mainView.vue'),
    children: [],
  }
]


const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: publicRoute
})
// console.log(router.getRoutes())

// router.addRoute({ name: 'admin', path: '/admin', component: () => import('../views/lokiView.vue') })
// router.addRoute('admin', { path: 'settings', component: () => import('../views/lokiView.vue') })
// router.addRoute({
//   name: 'main',
//   path: '/',
//   redirect: '/home',
//   component: () => import('../views/mainView.vue') ,
//   children: [{ path: '/log/loki',name:"loki", component: () => import('../views/lokiView.vue')  },
//     { path: '/home', name:'home',component: () => import('../views/homeView.vue')  }
//   ],
// })
// console.log("xxssdad")
// console.log(router.getRoutes())
// 路由守卫
router.beforeEach(async (to, from, next) => {
  if (to.path === '/login') {
    if (localStorage.getItem('token')) {
      next('/')
    } else {
      next();
    }
  } else {
    let token = localStorage.getItem('token');
    if (token === null || token === '') {
      next('/login');
    } else {
      // console.log('判断是否获取动态路由')

      // 获取路由
      const dynamicCreateRoute = store.state.dynamicCreateRoute
      // 判断是否要获取新的路由
      if (!dynamicCreateRoute) {
        console.log('获取动态路由')
        store.commit("updateDynamicCreateRoute", true)
        // 获取动态路由
        // await store.dispatch('getRouteInfoAction', {role:store.state.role})
        await store.dispatch('getRoleMenu', { role: store.state.role })
        // console.log(store.state.menuInfo)
        // const drouteinfo = store.state.routeInfo
        console.log(store.state.menuInfo)
        if (store.state.menuInfo.length === 0) {
          next('/login')
          return
        }

        dealWithRoute(store.state.menuInfo, publicRoute)

        // print()
        next({ ...to, replace: true })
      } else {
        // 判断路由中的权限
        if (to.meta.role) {
          let currentRoleList = JSON.parse(localStorage.getItem('role'));
          let allowRoleList = to.meta.role
          let hasRoleList = allowRoleList.filter(item => currentRoleList.includes(item))
          // console.log(123)
          // console.log
          if (hasRoleList.length == 0) {
            next('/login');
          } else {
            next();
          }
        } else {
          next();
        }
      }

      // next()



    }
  }
});


export default router
