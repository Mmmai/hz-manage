<template>
  <div class="card">
    <!-- <el-tabs
      v-model="activeName"
      type="card"
      class="demo-tabs"
      @tab-click="handleClick"
    >
      <el-tab-pane label="主机" name="hosts"></el-tab-pane>
      <el-tab-pane label="交换机" name="switches"></el-tab-pane>
    </el-tabs> -->
    <div class="table-header">
      <div class="header-button-lf">
        <el-button
          v-permission="`${route.name?.replace('_info', '')}:add`"
          type="primary"
          @click="addNew()"
          >添加</el-button
        >
      </div>
      <div class="header-button-ri">
        <el-select v-model="colValue" placeholder="Select" style="width: 120px">
          <el-option
            v-for="item in filterOptions"
            :key="item.value"
            :label="item.name"
            :value="item.value"
          />
        </el-select>
        <el-input
          v-model="filterValue"
          style="width: 240px"
          placeholder="回车查询"
          clearable
          @clear="getProxyData()"
          @keyup.enter.native="getProxyData()"
        />
        <!-- <el-button :icon="Refresh" circle @click="reloadWind" /> -->
      </div>
    </div>
    <el-table
      v-loading="isLoading"
      ref="multipleTableRef"
      :data="syncHosts"
      style="width: 100%"
      border
      :row-key="(row) => row.id"
      @sort-change="sortMethod"
      @selection-change="handleSelectionChange"
      @filter-change="filterMethod"
    >
      <el-table-column type="selection" :reserve-selection="true" width="55" />

      <el-table-column property="name" label="代理名称" sortable="custom" />
      <el-table-column
        property="verbose_name"
        label="中文名称"
        sortable="custom"
        width="140"
      ></el-table-column>
      <el-table-column
        property="proxy_type"
        sortable="custom"
        label="代理类型"
      ></el-table-column>
      <el-table-column property="ip_address" sortable="custom" label="ip地址" />
      <el-table-column property="port" sortable="custom" label="端口" />

      <el-table-column
        property="auth_user"
        sortable="custom"
        label="认证用户"
      />
      <!-- <el-table-column
        property="auth_pass"
        sortable="custom"
        label="用户密码"
      /> -->
      <el-table-column
        column-key="enabled"
        property="enabled"
        label="是否启用"
        sortable="custom"
        width="140"
        :filters="[
          { text: '启用', value: true },
          { text: '禁用', value: false },
        ]"
      >
        <template #default="scope">
          <el-switch
            v-model="scope.row.enable_sync"
            class="ml-2"
            style="
              --el-switch-on-color: #13ce66;
              --el-switch-off-color: #ff4949;
            "
            @change="switchUpdate(scope.row, 'enabled')"
          />
        </template>
      </el-table-column>
      <el-table-column
        property="node_count"
        sortable="custom"
        label="关联节点数"
      />
      <el-table-column property="description" label="备注信息" width="400" />

      <el-table-column fixed="right" width="80" label="操作">
        <template #default="scope">
          <!-- <el-tooltip
            class="box-item"
            effect="dark"
            content="查看详情"
            placement="top"
          >
            <el-button
              v-permission="`${route.name?.replace('_info', '')}:edit`"
              link
              type="primary"
              :icon="View"
              @click="showInfo({ id: scope.row.id })"
            ></el-button>
          </el-tooltip> -->
          <!-- <el-tooltip
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
          </el-tooltip> -->
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
              @click="gotoInfo(scope.row)"
            ></el-button>
          </el-tooltip>
          <el-tooltip
            class="box-item"
            effect="dark"
            content="代理删除"
            placement="top"
          >
            <el-button
              v-permission="`${route.name?.replace('_info', '')}:edit`"
              link
              type="primary"
              :icon="Delete"
              @click="deleteRow({ id: scope.row.id })"
            ></el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="[10, 20, 50, 100, 200]"
      :size="size"
      :disabled="disabled"
      layout="total, sizes, prev, pager, next, jumper"
      :total="totalCount"
      style="margin-top: 5px; justify-content: flex-end"
      @update:current-page="pageChange()"
      @update:page-size="pageChange()"
    >
    </el-pagination>
    <!-- 添加proxy 对话框 -->
    <el-dialog v-model="dialogVisible" title="添加代理" width="500px">
      <!-- proxy表单 -->
      <el-form
        ref="proxyFormRef"
        :model="proxyForm"
        :rules="proxyFormRules"
        label-width="100px"
      >
        <el-form-item label="代理名称" prop="name">
          <el-input v-model="proxyForm.name" placeholder="请输入代理名称" />
        </el-form-item>
        <el-form-item label="中文名称" prop="verbose_name">
          <el-input
            v-model="proxyForm.verbose_name"
            placeholder="请输入中文名称"
          />
        </el-form-item>
        <el-form-item label="代理类型" prop="proxy_type">
          <el-select
            v-model="proxyForm.proxy_type"
            placeholder="请选择代理类型"
          >
            <el-option
              v-for="item in proxyTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            >
              <span style="float: left">{{ item.label }}</span>
              <span
                style="
                  float: right;
                  color: var(--el-text-color-secondary);
                  font-size: 13px;
                "
              >
                {{ item.description }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="是否启用" prop="enabled">
          <el-switch v-model="proxyForm.enabled" />
        </el-form-item>
        <el-form-item label="代理ip" prop="ip_address">
          <el-input v-model="proxyForm.ip_address" placeholder="请输入代理ip" />
        </el-form-item>

        <el-form-item label="代理端口" prop="port">
          <el-input-number
            v-model="proxyForm.port"
            placeholder="请输入代理端口"
            :min="1"
            :max="65535"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="认证用户" prop="auth_user">
          <el-input
            v-model="proxyForm.auth_user"
            placeholder="请输入认证用户"
          />
        </el-form-item>
        <el-form-item label="用户密码" prop="auth_pass">
          <el-input
            v-model="proxyForm.auth_pass"
            type="password"
            placeholder="请输入用户密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="备注信息" prop="description">
          <el-input
            v-model="proxyForm.description"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeDia()">取消</el-button>
          <el-button v-if="isAdd" type="primary" @click="addAction()"
            >提交</el-button
          >
          <el-button v-else type="primary" @click="updateAction()"
            >更新</el-button
          >
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import {
  Delete,
  Edit,
  CircleClose,
  CirclePlus,
  Refresh,
  View,
  Compass,
} from "@element-plus/icons-vue";
import {
  ref,
  computed,
  watch,
  getCurrentInstance,
  onMounted,
  reactive,
  nextTick,
  onUnmounted,
} from "vue";
const { proxy } = getCurrentInstance();
import { useStore } from "vuex";
const store = useStore();
const syncHosts = ref([]);
import { ElMessageBox, ElMessage, ElNotification } from "element-plus";

import { de, pa, tr } from "element-plus/es/locale/index.mjs";
import { Row } from "element-plus/es/components/table-v2/src/components/index.mjs";
defineOptions({ name: "ciSyncZabbix" });
import type { TabsPaneContext } from "element-plus";
import { add } from "lodash";
import { useRoute, useRouter } from "vue-router";
const router = useRouter();
const route = useRoute();
const activeName = ref("hosts");

const handleClick = (tab: TabsPaneContext, event: Event) => {
  console.log(tab, event);
  console.log(activeName.value);
};
const colValue = ref("model_instance_name");
const filterValue = ref<string>("");
const isLoading = ref(true);
// const filterParam = computed(() => {
//   return { [colValue.value]: filterValue.value };
// });
// watch
const colLists = ref([
  {
    value: "model_instance_name",
    label: "唯一标识",
    sort: true,
    filter: true,
    type: "string",
    required: true,
  },
  {
    value: "ip_address",
    label: "ip地址",
    sort: false,
    filter: true,
    type: "string",
    required: true,
  },
  // {
  //   value: "interface_available",
  //   label: "接口可用性",
  //   sort: true,
  //   filter: true,
  //   type: "string",
  //   required: true,
  // },
  // {
  //   value: "agent_installed",
  //   label: "agent状态",
  //   sort: true,
  //   filter: true,
  //   type: "string",
  // },
]);
// 过滤选项
const filterOptions = computed(() => {
  let tempArr = [];
  colLists.value.forEach((item) => {
    if (item.filter) {
      tempArr.push({ name: item.label, value: item.value });
    }
  });
  return tempArr;
});
// 表格字段
// const tableCol = computed(() => {
//   return colLists.value.map(item => {
//     if (item.sort) {
//       return { name: item.label, value: item.value }
//     }
//   })
// })
const formRef = ref("");
// 表单字段
const proxyForm = reactive({
  name: "",
  verbose_name: "",
  proxy_type: "all",
  enabled: true,
  ip_address: "",
  port: 22,
  auth_user: "",
  auth_pass: "",
  description: "",
});
// 代理类型选项
const proxyTypeOptions = [
  { label: "all", value: "all", description: "所有类型,支持zabbix和ansible" },
  { label: "zabbix", value: "zabbix", description: "zabbix代理" },
  { label: "ansible", value: "ansible", description: "ansible代理" },
];

// 表单验证规则
const proxyFormRules = {
  name: [
    { required: true, message: "请输入代理名称(不支持中文)", trigger: "blur" },
    {
      pattern:
        /^((\d{1,3}\.){1,3}\d{1,3})?[a-zA-Z0-9_-]{1,32}((\d{1,3}\.){1,3}\d{1,3})?$/,
      message: "请输入正确的代理名称,不支持中文等特殊符号",
      trigger: "blur",
    },
  ],

  proxy_type: [
    { required: true, message: "请选择代理类型", trigger: "change" },
  ],
  ip_address: [
    { required: true, message: "请输入代理IP", trigger: "blur" },
    {
      pattern: /^(\d{1,3}\.){3}\d{1,3}$/,
      message: "请输入正确的IP地址格式",
      trigger: "blur",
    },
  ],
  port: [
    { required: true, message: "请输入代理端口", trigger: "blur" },
    {
      type: "number",
      min: 1,
      max: 65535,
      message: "端口号应在1-65535之间",
      trigger: "blur",
    },
  ],
  auth_user: [{ required: true, message: "请输入认证用户", trigger: "blur" }],
  auth_pass: [{ required: true, message: "请输入用户密码", trigger: "blur" }],
};
// 分页
const currentPage = ref(1);
const pageSize = ref(10);
const size = ref("default");
const disabled = ref(false);
const totalCount = ref(0);
const pageChange = () => {
  getProxyData();
};

const sortParam = ref({ ordering: "-name" });
const sortMethod = (data) => {
  // console.log(data);
  if (data.order === "ascending") {
    sortParam.value["ordering"] = data.prop;
  } else if (data.order === "descending") {
    sortParam.value["ordering"] = "-" + data.prop;
  } else {
    sortParam.value = { ordering: "-name" };
  }
  // 发起请求
  getProxyData();
};
// 弹出框
const dialogVisible = ref(false);
const handleClose = () => {
  dialogVisible.value = false;
  resetForm(formRef.value);
  nowRow.value = {};
};

const nowRow = ref({});
const beforeEditFormData = ref({});

const reInstall = (row) => {};

const resetForm = (formEl) => {
  if (!formEl) return;
  formEl.resetFields();
  tmpFormData.value = [{ name: "", value: "" }];
};
// 获取字段类型字典
const fieldOptions = ref([]);
const validate_type = ref([]);
// 后端请求

const getProxyData = async (params = null) => {
  let res = await proxy.$api.getProxy({
    page: currentPage.value,
    page_size: pageSize.value,
    ...filterParam.value,
    ...sortParam.value,
    ...params,
  });
  // console.log(res);
  syncHosts.value = res.data.results;
  // syncHosts.value = res.data;
  totalCount.value = res.data.count;
  isLoading.value = false;
};
// 添加按钮
const isAdd = ref(true);
const addNew = () => {
  isAdd.value = true;
  nextTick(() => {
    dialogVisible.value = true;
  });
};
// 添加
const addAction = async () => {
  let res = await proxy.$api.addProxy(proxyForm);
  if (res.status == 201) {
    ElMessage({
      type: "success",
      message: "添加成功",
    });
    dialogVisible.value = false;
    getProxyData();
  } else {
    ElMessage({
      type: "error",
      message: `添加失败: ${res.data}`,
    });
  }
};
// 删除
const deleteRow = async (row) => {
  ElMessageBox.confirm("是否确认删除?", "Warning", {
    confirmButtonText: "确认删除",
    cancelButtonText: "取消",
    type: "warning",
    draggable: true,
  }).then(async () => {
    // 判断是否可以删除，如果有节点关联到代理，则不能删除
    if (row.node_count > 0) {
      ElMessage({
        type: "error",
        message: `已有${row.node_count}个节点关联到代理，无法删除proxy`,
      });
      return;
    }

    // 发起删除请求
    let res = await proxy.$api.deleteProxy(row.id);
    if (res.status == 204) {
      ElMessage({
        type: "success",
        message: "删除成功",
      });
      getProxyData();
    } else {
      ElMessage({
        type: "error",
        message: `删除失败: ${res.data}`,
      });
    }
  });
};
// 编辑按钮
const editRow = (row) => {
  dialogVisible.value = true;
  isAdd.value = false;
  // 将行数据赋予表单
  nextTick(() => {
    Object.assign(proxyForm, row);
  });
};
// 视图切换
const gotoInfo = (row) => {
  router.push({ path: route.path + "/" + row.id });
};
// 更新
const updateAction = async () => {
  let res = await proxy.$api.updateProxy({ id: row.id, ...proxyForm });
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "更新成功",
    });
    dialogVisible.value = false;
    getProxyData();
    resetForm(formRef.value);
  } else {
    ElMessage({
      type: "error",
      message: `更新失败: ${res.data}`,
    });
  }
};
// 更新状态
const switchUpdate = async (row, key) => {
  let params = {};
  params[key] = row[key];
  // console.log(params);
  let res = await proxy.$api.updateProxy({ id: row.id, ...params });
  // console.log(res);
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "更新成功",
    });
    getProxyData();
  } else {
    ElMessage({
      type: "error",
      message: "更新失败",
    });
  }
};
onMounted(() => {
  getProxyData();
});

const multipleSelection = ref([]);
const handleSelectionChange = (val) => {
  multipleSelection.value = val.map((item) => item.id);
};

// 过滤
const filterTag = (value, row) => {
  return row.tag === value;
};
const filterParam = ref({});
watch(filterValue, (n) => {
  // console.log(filterParam);
  filterParam.value = { [colValue.value]: n };
});

const filterMethod = (filters: object) => {
  console.log(filters);
  nextTick(() => {
    getProxyData();
  });
};

// 添加proxy
const openDia = () => {
  dialogVisible.value = true;
};
const closeDia = () => {
  dialogVisible.value = false;
  resetForm(formRef.value);
};

onUnmounted(() => {});
</script>

<style scoped></style>
