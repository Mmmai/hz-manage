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
          <router-view>
            <template #default="{ Component, route }">
              <keep-alive>
                <component
                  :is="Component"
                  :key="route.path"
                  v-if="!['model', 'iframe'].includes($route.name)"
                />
              </keep-alive>
            </template>
          </router-view>
          <iframe-view v-show="route.meta.is_iframe"></iframe-view>
          <router-view v-if="['model'].includes($route.name)"></router-view>
          <!-- </el-scrollbar> -->
        </el-main>
        <el-footer class="efooter">
          <el-text tag="p">
            2024 © 智维 By 工程售后服务中心-技术管理室
          </el-text>
        </el-footer>
      </el-container>
    </el-container>
  </div>
</template>
<script setup>
import headerCom from "../components/layout/headerCom.vue";
import asideCom from "../components/layout/asideCom.vue";
import tabNewCom from "../components/layout/tabNewCom.vue";
import iframeView from "./iframeView.vue";
import { onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getCurrentInstance } from "vue";
const { proxy } = getCurrentInstance();
// import router from '../router';
// proxy.$api.test().then(res => {
//   console.log(res)
// })
import { useStore } from "vuex";
const store = useStore();

const route = useRoute();
const router = useRouter();
onMounted(async () => {
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