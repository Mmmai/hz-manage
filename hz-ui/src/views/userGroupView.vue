<template>
  <div class="card">
    <div class="table-header">
      <div class="header-button-lf">
        <el-button type="primary" @click="addUserGroup">添加</el-button>
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
      <el-table-column property="userinfo_set" label="用户列表" />
      <el-table-column fixed="right" width="100" label="操作">
        <template #default="scope">
          <el-tooltip
            class="box-item"
            effect="dark"
            content="编辑"
            placement="top"
          >
            <el-button
              link
              type="primary"
              :icon="Edit"
              @click="editRow(scope.row)"
            ></el-button>
          </el-tooltip>
          <el-tooltip
            class="box-item"
            effect="dark"
            content="删除"
            placement="top"
          >
            <el-button
              link
              type="danger"
              :icon="Delete"
              :disabled="scope.row.built_in"
              @click="deleteRow(scope.row.id)"
            ></el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>
    <!-- 弹出框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="action == 'add' ? '新增用户组' : '编辑用户组'"
      width="45%"
      :before-close="handleClose"
    >
      <el-form
        :inline="true"
        :model="formInline"
        class="demo-form-inline"
        label-position="right"
        ref="userFrom"
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
            :disabled="isDisabled"
          />
        </el-form-item>

        <el-form-item label="关联角色" prop="roles">
          <el-select
            v-model="formInline.roles"
            placeholder=""
            clearable
            multiple
            collapse-tags
            collapse-tags-tooltip
            :max-collapse-tags="3"
            :disabled="isDisabled"
            style="width: 120px"
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
            <el-button @click="cancelAdd">取消</el-button>
            <el-button type="primary" @click="handleCommit"> 确定</el-button>
          </el-form-item>
        </el-row>
        <!-- </div> -->
      </el-form>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { Delete, Edit } from "@element-plus/icons-vue";
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
const { proxy } = getCurrentInstance();
import { useStore } from "vuex";
const store = useStore();
const userGroupData = ref([]);
const isDisabled = ref(false);
const dialogVisible = ref(false);
const roleInfo = ref([]);
const action = ref("add");
const roleOptions = computed(() => {
  let tmpArr = new Array();
  roleInfo.value.forEach((item) => {
    console.log(item);
    tmpArr.push({ label: item.role, value: item.id });
  });
  return tmpArr;
});
const formInline = reactive({
  group_name: "",
  roles: [],
});

const resetForm = (formEl) => {
  if (!formEl) return;
  formEl.resetFields();
};
watch(
  () => roleOptions.value,
  (n) => {
    console.log(roleOptions.value);
  }
);
const getRoleData = async () => {
  let res = await proxy.$api.getRole();
  roleInfo.value = res.data.results;
  console.log(roleInfo.value);
  // 将role列表转化为dict
  // console.log(roleInfo.value)
};
const getUserGroupData = async () => {
  let res = await proxy.$api.getUserGroup();
  userGroupData.value = res.data.results;
  // 将role列表转化为dict
  // console.log(roleInfo.value)
  console.log(userGroupData.value);
};
const multipleTableRef = ref(null);
const handleClose = () => {};
const addUserGroup = () => {
  dialogVisible.value = true;
};
const editRow = (params) => {};
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
onMounted(async () => {
  await getRoleData();
  await getUserGroupData();
});
</script>
<style scoped lang="scss">
</style>