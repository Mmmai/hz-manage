<template>
  <div class="card">
    <div class="role-menu">
      <div style="width: 100%">
        <div class="user-header">
          <div>
            <el-button
              v-permission="`${route.name?.replace('_info', '')}:add`"
              type="primary"
              size="small"
              @click="handleAdd"
              >+新增</el-button
            >
          </div>
        </div>
        <!-- 表格内容 -->
        <div>
          <el-table
            border
            v-loading="loading"
            :data="menuList"
            style="width: 100%"
            max-height="100%"
            highlight-current-row
            row-key="id"
            table-layout="fixed"
            @selection-change="handleSelectionChange"
            @row-click="handleClick"
          >
            <el-table-column
              type="selection"
              width="55"
              :selectable="selectFilter"
            />
            <!-- <el-table-column type="expand">
      <template #default="props">
        <div  v-if="props.row.is_menu" m="4">
1111
        </div>
      </template>
    </el-table-column> -->
            <el-table-column
              v-for="item in menuListCol"
              :key="item.prop"
              :label="item.label"
              :prop="item.prop"
            >
              <template #default="scope" v-if="item.prop === 'is_menu'">
                <el-switch
                  v-permission="{
                    id: `${route.name?.replace('_info', '')}:edit`,
                    action: 'disabled',
                  }"
                  v-model="scope.row.is_menu"
                  class="ml-2"
                  style="
                    --el-switch-on-color: #13ce66;
                    --el-switch-off-color: #ff4949;
                  "
                  @change="updateIsMenu(scope.row)"
                />
              </template>
              <template #default="scope" v-if="item.prop === 'status'">
                <el-switch
                  v-permission="{
                    id: `${route.name?.replace('_info', '')}:edit`,
                    action: 'disabled',
                  }"
                  v-model="scope.row.status"
                  class="ml-2"
                  style="
                    --el-switch-on-color: #13ce66;
                    --el-switch-off-color: #ff4949;
                  "
                  @change="updateStatus(scope.row, 'status')"
                />
              </template>
              <template #default="scope" v-if="item.prop === 'keepalive'">
                <el-switch
                  v-permission="{
                    id: `${route.name?.replace('_info', '')}:edit`,
                    action: 'disabled',
                  }"
                  v-model="scope.row.keepalive"
                  class="ml-2"
                  style="
                    --el-switch-on-color: #13ce66;
                    --el-switch-off-color: #ff4949;
                  "
                  @change="updateStatus(scope.row, 'keepalive')"
                />
              </template>
              <template #default="scope" v-if="item.prop === 'icon'">
                <!-- <el-icon>
                  <component :is="scope.row.icon" />

                </el-icon> -->
                <el-icon>
                  <!-- <Icon :icon="scope.row.icon"></Icon>
                    -->
                  <iconifyOffline :icon="scope.row.icon" />
                </el-icon>
              </template>
              <template #default="scope" v-if="item.prop === 'buttons'">
                <!-- <el-icon>
                  <component :is="scope.row.icon" />

                </el-icon> -->
                <el-space wrap>
                  <el-tag
                    type="success"
                    round
                    effect="plain"
                    :key="aItem.id"
                    v-for="aItem in scope.row.buttons"
                    >{{ aItem.name }}</el-tag
                  >
                </el-space>
              </template>
            </el-table-column>
            <el-table-column fixed="right" label="操作" width="150">
              <template #default="scope">
                <el-tooltip
                  class="box-item"
                  effect="dark"
                  content="编辑按钮"
                  placement="top"
                  v-if="scope.row.is_menu"
                >
                  <el-button
                    v-permission="`${route.name?.replace('_info', '')}:edit`"
                    link
                    type="primary"
                    :icon="Pointer"
                    @click="buttonEdit(scope.row)"
                  ></el-button>
                </el-tooltip>
                <el-tooltip
                  class="box-item"
                  effect="dark"
                  content="编辑菜单"
                  placement="top"
                >
                  <el-button
                    v-permission="`${route.name?.replace('_info', '')}:edit`"
                    link
                    type="primary"
                    :icon="Edit"
                    @click="handleEdit(scope.row)"
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
                    type="danger"
                    :icon="Delete"
                    @click="handleDelete(scope.row)"
                  ></el-button>
                </el-tooltip>
              </template>
            </el-table-column>
          </el-table>
          <!-- 分页 -->
        </div>
      </div>
    </div>

    <!-- 新增的弹出框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="action == 'add' ? '新增菜单' : '编辑菜单'"
      width="40%"
      :before-close="handleClose"
    >
      <el-form
        :inline="true"
        :model="formInline"
        class="demo-form-inline"
        label-position="right"
        label-width="80px"
        ref="userFrom"
        status-icon
      >
        <el-form-item
          label="菜单名称"
          prop="label"
          :rules="[{ required: true }]"
        >
          <el-input
            v-model="formInline.label"
            placeholder=""
            clearable
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item
          label="菜单标识"
          prop="name"
          :rules="[{ required: true }]"
        >
          <el-input
            v-model="formInline.name"
            placeholder=""
            clearable
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item label="路由" prop="path">
          <el-input
            v-model="formInline.path"
            placeholder=""
            clearable
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item label="图标" prop="icon" :rules="[{ required: true }]">
          <!-- <el-input v-model="formInline.icon" placeholder="" clearable /> -->
          <!-- <el-button
            @click="isShowIconSelect"
            :icon="formInline.icon"
          ></el-button> -->
          <el-button @click="isShowIconSelect">
            <iconifyOffline :icon="formInline.icon" />
          </el-button>

          <iconSelectCom
            v-model:isShow="isShow"
            v-model:iconName="formInline.icon"
          />
        </el-form-item>
        <el-form-item label="序号" prop="sort">
          <el-input-number
            v-model="formInline.sort"
            placeholder=""
            clearable
            style="width: 120px"
          />
        </el-form-item>
        <el-form-item label="父级节点" prop="parentid">
          <!-- <el-input v-model="formInline.parentid" placeholder="" clearable /> -->
          <el-tree-select
            v-model="formInline.parentid"
            ref="elTreeSelectRef"
            :data="menuList"
            clearable
            check-strictly
            :render-after-expand="false"
            node-key="id"
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formInline.description"
            placeholder=""
            clearable
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item label="启用" prop="status" :rules="[{ required: true }]">
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
          />
        </el-form-item>
        <el-form-item
          label="缓存"
          prop="keepalive"
          :rules="[{ required: true }]"
        >
          <el-switch
            v-model="formInline.keepalive"
            class="ml-2"
            inline-prompt
            style="
              --el-switch-on-color: #13ce66;
              --el-switch-off-color: #ff4949;
            "
            active-text="Y"
            inactive-text="N"
          />
        </el-form-item>
        <el-form-item
          label="是否菜单"
          prop="is_menu"
          :rules="[{ required: true }]"
        >
          <el-switch
            v-model="formInline.is_menu"
            class="ml-2"
            inline-prompt
            style="
              --el-switch-on-color: #13ce66;
              --el-switch-off-color: #ff4949;
            "
            active-text="Y"
            inactive-text="N"
          />
        </el-form-item>
        <el-form-item label="详单">
          <el-switch
            v-model="formInline.has_info"
            class="ml-2"
            style="
              --el-switch-on-color: #13ce66;
              --el-switch-off-color: #ff4949;
            "
          />
        </el-form-item>
        <el-form-item label="视图名" v-if="formInline.has_info">
          <el-input v-model="formInline.info_view_name" style="width: 180px" />
        </el-form-item>
        <el-row>
          <el-col :span="6">
            <el-form-item
              label="是否内嵌"
              prop="is_iframe"
              :rules="[{ required: true }]"
            >
              <el-switch
                v-model="formInline.is_iframe"
                class="ml-2"
                inline-prompt
                style="
                  --el-switch-on-color: #13ce66;
                  --el-switch-off-color: #ff4949;
                "
                active-text="Y"
                inactive-text="N"
              />
            </el-form-item>
          </el-col>
          <el-col :span="18">
            <el-form-item label="访问地址" v-if="formInline.is_iframe">
              <el-input
                v-model="formInline.iframe_url"
                style="width: 300px"
                type="textarea"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row style="justify-content: space-around">
          <el-form-item>
            <el-button @click="cancelAdd">取消</el-button>
            <el-button type="primary" @click="handleCommit"> 确定</el-button>
          </el-form-item>
        </el-row>
        <!-- </div> -->
      </el-form>
    </el-dialog>
    <menuButtonCom
      ref="menuButtonComRef"
      v-model:showDrawer="showButtonDia"
      :nowMenu="nowMenu"
      @getMenuData="getMenuData"
    />
  </div>
</template>

<script lang="ts" setup>
import { getCurrentInstance, onMounted, nextTick, ref, reactive } from "vue";
import iconSelectCom from "../components/iconSelectCom.vue";
import menuButtonCom from "../components/menuButtonCom.vue";
import { useRoute } from "vue-router";
const route = useRoute();
import { Icon } from "@iconify/vue";
defineOptions({ name: "menu" });

import { useStore } from "vuex";
const store = useStore();

const currentSelectRow = ref({});
const { proxy } = getCurrentInstance();
// 搜素框变量
const filterObject = reactive({
  search: "",
});
// 表格变量
const loading = ref(false);
const menuList = ref([]);
const menuTree = ref([]);

// const currentUserList = ref([])
const tableLayout = ref("auto");
// 表头
const menuListCol = ref([
  {
    prop: "label",
    label: "菜单名称",
  },
  {
    prop: "icon",
    label: "图标",
  },
  {
    prop: "is_menu",
    label: "是否菜单",
  },
  {
    prop: "status",
    label: "启用",
  },
  {
    prop: "keepalive",
    label: "缓存",
  },
  {
    prop: "sort",
    label: "序号",
  },
  {
    prop: "path",
    label: "路由地址",
  },
  {
    prop: "name",
    label: "菜单编码",
  },
  {
    prop: "description",
    label: "描述",
  },
  {
    prop: "buttons",
    label: "权限按钮",
  },
]);
// 分页变量
const currentPage = ref(1);
const pageSize = ref(10);
const small = ref(false);
const background = ref(false);
const disabled = ref(false);
const totalCount = ref(0);
// const pageConfig = reactive({
//   page: currentPage.value,
//   size: pageSize.value,
//   search: "",
//   ordering: "id",
// });
// 少于分页需求则不显示分页
const isSinglePage = ref(false);
const roleObj = ref({});
// role角色信息
const getRoleData = async () => {
  let roleInfo = await proxy.$api.getRole();
  roleInfo.data.results.forEach((item) => {
    roleObj[item.role] = item;
  });
};
// cumputed
onMounted(async () => {
  // 初始化数据切片
  // api请求获取所有数据
  await getMenuData();
  // await getRoleData();
  // selectFirst()
});

//递归多级菜单,新增key值
const deepGetFunc = (val) => {
  val.forEach((item) => {
    item.value = item.id;
    item.disabled = item.is_menu ? true : false;
    if (item.children) {
      deepGetFunc(item.children);
    }
  });
  return val;
};
// 获取菜单数据
const getMenuData = async () => {
  let res = await proxy.$api.getMenuList();
  menuList.value = res.data.results;
  menuTree.value = deepGetFunc(res.data.results);

  totalCount.value = res.data.count;
  // 隐藏下面的分页
  if (totalCount.value < pageSize.value) {
    isSinglePage.value = true;
  }
};
const handleClick = (val) => {
  // console.log(val)
  currentSelectRow.value = val;
};

// 弹出框

// 新增按钮
import { ElMessageBox, ElMessage } from "element-plus";
const dialogVisible = ref(false);
// from表单数据
const formInline = reactive({
  label: "",
  icon: "",
  sort: 0,
  is_menu: true,
  description: "",
  path: "",
  name: "",
  parentid: null,
  has_info: false,
  info_view_name: "",
  is_iframe: false,
  iframe_url: "",
  status: true,
  keepalive: true,
});
const action = ref("add");
// 显示新增弹出框
const handleAdd = () => {
  action.value = "add";
  dialogVisible.value = true;
};
// 取消新增弹出框
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
// 点击触发提交
const handleCommit = () => {
  proxy.$refs.userFrom.validate(async (valid) => {
    if (valid) {
      // 新增接口
      if (action.value == "add") {
        let res = await proxy.$api.menuAdd(formInline);
        //
        if (res.status == 201) {
          dialogVisible.value = false;
          // 重置表单
          proxy.$refs.userFrom.resetFields();
          getMenuData();
          // 更新路由
          await store.dispatch("getRoleMenu", {
            role: store.state.role,
          });
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
        let res = await proxy.$api.menuUpdate({
          id: nowRow.value.id,
          ...formInline,
        });
        if (res.status == 200) {
          dialogVisible.value = false;
          // 重置表单
          proxy.$refs.userFrom.resetFields();
          getMenuData();
          await store.dispatch("getRoleMenu", {
            role: store.state.role,
          });
        } else {
          ElMessage({
            showClose: true,
            message: "更新失败:" + JSON.stringify(res.data),
            type: "error",
          });
        }
      }
      // getMenuData();
      // 更新路由
    } else {
      ElMessage({
        showClose: true,
        message: "请输入正确内容.",
        type: "error",
      });
    }
  });
};
import { ElTree } from "element-plus";
import { ro } from "element-plus/es/locale/index.mjs";
import { Delete, Edit, Pointer } from "@element-plus/icons-vue";
const elTreeSelectRef = ref<InstanceType<typeof ElTree>>();

// 编辑
const nowRow = ref({});
const handleEdit = (row) => {
  action.value = "edit";
  nowRow.value = row;
  dialogVisible.value = true;
  // 清除新增按钮会显示编辑按钮的记录
  nextTick(() => {
    Object.keys(formInline).forEach((item) => {
      formInline[item] = row[item];
    });
  });
  console.log(formInline);
  // formInline.roleMenus = row.menu
  // elTreeSelectRef.value.setCurrentKey()
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
      let res = await proxy.$api.menuDel(row.id);
      if (res.status == 204) {
        ElMessage({
          type: "success",
          message: "删除成功",
        });
        await getMenuData();
        // 更新路由
        await store.dispatch("getRoleMenu", {
          role: store.state.role,
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
        message: "Delete canceled",
      });
    });
};

const multipleSelect = ref([]);
// 按照返回条件禁止某些行变为可勾选的
const selectFilter = (row, index) => {
  // return row.role != "管理员";
};
const handleSelectionChange = (val) => {
  multipleSelect.value = val;
};

// 搜索框
// const hanldeSearch = async() =>{
//   pageConfig.search = filterObject.search
//     }
// 添加菜单选择，20241111
const isShow = ref(false);

const isShowIconSelect = () => {
  isShow.value = true;
};
const updateStatus = async (param, vars) => {
  let res = await proxy.$api.menuUpdate({
    [vars]: param[vars],
    id: param.id,
  });
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "更新成功",
    });
    // 重置表单
    // proxy.$refs.pgroupForm.resetFields();
    getMenuData();
    await store.dispatch("getRoleMenu", {
      role: store.state.role,
    });
  } else {
    ElMessage({
      showClose: true,
      message: "更新失败:" + JSON.stringify(res.data),
      type: "error",
    });
  }
};
// 20241111，实现表格点击可以更新
const updateIsMenu = async (param) => {
  let res = await proxy.$api.menuUpdate({
    is_menu: param.is_menu,
    id: param.id,
  });
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "更新成功",
    });
    // 重置表单
    // proxy.$refs.pgroupForm.resetFields();
    getMenuData();
    await store.dispatch("getRoleMenu", {
      role: store.state.role,
    });
  } else {
    ElMessage({
      showClose: true,
      message: "更新失败:" + JSON.stringify(res.data),
      type: "error",
    });
  }
};
// const iconName = ref('ElemeFilled')

const showButtonDia = ref(false);
const nowMenu = ref({});
// 按钮编辑
const menuButtonComRef = ref(null);
const buttonEdit = (row) => {
  showButtonDia.value = true;
  // console.log
  nowMenu.value = row;
  menuButtonComRef.value!.updateMenuButtonList(row.buttons);
};
</script>
<style scoped lang="less">
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

// :deep(.el-form-item__content) {
//     width: 200px;
// }
</style>
