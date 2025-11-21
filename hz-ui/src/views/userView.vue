<template>
  <div class="card">
    <div class="user-header">
      <div>
        <el-button
          v-permission="`${route.name?.replace('_info', '')}:add`"
          type="primary"
          @click="handleAdd"
          >新增</el-button
        >
        <!-- <el-button  type="primary" size="small" @click="insertDaemonData">插入样例数据</el-button> -->
        <el-button
          v-permission="`${route.name?.replace('_info', '')}:delete`"
          :disabled="multipleSelect.length == 0"
          type="danger"
          @click="handleDeleteMore"
          >批量删除</el-button
        >
      </div>
      <el-form :inline="true" :model="filterObject" class="demo-form-inline">
        <el-form-item label="用户名检索">
          <el-input
            v-model="filterObject.search"
            placeholder="请输入用户名"
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="small" @click="hanldeSearch"
            >查询</el-button
          >
        </el-form-item>
      </el-form>
    </div>
    <!-- 表格内容 -->
    <div>
      <el-table
        border
        v-loading="loading"
        :data="userList"
        style="width: 100%"
        max-height="500px"
        :table-layout="tableLayout"
        @selection-change="handleSelectionChange"
      >
        <el-table-column
          type="selection"
          width="50"
          :selectable="selectFilter"
        />
        <el-table-column
          v-for="item in userListCol"
          :key="item.prop"
          :label="item.label"
          :prop="item.prop"
        >
          <template #default="scope" v-if="item.prop === 'status'">
            <el-switch
              v-permission="{
                id: `${route.name?.replace('_info', '')}:edit`,
                action: 'disabled',
              }"
              v-model="scope.row.status"
              :disabled="scope.row.username == 'admin' ? true : false"
              class="ml-2"
              style="
                --el-switch-on-color: #13ce66;
                --el-switch-off-color: #ff4949;
              "
              @change="updateStatus(scope.row)"
            />
          </template>
          <template #default="scope" v-if="item.prop === 'groups'">
            <div class="flexJstart gap-5">
              <el-tag v-for="item in scope.row.groups" :key="item">
                {{ item.group_name }}
              </el-tag>
            </div>
          </template>
          <template #default="scope" v-if="item.prop === 'roles'">
            <div class="flexJstart gap-5">
              <el-tag
                v-for="item in scope.row.roles"
                :key="item"
                type="warning"
              >
                {{ item.role_name }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column fixed="right" label="操作" width="180">
          <template #default="scope">
            <el-button
              v-permission="`${route.name?.replace('_info', '')}:edit`"
              link
              type="primary"
              :icon="Edit"
              @click="handleEdit(scope.row)"
            ></el-button>
            <el-tooltip content="重置密码" placement="top">
              <el-button
                v-permission="`${route.name?.replace('_info', '')}:edit`"
                link
                type="primary"
                :icon="Lock"
                @click="handleResetPassword(scope.row)"
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
            <el-button
              v-permission="`${route.name?.replace('_info', '')}:delete`"
              :disabled="scope.row.username == 'admin' ? true : false"
              link
              type="danger"
              :icon="Delete"
              @click="handleDelete(scope.row)"
            ></el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div class="demo-pagination-block">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 30, 40]"
        :small="small"
        :disabled="disabled"
        :background="background"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalCount"
        :hide-on-single-page="isSinglePage"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    <!-- 新增的弹出框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="action == 'add' ? '新增用户' : '编辑用户'"
      width="40%"
      :before-close="handleClose"
    >
      <el-form
        :inline="true"
        :model="formInline"
        class="demo-form-inline"
        ref="userFrom"
        label-position="right"
        label-width="auto"
        status-icon
        :rules="rules"
      >
        <el-row>
          <el-col :span="12">
            <el-form-item
              label="用户名称"
              prop="username"
              :rules="[{ required: true }]"
            >
              <el-input
                v-model="formInline.username"
                placeholder=""
                clearable
                :disabled="action == 'add' ? false : true"
                style="width: 200px"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="真实名称" prop="real_name">
              <el-input
                v-model="formInline.real_name"
                placeholder=""
                clearable
                style="width: 200px"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- <el-form-item label="状态">
      <el-input v-model="formInline.status" placeholder="" clearable />
    </el-form-item> -->
        <el-row>
          <el-col :span="12">
            <el-form-item label="用户组" prop="group_ids" required>
              <el-select
                v-model="formInline.group_ids"
                placeholder=""
                clearable
                multiple
                collapse-tags
                collapse-tags-tooltip
                :max-collapse-tags="3"
                :disabled="isDisabled"
                style="width: 200px"
              >
                <el-option
                  v-for="item in userGroupData"
                  :key="item.id"
                  :label="item.group_name"
                  :value="item.id"
                />
                <!-- <el-option label="禁用" value="False" /> -->
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="角色" prop="role_ids">
              <el-select
                v-model="formInline.role_ids"
                placeholder=""
                clearable
                multiple
                collapse-tags
                collapse-tags-tooltip
                :max-collapse-tags="3"
                :disabled="isDisabled"
                style="width: 200px"
              >
                <el-option
                  v-for="item in roleInfo"
                  :key="item.id"
                  :label="item.role_name"
                  :value="item.id"
                />
                <!-- <el-option label="禁用" value="False" /> -->
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="12" style="display: flex; flex-direction: column">
            <!-- 过期时间 -->
            <el-form-item label="有效期" prop="expire_time">
              <el-date-picker
                v-model="formInline.expire_time"
                type="date"
                placeholder="选择日期"
                :disabled="isDisabled"
                style="width: 200px"
              />
            </el-form-item>
            <el-form-item label="状态" prop="status">
              <el-switch
                v-model="formInline.status"
                class="ml-2"
                inline-prompt
                style="
                  --el-switch-on-color: #13ce66;
                  --el-switch-off-color: #ff4949;
                "
                active-text="Y"
                inactive-text="N"
                :disabled="isDisabled"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item
              label="密码"
              prop="password"
              :required="action === 'add' || changePassword"
            >
              <el-input
                v-model="formInline.password"
                type="password"
                autocomplete="off"
                :show-password="true"
                v-if="changePassword"
              />
              <el-button link type="primary" @click="resetPassword" v-else
                >重置密码</el-button
              >
            </el-form-item>
            <el-form-item
              label="确认密码"
              prop="confirmPassword"
              :required="action === 'add' || changePassword"
              v-show="action === 'add' || changePassword"
            >
              <el-input
                v-model="formInline.confirmPassword"
                type="password"
                autocomplete="off"
                show-password
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row style="justify-content: flex-end">
          <el-form-item>
            <el-button @click="cancelAdd">取消</el-button>
            <el-button type="primary" @click="handleCommit"> 确定</el-button>
          </el-form-item>
        </el-row>
        <!-- </div> -->
      </el-form>
    </el-dialog>
    <!-- 重置密码弹窗 -->
    <el-dialog v-model="pwdDialogVisible" title="重置密码" width="30%">
      <el-form
        ref="pwdFormRef"
        :model="pwdForm"
        :rules="pwdRules"
        label-width="100px"
      >
        <el-form-item label="用户名">
          <el-input v-model="pwdForm.username" disabled />
        </el-form-item>
        <el-form-item label="新密码" prop="password">
          <el-input
            v-model="pwdForm.password"
            type="password"
            show-password
            placeholder="请输入新密码"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="pwdForm.confirmPassword"
            type="password"
            show-password
            placeholder="请再次输入新密码"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="pwdDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitResetPassword"
            >确定</el-button
          >
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { Delete, Edit, Key, Lock } from "@element-plus/icons-vue";
import { useRoute, useRouter } from "vue-router";
const route = useRoute();
import {
  getCurrentInstance,
  onMounted,
  ref,
  reactive,
  watch,
  computed,
  nextTick,
} from "vue";
defineOptions({ name: "user" });
import type { FormInstance, FormRules } from "element-plus";
import { ElMessageBox, ElMessage } from "element-plus";
import { PassThrough } from "stream";
const router = useRouter();
const { proxy } = getCurrentInstance();
// 搜素框变量
const filterObject = reactive({
  search: "",
});
// 表格变量
const loading = ref(false);
const userList = ref([]);
// const currentUserList = ref([])
const tableLayout = ref("auto");
const userListCol = ref([
  {
    prop: "username",
    label: "用户名称",
  },
  {
    prop: "real_name",
    label: "真实姓名",
  },
  {
    prop: "status",
    label: "状态",
  },
  {
    prop: "groups",
    label: "用户组列表",
  },
  {
    prop: "roles",
    label: "角色列表",
  },
  {
    prop: "expire_time",
    label: "到期时间",
  },
  // {
  //   prop: "create_time",
  //   label: "创建时间",
  // },
]);
interface RuleForm {
  username: string;
  real_name: string;
  password: string;
  confirmPassword: string;
  status: boolean;
  location: string;
}

// 自定义验证确认密码的函数
const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if ((action.value === "add" || changePassword.value) && value === "") {
    callback(new Error("请再次输入密码"));
  } else if (
    (action.value === "add" || changePassword.value) &&
    value !== formInline.password
  ) {
    callback(new Error("两次输入的密码不一致"));
  } else {
    callback();
  }
};

const rules = reactive<FormRules<RuleForm>>({
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 5, message: "密码长度不能低于5", trigger: "blur" },
  ],
  confirmPassword: [
    {
      validator: validateConfirmPassword,
      trigger: "blur",
    },
  ],
});
// 分页变量
const currentPage = ref(1);
const pageSize = ref(10);
const small = ref(false);
const background = ref(false);
const disabled = ref(false);
const totalCount = ref(0);
const pageConfig = reactive({
  page: currentPage.value,
  size: pageSize.value,
  search: "",
  ordering: "id",
});
// 少于分页需求则不显示分页
const isSinglePage = ref(false);

// 角色列表
const roleInfo = ref([]);
// cumputed

// 获取角色数据
const getRoleData = async (config) => {
  let roleinfo = await proxy.$api.getRole(config);
  roleInfo.value = roleinfo.data.results;
};
const userGroupData = ref([]);

const getUserGroupData = async () => {
  let res = await proxy.$api.getUserGroup();
  userGroupData.value = res.data.results;
};
// 获取用户数据
const getUserData = async (conf) => {
  loading.value = true;
  // console.log('11111',pageConfig.value)
  let res = await proxy.$api.user(conf);
  userList.value = res.data.results;
  totalCount.value = res.data.count;
  loading.value = false;
};

const handleSizeChange = (val) => {
  pageConfig.size = val;
  // getTableNowData(pageSize,currentPage);
  // if (totalCount.value <= pageSize.value){
  //   isSinglePage.value = true
  // }
  getUserData(pageConfig);
};
const handleCurrentChange = (val) => {
  pageConfig.page = val;
  // getTableNowData(pageSize,currentPage);
  getUserData(pageConfig);
};

// 新增按钮
const dialogVisible = ref(false);
// from表单数据
const formInline = reactive({
  username: "",
  real_name: null,
  password: "",
  confirmPassword: "",
  status: true,
  role_ids: [],
  group_ids: [],
  expire_time: new Date(2999, 1, 1),
});
const action = ref("add");

// 保存编辑前的原始数据
const originalData = ref({});

// 显示弹出框
const handleAdd = () => {
  action.value = "add";
  dialogVisible.value = true;
  changePassword.value = true;
};
// 取消弹出框
const cancelAdd = () => {
  dialogVisible.value = false;
  // 重置表单
  proxy.$refs.userFrom.resetFields();
};
// 关闭弹出框
const handleClose = (done) => {
  ElMessageBox.confirm("是否确认关闭?")
    .then(() => {
      done();
      proxy.$refs.userFrom.resetFields();
    })
    .catch(() => {
      // catch error
    });
};

// 比较两个值是否相等（处理数组等复杂类型）
const isEqual = (value1: any, value2: any): boolean => {
  // 处理数组类型
  if (Array.isArray(value1) && Array.isArray(value2)) {
    if (value1.length !== value2.length) return false;
    const sorted1 = [...value1].sort();
    const sorted2 = [...value2].sort();
    return JSON.stringify(sorted1) === JSON.stringify(sorted2);
  }

  // 处理其他类型
  return value1 === value2;
};

// 获取变更的数据
const getChangedData = (): object => {
  const changedData: any = {};

  // 遍历表单数据，只收集变更过的字段
  for (const key in formInline) {
    // 忽略确认密码字段，因为它不直接提交到后端
    if (key === "confirmPassword") continue;

    // 新增操作时，所有字段都需要提交
    if (action.value === "add") {
      changedData[key] = formInline[key];
      continue;
    }
    // 编辑操作时，只提交变更的字段
    if (!isEqual(formInline[key], originalData.value[key])) {
      console.log("key", key);

      changedData[key] = formInline[key];
    }
  }
  console.log("changedData", changePassword.value);
  // 如果是编辑状态且重置了密码，则强制添加密码字段
  if (action.value === "edit" && changePassword.value) {
    console.log(123);
    changedData.password = formInline.password;
  }
  console.log("123333", changedData);
  return changedData;
};

// 点击触发提交
const handleCommit = () => {
  proxy.$refs.userFrom.validate(async (valid) => {
    if (valid) {
      // 新增接口
      if (action.value == "add") {
        let res = await proxy.$api.useradd(formInline);
        console.log(res);
        if (res.status == 201) {
          dialogVisible.value = false;
          // 重置表单
          proxy.$refs.userFrom.resetFields();
          getUserData(pageConfig);
        } else {
          ElMessage({
            showClose: true,
            message: "添加失败:" + JSON.stringify(res.data),
            type: "error",
          });
        }
      }
      // 编辑接口
      else {
        // 只获取变更的数据
        const changedData = getChangedData();
        console.log("changedData", changedData);
        // 如果没有变更任何数据，则直接关闭对话框
        if (Object.keys(changedData).length === 0) {
          dialogVisible.value = false;
          ElMessage({
            showClose: true,
            message: "没有变更任何数据",
            type: "info",
          });
          return;
        }

        console.log("变更的数据:", JSON.stringify(changedData));
        let res = await proxy.$api.userupdate({
          id: nowRow.value.id,
          ...changedData,
        });
        console.log(res);
        if (res.status == 200) {
          dialogVisible.value = false;
          // 重置表单
          proxy.$refs.userFrom.resetFields();
          getUserData(pageConfig);
        } else {
          console.log();
          ElMessage({
            showClose: true,
            message: "更新失败:" + JSON.stringify(res.data),
            type: "error",
          });
        }
      }
    } else {
      ElMessage({
        showClose: true,
        message: "请输入正确内容.",
        type: "error",
      });
    }
    console.log(formInline);
  });
};
const updateStatus = async (param) => {
  let res = await proxy.$api.userupdate({
    status: param.status,
    id: param.id,
  });
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "更新成功",
    });
    // 重置表单
    // proxy.$refs.pgroupForm.resetFields();
    getUserData(pageConfig);
  } else {
    ElMessage({
      showClose: true,
      message: "更新失败:" + JSON.stringify(res.data),
      type: "error",
    });
  }
};
const nowRow = ref({});
// 编辑
const handleEdit = (row) => {
  action.value = "edit";
  changePassword.value = false;
  dialogVisible.value = true;
  nowRow.value = row;

  // 保存原始数据用于比较
  originalData.value = {
    username: row.username,
    real_name: row.real_name,
    status: row.status,
    role_ids: row.roles ? row.roles.map((r: any) => r.id) : [],
    group_ids: row.groups ? row.groups.map((g: any) => g.id) : [],
    password: row.password,
  };

  // 清除新增按钮会显示编辑按钮的记录
  // proxy.$nextTick(() => {Object.assign(formInline,row)})
  nextTick(() => {
    Object.keys(formInline).forEach((item) => {
      if (["group_ids"].includes(item)) {
        const groupIds = row["groups"]
          ? row["groups"].map((ary: any) => ary.id)
          : [];
        formInline[item] = groupIds;
        originalData.value[item] = [...groupIds]; // 保存副本用于比较
      } else if (["role_ids"].includes(item)) {
        const roleIds = row["roles"]
          ? row["roles"].map((ary: any) => ary.id)
          : [];
        formInline[item] = roleIds;
        originalData.value[item] = [...roleIds]; // 保存副本用于比较
      } else {
        formInline[item] = row[item];
        originalData.value[item] = row[item];
      }
    });
    // 清空密码字段
    formInline.confirmPassword = "";
  });
  console.log(formInline);
};
// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm("是否确认删除?", "Warning", {
    confirmButtonText: "确认删除",
    cancelButtonText: "取消",
    type: "warning",
    draggable: true,
  })
    .then(async () => {
      // 发起删除请求
      let res = await proxy.$api.userdel(row.id);
      if (res.status == 204) {
        ElMessage({
          type: "success",
          message: "删除成功",
        });
      } else {
        ElMessage({
          type: "error",
          message: "删除失败",
        });
      }
      getUserData(pageConfig);
    })
    .catch(() => {
      ElMessage({
        type: "info",
        message: "Delete canceled",
      });
    });
};
// 批量删除
// 获取勾选值

const multipleSelect = ref([]);
// 按照返回条件禁止某些行变为可勾选的
const selectFilter = (row, index) => {
  return row.username != "admin";
};
const handleSelectionChange = (val) => {
  multipleSelect.value = val;
};
function sleep(delay) {
  var start = new Date().getTime();
  while (new Date().getTime() - start < delay) {
    continue;
  }
}

const handleDeleteMore = () => {
  ElMessageBox.confirm("是否确认删除?", "Warning", {
    confirmButtonText: "确认删除",
    cancelButtonText: "取消",
    type: "warning",
    draggable: true,
  })
    .then(async () => {
      // 发起删除请求
      // await multipleSelect.value.forEach((row)=>{
      // const res =  proxy.$api.userdel(row.id)
      // let delList = multipleSelect.value.forEach((row)=>{
      let delList = [];
      for (let row in multipleSelect.value) {
        delList.push(multipleSelect.value[row].id);
      }
      console.log(delList);

      let res = await proxy.$api.usermuldel({ pks: delList });

      if (res.status == 204) {
        ElMessage({
          type: "success",
          message: "删除成功",
        });
      } else {
        ElMessage({
          type: "error",
          message: "删除失败",
        });
      }
      // sleep(20000)
      getUserData(pageConfig);
    })
    .catch(() => {
      ElMessage({
        type: "info",
        message: "Delete canceled",
      });
    });
};
// 搜索框
const hanldeSearch = async () => {
  pageConfig.search = filterObject.search;
  getUserData(pageConfig);
};

// 当编辑用户为admin时，禁用改登录名
const isDisabled = ref(false);
watch(
  () => formInline.username,
  (n) => {
    if (n == "admin") {
      isDisabled.value = true;
    } else {
      isDisabled.value = false;
    }
  }
);
// 密码重置
const changePassword = ref(false);
const resetPassword = () => {
  changePassword.value = true;
  // 清空密码输入框
  formInline.password = "";
  formInline.confirmPassword = "";
};

// 添加密码重置相关的变量
const pwdDialogVisible = ref(false);
const pwdFormRef = ref<FormInstance>();
const pwdForm = reactive({
  username: "",
  password: "",
  confirmPassword: "",
  userId: 0,
});

// 密码验证规则
const validatePass = (rule: any, value: any, callback: any) => {
  if (value === "") {
    callback(new Error("请输入密码"));
  } else {
    if (value.length < 6) {
      callback(new Error("密码长度不能少于6位"));
    }
    callback();
  }
};

const validateConfirmPass = (rule: any, value: any, callback: any) => {
  if (value === "") {
    callback(new Error("请再次输入密码"));
  } else if (value !== pwdForm.password) {
    callback(new Error("两次输入的密码不一致"));
  } else {
    callback();
  }
};

const pwdRules = reactive<FormRules>({
  password: [{ validator: validatePass, trigger: "blur" }],
  confirmPassword: [{ validator: validateConfirmPass, trigger: "blur" }],
});

// 快速重置密码
const handleResetPassword = (row) => {
  pwdForm.username = row.username;
  pwdForm.userId = row.id;
  pwdForm.password = "";
  pwdForm.confirmPassword = "";
  pwdDialogVisible.value = true;

  // 重置表单验证状态
  nextTick(() => {
    pwdFormRef.value?.clearValidate();
  });
};

// 提交重置密码
const submitResetPassword = async () => {
  if (!pwdFormRef.value) return;

  await pwdFormRef.value.validate(async (valid, fields) => {
    if (valid) {
      const res = await proxy.$api.userupdate({
        id: pwdForm.userId,
        password: pwdForm.password,
      });

      if (res.status === 200) {
        ElMessage.success("密码重置成功");
        pwdDialogVisible.value = false;
      } else {
        ElMessage.error("密码重置失败: " + JSON.stringify(res.data));
      }
    }
  });
};
const goToPermission = (row) => {
  router.push({
    name: "permission",
    query: { user: row.id },
  });
};

onMounted(() => {
  // 初始化数据切片
  getRoleData(pageConfig);
  getUserGroupData();
  // api请求获取所有数据
  getUserData(pageConfig);
});
</script>
<style scoped>
.el-pagination {
  justify-content: flex-end;
}
.user-header {
  display: flex;
  justify-content: space-between;
}

.el-form-button-add {
  display: flex;
  align-items: center;
}
</style>