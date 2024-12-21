

<template>
  <router-view></router-view>
</template>
<script setup lang="ts">
// import { RouterLink, RouterView } from 'vue-router'
</script>
<style lang="scss">
html,
body {
  height: 100%;
  margin: 0px;
  /* 滚动条 */
  body *::-webkit-scrollbar {
    width: 5px;
    height: 5px;
  }
  body *::-webkit-scrollbar-track {
    background: #fff;
    border-radius: 2px;
  }
  body *::-webkit-scrollbar-thumb {
    background: rgb(205, 206, 206);

    border-radius: 10px;
  }
  body *::-webkit-scrollbar-thumb:hover {
    background: #333;
  }
  body *::-webkit-scrollbar-corner {
    background: #fff;
  }
}
#app {
  min-height: 100%;
  height: 100%;
}
.el-drawer__header {
  margin-bottom: 0px !important;
}
// .el-divider--horizontal {
//   margin: 20px 0 !important;
// }
</style>
