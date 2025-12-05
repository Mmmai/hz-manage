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

        <el-main
          ref="mainRef"
          v-loading="isRefreshing"
          class="scroll-container"
          element-loading-text="页面刷新中..."
        >
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
              <keep-alive :include="keepAliveName">
                <component
                  :is="Component"
                  :key="`${route.path}-${refreshKey}`"
                />
              </keep-alive>
            </template>
          </router-view>
          <!-- <iframe-view v-show="route.meta.is_iframe"></iframe-view>
          <router-view v-if="['model'].includes($route.name)"></router-view> -->
          <!-- </el-scrollbar> -->
          <el-backtop target=".scroll-container" :right="40" :bottom="40" />
        </el-main>
        <el-footer class="efooter">
          <el-text tag="p">
            {{ `2025 © 智维_${appVersion} By 工程售后服务中心-技术管理室` }}
          </el-text>
        </el-footer>
      </el-container>
    </el-container>
  </div>
</template>
<script setup lang="ts">
// ... existing code ...
import headerCom from "../components/layout/headerCom.vue";
import asideCom from "../components/layout/asideCom.vue";
import tabNewCom from "../components/layout/tabNewCom.vue";
import iframeView from "./fromOtherView.vue";
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getCurrentInstance, nextTick, provide } from "vue";
const { proxy } = getCurrentInstance();
// import router from '../router';
// proxy.$api.test().then(res => {
//   console.log(res)
// })
import { storeToRefs } from "pinia";
import { useStore } from "vuex";
import { computed } from "@vue/reactivity";
import useConfigStore from "@/store/config";
const configStore = useConfigStore();
import { useKeepAliveStore } from "@/store/keepAlive";
const keepAliveStore = useKeepAliveStore();
const { keepAliveName } = storeToRefs(keepAliveStore);

const { appVersion } = storeToRefs(configStore);
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

// 添加刷新状态
const isRefreshing = ref(false);
// 添加刷新key
const refreshKey = ref(0);
// 添加main区域引用
const mainRef = ref();

// 刷新方法
const forceRefresh = () => {
  refreshKey.value = Date.now();
};

// 提供刷新方法给子组件
provide("forceRefresh", forceRefresh);

// 监听刷新事件
const handleRefreshStart = () => {
  isRefreshing.value = true;
};

const handleRefreshFinish = () => {
  isRefreshing.value = false;
};

// 监听强制刷新事件
const handleForceRefresh = () => {
  forceRefresh();
};

onMounted(async () => {
  await configStore.getAppVersion();
  // 监听刷新事件
  window.addEventListener("refresh-page", handleRefreshStart);
  window.addEventListener("refresh-page-finished", handleRefreshFinish);
  // 监听强制刷新事件
  window.addEventListener("force-refresh", handleForceRefresh);
  // await store.dispatch("getSecret");
  // console.log("route", route);
  // console.log("router", router, router.getRoutes());
});

// 清理事件监听器
// 如果需要在组件卸载时清理，可以使用 onUnmounted 钩子
</script>
// ... rest of the code ...
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
  background-color: var(--el-bg-color);
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
    background-color: var(--el-bg-color);
    display: flex;
    gap: 10px;
    justify-content: center;
  }
}

.el-footer {
  height: 20px;
  background-color: var(--el-bg-color);
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