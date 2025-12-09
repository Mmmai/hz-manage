<template>
  <div class="asset-config-layout">
    <el-container class="full-height">
      <el-aside width="200px" class="aside">
        <div class="logo">
          <h3>资产配置</h3>
        </div>
        <el-scrollbar>
          <el-menu
            :default-active="activeMenu"
            class="el-menu-vertical"
            @select="handleMenuSelect"
          >
            <template v-for="menu in assetMenus" :key="menu.name">
              <el-sub-menu
                v-if="menu.children && menu.children.length > 0"
                :index="menu.name"
              >
                <template #title>
                  <el-icon v-if="menu.icon">
                    <iconifyOffline :icon="menu.icon" />
                  </el-icon>
                  <span>{{ menu.label }}</span>
                </template>
                <template v-for="child in menu.children" :key="child.name">
                  <el-sub-menu
                    v-if="child.children && child.children.length > 0"
                    :index="child.name"
                  >
                    <template #title>
                      <el-icon v-if="child.icon">
                        <iconifyOffline :icon="child.icon" />
                      </el-icon>
                      <span>{{ child.label }}</span>
                    </template>
                    <el-menu-item
                      v-for="grandChild in child.children"
                      :key="grandChild.name"
                      :index="grandChild.name"
                    >
                      <el-icon v-if="grandChild.icon">
                        <iconifyOffline :icon="grandChild.icon" />
                      </el-icon>
                      <span>{{ grandChild.label }}</span>
                    </el-menu-item>
                  </el-sub-menu>
                  <el-menu-item v-else :index="child.name">
                    <el-icon v-if="child.icon">
                      <iconifyOffline :icon="child.icon" />
                    </el-icon>
                    <span>{{ child.label }}</span>
                  </el-menu-item>
                </template>
              </el-sub-menu>
              <el-menu-item v-else :index="menu.name">
                <el-icon v-if="menu.icon">
                  <iconifyOffline :icon="menu.icon" />
                </el-icon>
                <template #title>{{ menu.label }}</template>
              </el-menu-item>
            </template>
          </el-menu>
        </el-scrollbar>
      </el-aside>

      <el-main class="main-content">
        <!-- 使用 router-view 替代动态组件 -->
        <router-view>
          <template #default="{ Component, route }">
            <keep-alive :include="keepAliveName">
              <component :is="Component" :key="route.path" />
            </keep-alive>
          </template>
        </router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useStore } from "vuex";
import { useRoute, useRouter } from "vue-router";
import iconifyOffline from "@/components/iconifyOffline.vue";
import { storeToRefs } from "pinia";
import { useKeepAliveStore } from "@/store/keepAlive";
const keepAliveStore = useKeepAliveStore();
const { keepAliveName } = storeToRefs(keepAliveStore);
import { useElementPlusTheme } from "use-element-plus-theme";
useElementPlusTheme("#749bc7"); // 初始化主题色
import { useDark, useToggle, useStorage } from "@vueuse/core";
import { onUnmounted } from "vue";
const isDark = useDark();
useToggle(isDark);
const route = useRoute();
const router = useRouter();

const store = useStore();

// 当前激活的菜单
const activeMenu = computed(() => {
  // 从路由中获取当前激活的菜单
  const routeName = route.name;
  if (!routeName) return "";

  // 移除前缀以匹配菜单项名称
  if (typeof routeName === "string" && routeName.startsWith("cmdb_only_")) {
    return routeName.replace("cmdb_only_", "");
  }
  return routeName.toString();
});

// 菜单列表
const menuList = computed(() => {
  return store.state.menuInfo || [];
});
// 只保留资产配置相关的菜单
const assetMenus = computed(() => {
  // 查找"资产配置"顶级菜单项
  const assetMenu = menuList.value.find((menu) => menu.name === "cmdb");
  if (assetMenu && assetMenu.children) {
    return assetMenu.children;
  }
  // 如果没有找到cmdb顶级菜单，则查找所有与资产配置相关的菜单项
  return menuList.value.filter(
    (menu) =>
      menu.name === "cidata" ||
      menu.name === "cimodelManage" ||
      menu.parentid_id === "cmdb" ||
      menu.parentid_id === "cimodelManage"
  );
});
console.log("菜单", assetMenus.value);

// 查找菜单项
const findMenu = (menus, name) => {
  for (const menu of menus) {
    if (menu.name === name) {
      return menu;
    }
    if (menu.children && menu.children.length > 0) {
      const found = findMenu(menu.children, name);
      if (found) {
        return found;
      }
    }
  }
  return null;
};

// 处理菜单选择
const handleMenuSelect = async (index) => {
  // 查找选中的菜单项
  const menu = findMenu(menuList.value, index);
  if (menu) {
    // 使用路由跳转替代动态组件加载
    router.push({
      name: `cmdb_only_${menu.name}`,
    });
  }
};
let originalBgColor = ref("");

// 初始化菜单数据
onMounted(async () => {
  // 如果菜单数据为空，获取菜单数据
  if (!store.state.menuInfo || store.state.menuInfo.length === 0) {
    try {
      await store.dispatch("getRoleMenu", { role: store.state.role });
    } catch (error) {
      console.error("获取菜单失败:", error);
    }
  }
});
// 新增：组件卸载时移除CMDB专用暗黑主题类，避免影响其他页面
onUnmounted(() => {
  // document.documentElement.classList.remove("cmdb-dark-theme");
});
</script>

<style scoped>
/* CMDB独立暗黑主题 */
.asset-config-layout {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.full-height {
  height: 100%;
}

.aside {
  background-color: var(--el-menu-bg-color);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.el-menu-vertical {
  border: none;
  height: calc(100% - 60px);
}

.main-content {
  padding: 10px;
  height: 100%;
  overflow: auto;
  display: flex;
}

:deep(.el-main) {
  background-color: var(--el-menu-bg-color);
}

.view-container {
  display: flex;
  height: 100%;
  border-radius: 4px;
  padding: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.welcome-container {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-menu-item [class^="el-icon"] {
  margin-right: 8px;
}

.el-sub-menu [class^="el-icon"] {
  margin-right: 8px;
}
</style>