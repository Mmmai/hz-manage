<template>
  <div class="card">
    <div class="table-header">
      <div class="header-button-lf">
        <el-tooltip
          class="box-item"
          effect="dark"
          content="触发主机信息同步到zabbix"
          placement="top"
        >
          <el-button
            v-permission="`${route.name?.replace('_info', '')}:add`"
            type="primary"
            @click="syncToZabbix()"
            >触发同步</el-button
          >
        </el-tooltip>
        <el-tooltip
          class="box-item"
          effect="dark"
          content="更新Zabbix接口可用性的状态信息"
          placement="top"
        >
          <el-button
            v-permission="`${route.name?.replace('_info', '')}:add`"
            type="primary"
            @click="getZabbixStatus()"
            >可用性更新</el-button
          >
        </el-tooltip>

        <el-tooltip
          class="box-item"
          effect="dark"
          content="触发重装已勾选的主机"
          placement="top"
        >
          <el-button
            v-permission="`${route.name?.replace('_info', '')}:add`"
            type="primary"
            :disabled="multipleSelection.length >>> 0 ? false : true"
            @click="installAction({ ids: multipleSelection })"
            >批量安装</el-button
          >
        </el-tooltip>

        <el-button
          v-permission="`${route.name?.replace('_info', '')}:add`"
          type="primary"
          @click="installAction({ all: true })"
          >触发失败重装</el-button
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
          @clear="getZabbixSyncHost()"
          @keyup.enter.native="getZabbixSyncHost()"
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

      <el-table-column property="name" label="唯一标识" sortable="custom" />
      <el-table-column property="ip" label="ip地址" />
      <el-table-column
        column-key="interface_available"
        property="interface_available"
        label="接口可用性"
        sortable="custom"
        width="140"
        :filters="[
          { text: '未知', value: 0 },
          { text: '可用', value: 1 },
          { text: '不可用', value: 2 },
        ]"
      >
        <template #default="scope">
          <el-tag :type="avaiableTag[scope.row.interface_available].level">{{
            avaiableTag[scope.row.interface_available].label
          }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column
        column-key="agent_installed"
        property="agent_installed"
        label="agent状态"
        sortable="custom"
        width="140"
        :filters="[
          { text: '已安装', value: true },
          { text: '未安装', value: false },
        ]"
      >
        <template #default="scope">
          <el-tag
            :type="scope.row.agent_installed ? 'success' : 'danger'"
            effect="dark"
            >{{ scope.row.agent_installed ? "已安装" : "未安装" }}</el-tag
          >
        </template>
      </el-table-column>
      <el-table-column
        property="installation_error"
        label="报错信息"
        width="400"
      />
      <el-table-column fixed="right" width="80" label="操作">
        <template #default="scope">
          <el-tooltip
            class="box-item"
            effect="dark"
            content="触发安装"
            placement="top"
          >
            <el-button
              v-permission="`${route.name?.replace('_info', '')}:edit`"
              link
              type="primary"
              :icon="Refresh"
              @click="installAction({ ids: [scope.row.id] })"
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
  </div>
</template>

<script setup lang="ts">
import {
  Delete,
  Edit,
  CircleClose,
  CirclePlus,
  Refresh,
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
import { useRoute } from "vue-router";
import { ElMessageBox, ElMessage, ElNotification } from "element-plus";

import { pa, tr } from "element-plus/es/locale/index.mjs";
import { Row } from "element-plus/es/components/table-v2/src/components/index.mjs";
defineOptions({ name: "ciSyncZabbix" });

const route = useRoute();
const colValue = ref("name");
const filterValue = ref<string>("");
const isLoading = ref(true);
// const filterParam = computed(() => {
//   return { [colValue.value]: filterValue.value };
// });
// watch
const colLists = ref([
  {
    value: "name",
    label: "唯一标识",
    sort: true,
    filter: true,
    type: "string",
    required: true,
  },
  {
    value: "ip",
    label: "主机ip",
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
const formInline = reactive({
  name: null,
  verbose_name: null,
  field_type: "string",
  type: "regex",
  rule: null,
  description: null,
});

// 监听更新校验类型的值,默认拿第一个
watch(
  () => formInline.field_type,
  (n) => {
    formInline.type = validate_type.value[n][0].type;
  },
  { deep: true }
);
// 分页
const currentPage = ref(1);
const pageSize = ref(10);
const size = ref("default");
const disabled = ref(false);
const totalCount = ref(0);
const pageChange = () => {
  getZabbixSyncHost();
};
// const handleCurrentChange = () => {
//   getZabbixSyncHost();
// };
// watch(currentPage, (n) => {
//   getZabbixSyncHost();
// });
// watch(pageSize, (n) => {
//   getZabbixSyncHost();
// });
const sortParam = ref({ ordering: "-update_time" });
const sortMethod = (data) => {
  sortParam.value = { ordering: "-update_time" };
  if (data.order === "ascending") {
    sortParam.value["ordering"] = data.prop;
  } else if (data.order === "descending") {
    sortParam.value["ordering"] = "-" + data.prop;
  } else {
    sortParam.value = { ordering: "-update_time" };
  }
  // 发起请求
  getZabbixSyncHost();
};
// 弹出框
const dialogVisible = ref(false);
const handleClose = () => {
  dialogVisible.value = false;
  resetForm(formRef.value);
  nowRow.value = {};
};
const isAdd = ref(true);
const addData = () => {
  isAdd.value = true;
  nextTick(() => {
    dialogVisible.value = true;
  });
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

const getZabbixSyncHost = async (params = null) => {
  let res = await proxy.$api.getZabbixSync({
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

onMounted(() => {
  getZabbixSyncHost();
});

const multipleSelection = ref([]);
const handleSelectionChange = (val) => {
  multipleSelection.value = val.map((item) => item.id);
};

// 可用性tag标签
const avaiableTag = {
  0: { level: "info", label: "未知" },
  1: { level: "success", label: "可用" },
  2: { level: "danger", label: "不可用" },
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
  //
  // nextTick(() => {
  //   getZabbixSyncHost();
  // });
  if (Object.keys(filters)[0] === "agent_installed") {
    if (Object.values(filters)[0].length > 1) {
      filterParam.value[`${Object.keys(filters)[0]}`] = null;
    } else {
      filterParam.value[Object.keys(filters)[0]] = Object.values(filters)[0][0];
    }
  } else {
    console.log(filters);
    // console.log(Object.keys(filters)[0]);
    if (Object.values(filters)[0].length > 0) {
      filterParam.value[`${Object.keys(filters)[0]}__in`] =
        Object.values(filters)[0].join(",");
    } else {
      filterParam.value[Object.keys(filters)[0]] = null;
    }
  }

  // console.log(column);
  // console.log(filterParam.value);
  nextTick(() => {
    getZabbixSyncHost();
  });
};

const getZabbixStatus = async () => {
  let res = await proxy.$api.updateZabbixAvailability();
  // console.log(res);
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "触发成功",
    });
  }
};
const syncToZabbix = async () => {
  let res = await proxy.$api.syncZabbixHost();
  // console.log(res);
  ElMessage({
    type: "success",
    message: "触发主机同步~",
  });
};
const eventSource = ref(null);
const openSse = (sseUrl) => {
  eventSource.value = new EventSource(sseUrl);
  eventSource.value.onmessage = (event) => {
    console.log(event);
    // if (JSON.parse(event.data).status === "SUCCESS") {
    //   eventSource.value.close();
    // }

    if (JSON.parse(event.data).status === "completed") {
      closeSse();
      nextTick(() => {
        getZabbixSyncHost();
      });
    }
  };
};
const closeSse = () => {
  eventSource.value?.close();
};
// 安装agent
const installAction = async (params: object) => {
  let res = await proxy.$api.installAgent(params);
  // console.log(res);
  if (res.status == 200) {
    if (res.data.cache_key) {
      ElMessage({
        type: "success",
        message: "触发成功",
      });
      isLoading.value = true;
      openSse(`/api/v1/agent_status_sse/?cache_key=${res.data.cache_key}`);
    } else {
      ElMessage({
        type: "error",
        message: `触发失败:${res.data.message}`,
      });
    }

    // if (params.all) {
    //   openSse(`/api/v1/agent_status_sse/?all=true`);
    // } else {
    //   openSse(`/api/v1/agent_status_sse/?ids=${JSON.stringify(params.ids)}`);
    // }
  } else {
    ElMessage({
      type: "error",
      message: "触发失败",
    });
  }
};
onUnmounted(() => {
  closeSse();
});
</script>

<style scoped></style>
