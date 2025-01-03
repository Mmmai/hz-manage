//处理树形数据
//dealWithRoute.js

import {
  pa
} from 'element-plus/es/locale/index.mjs';
import router from './index';
import {
  RouterView
} from "vue-router";
let modules =
  import.meta.glob('../views/*.vue')
let infoModules =
  import.meta.glob('../views/infoviews/*.vue')
const dealWithRoute1 = (data, parent = 'main') => {

  for (let item of data) {
    console.log(item)
    // if (item.name === 'loki') continue;
    //多级菜单
    if (item.children && item.children.length > 0) {
      router.addRoute(parent, {
        path: item.name,
        name: item.name,
        component: RouterView,
        meta: item.meta
      })
      dealWithRoute(item.children, item.name)

    } else { //一级菜单
      if (item.has_info) {
        console.log(111)
        router.addRoute(parent, {
          path: item.path + '/:id',
          name: item.name + '_info',
          component: infoModules[`../views/infoviews/${item.info_view_name}View.vue`],
          // component: () => import(`../views/${item.component}`),
          meta: item.meta
        });
      }
      router.addRoute('main', {
        path: item.path,
        name: item.name,
        component: modules[`../views/${item.name}View.vue`],
        // component: () => import(`../views/${item.component}`),
        meta: item.meta
      });


    }
  }
};

const forMenuRoute = (data, mainObject, parent = '') => {
  for (let item of data) {
    let pstr = parent + '/' + item.name
    // if (! item.status) return 
    if (item.is_menu) {
      if (item.is_iframe){
        mainObject.children.push({
          path: '/iframe',
          name: item.name,
          component: modules[`../views/iframeView.vue`],
          // component: () => import(`../views/${item.component}`),
          meta: item.meta
        })
      }else{
        mainObject.children.push({
          path: pstr,
          name: item.name,
          component: modules[`../views/${item.name}View.vue`],
          // component: () => import(`../views/${item.component}`),
          meta: item.meta
        })
      }

      if (item.has_info) {
        // let _tempMeta = item.meta
        // _tempMeta.title = item.meta.title + ''

        mainObject.children.push({
          path: pstr + '/:id',
          name: item.name + '_info',
          // name: item.name,

          component: infoModules[`../views/infoviews/${item.info_view_name}View.vue`],
          // component: () => import(`../views/${item.component}`),
          
          meta: {isInfo:true,...item.meta}
        })
      }
    } else {

      if (item.children && item.children.length > 0) {

        forMenuRoute(item.children, mainObject, pstr)
      }
    }
  }
}

const dealWithRoute = (data,obj) => {
  // let mainObject = {
  //   name: 'main',
  //   path: '/',
  //   redirect: '/home',
  //   component: () => import('../views/mainView.vue'),
  //   children: [],
  // }
  let mainObject  = obj.filter(item => item.name === 'main')[0]
  // forMenuRoute(data,mainObject,'main')
  forMenuRoute(data, mainObject)
  // console.log("获取路由后",mainObject)
  router.addRoute(mainObject)
  // console.log("router", router, router.getRoutes());
}

export default dealWithRoute;