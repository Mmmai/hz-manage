<template>
  <div class="card">
    <div class="user-header">
      <div>
        <el-button
          type="primary"
          @click="handleAdd"
          v-permission="`${route.name?.replace('_info', '')}:add`"
          >新增</el-button
        >
      </div>
    </div>
    <!-- 表格内容 -->
    <div>
      <el-table
        border
        v-loading="loading"
        :data="roleList"
        style="width: 100%"
        max-height="500px"
        highlight-current-row
        :table-layout="tableLayout"
        @selection-change="handleSelectionChange"
        @row-click="handleClick"
      >
        <el-table-column
          type="selection"
          width="55"
          :selectable="selectFilter"
        />
        <el-table-column
          v-for="item in roleListCol"
          :key="item.prop"
          :label="item.label"
          :prop="item.prop"
        >
        </el-table-column>
        <el-table-column fixed="right" label="操作" width="150">
          <template #default="scope">
            <el-button
              link
              v-permission="`${route.name?.replace('_info', '')}:edit`"
              type="primary"
              :icon="Edit"
              @click="handleEdit(scope.row)"
            ></el-button>
            <el-button
              v-permission="`${route.name?.replace('_info', '')}:delete`"
              :disabled="scope.row.built_in"
              icon-position="right"
              link
              type="danger"
              :icon="Delete"
              @click="handleDelete(scope.row)"
            ></el-button>
          </template>
        </el-table-column>
      </el-table>
      <!-- 分页 -->
    </div>
  </div>
  <!-- 新增的弹出框 -->
  <el-dialog
    v-model="dialogVisible"
    :title="action == 'add' ? '新增角色' : '编辑角色'"
    width="30%"
    :before-close="handleClose"
  >
    <el-form
      :model="formInline"
      class="demo-form-inline"
      label-position="right"
      label-width="80px"
      ref="userFrom"
      status-icon
    >
      <el-form-item label="角色" prop="role" :rules="[{ required: true }]">
        <el-input
          v-model="formInline.role"
          placeholder="请输入英文"
          clearable
          style="width: 30%"
          :disabled="nowRow.built_in"
        />
      </el-form-item>
      <el-form-item
        label="角色名称"
        prop="role_name"
        :rules="[{ required: true }]"
      >
        <el-input
          v-model="formInline.role_name"
          placeholder="中文名称"
          style="width: 30%"
          clearable
          :disabled="nowRow.built_in"
        />
      </el-form-item>
      <!-- <el-form-item label="菜单授权" prop="rolePermission">
        <div style="border: 1px solid var(--el-border-color); width: 90%">
          <el-tree
            ref="menuTreeRef"
            v-model="formInline.rolePermission"
            :data="dataSource"
            show-checkbox
            node-key="id"
            default-expand-all
            :expand-on-click-node="false"
            :props="{ class: customNodeClass }"
          >
            <template #default="{ node, data }">
              <span
                :class="{
                  buttonList: data.tree_type === 'button' ? true : false,
                }"
                >{{ node.label }}</span
              >
            </template>
          </el-tree>
        </div>
      </el-form-item> -->
      <el-row style="justify-content: space-around">
        <el-form-item>
          <el-button @click="cancelAdd">取消</el-button>
          <el-button type="primary" @click="handleCommit"> 确定</el-button>
        </el-form-item>
      </el-row>
      <!-- </div> -->
    </el-form>
  </el-dialog>
</template>

<script lang="ts" setup>
import {
  getCurrentInstance,
  onMounted,
  computed,
  ref,
  reactive,
  watch,
  toRaw,
  nextTick,
} from "vue";
const currentSelectRow = ref({});
const { proxy } = getCurrentInstance();
import { useRoute, useRouter } from "vue-router";
const router = useRouter();
const route = useRoute();
import { ElMessageBox, ElMessage } from "element-plus";
const customNodeClass = ({ tree_type }, node) => {
  if (tree_type === "menu") {
    return "is-menu";
  } else if (tree_type === "button") {
    return "is-button";
  } else {
    return "";
  }
};

// 搜素框变量
const filterObject = reactive({
  search: "",
});
// 表格变量
const loading = ref(false);
const roleList = ref([]);
// const currentUserList = ref([])
const tableLayout = ref("auto");
const roleListCol = ref([
  {
    prop: "role",
    label: "角色名",
  },
  {
    prop: "role_name",
    label: "角色名称",
  },
  {
    prop: "userGroup_count",
    label: "用户组数量",
  },
  {
    prop: "user_count",
    label: "用户数量",
  },
]);
// 分页变量

const totalCount = ref(0);

// 少于分页需求则不显示分页

// 角色列表
const roleObject = ref({});
// cumputed
onMounted(async () => {
  // 初始化数据切片
  // api请求获取所有数据

  await getRoleData();
  // getMenuListFunc();
  // selectFirst()
});
// 默认选中第1行
const selectFirst = () => {
  currentSelectRow.value = roleList.value[0];
};

// 获取角色数据
const getRoleData = async () => {
  let res = await proxy.$api.getRole();
  roleList.value = res.data.results;
  //   #roleList.value.length

  // 统计用户个数

  // 将role列表转化为dict
  // console.log(roleInfo.value)
  for (let key in roleList.value) {
    let rolename = roleList.value[key].role;
    let roleid = roleList.value[key].id;
    roleObject.value[roleid] = rolename;
  }
};

// 点击表格行
// const currentSelectRow = ref({})

const handleClick = (val) => {
  // console.log(val)
  currentSelectRow.value = val;
};
const test = () => {
  console.log(menuTreeRef.value!.getCheckedKeys());
  console.log(menuTreeRef.value!.getCheckedNodes());
};
// 弹出框

// 新增按钮
const dialogVisible = ref(false);
// from表单数据
const formInline = reactive({
  role: "",
  role_name: "",
  rolePermission: [],
});
const action = ref("add");
// 显示新增弹出框
const handleAdd = () => {
  // action.value = "add";
  // dialogVisible.value = true;
  router.push({ path: route.path + "/new" });
};
// 取消新增弹出框
const cancelAdd = () => {
  dialogVisible.value = false;
  // 重置表单
  proxy.$refs.userFrom.resetFields();
  // setCheckedKeys([]);
};
// 关闭弹出框
const handleClose = (done) => {
  ElMessageBox.confirm("是否确认关闭?")
    .then(() => {
      proxy.$refs.userFrom.resetFields();
      // setCheckedKeys([]);

      done();
    })
    .catch(() => {
      // catch error
    });
};

const rmMenuId = computed(() => {
  // getCheckNodeList.value
  let tmpArr = new Array();
  menuTreeRef.value!.getCheckedNodes().forEach((item) => {
    if (item.tree_type === "button") {
      tmpArr.push(item.id);
    }
  });
  return tmpArr;
});
// const getCheckNodeList = ref([]);
// 点击触发提交
const handleCommit = () => {
  // let newMenuList = menuTreeRef.value.getCheckedKeys().concat(menuTreeRef.value.getHalfCheckedKeys())
  // 更新对应关系
  // getCheckNodeList.value = menuTreeRef.value!.getCheckedNodes();
  formInline.rolePermission = rmMenuId.value;
  // getCheckedKeys()
  console.log(JSON.stringify(formInline));

  proxy.$refs.userFrom.validate(async (valid) => {
    if (valid) {
      // 新增接口
      if (action.value == "add") {
        let res = await proxy.$api.roleadd(formInline);
        if (res.status == 201) {
          dialogVisible.value = false;
          ElMessage({
            type: "success",
            message: "添加成功",
          });
          // 重置表单
          proxy.$refs.userFrom.resetFields();
          // setCheckedKeys([]);
          getRoleData();
          console.log(menuTreeRef.value!.getCheckedKeys());
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
        let res = await proxy.$api.roleupdate({
          id: nowRow.value.id,
          ...formInline,
        });
        console.log(res);
        if (res.status == 200) {
          dialogVisible.value = false;
          // 重置表单
          proxy.$refs.userFrom.resetFields();
          // setCheckedKeys([]);
          console.log(menuTreeRef.value!.getCheckedKeys());

          getRoleData();
          ElMessage({
            type: "success",
            message: "更新成功",
          });
        } else {
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
  });
};

// 编辑
const nowRow = ref({});
const handleEdit = (row) => {
  action.value = "edit";
  nowRow.value = row;
  dialogVisible.value = true;
  // 清除新增按钮会显示编辑按钮的记录
  // proxy.$nextTick(() => {
  //   Object.assign(formInline, row);
  // });
  nextTick(() => {
    Object.keys(formInline).forEach((item) => {
      formInline[item] = row[item];
    });
  });
  // setCheckedKeys(row.menu)
  // setCheckedKeys(row.rolePermission);
  // console.log(JSON.stringify(formInline));

  // formInline.rolePermission = row.menu
};
const gotoInfo = (row) => {
  router.push({ path: route.path + "/" + row.id });
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
      let res = await proxy.$api.roledel(row.id);
      if (res.status == 204) {
        ElMessage({
          type: "success",
          message: "删除成功",
        });
        nextTick(() => {
          getRoleData();
        });
        // selectFirst()
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

const multipleSelect = ref([]);
// 按照返回条件禁止某些行变为可勾选的
const selectFilter = (row, index) => {
  return row.role != "sysadmin";
};
const handleSelectionChange = (val) => {
  multipleSelect.value = val;
};

// 搜索框
// const hanldeSearch = async() =>{
//   pageConfig.search = filterObject.search
//     }
// 弹出框中的tree
import { ElTree } from "element-plus";

import type Node from "element-plus/es/components/tree/src/model/node";
import { Delete, Edit } from "@element-plus/icons-vue";

const menuTreeRef = ref<InstanceType<typeof ElTree>>();
interface Tree {
  id: number;
  label: string;
  children?: Tree[];
}
// 获取权限源
const dataSource = ref([]);
const getMenuListFunc = async () => {
  let res = await proxy.$api.getPermissionToRole();
  console.log(res);
  dataSource.value = res.data.results;
};

const setCheckedKeys = (val) => {
  nextTick().then(() => {
    menuTreeRef.value!.setCheckedKeys(val, false);
    console.log(menuTreeRef.value!.getCheckedKeys());
  });
};

const isDisabled = ref(false);
watch(
  () => formInline.role,
  (n) => {
    if (n == "sysadmin") {
      isDisabled.value = true;
    } else {
      isDisabled.value = false;
    }
  }
);
</script>
<style  scoped>
.el-pagination {
  justify-content: flex-end;
}

.user-header {
  display: flex;
  justify-content: space-between;
  margin: 10px 0px;
}

.el-tag-role-list {
  margin: 5px;
}

.el-form-button-add {
  display: flex;
  align-items: center;
}

.role-menu {
  display: flex;
  align-items: flex-start;
}
:deep(.el-tree .el-tree-node.is-menu > .el-tree-node__children) {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
}
:deep(
    .el-tree .el-tree-node.is-button > .el-tree-node__content:not(:first-child)
  ) {
  padding-left: 10px !important;
}
/* .is-menu > .el-tree-node__children > div {
  width: 25%;
} */
</style>