<template>
  <div class="card">
    <div class="portal-header">
      <div class="toolbar">
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
        <el-button
          v-permission="`${route.name?.replace('_info', '')}:delete`"
          :disabled="multipleSelect.length === 0"
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

      <div class="search-filters">
        <el-input
          v-model="searchText"
          placeholder="输入名称、链接或描述"
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
          style="width: 200px; margin-right: 10px"
        >
          <template #append>
            <el-button :icon="Search" @click="handleSearch" />
          </template>
        </el-input>

        <el-select
          v-model="filterGroupId"
          placeholder="选择分组"
          clearable
          @change="handleFilterChange"
          style="width: 150px; margin-right: 10px"
        >
          <el-option
            v-for="item in pgroupData"
            :key="item.id"
            :label="item.group"
            :value="item.id"
          />
        </el-select>

        <el-select
          v-model="filterSharingType"
          placeholder="共享类型"
          clearable
          @change="handleFilterChange"
          style="width: 120px; margin-right: 10px"
        >
          <el-option label="公共" value="public" />
          <el-option label="私人" value="private" />
        </el-select>

        <el-button @click="resetFilters">重置</el-button>
      </div>
    </div>

    <!-- 表格 -->
    <el-table
      border
      :data="tableData"
      style="width: 100%; flex: 1"
      max-height="100%"
      @selection-change="handleSelectionChange"
      v-loading="loading"
    >
      <el-table-column type="selection" width="55" />

      <el-table-column prop="name" label="名称" min-width="120" />

      <el-table-column prop="url" label="链接地址" min-width="180" />

      <el-table-column prop="group_name" label="分组" min-width="100">
        <template #default="scope">
          <el-tag>
            {{ scope.row.group_name }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="sharing_type" label="共享类型" min-width="80">
        <template #default="scope">
          <el-tag
            :type="scope.row.sharing_type === 'public' ? 'success' : 'warning'"
          >
            {{ scope.row.sharing_type === "public" ? "公共" : "私人" }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="owner_name" label="所有者" min-width="100">
        <template #default="scope">
          <span v-if="scope.row.owner_name">{{ scope.row.owner_name }}</span>
          <span v-else>-</span>
        </template>
      </el-table-column>

      <el-table-column prop="status" label="状态" width="80">
        <template #default="scope">
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

      <el-table-column prop="sort" label="排序" width="80" />

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

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="tablePageConfig.page"
      v-model:page-size="tablePageConfig.page_size"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      :total="tableDataTotal"
      style="margin-top: 15px; justify-content: flex-end"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    >
    </el-pagination>
  </div>

  <!-- 门户组的弹出框 -->
  <el-dialog v-model="diaglogPgroup" title="编辑分组" width="50%">
    <template #footer>
      <el-dialog
        v-model="innerVisible"
        width="30%"
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
            :rules="[
              { required: true, message: '请输入分组名称', trigger: 'blur' },
            ]"
          >
            <el-input
              v-model="pgroupFormInline.group"
              placeholder="请输入分组名称"
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
      <div class="pgroup-container">
        <div class="toolbar">
          <el-button type="primary" size="small" @click="handleAddPgroup"
            >新增</el-button
          >
          <el-button
            :disabled="multipleSelectPgroup.length === 0"
            type="danger"
            size="small"
            @click="handleDeleteMorePgroup"
            >批量删除</el-button
          >
        </div>
        <el-table
          :data="pgroupData"
          :default-sort="{ prop: 'id', order: 'ascending' }"
          @selection-change="handleSelectionChangePgroup"
          border
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="group" label="分组名" sortable />
          <el-table-column fixed="right" label="操作" width="120">
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
      </div>
    </template>
  </el-dialog>

  <!-- 门户弹出框 -->
  <el-dialog
    v-model="diaglogPortal"
    :title="portalAction == 'add' ? '新增链接' : '编辑链接'"
    width="600px"
  >
    <el-form
      :model="portalFormInline"
      class="portal-form"
      label-position="right"
      label-width="80px"
      ref="portalForm"
      status-icon
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item
            label="名称"
            prop="name"
            :rules="[
              { required: true, message: '请输入名称', trigger: 'blur' },
            ]"
          >
            <el-input
              v-model="portalFormInline.name"
              placeholder="请输入名称"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item
            label="链接地址"
            prop="url"
            :rules="[
              { required: true, message: '请输入链接地址', trigger: 'blur' },
            ]"
          >
            <el-input
              v-model="portalFormInline.url"
              placeholder="请输入链接地址"
              clearable
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item
            label="分组"
            prop="group"
            :rules="[
              { required: true, message: '请选择分组', trigger: 'change' },
            ]"
          >
            <el-select
              v-model="portalFormInline.group"
              filterable
              placeholder="请选择分组"
              style="width: 100%"
            >
              <el-option
                v-for="item in pgroupData"
                :key="item.id"
                :label="item.group"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item
            label="共享类型"
            prop="sharing_type"
            :rules="[
              { required: true, message: '请选择共享类型', trigger: 'change' },
            ]"
          >
            <el-select
              v-model="portalFormInline.sharing_type"
              placeholder="请选择共享类型"
              style="width: 100%"
            >
              <el-option label="公共" value="public" />
              <el-option label="私人" value="private" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="portalFormInline.username"
              placeholder="请输入用户名"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="portalFormInline.password"
              placeholder="请输入密码"
              clearable
              show-password
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="排序" prop="sort">
            <el-input-number
              v-model="portalFormInline.sort"
              controls-position="right"
              :min="0"
              style="width: 100%"
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
              active-text="新窗口"
              inactive-text="当前窗口"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="24">
          <el-form-item label="描述" prop="describe">
            <el-input
              v-model="portalFormInline.describe"
              placeholder="请输入描述"
              clearable
              type="textarea"
              :autosize="{ minRows: 2, maxRows: 4 }"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="状态" prop="status">
            <el-switch
              v-model="portalFormInline.status"
              class="ml-2"
              inline-prompt
              style="
                --el-switch-on-color: #13ce66;
                --el-switch-off-color: #ff4949;
              "
              active-text="启用"
              inactive-text="禁用"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row style="justify-content: flex-end; margin-top: 20px">
        <el-form-item>
          <el-button @click="cancelAdd">取消</el-button>
          <el-button type="primary" @click="handleCommit"> 确定</el-button>
        </el-form-item>
      </el-row>
    </el-form>
  </el-dialog>

  <el-dialog v-model="importData" title="导入" width="600px">
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
        <div class="upload-tip">
          <div>只支持从此系统下载的模板导入，请按下方按钮下载模板!</div>
          <el-button link type="primary" @click="exportTemplate()">
            下载模板
          </el-button>
        </div>
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
import { Delete, Edit, Search } from "@element-plus/icons-vue";
import { useStore } from "vuex";
import { useRoute } from "vue-router";

const route = useRoute();
const store = useStore();
const { proxy } = getCurrentInstance();

defineOptions({ name: "portalView" });

// 搜索和过滤
const searchText = ref("");
const filterGroupId = ref("");
const filterSharingType = ref("");

// 加载状态
const loading = ref(false);

// 分页配置
const tablePageConfig = reactive({
  page: 1,
  page_size: 10,
});

const allTableDataConfig = reactive({
  page: 1,
  page_size: 10,
  owner: store.state.userinfo.user_id,
});

// 表格数据
const tableData = ref([]);
const tableDataTotal = ref(0);

// 分组数据
const pgroupData = ref([]);

// 弹窗状态
const diaglogPgroup = ref(false);
const innerVisible = ref(false);
const diaglogPortal = ref(false);
const importData = ref(false);

// 表单数据
const portalFormInline = reactive({
  name: "",
  url: "",
  target: true,
  group: "",
  sharing_type: "public",
  status: true,
  username: "",
  password: "",
  sort: 9999,
  describe: "",
});

const pgroupFormInline = reactive({
  group: "",
});

// 操作类型
const portalAction = ref("add");
const pgroupAction = ref("add");

// 多选数据
const multipleSelect = ref([]);
const multipleSelectPgroup = ref([]);

// 文件上传相关
const fileList = ref([]);
const refUpload = ref(null);
const maxFiles = ref(10);

const headers = reactive({
  "Content-Type": "multipart/form-data",
});

// 计算属性
const mulSelectArr = computed(() => {
  return multipleSelect.value.map((item) => item.id);
});

// 监听分页变化
watch(
  () => tablePageConfig,
  (newVal) => {
    getTableData(newVal);
  },
  { deep: true }
);

// 监听过滤条件变化
watch([filterGroupId, filterSharingType], () => {
  handleFilterChange();
});

// 方法定义
const handleSearch = () => {
  tablePageConfig.page = 1;
  getTableData(tablePageConfig);
};

const handleFilterChange = () => {
  tablePageConfig.page = 1;
  getTableData(tablePageConfig);
};

const resetFilters = () => {
  searchText.value = "";
  filterGroupId.value = "";
  filterSharingType.value = "";
  tablePageConfig.page = 1;
  getTableData(tablePageConfig);
};

const handleSizeChange = (val) => {
  tablePageConfig.page_size = val;
  tablePageConfig.page = 1;
};

const handleCurrentChange = (val) => {
  tablePageConfig.page = val;
};

const handleSelectionChange = (val) => {
  multipleSelect.value = val;
};

const handleSelectionChangePgroup = (val) => {
  multipleSelectPgroup.value = val;
};

// 获取门户数据
const getTableData = async (config) => {
  loading.value = true;
  try {
    const params = {
      ...config,
      search: searchText.value,
      group: filterGroupId.value,
      sharing_type: filterSharingType.value,
    };

    // 清理空参数
    Object.keys(params).forEach((key) => {
      if (
        params[key] === "" ||
        params[key] === null ||
        params[key] === undefined
      ) {
        delete params[key];
      }
    });

    const res = await proxy.$api.portalGet(params);
    tableData.value = res.data.results;
    tableDataTotal.value = res.data.count;
  } catch (error) {
    ElMessage.error("获取门户数据失败");
    console.error(error);
  } finally {
    loading.value = false;
  }
};

// 获取分组数据
const getPgroupData = async () => {
  try {
    const res = await proxy.$api.pgroupGet({ page: 1, page_size: 1000 });
    pgroupData.value = res.data.results;
  } catch (error) {
    ElMessage.error("获取分组数据失败");
    console.error(error);
  }
};

// 门户操作
const handleAddPortal = () => {
  diaglogPortal.value = true;
  portalAction.value = "add";
  // 重置表单
  Object.assign(portalFormInline, {
    name: "",
    url: "",
    target: true,
    group: "",
    sharing_type: "public",
    status: true,
    username: "",
    password: "",
    sort: 9999,
    describe: "",
  });
};

const handleEdit = (row) => {
  diaglogPortal.value = true;
  portalAction.value = "edit";
  proxy.$nextTick(() => {
    Object.assign(portalFormInline, row);
  });
};

const cancelAdd = () => {
  diaglogPortal.value = false;
  proxy.$refs.portalForm?.resetFields();
};

const handleCommit = () => {
  proxy.$refs.portalForm.validate(async (valid) => {
    if (valid) {
      try {
        let res;
        if (portalAction.value === "add") {
          res = await proxy.$api.portalAdd(portalFormInline);
          if (res.status === 201) {
            ElMessage.success("添加成功");
            diaglogPortal.value = false;
            getTableData(tablePageConfig);
          } else {
            ElMessage.error("添加失败: " + JSON.stringify(res.data));
          }
        } else {
          res = await proxy.$api.portalUpdate(portalFormInline);
          if (res.status === 200) {
            ElMessage.success("更新成功");
            diaglogPortal.value = false;
            getTableData(tablePageConfig);
          } else {
            ElMessage.error("更新失败: " + JSON.stringify(res.data));
          }
        }
      } catch (error) {
        ElMessage.error("操作失败: " + error.message);
      }
    } else {
      ElMessage.error("请填写正确的表单信息");
    }
  });
};

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除门户 "${row.name}" 吗？`, "确认删除", {
    confirmButtonText: "确认",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      try {
        const res = await proxy.$api.portalDel(row.id);
        if (res.status === 204) {
          ElMessage.success("删除成功");
          getTableData(tablePageConfig);
        } else {
          ElMessage.error("删除失败");
        }
      } catch (error) {
        ElMessage.error("删除失败: " + error.message);
      }
    })
    .catch(() => {
      ElMessage.info("已取消删除");
    });
};

const handleDeleteMore = () => {
  if (multipleSelect.value.length === 0) {
    ElMessage.warning("请至少选择一项");
    return;
  }

  ElMessageBox.confirm(
    `确定要删除选中的 ${multipleSelect.value.length} 项吗？`,
    "确认删除",
    {
      confirmButtonText: "确认",
      cancelButtonText: "取消",
      type: "warning",
    }
  )
    .then(async () => {
      try {
        const delList = multipleSelect.value.map((item) => item.id);
        const res = await proxy.$api.portalMuldel({ pks: delList });
        if (res.status === 204) {
          ElMessage.success("删除成功");
          getTableData(tablePageConfig);
        } else {
          ElMessage.error("删除失败");
        }
      } catch (error) {
        ElMessage.error("删除失败: " + error.message);
      }
    })
    .catch(() => {
      ElMessage.info("已取消删除");
    });
};

// 分组操作
const handleShowPgroup = () => {
  diaglogPgroup.value = true;
};

const handleAddPgroup = () => {
  innerVisible.value = true;
  pgroupAction.value = "add";
  pgroupFormInline.group = "";
};

const handleEditPgroup = (row) => {
  innerVisible.value = true;
  pgroupAction.value = "edit";
  proxy.$nextTick(() => {
    Object.assign(pgroupFormInline, row);
  });
};

const handleCommitPgroup = () => {
  proxy.$refs.pgroupForm.validate(async (valid) => {
    if (valid) {
      try {
        let res;
        if (pgroupAction.value === "add") {
          res = await proxy.$api.pgroupAdd(pgroupFormInline);

          if (res.status === 201) {
            ElMessage.success("添加成功");
            innerVisible.value = false;
            getPgroupData();
          } else {
            ElMessage.error("添加失败: " + JSON.stringify(res.data));
          }
        } else {
          res = await proxy.$api.pgroupUpdate(pgroupFormInline);
          if (res.status === 200) {
            ElMessage.success("更新成功");
            innerVisible.value = false;
            getPgroupData();
          } else {
            ElMessage.error("更新失败: " + JSON.stringify(res.data));
          }
        }
      } catch (error) {
        ElMessage.error("操作失败: " + error.message);
      }
    } else {
      ElMessage.error("请输入正确的分组名称");
    }
  });
};

const handleDeletePgroup = (row) => {
  ElMessageBox.confirm(`确定要删除分组 "${row.group}" 吗？`, "确认删除", {
    confirmButtonText: "确认",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      try {
        const res = await proxy.$api.pgroupDel(row.id);
        if (res.status === 204) {
          ElMessage.success("删除成功");
          getPgroupData();
        } else {
          ElMessage.error("删除失败");
        }
      } catch (error) {
        ElMessage.error("删除失败: " + error.message);
      }
    })
    .catch(() => {
      ElMessage.info("已取消删除");
    });
};

const handleDeleteMorePgroup = () => {
  if (multipleSelectPgroup.value.length === 0) {
    ElMessage.warning("请至少选择一项");
    return;
  }

  ElMessageBox.confirm(
    `确定要删除选中的 ${multipleSelectPgroup.value.length} 个分组吗？`,
    "确认删除",
    {
      confirmButtonText: "确认",
      cancelButtonText: "取消",
      type: "warning",
    }
  )
    .then(async () => {
      try {
        const delList = multipleSelectPgroup.value.map((item) => item.id);
        const res = await proxy.$api.pgroupMuldel({ pks: delList });
        if (res.status === 204) {
          ElMessage.success("删除成功");
          getPgroupData();
        } else {
          ElMessage.error("删除失败");
        }
      } catch (error) {
        ElMessage.error("删除失败: " + error.message);
      }
    })
    .catch(() => {
      ElMessage.info("已取消删除");
    });
};

// 状态更新
const updatePartolStatus = async (row) => {
  try {
    const res = await proxy.$api.portalUpdate({
      status: row.status,
      id: row.id,
    });
    if (res.status === 200) {
      ElMessage.success("状态更新成功");
    } else {
      ElMessage.error("状态更新失败");
    }
  } catch (error) {
    ElMessage.error("状态更新失败: " + error.message);
  }
};

// 导入导出功能
const exportData = async () => {
  try {
    const res = await proxy.$api.portalDataExport();
    // 处理导出逻辑
  } catch (error) {
    ElMessage.error("导出失败: " + error.message);
  }
};

const exportTemplate = async () => {
  try {
    const res = await proxy.$api.portalTemplateExport();
    // 处理模板导出逻辑
  } catch (error) {
    ElMessage.error("模板导出失败: " + error.message);
  }
};

const beforeUpload = (file) => {
  const fileType = ["xlsx"];
  const fileName = file.name;

  if (file.type !== "" || file.type !== null || file.type !== undefined) {
    // 截取文件的后缀，判断文件类型
    const fileExt = file.name.replace(/.+\./, "").toLowerCase();
    // 计算文件的大小
    const isLt5M = file.size / 1024 / 1024 < 5; // 这里做文件大小限制

    // 如果大于5MB
    if (!isLt5M) {
      ElMessage.error("上传文件大小不能超过 5MB!");
      return false;
    }

    // 如果文件类型不在允许上传的范围内
    if (fileType.includes(fileExt)) {
      const found = fileList.value.find(
        (item) =>
          item.name === fileName && item.lastModified === file.lastModified
      );
      if (found) {
        ElMessage.error("该文件已上传！");
        return false;
      }
      return true;
    } else {
      ElMessage.error(`不能上传${fileExt}类型的文件`);
      return false;
    }
  }
};

const uploadFile = async (item) => {
  const formDatas = new FormData();
  formDatas.append("file", item.file);

  try {
    const res = await proxy.$api.importPortalData(
      formDatas,
      headers,
      2 * 60 * 1000
    );
    if (res.status === 200) {
      ElMessage.success(`导入成功: ${JSON.stringify(res.data)}`);
      getTableData(tablePageConfig);
      getPgroupData();
    } else {
      ElMessage.error(`导入异常: ${JSON.stringify(res.data)}`);
    }
  } catch (error) {
    ElMessage.error(`导入失败: ${error.message}`);
  }
};

// 初始化
onMounted(async () => {
  await Promise.all([getPgroupData(), getTableData(tablePageConfig)]);
});
</script>

<style scoped>
.portal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
  gap: 10px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.search-filters {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.portal-form .el-row {
  margin-bottom: 15px;
}

.upload-tip {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pgroup-container {
  padding: 10px 0;
}

@media (max-width: 768px) {
  .portal-header {
    flex-direction: column;
    align-items: stretch;
  }

  .search-filters {
    margin-top: 10px;
  }

  .search-filters .el-input,
  .search-filters .el-select {
    width: 100%;
    margin-right: 0 !important;
    margin-bottom: 10px;
  }
}
</style>