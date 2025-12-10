<template>
  <div class="node-detail-view">
    <el-card class="breadcrumb-card">
      <!-- <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/node_control/nodeManage' }"
          >节点管理</el-breadcrumb-item
        >
        <el-breadcrumb-item>节点详情</el-breadcrumb-item>
      </el-breadcrumb> -->
      <el-page-header @back="goBack">
        <template #content>
          <span> 节点详情</span>
        </template>
      </el-page-header>
    </el-card>

    <el-card class="node-info-card">
      <template #header>
        <div class="card-header">
          <span>节点基本信息</span>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="实例名称">{{
          nodeInfo.model_instance_name
        }}</el-descriptions-item>
        <el-descriptions-item label="节点ID">{{
          nodeInfo.id
        }}</el-descriptions-item>

        <el-descriptions-item label="IP地址">{{
          nodeInfo.ip_address
        }}</el-descriptions-item>
        <el-descriptions-item label="模型">{{
          nodeInfo.model_name
        }}</el-descriptions-item>
        <el-descriptions-item label="代理">
          <el-tag v-if="nodeInfo.proxy_name">{{ nodeInfo.proxy_name }}</el-tag>
          <span v-else>无</span>
        </el-descriptions-item>
        <el-descriptions-item label="同步状态">
          <el-tag :type="nodeInfo.enable_sync ? 'success' : 'danger'">
            {{ nodeInfo.enable_sync ? "启用" : "禁用" }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="管理状态">
          <el-tag :type="getStatusType(nodeInfo.manage_status)">
            {{ getStatusText(nodeInfo.manage_status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Agent状态">
          <el-tag :type="getStatusType(nodeInfo.agent_status)">
            {{ getStatusText(nodeInfo.agent_status) }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- <el-card class="task-history-card">
      <template #header>
        <div class="card-header">
          <span>任务执行历史</span>
          <el-button type="primary" @click="refreshTasks">刷新</el-button>
        </div>
      </template>

      <el-table
        :data="taskHistory"
        style="width: 100%"
        v-loading="tasksLoading"
      >
        <el-table-column prop="created_at" label="执行时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getTaskStatusType(scope.row.status)">
              {{ getTaskStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="cost_time" label="耗时(秒)" width="100" />
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="viewTaskDetail(scope.row)"
              >查看详情</el-button
            >
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalTasks"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: flex-end; display: flex"
      />
    </el-card> -->
    <el-card class="task-history-card">
      <template #header>
        <div class="card-header">
          <span>任务执行历史</span>
          <div class="header-actions">
            <el-input
              v-model="taskNameFilter"
              placeholder="按任务名过滤"
              clearable
              style="width: 200px; margin-right: 10px"
              @clear="refreshTasks"
              @keyup.enter="refreshTasks"
            />
            <el-button type="primary" @click="refreshTasks">刷新</el-button>
          </div>
        </div>
      </template>

      <el-timeline v-loading="tasksLoading">
        <el-timeline-item
          v-for="task in taskHistory"
          :key="task.id"
          :type="getTaskStatusType(task.status)"
          :timestamp="formatDate(task.created_at)"
          placement="top"
        >
          <el-card shadow="hover" @click="viewTaskDetail(task)">
            <el-tooltip content="点击查看任务详情" placement="top">
              <div class="task-item-header">
                <el-tag type="primary" size="small">
                  {{ task.task_name }}
                </el-tag>
                <el-tag :type="getTaskStatusType(task.status)" size="small">
                  {{ getTaskStatusText(task.status) }}
                </el-tag>
                <span>耗时: {{ task.cost_time }} 秒</span>
                <span style="flex: 1" v-if="task.error_message"
                  >错误信息: {{ task.error_message }}</span
                >

                <!-- <el-button size="small" @click="viewTaskDetail(task)"
                >查看详情</el-button
              > -->
              </div>
            </el-tooltip>
          </el-card>
        </el-timeline-item>
        <el-timeline-item v-if="taskHistory.length === 0 && !tasksLoading">
          <el-card>
            <div class="empty-task">暂无任务执行历史</div>
          </el-card>
        </el-timeline-item>
      </el-timeline>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalTasks"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: flex-end; display: flex"
      />
    </el-card>
    <el-dialog
      v-model="dialogVisible"
      title="任务执行详情"
      width="70%"
      top="5vh"
    >
      <div class="task-detail-dialog">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="概览" name="overview">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="任务ID">{{
                currentTask.id
              }}</el-descriptions-item>
              <el-descriptions-item label="任务名称">{{
                currentTask.task_name
              }}</el-descriptions-item>
              <el-descriptions-item label="执行时间">{{
                formatDate(currentTask.created_at)
              }}</el-descriptions-item>
              <el-descriptions-item label="完成时间">{{
                currentTask.completed_at
                  ? formatDate(currentTask.completed_at)
                  : "未完成"
              }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="getTaskStatusType(currentTask.status)">
                  {{ getTaskStatusText(currentTask.status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="耗时">{{
                currentTask.cost_time ? currentTask.cost_time + " 秒" : "未知"
              }}</el-descriptions-item>
              <el-descriptions-item
                label="错误信息"
                v-if="currentTask.error_message"
              >
                <div class="error-message">{{ currentTask.error_message }}</div>
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>

          <el-tab-pane label="详细输出" name="output">
            <div class="output-container">
              <pre
                v-if="currentTask.results"
                class="output-pre"
                v-html="formatAnsibleOutput(currentTask.results)"
              ></pre>
              <div v-else class="no-output">暂无详细输出</div>
            </div>
          </el-tab-pane>

          <!-- <el-tab-pane label="资产信息" name="asset">
            <div class="asset-info-container">
              <pre v-if="currentTask.asset_info" class="asset-pre">{{
                formatJson(currentTask.asset_info)
              }}</pre>
              <div v-else class="no-asset">暂无资产信息</div>
            </div>
          </el-tab-pane> -->
        </el-tabs>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { Search, Refresh } from "@element-plus/icons-vue";
// 为了确保API调用能够正常工作，我们需要获取全局代理
import { getCurrentInstance } from "vue";
import { AnsiUp } from "ansi_up";

const { proxy } = getCurrentInstance() as any;
// 定义响应式数据
const ansiUp = new AnsiUp();
const route = useRoute();
const router = useRouter();
const nodeId = ref("");
const nodeInfo = ref({
  id: "",
  model_instance_name: "",
  ip_address: "",
  model_name: "",
  proxy_name: "",
  enable_sync: true,
  manage_status: 2,
  agent_status: 2,
});

// 任务历史相关
const taskHistory = ref([]);
const tasksLoading = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
const totalTasks = ref(0);
const taskNameFilter = ref("");

// 任务详情对话框相关
const dialogVisible = ref(false);
const currentTask = ref({
  id: "",
  created_at: "",
  completed_at: "",
  status: 2,
  cost_time: 0,
  error_message: "",
  results: "",
  asset_info: null,
});
const activeTab = ref("overview");
const formatAnsibleOutput = (data) => {
  if (!data) return "";

  try {
    let output = "";

    // 如果是字符串，直接使用
    if (typeof data === "string") {
      output = JSON.parse(data);
    }
    // 如果是对象
    else if (typeof data === "object") {
      // 检查 stdout 字段（Ansible的实际输出）
      if (data.stdout) {
        output = data.stdout;
      }
      // 检查 results 字段
      else if (data.results) {
        output =
          typeof data.results === "string"
            ? data.results
            : JSON.stringify(data.results, null, 2);
      }
      // 其他情况，格式化整个对象
      else {
        output = JSON.stringify(data, null, 2);
      }
    }

    // 使用 ansi_up 处理 ANSI 颜色代码
    return ansiUp.ansi_to_html(output);
  } catch (e) {
    // 如果处理失败，回退到原始的formatJson方法
    console.error("Failed to process ANSI codes:", e);
    return formatJson(data);
  }
};
// 组件挂载时获取数据
onMounted(() => {
  nodeId.value = (route.params.nodeId as string)
    ? route.params.nodeId
    : route.path.split("/").at(-1);
  getNodeInfo();
  getTaskHistory();
});
const goBack = () => {
  router.push({ path: "/node_control/nodeManage" });
};
// // 监听路由变化
// watch(
//   () => nodeId.value,
//   (newVal) => {
//     if (newVal) {
//       getNodeInfo();
//       getTaskHistory();
//     }
//   }
// );

// 获取节点基本信息
const getNodeInfo = async () => {
  try {
    const res = await proxy.$api.getNodeDetail(nodeId.value);
    if (res.status === 200) {
      nodeInfo.value = res.data;
      // nodeInfo.value = {
      //   id: res.data.id,
      //   model_instance_name: res.data.model_instance_name?.model_instance_name || "",
      //   ip_address: res.data.ip_address,
      //   model_name: res.data.model?.verbose_name || res.data.model?.name || "",
      //   proxy_name: res.data.proxy?.name || "",
      //   enable_sync: res.data.enable_sync,
      //   manage_status:
      //     res.data.manage_status !== undefined ? res.data.manage_status : 2,
      //   agent_status:
      //     res.data.agent_status !== undefined ? res.data.agent_status : 2,
      // };
    }
  } catch (error) {
    ElMessage.error("获取节点信息失败");
  }
};
// 获取任务历史
const getTaskHistory = async () => {
  tasksLoading.value = true;
  try {
    const params: any = {
      node_id: nodeId.value,
      page: currentPage.value,
      page_size: pageSize.value,
    };

    // 如果有过滤条件，添加到请求参数中
    if (taskNameFilter.value) {
      params.task_name = taskNameFilter.value;
    }

    const res = await proxy.$api.getNodeInfoTasks(params);
    if (res.status === 200) {
      taskHistory.value = res.data.results;
      totalTasks.value = res.data.count;
    }
  } catch (error) {
    ElMessage.error("获取任务历史失败");
  } finally {
    tasksLoading.value = false;
  }
};

// 刷新任务历史
const refreshTasks = () => {
  currentPage.value = 1;
  getTaskHistory();
};

// 查看任务详情
const viewTaskDetail = (task) => {
  currentTask.value = {
    id: task.id,
    created_at: task.created_at,
    completed_at: task.completed_at,
    status: task.status,
    cost_time: task.cost_time,
    error_message: task.error_message,
    results: task.results,
    record_info: task.record_info,
    task_name: task.task_name,
  };
  dialogVisible.value = true;
};

// 分页相关方法
const handleSizeChange = (val: number) => {
  pageSize.value = val;
  currentPage.value = 1;
  getTaskHistory();
};

const handleCurrentChange = (val: number) => {
  currentPage.value = val;
  getTaskHistory();
};

// 工具方法
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

const getTaskStatusType = (status: number) => {
  const statusMap = {
    0: "danger", // 失败
    1: "success", // 成功
    2: "info", // 未知
  };
  return statusMap[status] || "info";
};

const getTaskStatusText = (status: number) => {
  const statusMap = {
    0: "失败",
    1: "成功",
    2: "未知",
  };
  return statusMap[status] || "未知";
};

const formatDate = (dateString: string) => {
  if (!dateString) return "未知";
  const date = new Date(dateString);
  return date.toLocaleString("zh-CN");
};

const formatJson = (data: any) => {
  if (!data) return "";

  try {
    // 如果是字符串，尝试解析为JSON
    if (typeof data === "string") {
      const parsed = JSON.parse(data);
      return JSON.stringify(parsed, null, 2);
    }
    // 如果是对象，直接格式化
    return JSON.stringify(data, null, 2);
  } catch (e) {
    // 如果解析失败，直接返回原始数据
    return typeof data === "string" ? data : JSON.stringify(data, null, 2);
  }
};
</script>

<style scoped>
.node-detail-view {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100%;
  width: 100%;
}

.breadcrumb-card {
  margin-bottom: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-actions {
  display: flex;
  align-items: center;
}
.node-info-card {
  margin-bottom: 10px;
}

.task-history-card {
  margin-bottom: 10px;
}

.task-item-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.task-cost-time {
  flex: 1;
}

.empty-task {
  text-align: center;
  color: #909399;
  padding: 20px;
}
.output-container,
.asset-info-container {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 10px;
}

.output-pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  font-family: "Courier New", Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
  background-color: #1e1e1e;
  color: #dcdcdc;
  padding: 15px;
  border-radius: 4px;
  max-height: 500px;
  overflow-y: auto;
}
.asset-pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  font-family: "Courier New", Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
}

.no-output,
.no-asset {
  text-align: center;
  color: #909399;
  padding: 20px;
}

.error-message {
  color: #f56c6c;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.task-detail-dialog :deep(.el-tabs__content) {
  padding: 20px 0;
}
</style>