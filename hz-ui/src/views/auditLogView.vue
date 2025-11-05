<template>
  <div class="divVertical">
    <div class="card filter-card">
      <!-- 筛选区域 -->
      <div class="filter-container">
        <!-- 模型筛选 -->
        <div class="filter-row">
          <div class="filter-item">
            <span class="filter-label">操作对象：</span>
            <el-tag
              v-for="(label, value, index) in targetTypeMap"
              :key="index"
              :type="selectedModels.includes(value) ? 'primary' : 'info'"
              @click="toggleModel(value)"
              class="filter-tag"
            >
              {{ label }}
            </el-tag>
          </div>
        </div>

        <!-- 其他筛选条件 -->
        <div class="filter-row filter-row-flex">
          <!-- 操作类型筛选 -->
          <div class="filter-item">
            <span class="filter-label">操作类型：</span>
            <el-tag
              v-for="tag in operationTags"
              :key="tag.value"
              :type="
                selectedOperations.includes(tag.value) ? 'primary' : 'info'
              "
              @click="toggleOperation(tag.value)"
              class="filter-tag"
            >
              {{ tag.label }}
            </el-tag>
          </div>

          <!-- 时间筛选 -->
          <div class="filter-item">
            <span class="filter-label">时间范围：</span>
            <el-date-picker
              v-model="timeRange"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始时间"
              end-placeholder="结束时间"
              value-format="YYYY-MM-DDTHH:mm:ss"
              :shortcuts="shortcuts"
              @change="handleTimeChange"
            />
          </div>

          <!-- 搜索框 -->
          <div class="filter-item">
            <el-input
              v-model="searchKeyword"
              placeholder="请输入搜索关键词"
              clearable
              style="width: 200px"
              @keyup.enter="handleSearch"
            >
              <template #append>
                <el-button :icon="Search" @click="handleSearch" />
              </template>
            </el-input>
          </div>

          <!-- 重置按钮 -->
          <div class="filter-item">
            <el-button @click="resetFilters">重置</el-button>
          </div>
        </div>
      </div>
    </div>
    <div class="card table-container" style="width: 100%">
      <!-- 审计日志表格 -->
      <el-table
        :data="auditLogs"
        style="flex: 1"
        border
        table-layout="fixed"
        highlight-current-row
      >
        <el-table-column prop="target_type" label="操作对象" width="120">
          <template #default="scope">
            <el-tooltip content="查看详情" placement="right" effect="dark">
              <span class="target-type-link" @click="showDetail(scope.row)">
                {{ formatTargetType(scope.row.target_type) }}</span
              >
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="操作类型" width="120">
          <template #default="scope">
            <el-tag :type="formatActionTag(scope.row.action)">{{
              formatActionType(scope.row.action)
            }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operator" label="操作人" width="120" />
        <el-table-column prop="operator_ip" label="操作人IP" width="120" />

        <el-table-column
          prop="comment"
          label="操作描述"
          show-overflow-tooltip
        />
        <el-table-column label="变更内容">
          <template #default="scope">
            <div class="change-content">
              <div
                v-if="scope.row.action == 'UPDATE'"
                v-for="(change, index) in formatChanges(scope.row)"
                :key="index"
                class="change-item"
              >
                <el-text tag="b">{{ change.field }}: </el-text>
                <span v-if="change.oldValue !== undefined" class="old-value">{{
                  change.oldValue !== null ? change.oldValue : "null"
                }}</span>
                <el-text v-else>null</el-text>
                <el-text
                  v-if="
                    change.oldValue !== undefined &&
                    change.newValue !== undefined
                  "
                  tag="b"
                  type="warning"
                >
                  →
                </el-text>
                <span v-if="change.newValue !== undefined" class="new-value">{{
                  change.newValue !== null ? change.newValue : "null"
                }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="timestamp" label="操作时间" width="300" />
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100, 200]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @update:current-page="pageChange()"
        @update:page-size="pageChange()"
        style="margin-top: 20px; justify-content: flex-end; display: flex"
      />
    </div>

    <!-- 抽屉组件用于显示详细信息 -->
    <el-drawer
      v-model="drawerVisible"
      title="详细信息"
      direction="rtl"
      size="50%"
    >
      <div class="drawer-content">
        <json-viewer
          :value="currentRowData"
          :expand-depth="5"
          copyable
          boxed
          sort
        ></json-viewer>
      </div>
    </el-drawer>
  </div>
</template>
<script lang="ts" setup>
import {
  ref,
  computed,
  watch,
  getCurrentInstance,
  onMounted,
  reactive,
  nextTick,
} from "vue";
import { Search } from "@element-plus/icons-vue";
import { ElDrawer } from "element-plus";
import { JsonViewer } from "vue3-json-viewer";
import "vue3-json-viewer/dist/vue3-json-viewer.css";
const { proxy } = getCurrentInstance();
import { encrypt_sm4, decrypt_sm4 } from "@/utils/gmCrypto.ts";

import useConfigStore from "@/store/config";
const configStore = useConfigStore();
const gmConfig = computed(() => configStore.gmCry);

// 模型标签选项
const modelTags = ref([
  { value: "host", label: "主机" },
  { value: "switch", label: "交换机" },
  // 可以根据实际需求添加更多模型
]);

// 操作类型标签选项
const operationTags = ref([
  { value: "CREATE", label: "创建" },
  { value: "DELETE", label: "删除" },
  { value: "UPDATE", label: "修改" },
]);

// 已选中的模型
const selectedModels = ref([]);

// 已选中的操作类型
const selectedOperations = ref([]);

// 时间范围
const timeRange = ref([]);
const shortcuts = [
  {
    text: "最近1天",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(end.getTime() - 3600 * 1000 * 24 * 1);
      return [start, end];
    },
  },
  {
    text: "最近3天",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(end.getTime() - 3600 * 1000 * 24 * 3);
      return [start, end];
    },
  },
  {
    text: "最近5天",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(end.getTime() - 3600 * 1000 * 24 * 5);
      return [start, end];
    },
  },
  {
    text: "最近7天",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(end.getTime() - 3600 * 1000 * 24 * 7);
      return [start, end];
    },
  },
  {
    text: "最近1周",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(end.getTime() - 3600 * 1000 * 24 * 7);
      return [start, end];
    },
  },
  {
    text: "最近1个月",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(end.getTime() - 3600 * 1000 * 24 * 30);
      return [start, end];
    },
  },
  {
    text: "最近3个月",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setTime(end.getTime() - 3600 * 1000 * 24 * 90);
      return [start, end];
    },
  },
];

// 设置默认时间范围为当天00:00到23:59
const setDefaultTimeRange = () => {
  const start = new Date();
  const end = new Date();
  end.setHours(23, 59, 59, 999); // 设置为当天23:59:59
  start.setTime(end.getTime() - 3600 * 1000 * 24 * 30); //设置为一个月前的时间
  start.setHours(0, 0, 0, 0); // 设置为当天00:00:00
  // 转换为北京时间字符串格式
  const formatDate = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const seconds = String(date.getSeconds()).padStart(2, "0");
    const milliseconds = String(date.getMilliseconds()).padStart(3, "0");
    return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}.${milliseconds}`;
  };

  timeRange.value = [formatDate(start), formatDate(end)];
};

// 搜索关键词
const searchKeyword = ref("");

// 切换模型筛选条件
const toggleModel = (model) => {
  const index = selectedModels.value.indexOf(model);
  if (index === -1) {
    selectedModels.value.push(model);
  } else {
    selectedModels.value.splice(index, 1);
  }
  // 触发筛选
  fetchAuditLogs();
};

// 切换操作类型筛选条件
const toggleOperation = (operation) => {
  const index = selectedOperations.value.indexOf(operation);
  if (index === -1) {
    selectedOperations.value.push(operation);
  } else {
    selectedOperations.value.splice(index, 1);
  }
  // 触发筛选
  fetchAuditLogs();
};

// 处理时间范围变化
const handleTimeChange = (val) => {
  timeRange.value = val;
  console.log("时间范围:", val);
  // 触发筛选
  fetchAuditLogs();
};

// 处理搜索
const handleSearch = () => {
  // 触发筛选
  fetchAuditLogs();
};

// 表格
const auditLogs = ref([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const pageChange = () => {
  fetchAuditLogs();
};

// 抽屉相关变量
const drawerVisible = ref(false);
const currentRowData = ref({});
const formattedJson = computed(() => {
  return JSON.stringify(currentRowData.value, null, 2);
});

// 显示详情抽屉
const showDetail = (row) => {
  currentRowData.value = row;
  drawerVisible.value = true;
};

const targetTypeMap = {
  model: "模型",
  model_field: "字段",
  model_instance: "实例",
  model_group: "模型组",
  unique_constraint: "唯一约束",
  model_field_group: "模型字段组",
  validation_rule: "校验规则",
  model_instance_group: "实例组",
  relation_definition: "关系定义",
  // 可以根据实际需求添加更多模型
};
const formatTargetType = (type) => {
  return targetTypeMap[type] || type;
};
const actionTypeMap = {
  CREATE: "创建",
  UPDATE: "修改",
  DELETE: "删除",
};

// 格式化操作类型显示
const formatActionType = (action) => {
  return actionTypeMap[action] || action;
};
const formatActionTag = (action: string) => {
  // CREATE -> return primary
  // UPDATE -> return success
  // DELETE -> return danger
  const tagMap: Record<string, string> = {
    CREATE: "success",
    UPDATE: "warning",
    DELETE: "danger",
  };
  return tagMap[action] || "";
};
// 获取变更内容
// ... existing code ...
const changeMap = {
  groups: "实例组",
  instance_name: "实例名称",
  order: "排序",
  verbose_name: "字段名称",
  model_field_group: "字段分组",
  instance_name_template: "实例名称模板",
  fields: "字段组合",
  // update_user: "更新用户",
};
const formatChanges = (row) => {
  const changes = [];

  // 处理 changed_fields 字段
  if (row.changed_fields) {
    Object.keys(row.changed_fields).forEach((field) => {
      const values = row.changed_fields[field];
      if (field === "update_user") {
        return;
      } else if (field === "groups") {
        changes.push({
          field: changeMap[field],
          oldValue: values[0].map((item) => item.path).join(","),
          newValue: values[1].map((item) => item.path).join(","),
        });
      } else if (field === "instance_name_template") {
        // console.log(
        //   "instance_name_template:",
        //   values[0].map((item) => item.verbose_name).join("-") ? 111 : 222
        // );
        changes.push({
          field: changeMap[field],
          oldValue:
            values[0].length >> 0
              ? values[0].map((item) => item.verbose_name).join("-")
              : null,
          newValue:
            values[1].length >> 0
              ? values[1].map((item) => item.verbose_name).join("-")
              : null,
        });
      } else {
        changes.push({
          field: changeMap.hasOwnProperty(field) ? changeMap[field] : field,
          oldValue: formatDetails(values[0]),
          newValue: formatDetails(values[1]),
        });
      }
    });
  }

  // 处理 details 字段
  if (row.details) {
    row.details.forEach((detail) => {
      changes.push({
        field: detail.verbose_name || detail.name,
        oldValue: formatDetails(detail.old_value),
        newValue: formatDetails(detail.new_value),
      });
    });
  }

  return changes;
};
// 处理enum,model_ref
const formatDetails = (text) => {
  const processObject = (parsed) => {
    if (typeof parsed === "object" && parsed !== null) {
      if (parsed.hasOwnProperty("label") && parsed.label !== undefined) {
        return parsed.label;
      } else if (
        parsed.hasOwnProperty("instance_name") &&
        parsed.instance_name !== undefined
      ) {
        return parsed.instance_name;
      } else if (
        parsed.hasOwnProperty("verbose_name") &&
        parsed.verbose_name !== undefined
      ) {
        return parsed.verbose_name;
      } else if (
        parsed.hasOwnProperty("password") &&
        parsed.password !== undefined
      ) {
        if (configStore.isShowPass) {
          return decrypt_sm4(
            gmConfig.value.key,
            gmConfig.value.mode,
            parsed.password
          );
        } else {
          return "******";
        }
      } else if (typeof parsed === "object") {
        // console.log("text:", parsed);
        return parsed.map((item) => item.verbose_name).join("-");
      }
    }
  };
  if (text === null) return text;

  // 如果是对象，直接处理
  if (typeof text === "object") {
    return processObject(text);
  }

  // 如果是字符串，尝试解析为对象后再处理
  else if (typeof text === "string") {
    try {
      const parsed = JSON.parse(text);
      return processObject(parsed);
    } catch (e) {
      // 解析失败则按普通字符串处理
      return text;
    }
  }
  return text;
};
// 请求
// 获取审计日志数据
const fetchAuditLogs = async () => {
  try {
    // 构造查询参数
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      // 添加筛选条件
      target_type: selectedModels.value.length
        ? selectedModels.value.join(",")
        : undefined,
      action: selectedOperations.value.length
        ? selectedOperations.value.join(",")
        : undefined,
      time_after:
        timeRange.value && timeRange.value[0] ? timeRange.value[0] : undefined,
      time_before:
        timeRange.value && timeRange.value[1] ? timeRange.value[1] : undefined,
      search: searchKeyword.value || undefined,
    };

    // 调用API获取数据
    // 这里需要替换为实际的API调用
    const res = await proxy.$api.getAuditLog(params);

    auditLogs.value = res.data.results;
    total.value = res.data.count;
  } catch (error) {
    console.error("获取审计日志失败:", error);
    proxy.$message.error("获取审计日志失败");
  }
};

// 重置筛选条件
const resetFilters = () => {
  selectedModels.value = [];
  selectedOperations.value = [];
  timeRange.value = [];
  searchKeyword.value = "";
  setDefaultTimeRange();
  // 触发筛选
  fetchAuditLogs();
};

// 当筛选条件变化时重新获取数据
// watch(
//   [selectedModels, selectedOperations, timeRange],
//   () => {
//     fetchAuditLogs();
//   },
//   { deep: true }
// );
// 页面加载时获取数据
onMounted(() => {
  setDefaultTimeRange();
  fetchAuditLogs();
});
</script>
<style scoped lang="scss">
.filter-card {
  height: 100px;
  padding: 10px 15px;
  overflow-y: auto;
  flex: none;
}

.table-container {
  flex: 1;
  overflow: auto;
}

.filter-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 15px;
}

.filter-row-flex {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.filter-item {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.filter-label {
  font-weight: bold;
  margin-right: 8px;
  white-space: nowrap;
}

.filter-tag {
  margin-right: 8px;
  cursor: pointer;
  user-select: none;
}

.filter-tag:last-child {
  margin-right: 0;
}

.quick-select-container {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  padding: 10px;
  border-top: 1px solid #ebeef5;
  margin-top: 5px;
}

.target-type-link {
  color: #409eff;
  cursor: pointer;
  text-decoration: underline;
}

.drawer-content {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
}

.drawer-content pre {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  font-family: "Courier New", Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .filter-row-flex {
    flex-direction: column;
    align-items: flex-start;
  }

  .filter-item {
    width: 100%;
    margin-bottom: 10px;
  }

  .filter-card {
    height: auto;
    max-height: 180px;
  }
}
</style>