<template>
  <div class="card">
    <el-tabs
      v-model="activeName"
      type="card"
      class="demo-tabs"
      @tab-click="handleClick"
    >
      <el-tab-pane
        :label="item.label"
        :name="item.name"
        :key="index"
        v-for="(item, index) in manageModelArr"
      >
      </el-tab-pane>
    </el-tabs>
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
          content="触发重装已勾选的主机"
          placement="top"
        >
          <el-button
            v-permission="`${route.name?.replace('_info', '')}:add`"
            type="primary"
            :disabled="multipleSelection.length >>> 0 ? false : true"
            @click="installAgentTask({ id: multipleSelection })"
            >批量安装</el-button
          >
        </el-tooltip>

        <!-- <el-button
          v-permission="`${route.name?.replace('_info', '')}:add`"
          type="primary"
          @click="installAgentTask({ all: true })"
          >触发失败重装</el-button
        > -->
      </div>
      <div class="header-button-ri">
        <!-- <el-select v-model="colValue" placeholder="Select" style="width: 120px">
          <el-option
            v-for="item in filterOptions"
            :key="item.value"
            :label="item.name"
            :value="item.value"
          />
        </el-select> -->
        <!-- <el-text>搜索</el-text> -->
        <el-input
          v-model="searchText"
          style="width: 240px"
          placeholder="回车查询"
          clearable
          :prefix-icon="Search"
          @clear="getNodesData()"
          @keyup.enter.native="getNodesData()"
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

      <el-table-column
        property="model_instance_name"
        label="唯一标识"
        sortable="custom"
      />
      <el-table-column property="ip_address" sortable="custom" label="ip地址" />
      <el-table-column
        property="proxy_name"
        label="代理"
        sortable="custom"
        width="120"
      >
        <template #default="scope">
          <el-tag v-if="scope.row.proxy_name ? true : false">
            {{ scope.row.proxy_name }}
          </el-tag>
          <!-- <el-tag
            :type="scope.row.status ? 'success' : 'danger'"
            effect="dark"
            >{{ scope.row.status ? "正常" : "异常" }}</el-tag
          > -->
        </template>
      </el-table-column>

      <el-table-column
        column-key="manage_status"
        property="manage_status"
        label="管理状态"
        sortable="custom"
        width="140"
        :filters="[
          { text: '正常', value: 1 },
          { text: '异常', value: 0 },
          { text: '未知', value: 2 },
        ]"
        v-if="activeName === 'hosts'"
      >
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.manage_status)" effect="dark">
            {{ getStatusText(scope.row.manage_status) }}
          </el-tag>
          <!-- <el-tag
            :type="scope.row.status ? 'success' : 'danger'"
            effect="dark"
            >{{ scope.row.status ? "正常" : "异常" }}</el-tag
          > -->
        </template>
      </el-table-column>
      <el-table-column
        column-key="enable_sync"
        property="enable_sync"
        label="是否同步"
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
            @change="switchUpdate(scope.row, 'enable_sync')"
          />
        </template>
      </el-table-column>
      <el-table-column
        column-key="agent_status"
        property="agent_status"
        label="agent状态"
        sortable="custom"
        width="140"
        :filters="[
          { text: '正常', value: 1 },
          { text: '异常', value: 0 },
          { text: '未知', value: 2 },
        ]"
        v-if="activeName === 'hosts'"
      >
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.agent_status)" effect="dark">
            {{ getStatusText(scope.row.agent_status) }}
          </el-tag>
          <!-- <el-tag
            :type="scope.row.status ? 'success' : 'danger'"
            effect="dark"
            >{{ scope.row.status ? "正常" : "异常" }}</el-tag
          > -->
        </template>
      </el-table-column>
      <el-table-column
        column-key="zbx_status"
        property="zbx_status"
        label="ZBX状态"
        sortable="custom"
        width="140"
        :filters="[
          { text: '正常', value: 1 },
          { text: '异常', value: 0 },
          { text: '未知', value: 2 },
        ]"
        v-if="activeName === 'hosts'"
      >
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.zbx_status)" effect="dark">
            {{ getStatusText(scope.row.zbx_status) }}
          </el-tag>
          <!-- <el-tag
            :type="scope.row.status ? 'success' : 'danger'"
            effect="dark"
            >{{ scope.row.status ? "正常" : "异常" }}</el-tag
          > -->
        </template>
      </el-table-column>
      <el-table-column
        property="manage_error_message"
        label="管理错误信息"
        width="500"
        v-if="activeName === 'hosts'"
      />
      <el-table-column
        property="agent_error_message"
        label="agent错误信息"
        width="500"
        v-if="activeName === 'hosts'"
      />

      <el-table-column fixed="right" width="120" label="操作">
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
          <el-tooltip
            class="box-item"
            effect="dark"
            content="触发同步"
            placement="top"
          >
            <el-button
              v-permission="`${route.name?.replace('_info', '')}:edit`"
              link
              type="primary"
              :icon="Promotion"
              @click="syncNodeToZabbix({ id: scope.row.id })"
            ></el-button>
          </el-tooltip>
          <el-tooltip
            class="box-item"
            effect="dark"
            content="管理状态更新"
            placement="top"
            v-if="activeName === 'hosts'"
          >
            <el-button
              v-permission="`${route.name?.replace('_info', '')}:edit`"
              link
              type="primary"
              :icon="Compass"
              @click="assetInfoTask({ id: scope.row.id })"
            ></el-button>
          </el-tooltip>
          <el-tooltip
            class="box-item"
            effect="dark"
            content="触发agent安装"
            placement="top"
            v-if="activeName === 'hosts'"
          >
            <el-button
              v-permission="`${route.name?.replace('_info', '')}:edit`"
              link
              type="primary"
              :icon="Refresh"
              @click="installAgentTask({ id: scope.row.id })"
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
  View,
  Promotion,
  Compass,
  Search,
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
import { useRoute } from "vue-router";
import {
  ElMessageBox,
  ElMessage,
  ElNotification,
  rowContextKey,
} from "element-plus";

import { pa, tr } from "element-plus/es/locale/index.mjs";
import { Row } from "element-plus/es/components/table-v2/src/components/index.mjs";
defineOptions({ name: "ciSyncZabbix" });
import type { TabsPaneContext } from "element-plus";

// ========== 响应式数据 ==========
const activeName = ref("hosts");
const route = useRoute();
const syncHosts = ref([]);
const isLoading = ref(true);

// 表单相关
const formRef = ref("");
const isAdd = ref(true);
const dialogVisible = ref(false);
const nowRow = ref({});
const beforeEditFormData = ref({});

// 分页相关
const currentPage = ref(1);
const pageSize = ref(10);
const size = ref("default");
const disabled = ref(false);
const totalCount = ref(0);

// 搜索和过滤相关
const searchText = ref("");
const colValue = ref("model_instance_name");
const filterValue = ref<string>("");
const filterParam = ref({});
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
]);

// 选择相关
const multipleSelection = ref([]);

// 字段类型字典
const fieldOptions = ref([]);
const validate_type = ref([]);

// 模型管理
const manageModelArr = ref([]);

// SSE相关
const eventSource = ref(null);

// ========== 计算属性 ==========
const filterOptions = computed(() => {
  let tempArr = [];
  colLists.value.forEach((item) => {
    if (item.filter) {
      tempArr.push({ name: item.label, value: item.value });
    }
  });
  return tempArr;
});

// ========== 监听器 ==========
watch(filterValue, (n) => {
  // console.log(filterParam);
  filterParam.value = { [colValue.value]: n };
});

// ========== API请求函数 ==========
/**
 * 获取管理模型配置数据
 * 从后端获取模型配置信息，过滤出is_manage为true的模型，
 * 并以{label:"名称",value:"name"}的形式组织数据后赋值给manageModelArr
 */
const getMangeModel = async () => {
  let res = await proxy.$api.getModelConfig({ ordering: "create_time" });
  if (res.status == 200) {
    manageModelArr.value = res.data.results
      .filter((item) => item.is_manage === true)
      .map((item) => ({
        label: item.model_verbose_name || item.model_name,
        name: item.model_name,
      }));
  }
};

const getNodesData = async () => {
  let res = await proxy.$api.getNodes({
    model_name: activeName.value,
    page: currentPage.value,
    page_size: pageSize.value,
    search: searchText.value,
    ...filterParam.value,
    ...sortParam.value,
  });
  // console.log(res);
  syncHosts.value = res.data.results;
  // syncHosts.value = res.data;
  totalCount.value = res.data.count;
  isLoading.value = false;
};

// 更新状态
const switchUpdate = async (row: object, key: string) => {
  let params = {};
  params[key] = row[key];
  // console.log(params);
  let res = await proxy.$api.updateNodes({ id: row.id, ...params });
  // console.log(res);
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "更新成功",
    });
    getNodesData();
  } else {
    ElMessage({
      type: "error",
      message: "更新失败",
    });
  }
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
  let res = await proxy.$api.syncZabbixHost({ model_name: activeName.value });
  // console.log(res);
  ElMessage({
    type: "success",
    message: "触发主机同步~",
  });
};
const syncNodeToZabbix = async (params: { id: string }) => {
  let res = await proxy.$api.syncZabbixHost({ node_id: params.id });
  // console.log(res);
  ElMessage({
    type: "success",
    message: "触发主机同步~",
  });
};
// 安装agent
const installAgentTask = async (params: object) => {
  let res = await proxy.$api.installAgent(params);
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "触发成功",
    });
    // openSse(`/api/v1/agent_status_sse/?cache_key=${res.data.cache_key}`);
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
};

const assetInfoTask = async (params: object) => {
  let res = await proxy.$api.get_inventory(params);
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "触发成功",
    });
    // openSse(`/api/v1/agent_status_sse/?cache_key=${res.data.cache_key}`);
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
};

// ========== 事件处理函数 ==========
const handleClick = (tab: TabsPaneContext, event: Event) => {
  console.log(tab, event);
  nextTick(() => {
    console.log(activeName.value);
    getNodesData();
  });
  // 获取数据
};

const pageChange = () => {
  getNodesData();
};

const sortParam = ref({ ordering: "-model_instance_name" });
const sortMethod = (data: any) => {
  // console.log(data);
  if (data.order === "ascending") {
    sortParam.value["ordering"] = data.prop;
  } else if (data.order === "descending") {
    sortParam.value["ordering"] = "-" + data.prop;
  } else {
    sortParam.value = { ordering: "-model_instance_name" };
  }
  // 发起请求
  getNodesData();
};

const handleClose = () => {
  dialogVisible.value = false;
  resetForm(formRef.value);
  nowRow.value = {};
};

const addData = () => {
  isAdd.value = true;
  nextTick(() => {
    dialogVisible.value = true;
  });
};

const reInstall = (row) => {};

const resetForm = (formEl) => {
  if (!formEl) return;
  formEl.resetFields();
  tmpFormData.value = [{ name: "", value: "" }];
};

const getStatusType = (status: number) => {
  if (status === 1) {
    return "success";
  } else if (status === 0) {
    return "danger";
  } else {
    return "info";
  }
};

const getStatusText = (status: number) => {
  if (status === 1) {
    return "正常";
  } else if (status === 0) {
    return "异常";
  } else {
    return "未知";
  }
};

const handleSelectionChange = (val) => {
  multipleSelection.value = val.map((item) => item.id);
};

// 过滤
const filterTag = (value, row) => {
  return row.tag === value;
};

const filterMethod = (filters: object) => {
  console.log(filters);

  const filterKey = Object.keys(filters)[0];
  const filterValues = Object.values(filters)[0];

  // 定义需要特殊处理的字段列表（这些字段在多选时应设为null）
  const specialFields = [
    "status",
    "manage_status",
    "agent_status",
    "zbx_status",
    "enable_sync",
  ];

  // if (specialFields.includes(filterKey)) {
  //   // 对于特殊字段，当有多个值时设为null，单个值时使用该值
  //   if (filterValues.length > 1) {
  //     filterParam.value[filterKey] = null;
  //   } else {
  //     filterParam.value[filterKey] = filterValues[0];
  //   }
  // } else {
  // 通用处理其他字段
  if (filterValues.length === 1) {
    // 单值过滤使用等于查询
    filterParam.value[filterKey] = filterValues[0];
  } else if (filterValues.length > 1) {
    filterParam.value[`${filterKey}`] = filterValues.join(",");
  } else {
    // 无过滤条件时清空该字段
    filterParam.value[filterKey] = null;
  }
  nextTick(() => {});
  // }

  //   nextTick(() => {
  //     getNodesData();
  //   });
  // };else {
  //     console.log(filters);
  //     // console.log(Object.keys(filters)[0]);
  //     if (Object.values(filters)[0].length > 0) {
  //       filterParam.value[`${Object.keys(filters)[0]}__in`] =
  //         Object.values(filters)[0].join(",");
  //     } else {
  //       filterParam.value[Object.keys(filters)[0]] = null;
  //     }
  //   }

  // console.log(column);
  // console.log(filterParam.value);
  nextTick(() => {
    getNodesData();
    console.log(filterParam.value);
  });
};

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
        getNodesData();
      });
    }
  };
};

const closeSse = () => {
  eventSource.value?.close();
};

// ========== 生命周期钩子 ==========
onMounted(() => {
  getNodesData();
  getMangeModel();
});

onUnmounted(() => {
  closeSse();
});
</script>

<style scoped></style>
