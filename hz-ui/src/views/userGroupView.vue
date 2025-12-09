<template>
  <div class="card">
    <div class="table-header">
      <div class="header-button-lf">
        <el-button
          v-permission="`${route.name?.replace('_info', '')}:add`"
          type="primary"
          @click="addGroup"
          >添加</el-button
        >
      </div>
    </div>
    <el-table
      ref="multipleTableRef"
      :data="userGroupData"
      style="width: 100%"
      border
    >
      <el-table-column
        property="group_name"
        label="用户组名"
        sortable="custom"
      />
      <el-table-column property="user_count" label="关联用户数" />
      <el-table-column property="users" label="用户列表">
        <template #default="scope">
          <div class="flexJstart gap-5">
            <el-tag v-for="item in scope.row.users" :key="item">
              {{ item.username }}
            </el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column property="roles" label="角色列表">
        <template #default="scope">
          <div class="flexJstart gap-5">
            <el-tag v-for="item in scope.row.roles" :key="item" type="warning">
              {{ item.role_name }}
            </el-tag>
          </div>
        </template>
      </el-table-column>

      <el-table-column fixed="right" width="120" label="操作">
        <template #default="scope">
          <el-tooltip
            class="box-item"
            effect="dark"
            content="编辑"
            placement="top"
          >
            <el-button
              v-permission="`${route.name?.replace('_info', '')}:edit`"
              link
              type="primary"
              :icon="Edit"
              @click="editRow(scope.row)"
            ></el-button>
          </el-tooltip>
          <el-tooltip content="权限配置" placement="top">
            <el-button
              v-permission="`${route.name?.replace('_info', '')}:edit`"
              link
              type="primary"
              :icon="Key"
              @click="goToPermission(scope.row)"
            ></el-button>
          </el-tooltip>
          <el-tooltip
            class="box-item"
            effect="dark"
            content="删除"
            placement="top"
          >
            <el-button
              v-permission="`${route.name?.replace('_info', '')}:delete`"
              link
              :disabled="scope.row.built_in"
              type="danger"
              :icon="Delete"
              @click="deleteRow(scope.row.id)"
            ></el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>
    <!-- 弹出框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isAdd ? '新增用户组' : '编辑用户组'"
      width="45%"
      :before-close="handleClose"
    >
      <el-form
        :inline="true"
        :model="formInline"
        class="demo-form-inline"
        label-position="right"
        ref="userGroupFrom"
        status-icon
      >
        <el-form-item
          label="用户组名称"
          prop="group_name"
          :rules="[{ required: true }]"
        >
          <el-input
            v-model="formInline.group_name"
            placeholder=""
            clearable
            :disabled="!isAdd && nowRow.built_in"
            style="width: 220px"
          />
        </el-form-item>
        <el-form-item label="关联用户" prop="user_ids">
          <el-select
            v-model="formInline.user_ids"
            placeholder=""
            clearable
            multiple
            collapse-tags
            collapse-tags-tooltip
            :max-collapse-tags="3"
            style="width: 220px"
          >
            <el-option
              v-for="item in userInfo"
              :key="item.id"
              :label="item.username"
              :value="item.id"
            />
            <!-- <el-option label="禁用" value="False" /> -->
          </el-select>
        </el-form-item>
        <el-form-item label="关联角色" prop="role_ids">
          <el-select
            v-model="formInline.role_ids"
            placeholder=""
            clearable
            multiple
            collapse-tags
            collapse-tags-tooltip
            :max-collapse-tags="3"
            :disabled="!isAdd && nowRow.built_in"
            style="width: 220px"
          >
            <el-option
              v-for="item in roleInfo"
              :key="item.id"
              :label="item.role"
              :value="item.id"
            />
            <!-- <el-option label="禁用" value="False" /> -->
          </el-select>
        </el-form-item>

        <el-row style="justify-content: space-around">
          <el-form-item>
            <el-button @click="handleClose">取消</el-button>
            <el-button type="primary" @click="submitAction(userGroupFrom)">
              确定</el-button
            >
          </el-form-item>
        </el-row>
        <!-- </div> -->
      </el-form>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { Delete, Edit, Key } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  ref,
  computed,
  watch,
  getCurrentInstance,
  onMounted,
  reactive,
  nextTick,
} from "vue";
defineOptions({ name: "userGroup" });

import { useRoute } from "vue-router";
const route = useRoute();
const { proxy } = getCurrentInstance();
import { useStore } from "vuex";
const store = useStore();
const userGroupData = ref([]);
const isDisabled = ref(false);
const dialogVisible = ref(false);
const userGroupFrom = ref(null);
const roleInfo = ref([]);
const action = ref("add");
const roleByIdObject = computed(() => {
  let tmpArr = new Object();
  roleInfo.value.forEach((item) => {
    tmpArr[item.id] = item;
  });
  return tmpArr;
});
const formInline = reactive({
  group_name: "",
  role_ids: [],
  user_ids: [],
});

const resetForm = (formEl) => {
  if (!formEl) return;
  formEl.resetFields();
};

const getRoleData = async () => {
  let res = await proxy.$api.getRole();
  roleInfo.value = res.data.results;
};
const userInfo = ref([]);
const getUserData = async () => {
  let res = await proxy.$api.user();
  userInfo.value = res.data.results;
};
const getUserGroupData = async () => {
  let res = await proxy.$api.getUserGroup();
  userGroupData.value = res.data.results;
  console.log(userGroupData.value);
};
const multipleTableRef = ref(null);
const handleClose = () => {
  dialogVisible.value = false;
  resetForm(userGroupFrom.value);
};
const addGroup = () => {
  dialogVisible.value = true;
  nowRow.value = {};
};
const nowRow = ref({});
const isAdd = ref(true);
const editRow = (row) => {
  dialogVisible.value = true;
  nowRow.value = row;
  isAdd.value = false;
  nextTick(() => {
    // Object.assign(formInline, row);
    formInline.group_name = row.group_name;
    formInline.role_ids = row.roles.map((ary) => ary.id);
    formInline.user_ids = row.users.map((ary) => ary.id);
    console.log(formInline);
  });
  console.log(formInline);
};
const deleteRow = (params) => {
  ElMessageBox.confirm("是否确认删除?", "删除", {
    confirmButtonText: "确认删除",
    cancelButtonText: "取消",
    type: "warning",
    draggable: true,
  })
    .then(async () => {
      // 发起删除请求
      let res = await proxy.$api.deleteUserGroup(params);
      //
      // let res = {status:204}
      if (res.status == 204) {
        ElMessage({
          type: "success",
          message: "删除成功",
        });
        // 重新加载页面数据
        await getUserGroupData();
        // dialogVisible.value = false;
      } else {
        ElMessage({
          type: "error",
          message: "删除失败",
        });
      }
    })
    .catch(() => {
      ElMessage({
        type: "info",
        message: "取消删除",
      });
    });
};

const submitAction = async (formEl) => {
  await formEl.validate(async (valid, fields) => {
    if (valid) {
      if (isAdd.value) {
        // 添加请求
        let res = await proxy.$api.addUserGroup({
          ...formInline,
        });
        if (res.status == "201") {
          ElMessage({ type: "success", message: "添加成功" });
          // 重置表单
          dialogVisible.value = false;
          resetForm(formEl);
          // getModelField();
          // 刷新页面
          await getUserGroupData();
        } else {
          ElMessage({
            showClose: true,
            message: "添加失败:" + JSON.stringify(res.data),
            type: "error",
          });
        }
      } else {
        let res = await proxy.$api.updateUserGroup({
          id: nowRow.value.id,
          ...formInline,
        });

        // console.log(123)
        if (res.status == "200") {
          ElMessage({ type: "success", message: "更新成功" });
          // 重置表单
          dialogVisible.value = false;
          resetForm(formEl);
          await getUserGroupData();

          // 获取数据源列表
        } else {
          ElMessage({
            showClose: true,
            message: "更新失败:" + JSON.stringify(res.data),
            type: "error",
          });
        }
      }
    }
  });
};
import { useRouter } from "vue-router";
const router = useRouter();
const goToPermission = (row) => {
  router.push({
    name: "permission",
    query: { user_group: row.id },
  });
};
onMounted(async () => {
  await getRoleData();
  await getUserData();
  await getUserGroupData();
});
</script>
<style scoped lang="scss"></style>