<template>
  <div class="top-tags">
    <el-tag
      :key="tag.name"
      v-for="(tag, index) in tags"
      :closable="tag.name !== 'home'"
      :disable-transitions="false"
      size="large"
      :effect="isDark(tag)"
      @click="changeMenu(tag)"
      @close="handleClose(tag, index)"
    >
      {{ tag.label }}
    </el-tag>
  </div>
</template>
<!-- :effect="$route.name === tag.name ? 'dark' : 'plain'" -->
<!-- <script setup> -->
<script  setup>
import { computed, ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useStore } from "vuex";
const store = useStore();
const isDark = (tag) => {
  if (tag.is_info) {
    if (route.path === tag.path) {
      return "dark";
    } else {
      return "plain";
    }
  } else {
    if (route.name === tag.name) {
      return "dark";
    } else {
      return "plain";
    }
  }
};
// const isUse = computed(()=>{
//   if ()
// })
// const store = useStore()
const tags = computed(() => {
  // return store.state.menuInfo.slice(0,1)
  return store.state.tagList;
});
// 定义router使用方法
const router = useRouter();
// 获取当前路由信息
const route = useRoute();

// tab菜单点击跳转路由
const changeMenu = (item) => {
  console.log(item);
  if (item.is_info) {
    console.log(item);
    router.push({ path: item.path, query: item.query });
  } else {
    router.push({ name: item.name });
  }
  store.commit("updateBreadcrumb", item);
};
const handleClose = (tag, index) => {
  let tagsLen = tags.value.length - 1;
  tags.value.splice(tags.value.indexOf(tag), 1);
  store.commit("updateTagList", tags.value);
  console.log(store.state.tagList);
  console.log(route.name);
  // 判断路由,当删除的tab是当前，则切换到上一个tab
  if (tag.name != route.name) {
    return;
  }
  if (index == tagsLen) {
    if (tags.value[index - 1].is_info) {
      router.push({
        path: tags.value[index - 1].path,
        query: tags.value[index - 1].query,
      });
    } else {
      router.push({ name: tags.value[index - 1].name });
    }
    // router.push({
    //   name: tags.value[index - 1].name
    // });
    // 更新，面包屑
    // store更新
    store.commit("updateBreadcrumb", tags.value[index - 1]);
  } else {
    if (tags.value[index].is_info) {
      router.push({
        path: tags.value[index].path,
        query: tags.value[index].query,
      });
    } else {
      router.push({ name: tags.value[index].name });
    }
    // router.push({
    //   name: tags.value[index].name
    // });
    // 更新，面包屑
    // store更新
    store.commit("updateBreadcrumb", tags.value[index]);
  }
};
// 监听刷新界面
const beforeUnload = () => {
  window.addEventListener("beforeunload", () => {
    console.log("测试刷新");
  });
};
// const afterUnload = ()=>{
//   window.addEventListener("beforeunload", () => {
//     console.log('测试刷新')
//   })
// }

// onMounted(()=>{
//   beforeUnload();
//   console.log(store.state.tagList)

// })
</script>

<style scoped>
.top-tags {
  padding: 5px 5px;
  border-bottom: 1px solid #dcdcdc;
  margin: 5px;
}
.el-tag {
  margin-right: 5px;
}
</style>