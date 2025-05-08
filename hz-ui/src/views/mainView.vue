<template>
  <div class="common-layout">
    <el-container>
      <!-- <el-scrollbar> -->
      <asideCom />
      <!-- </el-scrollbar> -->
      <el-container class="l-container">
        <el-header>
          <headerCom />
        </el-header>
        <!-- <tabNewCom /> -->
        <tabNewCom />

        <el-main>
          <!-- <el-scrollbar> -->
          <!-- <tabCom /> -->

          <!-- <router-view></router-view> -->
          <!-- <keep-alive include="lokiView">
                  <component :is="Component" />
                </keep-alive> -->

          <!-- <component
                  :is="Component"
                  :key="route.path"
                  v-if="!['model', 'iframe'].includes($route.name)"
                /> -->
          <router-view>
            <template #default="{ Component, route }">
              <KeepAlive :include="keepAliveName">
                <component :is="Component" :key="route.path" />
              </KeepAlive>
            </template>
          </router-view>
          <!-- <iframe-view v-show="route.meta.is_iframe"></iframe-view>
          <router-view v-if="['model'].includes($route.name)"></router-view> -->
          <!-- </el-scrollbar> -->
        </el-main>
        <el-footer class="efooter">
          <el-text tag="p">
            {{ `2024 © 智维_${appVersion} By 工程售后服务中心-技术管理室` }}
          </el-text>
        </el-footer>
      </el-container>
    </el-container>
  </div>
</template>
<script setup lang="ts">
import headerCom from "../components/layout/headerCom.vue";
import asideCom from "../components/layout/asideCom.vue";
import tabNewCom from "../components/layout/tabNewCom.vue";
import iframeView from "./iframeView.vue";
import { onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getCurrentInstance, ref, nextTick, provide } from "vue";
const { proxy } = getCurrentInstance();
import { useKeepAliveStore } from "@/store/keepAlive";
// import router from '../router';
// proxy.$api.test().then(res => {
//   console.log(res)
// })
import { storeToRefs } from "pinia";
import { useStore } from "vuex";
import { computed } from "@vue/reactivity";
import useConfigStore from "@/store/config";
const configStore = useConfigStore();
const keepAliveStore = useKeepAliveStore();
const { appVersion } = storeToRefs(configStore);
const { keepAliveName } = storeToRefs(keepAliveStore);
const store = useStore();
// const appVersion = ref(process.env.APP_VERSION);
const route = useRoute();
const router = useRouter();
const noKeepAliveName = computed(() => {
  return route.matched
    .filter((record) => !record.meta.keepalive)
    .map((record) => record.name);
});
// import { RouterLink, RouterView } from 'vue-router'
const isRouterShow = ref(true);
const refreshCurrentPage = (val: boolean) => (isRouterShow.value = val);
provide("refresh", refreshCurrentPage);

onMounted(async () => {
  await configStore.getAppVersion();
  // await store.dispatch("getSecret");
  // console.log("route", route);
  // console.log("router", router, router.getRoutes());
});
</script>
<style scoped lang="scss">
header {
  /* 元素呈现为块级弹性框 */
  display: flex;
  justify-content: space-between;
  align-items: center;
  /* width: 100%; */
}

.el-header {
  padding: 0px 5px;
  border-bottom: 1px solid #dcdcdc;
  height: $headerHeight;
}

.common-layout {
  height: 100%;
  display: flex;
  // flex-direction: column;

  // &>.el-container {
  //   height: 100%;
  // }

  .el-main {
    padding: 10px 12px;
    // height: $mainHeight;
    // height: 100%;
    // overflow: hidden;
    flex: 1;
    /* border: 2px solid #DCDCDC; */
    background-color: var(--el-bg-color-page);
    display: flex;
    gap: 10px;
  }
}

.el-footer {
  height: 20px;
}

.l-container {
}

/* .el-header{
  padding: 0px 5px;
  background-color: #fff;
  border-bottom: 1px solid #DCDCDC;
}

.common-layout {
  height: 100%;
  & > .el-container {
    height: 100%;
  }
  .el-main {
    padding: 20px;
    border: 10px solid #f3f3f3;

  }
} */
.efooter {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>