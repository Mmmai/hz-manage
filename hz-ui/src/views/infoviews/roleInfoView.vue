<template>
  <div class="divVertical">
    <div class="card flexJstart gap-5" style="height: 50px; flex: none">
      <el-tooltip
        class="box-item"
        effect="dark"
        content="返回角色列表"
        placement="top"
      >
        <el-button @click="goBack()" :icon="Back" plain size="small">
        </el-button>
      </el-tooltip>
      <el-text tag="b" size="large">{{
        isAdd ? "创建新角色" : `角色详情【${roleForm.role_name}】`
      }}</el-text>
    </div>
    <div class="card" style="flex: none">
      <!-- 角色表单 -->
      <el-form
        ref="roleFormRef"
        :model="roleForm"
        :rules="roleFormRules"
        label-width="100px"
        style="width: 100%; margin-top: 10px"
      >
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="角色" prop="role">
              <el-input
                v-model="roleForm.role"
                placeholder="请输入角色英文名"
                :disabled="!isAdd"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="角色名称" prop="role_name">
              <el-input
                v-model="roleForm.role_name"
                placeholder="请输入角色中文名称"
                :disabled="isSysAdmin"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <el-row justify="center">
        <el-button type="primary" @click="updateAction()" v-if="!isSysAdmin">{{
          isAdd ? "添加" : "更新"
        }}</el-button>
      </el-row>
    </div>

    <div class="card">
      <el-tabs
        v-model="activeName"
        type="card"
        class="demo-tabs"
        @tab-click="handleClick"
      >
        <el-tab-pane label="菜单权限" name="menuPermission">
          <div style="text-align: center">
            <TreeTransfer
              v-model="selectedKeys"
              :data="treeData"
              :leaf-only="true"
              :hide-fully-assigned-parents="true"
              :titles="['可选权限', '已选权限']"
              :check-strictly="false"
              @change="handleChange"
              :disabled="isSysAdmin"
            /></div
        ></el-tab-pane>
        <el-tab-pane label="资产权限" name="cmdbPermission">Config</el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {
  ref,
  computed,
  getCurrentInstance,
  onMounted,
  reactive,
  nextTick,
} from "vue";
import { Back } from "@element-plus/icons-vue";
import { ElMessageBox, ElMessage } from "element-plus";
import { useRoute, useRouter } from "vue-router";
const router = useRouter();
const route = useRoute();
const { proxy } = getCurrentInstance();
import TreeTransfer from "@/components/common/treeTransfer.vue";
import { get } from "lodash";

const isAdd = ref(false);
const editMode = ref(false);
// roleId
const roleId = ref<any>(null);
const activeName = ref("first");
const handleClick = () => {};
const goBack = () => {
  router.push({
    path: "/settings/role",
  });
};

// 表单字段
const roleForm = reactive({
  role: "",
  role_name: "",
});

// 表单验证规则
const roleFormRules = {
  role: [
    { required: true, message: "请输入角色英文名", trigger: "blur" },
    // 添加纯英文检验
    {
      validator: (rule, value, callback) => {
        if (!/^[a-zA-Z]+$/.test(value)) {
          callback(new Error("请输入纯英文"));
        } else {
          callback();
        }
      },
    },
  ],
  role_name: [
    { required: true, message: "请输入角色中文名称", trigger: "blur" },
  ],
};

const isSysAdmin = computed(() => {
  return roleForm.role === "sysadmin";
});

// 权限树数据
const treeData = ref([]);

// 选中的权限keys
const selectedKeys = ref([]);

// 获取角色信息
const getRoleData = async () => {
  let res = await proxy.$api.getRoleInfo(roleId.value);
  if (res.status == 200) {
    // 赋值给表单
    roleForm.role = res.data.role;
    roleForm.role_name = res.data.role_name;

    // 获取角色已关联的权限
    selectedKeys.value = res.data.rolePermission.map((item) => {
      return item;
    });
  }
};

// 获取权限树数据
const getPermissionTreeData = async () => {
  let res = await proxy.$api.getPermissionToRole();
  treeData.value = res.data.results;
};

// 更新方法
const updateAction = async () => {
  if (isAdd) {
    let res = await proxy.$api.roleadd({
      ...roleForm,
      rolePermission: selectedKeys.value,
    });
    if (res.status == 201) {
      ElMessage({
        type: "success",
        message: "创建成功",
      });
      goBack();
    } else {
      ElMessage({
        type: "error",
        message: `更新失败: ${JSON.stringify(res.data)}`,
      });
    }
  } else {
    let res = await proxy.$api.roleupdate({
      id: roleId.value,
      ...roleForm,
    });
    if (res.status == 200) {
      ElMessage({
        type: "success",
        message: "更新成功",
      });
      getRoleData();
    } else {
      ElMessage({
        type: "error",
        message: `更新失败: ${JSON.stringify(res.data)}`,
      });
    }
  }
};

// 权限变更处理
const handleChange = (newVal, direction, movedKeys) => {
  if (isSysAdmin.value || isAdd.value) return;

  if (direction == "right") {
    // 添加权限
    addPermissions(movedKeys);
  } else {
    // 删除权限
    removePermissions(movedKeys);
  }
};

// 添加权限
const addPermissions = async (buttonIds) => {
  let res = await proxy.$api.addRolePermissions(roleId.value, {
    button_ids: buttonIds,
  });
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "权限添加成功",
    });
    nextTick(() => {
      getRoleData();
      getPermissionTreeData();
    });
  } else {
    ElMessage({
      type: "error",
      message: `权限添加失败: ${JSON.stringify(res.data)}`,
    });
  }
};

// 删除权限
const removePermissions = async (buttonIds) => {
  let res = await proxy.$api.removeRolePermissions(roleId.value, {
    button_ids: buttonIds,
  });
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "权限删除成功",
    });
    nextTick(() => {
      getRoleData();
      getPermissionTreeData();
    });
  } else {
    ElMessage({
      type: "error",
      message: `权限删除失败: ${JSON.stringify(res.data)}`,
    });
  }
};

onMounted(async () => {
  roleId.value = route.path.split("/").at(-1);

  if (roleId.value.includes("new")) {
    isAdd.value = true;
    editMode.value = true;
  } else {
    await getRoleData();
  }
  await getPermissionTreeData();
});
</script>

<style scoped>
:deep(.el-transfer-panel) {
  width: 500px;
}

:deep(.el-transfer) {
  --el-transfer-panel-body-height: 700px;
}
</style>