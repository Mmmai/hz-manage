<template>
  <div class="permission-container">
    <el-card class="permission-card">
      <!-- <template #header>
        <div class="card-header">
          <span class="card-title">权限管理系统</span>
          <el-tag type="success" effect="dark">精细化权限控制</el-tag>
        </div>
      </template> -->

      <el-splitter class="main-splitter">
        <el-splitter-panel :min="250" :size="250">
          <div class="left-panel">
            <div class="panel-header">
              <el-text class="panel-title">授权对象</el-text>
              <el-radio-group
                v-model="radio"
                size="small"
                @change="handleRadioChange"
              >
                <el-radio-button label="user">
                  <el-icon><User /></el-icon>
                  <span>用户</span>
                </el-radio-button>
                <el-radio-button label="user_group">
                  <el-icon>
                    <iconifyOffline icon="material-symbols:group-outline" />
                  </el-icon>
                  <span>用户组</span>
                </el-radio-button>
                <el-radio-button label="role">
                  <el-icon><UserFilled /></el-icon>
                  <span>角色</span>
                </el-radio-button>
              </el-radio-group>
            </div>

            <div class="tree-container">
              <el-input
                v-model="filterText"
                placeholder="搜索对象..."
                clearable
                class="search-input"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>

              <el-scrollbar class="tree-scrollbar">
                <el-tree
                  ref="treeRef"
                  class="object-tree"
                  :data="treeData"
                  :props="defaultProps"
                  default-expand-all
                  node-key="id"
                  highlight-current
                  :filter-node-method="filterNode"
                  @node-click="nodeClick"
                >
                  <template #default="{ node, data }">
                    <div class="custom-tree-node">
                      <span>{{ node.label }}</span>
                      <el-tag
                        v-if="data.disabled"
                        type="warning"
                        size="small"
                        effect="plain"
                      >
                        内置对象
                      </el-tag>
                    </div>
                  </template>
                </el-tree>
              </el-scrollbar>
            </div>
          </div>
        </el-splitter-panel>

        <el-splitter-panel :min-size="30">
          <div class="right-panel">
            <div v-if="!nowTreeName" class="empty-placeholder">
              <el-empty description="请选择左侧授权对象" />
            </div>

            <div v-else-if="isProtectedObject" class="protected-object">
              <el-result
                icon="info"
                title="受保护对象"
                sub-title="此对象为系统内置对象，无需配置权限"
              >
                <template #icon>
                  <el-icon class="protected-icon"><Lock /></el-icon>
                </template>
              </el-result>
            </div>

            <div v-else class="permission-config">
              <div class="config-header">
                <div class="header-info">
                  <el-avatar :size="40">{{
                    nowTreeName.charAt(0).toUpperCase()
                  }}</el-avatar>
                  <div class="header-text">
                    <div class="object-name">{{ nowTreeName }}</div>
                    <div class="object-type">
                      <el-tag :type="objectTagType" effect="plain">
                        {{ objectTypeLabel }}
                      </el-tag>
                    </div>
                  </div>
                </div>
              </div>

              <el-tabs
                v-model="activeName"
                type="border-card"
                class="permission-tabs"
                @tab-click="handleClick"
              >
                <el-tab-pane label="菜单授权" name="menu">
                  <menuPermission
                    ref="menuPermissionRef"
                    v-model:nowNodeObject="nowNodeObject"
                    v-model:permissionObject="radio"
                  />
                </el-tab-pane>
                <el-tab-pane label="资产授权" name="cmdb">
                  <!-- <div class="feature-coming">
                    <el-alert
                      title="功能开发中"
                      type="info"
                      description="资产授权功能正在开发中，敬请期待"
                      show-icon
                    />
                  </div> -->
                  <cmdbPermission
                    ref="cmdbPermissionRef"
                    v-model:nowNodeObject="nowNodeObject"
                    v-model:permissionObject="radio"
                  />
                </el-tab-pane>
              </el-tabs>
            </div>
          </div>
        </el-splitter-panel>
      </el-splitter>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import {
  ref,
  computed,
  watch,
  getCurrentInstance,
  onMounted,
  reactive,
  nextTick,
  onBeforeUnmount,
} from "vue";
import type { TabsPaneContext } from "element-plus";
import type { FilterNodeMethodFunction, TreeInstance } from "element-plus";
import menuPermission from "@/components/permission/menuPermission.vue";
import cmdbPermission from "@/components/permission/cmdbPermission.vue";

// 图标引入
import {
  User,
  UserFilled,
  Collection,
  Search,
  Lock,
} from "@element-plus/icons-vue";

interface Tree {
  [key: string]: any;
}

const { proxy } = getCurrentInstance();
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();
const radio = ref("user");
const treeData = ref<Tree[]>([]);
const filterText = ref("");
const treeRef = ref<TreeInstance>();
const menuPermissionRef = ref<typeof menuPermission>();
const cmdbPermissionRef = ref<typeof cmdbPermission>();
const defaultProps = {
  children: "children",
  label: "label",
  disabled: "disabled",
};

// 计算分割器高度
const splitterHeight = computed(() => {
  return window.innerHeight - 200 + "px";
});

// 监听窗口大小变化
const handleResize = () => {
  // 响应式调整将在样式中自动处理
};

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
});

watch(filterText, (val) => {
  treeRef.value!.filter(val);
});

// 根据radio，生成{user_id: xxx}|{user_group_id: xxx}|{role_id: xxx}
const getObjectId = (data) => {
  switch (radio.value) {
    case "user":
      return { user: data };
    case "user_group":
      return { user_group: data };
    case "role":
      return { role: data };
  }
};

const filterNode: FilterNodeMethodFunction = (value: string, data: Tree) => {
  if (!value) return true;
  return data.label.includes(value);
};

const activeName = ref("menu");
const handleClick = (tab: TabsPaneContext, event: Event) => {
  // console.log(tab, event);
};

const nowTreeName = ref("");
const nowNodeObject = ref({});

// 判断是否为受保护对象
const isProtectedObject = computed(() => {
  return ["admin", "sysadmin", "系统管理组"].includes(nowTreeName.value);
});

// 对象类型标签
const objectTypeLabel = computed(() => {
  const labels = {
    user: "用户",
    user_group: "用户组",
    role: "角色",
  };
  return labels[radio.value] || "未知";
});

// 对象标签类型
const objectTagType = computed(() => {
  const types = {
    user: "primary",
    user_group: "success",
    role: "warning",
  };
  return types[radio.value] || "info";
});

const nodeClick = (data: Tree) => {
  nowTreeName.value = data.label;
  nowNodeObject.value = getObjectId(data.id);

  if (isProtectedObject.value) return;

  nextTick(() => {
    menuPermissionRef.value!.getPermissionTreeData();
    menuPermissionRef.value!.getPermissionOnRight();
  });
};

const getUserList = async () => {
  const res = await proxy.$api.user();
  treeData.value = res.data.results.map((item) => ({
    id: item.id,
    label: item.username,
    disabled: item.username === "admin",
  }));
};

const getUserGroupList = async () => {
  const res = await proxy.$api.getUserGroup();
  treeData.value = res.data.results.map((item) => ({
    id: item.id,
    label: item.group_name,
    disabled: item.group_name === "系统管理组",
  }));
};

const getRoleList = async () => {
  const res = await proxy.$api.getRole();
  treeData.value = res.data.results.map((item) => ({
    id: item.id,
    label: item.role,
    disabled: item.role === "sysadmin",
  }));
};

const handleRadioChange = (val) => {
  console.log(111);
  switch (val) {
    case "user":
      getUserList();
      nowTreeName.value = "";
      break;
    case "user_group":
      getUserGroupList();
      nowTreeName.value = "";
      break;
    case "role":
      getRoleList();
      nowTreeName.value = "";
      break;
  }
};
// 新增：处理路由参数，自动选择对应的节点
const handleRouteQuery = async () => {
  // 检查是否存在查询参数
  if (Object.keys(route.query).length > 0) {
    console.log("Route query:", route.query);

    // 根据不同的参数类型处理
    if (route.query.role) {
      // 设置为角色模式
      radio.value = "role";
      // 加载角色列表
      await getRoleList();
      // 设置当前选中节点
      treeRef.value!.setCurrentKey(route.query.role);
      // 获取当前节点信息
      const nowNode = treeRef.value!.getNode(route.query.role);
      if (nowNode) {
        nowTreeName.value = nowNode.data.label;
        nowNodeObject.value = getObjectId(route.query.role);

        // 加载权限数据
        nextTick(() => {
          menuPermissionRef.value?.getPermissionTreeData();
          menuPermissionRef.value?.getPermissionOnRight();
        });
      }
    } else if (route.query.user) {
      // 设置为用户模式
      radio.value = "user";
      // 加载用户列表
      await getUserList();
      // 设置当前选中节点
      treeRef.value!.setCurrentKey(route.query.user);
      // 获取当前节点信息
      const nowNode = treeRef.value!.getNode(route.query.user);
      if (nowNode) {
        nowTreeName.value = nowNode.data.label;
        nowNodeObject.value = getObjectId(route.query.user);

        // 加载权限数据
        nextTick(() => {
          menuPermissionRef.value?.getPermissionTreeData();
          menuPermissionRef.value?.getPermissionOnRight();
        });
      }
    } else if (route.query.user_group) {
      // 设置为用户组模式
      radio.value = "user_group";
      // 加载用户组列表
      await getUserGroupList();
      // 设置当前选中节点
      treeRef.value!.setCurrentKey(route.query.user_group);
      // 获取当前节点信息
      const nowNode = treeRef.value!.getNode(route.query.user_group);
      if (nowNode) {
        nowTreeName.value = nowNode.data.label;
        nowNodeObject.value = getObjectId(route.query.user_group);

        // 加载权限数据
        nextTick(() => {
          menuPermissionRef.value?.getPermissionTreeData();
          menuPermissionRef.value?.getPermissionOnRight();
        });
      }
    }
  } else {
    // 默认加载用户列表
    handleRadioChange("user");
  }
};
onMounted(() => {
  window.addEventListener("resize", handleResize);
  // 处理路由参数
  handleRouteQuery();
});
</script>

<style scoped lang="scss">
:deep(.el-card__body) {
  height: 100%;
}

.permission-container {
  height: 100%;
  width: 100%;
  .permission-card {
    height: 100%;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .card-title {
        font-size: 18px;
        font-weight: bold;
        color: #303133;
      }
    }
  }

  .main-splitter {
    border: none;

    :deep(.el-splitter__pane) {
      overflow: hidden;
      scrollbar-width: auto !important;
      background-color: yellow;
    }
  }

  .left-panel {
    display: flex;
    flex-direction: column;
    height: 100%;

    .panel-header {
      padding: 10px 15px;
      border-bottom: 1px solid #ebeef5;

      .panel-title {
        display: block;
        margin-bottom: 12px;
        font-size: 14px;
        font-weight: bold;
        color: #606266;
      }

      :deep(.el-radio-group) {
        display: flex;

        .el-radio-button {
          flex: 1;

          .el-radio-button__inner {
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 5px;
          }
        }
      }
    }

    .tree-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      padding: 10px;

      .search-input {
        margin-bottom: 10px;
      }

      .tree-scrollbar {
        flex: 1;

        .object-tree {
          height: 100%;

          :deep(.el-tree-node) {
            &.is-current > .el-tree-node__content {
              background-color: #ecf5ff;
              color: #409eff;
            }
          }

          .custom-tree-node {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 14px;
            padding-right: 8px;
          }
        }
      }
    }
  }

  .right-panel {
    height: 100%;
    display: flex;
    flex-direction: column;

    .empty-placeholder {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .protected-object {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;

      :deep(.el-result__icon) {
        .protected-icon {
          font-size: 60px;
          color: #909399;
        }
      }
    }

    .permission-config {
      display: flex;
      flex-direction: column;
      height: 100%;

      .config-header {
        padding: 15px 20px;
        border-bottom: 1px solid #ebeef5;

        .header-info {
          display: flex;
          align-items: center;
          gap: 15px;

          .header-text {
            .object-name {
              font-size: 18px;
              font-weight: bold;
              color: #303133;
              margin-bottom: 4px;
            }

            .object-type {
              font-size: 12px;
            }
          }
        }
      }

      .permission-tabs {
        flex: 1;
        display: flex;
        flex-direction: column;
        border: none;
        box-shadow: none;

        :deep(.el-tabs__content) {
          flex: 1;
          padding: 15px 0 0;

          .el-tab-pane {
            height: 100%;
          }
        }
      }
    }
  }

  .feature-coming {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .permission-container {
    padding: 10px;

    .permission-card {
      .card-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
      }
    }
  }
}
</style>