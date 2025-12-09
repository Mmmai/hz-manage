import { createRouter, createWebHashHistory } from 'vue-router'
//createWebHashHistory
import dealWithRoute from './dynamicRoute'
import { computed, ref } from 'vue'
import store from '../store/index'
import useConfigStore from "@/store/config";

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
    redirect: '/cmdb_only/cmdb/cidata',

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

// console.log(router.getRoutes())
// 路由守卫
router.beforeEach(async (to, from, next) => {

  // 延迟获取store实例，确保Pinia已正确安装
  const configStore = useConfigStore();

  let token = JSON.parse(localStorage.getItem('configs'))?.token;
  if (to.path === '/login') {
    if (token) {
      next('/')
    } else {
      next();
    }
  } else {
    if (token === null || token === '') {
      next('/login');
    } else {
      // 获取路由
      // const dynamicCreateRoute = store.state.dynamicCreateRoute
      // 判断是否要获取新的路由
      if (!configStore.dynamicCreateRoute) {
        // 获取动态路由
        // await store.dispatch('getRouteInfoAction', {role:store.state.role})
        try {
          // await store.dispatch('getRoleMenu', { role: store.state.role })
          await configStore.getMenuInfo()
          configStore.setDynamicCreateRoute(true)
          // console.log(store.state.menuInfo)
          // const drouteinfo = store.state.routeInfo
          if (configStore.menuInfo.length === 0) {
            next('/login')
            return
          }
          dealWithRoute(configStore.menuInfo, publicRoute)

          // print()
          next({ ...to, replace: true })
        } catch (error) {
          // 处理token认证失败的情况
          console.error('获取菜单信息失败:', error);

          // 添加重试次数限制，避免无限循环
          const retryCount = sessionStorage.getItem('menuRetryCount') || '0';
          const newRetryCount = parseInt(retryCount) + 1;

          // 如果重试次数超过3次，则跳转到登录页
          if (newRetryCount > 3) {
            sessionStorage.removeItem('menuRetryCount');
            // 清除本地存储的token等信息
            localStorage.removeItem('configs');
            ElMessage.error('获取菜单信息失败，请重新登录');
            next('/login');
            return;
          }

          // 记录重试次数
          sessionStorage.setItem('menuRetryCount', newRetryCount.toString());

          // 延迟一段时间再重试
          setTimeout(() => {
            next('/login');
          }, 1000);
          return;
        }
      }
      else {
        // 判断路由中的权限
        // if (to.meta.role) {
        //   let allowRoleList = to.meta.role
        //   let hasRoleList = allowRoleList.filter(item => configStore.role.includes(item))
        //   // console.log(123)
        //   // console.log
        //   if (hasRoleList.length == 0) {
        //     next('/login');
        //   } else {
        //     next();
        //   }
        // } else {
        next();
        // }
      }

      // next()



    }
  }
});


export default router