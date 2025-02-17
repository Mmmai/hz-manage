<template>
  <div class="card">
    <div class="user-header">
      <div>
        <el-button
          type="primary"
          size="small"
          @click="handleAddPortal"
          v-permission="`${route.name?.replace('_info', '')}:add`"
          >新增</el-button
        >
        <el-button
          v-permission="`${route.name?.replace('_info', '')}:add`"
          type="primary"
          size="small"
          @click="handleShowPgroup"
          >新增分组</el-button
        >
        <!-- <el-button  type="primary" size="small" @click="insertDaemonData">插入样例数据</el-button> -->
        <el-button
          v-permission="`${route.name?.replace('_info', '')}:delete`"
          v-if="multipleSelect.length == 0"
          disabled
          type="danger"
          size="small"
          @click="handleDeleteMore"
          >批量删除</el-button
        >
        <el-button
          v-permission="`${route.name?.replace('_info', '')}:delete`"
          v-else
          type="danger"
          size="small"
          @click="handleDeleteMore"
          >批量删除</el-button
        >
        <el-dropdown
          size="small"
          split-button
          type="primary"
          style="margin-left: 15px; margin-right: 15px"
        >
          更多操作
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="exportData">全部导出</el-dropdown-item>
              <el-dropdown-item @click="importData = true"
                >批量导入</el-dropdown-item
              >
              <el-dropdown-item @click="exportTemplate"
                >模版下载</el-dropdown-item
              >
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
      <el-form
        :inline="true"
        :model="filterObject"
        size="small"
        class="demo-form-inline"
      >
        <el-form-item label="名称">
          <el-input
            v-model="filterObject.search"
            placeholder="输入名称"
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="small" @click="handleSearch"
            >查询</el-button
          >
        </el-form-item>
      </el-form>
    </div>
    <!-- 表格 -->

    <el-table
      border
      :data="tableData"
      style="width: 100%; flex: 1"
      max-height="100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column
        v-for="item in tableDataCol"
        :key="item.prop"
        :label="item.label"
        :prop="item.prop"
      >
        <template #default="scope" v-if="item.prop === 'group'">
          <el-tag>
            {{ pgroupObject[scope.row.group] }}
          </el-tag>
        </template>
        <template #default="scope" v-if="item.prop === 'status'">
          <el-switch
            v-model="scope.row.status"
            class="ml-2"
            style="
              --el-switch-on-color: #13ce66;
              --el-switch-off-color: #ff4949;
            "
            @change="updatePartolStatus(scope.row)"
          />
        </template>
      </el-table-column>

      <el-table-column fixed="right" label="操作" width="150">
        <template #default="scope">
          <el-button
            type="primary"
            size="small"
            @click="handleEdit(scope.row)"
            v-permission="`${route.name?.replace('_info', '')}:edit`"
          >
            编辑
          </el-button>

          <!-- <el-button v-if="scope.row.username == 'admin'" type="danger" size="small" disabled @click="handleDelete(scope.row)">删除</el-button> -->
          <el-button
            v-permission="`${route.name?.replace('_info', '')}:delete`"
            type="danger"
            size="small"
            @click="handleDelete(scope.row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-model:current-page="tablePageConfig.page"
      v-model:page-size="tablePageConfig.page_size"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      :total="tableDataTotal"
      style="margin-top: 5px; justify-content: flex-end"
    >
    </el-pagination>
    <!-- <div style="display: flex; justify-content: center; margin-top: 10px">
        <el-pagination
          v-model:current-page="tablePageConfig.page"
          v-model:page-size="tablePageConfig.size"
          small
          background
          layout="prev, pager, next"
          :total="tableDataTotal"
          :hide-on-single-page="tableIsPage"
          @current-change="handleCurrentChangeTable"
        />
      </div> -->
  </div>
  <!-- 门户组的弹出框 -->
  <el-dialog v-model="diaglogPgroup" title="编辑分组" width="30%">
    <template #footer>
      <el-dialog
        v-model="innerVisible"
        width="20%"
        :title="pgroupAction === 'add' ? '新增分组' : '编辑分组'"
        append-to-body
      >
        <el-form
          :inline="true"
          :model="pgroupFormInline"
          class="demo-form-inline"
          label-position="right"
          label-width="80px"
          ref="pgroupForm"
          status-icon
        >
          <el-form-item
            label="分组名称"
            prop="group"
            :rules="[{ required: true }]"
          >
            <el-input
              v-model="pgroupFormInline.group"
              placeholder=""
              clearable
            />
          </el-form-item>
          <el-row style="justify-content: space-around">
            <el-form-item>
              <el-button @click="innerVisible = false">取消</el-button>
              <el-button type="primary" @click="handleCommitPgroup">
                确定</el-button
              >
            </el-form-item>
          </el-row>
        </el-form>
      </el-dialog>
    </template>
    <template #default>
      <div class="user-header">
        <div>
          <el-button type="primary" size="small" @click="handleAddPgroup"
            >新增</el-button
          >
          <el-button
            v-if="multipleSelect.length == 0"
            disabled
            type="danger"
            size="small"
            @click="handleDeleteMorePgroup"
            >批量删除</el-button
          >
          <el-button
            v-else
            type="danger"
            size="small"
            @click="handleDeleteMorePgroup"
            >批量删除</el-button
          >
        </div>
      </div>
      <el-table
        :data="pgroupData"
        :default-sort="{ prop: 'id', order: 'ascending' }"
        @selection-change="handleSelectionChangePgroup"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="group" label="分组名" sortable />
        <el-table-column fixed="right" label="操作">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              v-permission="`${route.name?.replace('_info', '')}:edit`"
              link
              :icon="Edit"
              @click="handleEditPgroup(scope.row)"
            >
            </el-button>

            <!-- <el-button v-if="scope.row.username == 'admin'" type="danger" size="small" disabled @click="handleDelete(scope.row)">删除</el-button> -->
            <el-button
              type="danger"
              v-permission="`${route.name?.replace('_info', '')}:delete`"
              link
              size="small"
              :icon="Delete"
              @click="handleDeletePgroup(scope.row)"
            >
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </template>
  </el-dialog>

  <!-- 门户弹出框 -->
  <el-dialog
    v-model="diaglogPortal"
    :title="portalAction == 'add' ? '新增链接' : '编辑链接'"
    width="50%"
  >
    <el-form
      :inline="true"
      :model="portalFormInline"
      class="demo-form-inline"
      label-position="right"
      label-width="80px"
      ref="portalForm"
      status-icon
    >
      <el-row>
        <el-col :span="12">
          <el-form-item label="名称" prop="name" :rules="[{ required: true }]">
            <el-input
              v-model="portalFormInline.name"
              placeholder=""
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item
            label="链接地址"
            prop="url"
            :rules="[{ required: true }]"
            style="width: 90%"
          >
            <el-input v-model="portalFormInline.url" placeholder="" clearable />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row>
        <el-col :span="12">
          <el-form-item label="描述" prop="describe">
            <el-input
              v-model="portalFormInline.describe"
              placeholder=""
              clearable
              style="width: 100%"
              :autosize="{ minRows: 2, maxRows: 4 }"
              type="textarea"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="分组" prop="group" :rules="[{ required: true }]">
            <el-select
              v-model="portalFormInline.group"
              filterable
              placeholder="Select"
              style="width: 120px"
            >
              <el-option
                v-for="item in pgroupData"
                :key="item.value"
                :label="item.group"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row>
        <el-col :span="12">
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="portalFormInline.username"
              placeholder=""
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="portalFormInline.password"
              placeholder=""
              clearable
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row>
        <el-col :span="12">
          <el-form-item
            label="状态"
            prop="status"
            :rules="[{ required: true }]"
          >
            <el-switch
              v-model="portalFormInline.status"
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
        <el-col :span="12">
          <el-form-item label="跳转方式" prop="target">
            <el-switch
              v-model="portalFormInline.target"
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
  <el-dialog v-model="importData" title="导入" width="800">
    <el-upload
      class="upload-demo"
      drag
      action
      ref="refUpload"
      :headers="headers"
      :http-request="uploadFile"
      :file-list="fileList"
      :before-upload="beforeUpload"
      :limit="maxFiles"
      show-file-list
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">拖拽文件到此或者 <em>点击上传文件</em></div>
      <template #tip>
        <el-row justify="space-between" align="middle">
          <el-col :span="18">
            <div>只支持从此系统下载的模板导入，请按右侧按钮下载模板!</div>
          </el-col>
          <el-col :span="3">
            <!-- <el-button link type="primary" @click="rmFileList()"
              >清除文件列表</el-button
            > -->
            <el-button link type="primary" @click="exportTemplate()"
              >点击下载模板</el-button
            >
          </el-col>
        </el-row>
      </template>
    </el-upload>
  </el-dialog>
</template>

<script setup>
import {
  ref,
  getCurrentInstance,
  onMounted,
  reactive,
  watch,
  computed,
} from "vue";
import { ElMessageBox, ElMessage } from "element-plus";
import { Delete, Edit, CircleClose, CirclePlus } from "@element-plus/icons-vue";

import { useStore } from "vuex";
import upload from "../components/uploadCom.vue";
import { useRoute } from "vue-router";
const route = useRoute();
const store = useStore();
const { proxy } = getCurrentInstance();

const filterObject = ref({
  search: null,
});
const pgroupData = ref([]);
const pgroupDataPage = ref([]);
const diaglogPgroup = ref(false);
const innerVisible = ref(false);
const pgroupAction = ref("add");
const pgroupIsPage = ref(true);
const pgroupFormInline = reactive({
  group: "",
  owner: store.state.userinfo.user_id,
});

const pgroupTotal = ref(0);
const allDataConfig = reactive({
  owner: store.state.userinfo.user_id,
});

//
const handleShowPgroup = () => {
  diaglogPgroup.value = true;
};
// 分页

// pgroup多选
const multipleSelectPgroup = ref([]);
const handleSelectionChangePgroup = (val) => {
  multipleSelectPgroup.value = val;
};
// portal多选
const multipleSelect = ref([]);
const handleSelectionChange = (val) => {
  multipleSelect.value = val;
  console.log(multipleSelect.value);
};
const mulSelectArr = computed(() => {
  let delList = [];
  for (let row in multipleSelect.value) {
    delList.push(multipleSelect.value[row].id);
  }
  return delList;
});
// 批量删除
const handleDeleteMorePgroup = () => {
  ElMessageBox.confirm("是否确认删除?", "Warning", {
    confirmButtonText: "确认删除",
    cancelButtonText: "取消",
    type: "warning",
    draggable: true,
  })
    .then(async () => {
      // 发起删除请求
      let delList = [];
      for (let row in multipleSelect.value) {
        delList.push(multipleSelect.value[row].id);
      }

      let res = await proxy.$api.portalMuldel({ pks: delList });

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
      getPgroupData();
    })
    .catch(() => {
      ElMessage({
        type: "info",
        message: "Delete canceled",
      });
    });
};
const handleAddPgroup = () => {
  innerVisible.value = true;
  pgroupAction.value = "add";
};
const handleEditPgroup = (row) => {
  innerVisible.value = true;
  pgroupAction.value = "edit";
  proxy.$nextTick(() => {
    Object.assign(pgroupFormInline, row);
  });
};
const pgroupObject = computed(() => {
  let _pgroupObject = {};
  pgroupData.value.forEach((item) => {
    _pgroupObject[item.id] = item.group;
  });
  return _pgroupObject;
});
const getPgroupData = async () => {
  let res = await proxy.$api.pgroupGet({ page: 1, page_size: 1000 });
  pgroupData.value = res.data.results;
};
const handleDeletePgroup = (row) => {
  ElMessageBox.confirm("是否确认删除?", "Warning", {
    confirmButtonText: "确认删除",
    cancelButtonText: "取消",
    type: "warning",
    draggable: true,
  })
    .then(async () => {
      // 发起删除请求
      let res = await proxy.$api.pgroupDel(row.id);
      if (res.status == 204) {
        ElMessage({
          type: "success",
          message: "删除成功",
        });
        getPgroupData();
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
const handleCommitPgroup = () => {
  proxy.$refs.pgroupForm.validate(async (valid) => {
    console.log(pgroupFormInline);
    if (valid) {
      // 新增接口
      if (pgroupAction.value == "add") {
        let res = await proxy.$api.pgroupAdd(pgroupFormInline);
        if (res.status == 201) {
          innerVisible.value = false;
          ElMessage({
            type: "success",
            message: "添加成功",
          });
          // 重置表单
          proxy.$refs.pgroupForm.resetFields();
          getPgroupData();
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
        let res = await proxy.$api.pgroupUpdate({
          group: pgroupFormInline.group,
          id: pgroupFormInline.id,
        });
        if (res.status == 200) {
          innerVisible.value = false;

          ElMessage({
            type: "success",
            message: "更新成功",
          });
          // 重置表单
          proxy.$refs.pgroupForm.resetFields();
          getPgroupData();
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

// portal门户
const diaglogPortal = ref(false);
const portalFormInline = reactive({
  name: "",
  url: "",
  target: true,
  group: "",
  status: true,
  username: "",
  password: "",
  describe: "",
  owner: store.state.userinfo.user_id,
});
const tablePageConfig = reactive({
  page: 1,
  page_size: 10,
});
watch(
  () => tablePageConfig,
  (n) => {
    getTableData(n);
  },
  { deep: true }
);
const tableDataCol = ref([
  // {
  //   prop:'id',
  //   label:'ID'
  // },
  {
    prop: "name",
    label: "名称",
  },
  {
    prop: "url",
    label: "链接地址",
  },

  {
    prop: "target",
    label: "跳转方式",
  },
  {
    prop: "status",
    label: "状态",
  },
  {
    prop: "group",
    label: "分组",
  },
  {
    prop: "username",
    label: "登录用户名",
  },
  {
    prop: "password",
    label: "密码",
  },
  {
    prop: "describe",
    label: "描述",
  },
]);
const portalAction = ref("add");
const tableData = ref([]);
// const tableDataPage = ref([])
// const tableDataPage = computed(() => {
//   return proxy.$commonFunc.pageFunc(tableData.value, tablePageConfig);
// });
const tableDataTotal = ref(0);
// const tableIsPage = computed(() => {
//   return tableData.value.length <= tablePageConfig.size ? true : false;
// });
const allTableDataConfig = reactive({
  owner: store.state.userinfo.user_id,
});
const sourceTableData = ref([]);
const getTableData = async (config) => {
  let res = await proxy.$api.portalGet(config);
  tableData.value = res.data.results;
  tableDataTotal.value = res.data.count;
};
const handleAddPortal = () => {
  diaglogPortal.value = true;
  portalAction.value = "add";
};
const cancelAdd = () => {
  diaglogPortal.value = false;
  proxy.$refs.portalForm.resetFields();
};

// 添加确定
const handleCommit = () => {
  proxy.$refs.portalForm.validate(async (valid) => {
    if (valid) {
      // 新增接口
      if (portalAction.value == "add") {
        let res = await proxy.$api.portalAdd(portalFormInline);
        if (res.status == 201) {
          ElMessage({
            type: "success",
            message: "添加成功",
          });
          // 重置表单
          proxy.$refs.portalForm.resetFields();
          getTableData(allTableDataConfig);
          diaglogPortal.value = false;
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
        let res = await proxy.$api.portalUpdate(portalFormInline);
        if (res.status == 200) {
          ElMessage({
            type: "success",
            message: "更新成功",
          });
          // 重置表单
          proxy.$refs.portalForm.resetFields();
          getTableData(allTableDataConfig);
          diaglogPortal.value = false;
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
const handleEdit = (row) => {
  diaglogPortal.value = true;
  portalAction.value = "edit";
  proxy.$nextTick(() => {
    Object.assign(portalFormInline, row);
  });
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
      let res = await proxy.$api.portalDel(row.id);
      if (res.status == 204) {
        ElMessage({
          type: "success",
          message: "删除成功",
        });
        getTableData(allTableDataConfig);
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
// 批量删除
const handleDeleteMore = () => {
  ElMessageBox.confirm("是否确认删除?", "Warning", {
    confirmButtonText: "确认删除",
    cancelButtonText: "取消",
    type: "warning",
    draggable: true,
  })
    .then(async () => {
      // 发起删除请求
      let delList = [];
      for (let row in multipleSelect.value) {
        delList.push(multipleSelect.value[row].id);
      }

      let res = await proxy.$api.portalMuldel({ pks: delList });

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
      getTableData(allTableDataConfig);
    })
    .catch(() => {
      ElMessage({
        type: "info",
        message: "Delete canceled",
      });
    });
};
onMounted(async () => {
  await getPgroupData();
  //  await
  await getTableData(allTableDataConfig);
});

// 导出功能
// 默认导出
const exportData = async () => {
  let res = await proxy.$api.portalDataExport();
  console.log(res);
  // let res = await proxy.$api.exportXls(params);

  // console.log(res);
  // proxy.$commonFunc.downloadFunc(res);
};
// 勾选导出
const exportDataSelect = () => {
  // mulSelectArr
  console.log(mulSelectArr.value);
  exportData({ rowid: mulSelectArr.value });
};
// 导出模板
const exportTemplate = async () => {
  // exportData({ template: 111 });
  let res = await proxy.$api.portalTemplateExport();
  console.log(res);
};

// 查询功能
const handleSearch = () => {
  if (filterObject.value.search != null) {
    var reg = new RegExp(filterObject.value.search);
    let tempTableData = [];
    sourceTableData.value.forEach((item) => {
      if (reg.test(item.name)) {
        tempTableData.push(item);
      }
      tableData.value = tempTableData;
    });
  }
};

const updatePartolStatus = async (param) => {
  console.log(param);
  let res = await proxy.$api.portalUpdate({
    status: param.status,
    id: param.id,
  });
  x;
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "更新成功",
    });
    // 重置表单
    // proxy.$refs.pgroupForm.resetFields();
    getPgroupData();
  } else {
    ElMessage({
      showClose: true,
      message: "更新失败:" + JSON.stringify(res.data),
      type: "error",
    });
  }
};

// 数据导入
const importData = ref(false);
const fileList = ref([]);
const refUpload = ref(null);
const fileType = ["xlsx"];
const maxFiles = ref(10);
const beforeUpload = (file) => {
  let fileName = file.name;
  if (file.type != "" || file.type != null || file.type != undefined) {
    //截取文件的后缀，判断文件类型
    const fileExt = file.name.replace(/.+\./, "").toLowerCase();
    //计算文件的大小
    const isLt5M = file.size / 1024 / 1024 < 5; //这里做文件大小限制
    //如果大于50M
    if (!isLt5M) {
      ElMessage.error("上传文件大小不能超过 5MB!");
      return false;
    }
    //如果文件类型不在允许上传的范围内
    if (fileType.includes(fileExt)) {
      let found = fileList.value.find(
        (item) =>
          item.name == fileName && item.lastModified == file.lastModified
      );
      if (found) {
        ElMessage({
          type: "error",
          message: "该文件已上传！",
          showClose: true,
        });
        return false;
      }
      // console.log(fileList.value.length);

      return true;
    } else {
      ElMessage({
        message: `不能上传${fileExt}类型的文件`,
        type: "error",
        showClose: true,
      });
      return false;
    }
  }
};
const headers = reactive({
  "Content-Type": "multipart/form-data",
});
const uploadFile = async (item) => {
  let formDatas = new FormData();
  formDatas.append("file", item.file);
  //上传文件
  let res = await proxy.$api.importPortalData(
    formDatas,
    headers,
    2 * 60 * 1000
  );
  console.log(res);
  if (res.status == 200) {
    ElMessage({
      message: `导入成功: ${JSON.stringify(res.data)}`,
      type: "success",
      showClose: true,
    });
    getPgroupData();
  } else {
    ElMessage({
      message: `导入异常: ${JSON.stringify(res.data)}`,
      type: "error",
      showClose: true,
    });
  }
};
</script>

<style>
.user-header {
  display: flex;
  justify-content: space-between;
}
</style>