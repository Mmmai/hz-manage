<template>
  <div class="cmdb-search-container">
    <div class="search-header">
      <el-card class="search-card">
        <div class="search-form">
          <el-input
            v-model="searchKeyword"
            placeholder="请输入关键词搜索实例..."
            clearable
            @keyup.enter="performSearch"
            class="search-input"
            style="width: 400px"
            @clear="clearSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <div class="search-options">
            <el-checkbox v-model="regexp" @change="onRegexpChange">
              正则表达式
            </el-checkbox>
            <el-checkbox v-model="caseSensitive"> 区分大小写 </el-checkbox>
          </div>
        </div>
        <div v-if="regexpError" class="regexp-error-message">
          <el-icon color="#F56C6C"><Warning /></el-icon>
          <span class="error-text">{{ regexpError }}</span>
        </div>
        <div class="filter-section" v-if="allModels.length > 0">
          <div class="filter-title">模型筛选:</div>
          <el-checkbox
            v-model="selectAllModels"
            @change="handleSelectAllModels"
            class="select-all-checkbox"
          >
            全选
          </el-checkbox>
          <el-checkbox-group
            v-model="selectedModelIds"
            class="model-checkbox-group"
          >
            <el-checkbox
              v-for="model in allModels"
              :key="model.id"
              :label="model.id"
              class="model-checkbox"
            >
              {{ model.verbose_name }}
            </el-checkbox>
          </el-checkbox-group>
        </div>
      </el-card>
    </div>

    <div class="search-results" v-loading="searchLoading">
      <div class="results-header">
        <div class="results-count">
          找到 {{ filteredResults.length }} 个实例
          <span v-if="Object.keys(modelStats).length > 0" class="model-stats">
            (
            <el-tag
              v-for="(count, modelId) in modelStats"
              :key="modelId"
              :type="resultModelFilter === modelId ? 'primary' : 'info'"
              size="small"
              class="model-stat-tag"
              @click="toggleModelFilter(modelId)"
              :effect="resultModelFilter === modelId ? 'dark' : 'light'"
              style="cursor: pointer; margin-right: 5px"
            >
              {{ getModelVerboseName(modelId) }}: {{ count }}个
            </el-tag>
            <!-- <el-tag
              v-if="resultModelFilter"
              type="warning"
              size="small"
              class="clear-filter-tag"
              @click="clearModelFilter"
              style="cursor: pointer"
            >
              清除过滤
            </el-tag> -->
            )
          </span>
        </div>
        <div class="result-filters" v-if="searchResults.length > 0">
          <!-- <div class="model-filter">
            <span>模型过滤:</span>
            <el-select
              v-model="resultModelFilter"
              placeholder="全部模型"
              clearable
              @change="filterResultsByModel"
              class="model-filter-select"
            >
              <el-option
                v-for="(count, modelId) in modelStats"
                :key="modelId"
                :label="`${getModelVerboseName(modelId)} (${count})`"
                :value="modelId"
              />
            </el-select>
          </div> -->
          <div class="sort-options">
            <span>排序:</span>
            <el-select
              v-model="sortBy"
              @change="sortResults"
              class="sort-select"
            >
              <el-option label="模型名称" value="modelName" />
              <el-option label="实例名称" value="instanceName" />
            </el-select>
          </div>
        </div>
      </div>

      <div class="results-grid" v-if="filteredResults.length > 0">
        <el-card
          v-for="instance in filteredResults"
          :key="instance.instance_id"
          class="instance-card"
          shadow="hover"
        >
          <div class="card-content">
            <div class="card-header">
              <div class="instance-name" :title="instance.instance_name">
                {{ instance.instance_name }}
              </div>
              <el-tag
                :type="getModelTagType(instance.model_id)"
                class="model-tag"
              >
                {{ instance.model_verbose_name }}
              </el-tag>
            </div>

            <div class="card-body">
              <div class="instance-info">
                <div class="info-item">
                  <span class="info-label">唯一标识:</span>
                  <span class="info-value">{{ instance.instance_name }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">所属模型:</span>
                  <span class="info-value">{{
                    instance.model_verbose_name
                  }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">匹配字段:</span>
                  <span class="info-value">
                    <el-tag
                      v-for="match in instance.matches"
                      :key="match.field_name"
                      size="small"
                      class="match-tag"
                    >
                      {{ match.field_verbose_name }}: {{ match.display_value }}
                    </el-tag>
                  </span>
                </div>
                <!-- <div class="info-item" v-if="instance.max_score !== undefined">
                  <span class="info-label">匹配度:</span>
                  <span class="info-value">
                    <el-progress
                      :percentage="Math.round(instance.max_score * 100)"
                      :stroke-width="10"
                      :show-text="true"
                      class="score-progress"
                    />
                  </span>
                </div> -->
              </div>
            </div>

            <div class="card-footer">
              <el-button
                type="primary"
                size="small"
                @click="viewInstanceDetails(instance)"
                plain
              >
                查看详情
              </el-button>
            </div>
          </div>
        </el-card>
      </div>

      <el-empty
        v-else-if="!searchLoading && searchPerformed"
        description="未找到相关实例"
        class="no-results"
      />

      <div
        v-else-if="!searchLoading && !searchPerformed"
        class="initial-placeholder"
      >
        <el-icon size="48"><Search /></el-icon>
        <p>请输入关键词进行搜索</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, getCurrentInstance, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { Search, CaretTop } from "@element-plus/icons-vue";
import useModelStore from "@/store/cmdb/model";
import api from "@/api/index";
import { ElMessage } from "element-plus";
defineOptions({ name: "cidataSearch" });

const { proxy } = getCurrentInstance();
const router = useRouter();
const modelConfigStore = useModelStore();

// 搜索相关数据
const searchKeyword = ref("");
const searchLoading = ref(false);
const searchResults = ref([]); // 原始搜索结果
const filteredResults = ref([]); // 过滤后的结果
const searchPerformed = ref(false);

// 模型筛选相关数据
const allModels = computed(() => modelConfigStore.allModels);
const selectedModelIds = ref([]);
const selectAllModels = ref(true);

// 结果过滤相关数据
const resultModelFilter = ref(""); // 结果页面的模型过滤器

// 排序相关数据
const sortBy = ref("modelName");

// 全选模型处理
const handleSelectAllModels = (checked) => {
  if (checked) {
    selectedModelIds.value = allModels.value.map((model) => model.id);
  } else {
    selectedModelIds.value = [];
  }
};

// 监听模型列表变化，初始化选中状态
watch(allModels, (newModels) => {
  if (newModels.length > 0 && selectedModelIds.value.length === 0) {
    selectedModelIds.value = newModels.map((model) => model.id);
  }
});

// 计算模型统计信息
const modelStats = computed(() => {
  const stats = {};
  searchResults.value.forEach((instance) => {
    const modelId = instance.model_id;
    stats[modelId] = (stats[modelId] || 0) + 1;
  });
  return stats;
});

// 根据模型ID获取模型显示名称
const getModelVerboseName = (modelId) => {
  const model = allModels.value.find((m) => m.id === modelId);
  return model ? model.verbose_name : "未知模型";
};

// 获取模型标签类型（用于不同模型区分颜色）
const getModelTagType = (modelId) => {
  const modelIndex = allModels.value.findIndex((m) => m.id === modelId);
  const types = ["success", "warning", "danger", "info"];
  return types[modelIndex % types.length] || "success";
};
// 切换模型过滤器
const toggleModelFilter = (modelId) => {
  if (resultModelFilter.value === modelId) {
    // 如果点击的是当前已选中的模型，则清除过滤
    resultModelFilter.value = "";
  } else {
    // 否则设置为选中的模型
    resultModelFilter.value = modelId;
  }
  filterResultsByModel();
};

// 清除模型过滤器
const clearModelFilter = () => {
  resultModelFilter.value = "";
  filteredResults.value = [...searchResults.value];
  sortResults();
};
// 正则表达式相关
const regexp = ref(false);
const caseSensitive = ref(false);
const regexpError = ref("");

// 监听正则表达式变化并验证
const onRegexpChange = (value) => {
  if (value) {
    validateRegexp();
  } else {
    regexpError.value = "";
  }
};

// 验证正则表达式
const validateRegexp = () => {
  if (!regexp.value || !searchKeyword.value) {
    regexpError.value = "";
    return true;
  }

  try {
    new RegExp(searchKeyword.value);
    regexpError.value = "";
    return true;
  } catch (e) {
    regexpError.value = e.message;
    return false;
  }
};

// 执行搜索
const performSearch = async () => {
  if (!searchKeyword.value.trim()) {
    ElMessage.warning("请输入搜索关键词");
    return;
  }
  // 如果启用了正则表达式，先验证
  if (regexp.value) {
    if (!validateRegexp()) {
      ElMessage.error("正则表达式格式错误：" + regexpError.value);
      return;
    }
  }

  if (selectedModelIds.value.length === 0) {
    ElMessage.warning("请至少选择一个模型");
    return;
  }

  searchLoading.value = true;
  searchPerformed.value = true;
  resultModelFilter.value = ""; // 清空结果过滤器

  try {
    // 调用API搜索实例
    const res = await api.searchCiData({
      query: searchKeyword.value.trim(),
      models: selectedModelIds.value,
      limit: 20000,
      search_mode: "boolean",
      regexp: regexp.value,
      case_sensitive: caseSensitive.value,
    });

    searchResults.value = res.data.results || [];
    filteredResults.value = [...searchResults.value]; // 初始化过滤结果
    sortResults();
  } catch (error) {
    console.error("搜索失败:", error);
    ElMessage.error("搜索失败，请稍后重试");
    searchResults.value = [];
    filteredResults.value = [];
  } finally {
    searchLoading.value = false;
  }
};

// 根据模型过滤结果
const filterResultsByModel = () => {
  if (!resultModelFilter.value) {
    // 如果没有选择过滤模型，则显示所有结果
    filteredResults.value = [...searchResults.value];
  } else {
    // 根据选择的模型过滤结果
    filteredResults.value = searchResults.value.filter(
      (instance) => instance.model_id === resultModelFilter.value
    );
  }
  sortResults(); // 重新排序
};

// 排序结果
const sortResults = () => {
  const sorted = [...filteredResults.value];

  switch (sortBy.value) {
    case "modelName":
      sorted.sort((a, b) =>
        a.model_verbose_name.localeCompare(b.model_verbose_name)
      );
      break;
    case "instanceName":
      sorted.sort((a, b) => a.instance_name.localeCompare(b.instance_name));
      break;
    case "relevance":
      sorted.sort((a, b) => (b.max_score || 0) - (a.max_score || 0));
      break;
    default:
      break;
  }

  filteredResults.value = sorted;
};

// 清空搜索
const clearSearch = () => {
  regexpError.value = "";
  searchKeyword.value = "";
  searchResults.value = [];
  filteredResults.value = [];
  searchPerformed.value = false;
  resultModelFilter.value = "";
};

// 查看实例详情
const viewInstanceDetails = (instance) => {
  // 跳转到实例详情页
  router.push({
    path: "/cmdb/cidata/" + instance.instance_id,
  });
};

// 初始化数据
onMounted(async () => {
  try {
    // 确保模型数据已加载
    if (allModels.value.length === 0) {
      await modelConfigStore.getModel();
    }

    // 初始化选中所有模型
    selectedModelIds.value = allModels.value.map((model) => model.id);
  } catch (error) {
    console.error("初始化数据失败:", error);
    ElMessage.error("初始化数据失败");
  }
});
</script>

<style scoped lang="scss">
.cmdb-search-container {
  padding: 10px;
  // height: 100%;
  width: 100%;
  position: relative;
  .search-header {
    margin-bottom: 20px;

    .search-card {
      border-radius: 8px;
      box-shadow: var(--el-box-shadow-light);

      .regexp-error-message {
        display: flex;
        align-items: center;
        gap: 5px;
        margin: 0px 0 5px 0;
        padding: 5px 10px;
        background-color: #fef0f0;
        border: 1px solid #fde2e2;
        border-radius: 4px;
        color: #f56c6c;
        font-size: 12px;
        width: 379px;
        .error-text {
          flex: 1;
        }
      }
      .search-form {
        display: flex;
        gap: 15px;
        margin-bottom: 5px;
        align-items: flex-start;

        .search-button,
        .clear-button {
          height: 40px;
          align-self: flex-start;
          margin-top: 32px; /* 与输入框对齐 */
        }
      }

      .search-options {
        display: flex;
        align-items: center;
        // gap: 20px;
        // margin-bottom: 15px;
        // padding: 10px 15px;
        // background-color: var(--el-fill-color-light);
        border-radius: 4px;
      }

      .filter-section {
        border-top: 1px solid var(--el-border-color-light);
        padding-top: 15px;

        .filter-title {
          font-weight: bold;
          margin-bottom: 10px;
          color: var(--el-text-color-primary);
        }

        .select-all-checkbox {
          margin-bottom: 10px;
          display: block;
        }

        .model-checkbox-group {
          display: flex;
          flex-wrap: wrap;
          gap: 15px;

          .model-checkbox {
            margin-right: 0;
          }
        }
      }
    }
  }

  .search-results {
    .results-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 20px;
      padding: 0 5px;
      flex-wrap: wrap;
      gap: 15px;

      .results-count {
        font-size: 16px;
        font-weight: bold;
        color: var(--el-text-color-primary);

        .model-stats {
          font-weight: normal;
          font-size: 14px;
          color: var(--el-text-color-secondary);
        }

        .model-stat-item {
          white-space: nowrap;
        }
        .model-stat-tag {
          margin-right: 5px;
          cursor: pointer;
        }
      }

      .result-filters {
        display: flex;
        gap: 15px;
        align-items: center;
        flex-wrap: wrap;

        .model-filter {
          display: flex;
          align-items: center;
          gap: 10px;

          .model-filter-select {
            width: 200px;
          }
        }

        .sort-options {
          display: flex;
          align-items: center;
          gap: 10px;

          .sort-select {
            width: 150px;
          }
        }
      }
    }

    .results-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
      gap: 20px;

      .instance-card {
        border-radius: 8px;
        transition: transform 0.2s, box-shadow 0.2s;

        &:hover {
          transform: translateY(-2px);
        }

        .card-content {
          .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--el-border-color-light);

            .instance-name {
              font-size: 16px;
              font-weight: bold;
              color: var(--el-text-color-primary);
              flex: 1;
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
              margin-right: 10px;
            }

            .model-tag {
              flex-shrink: 0;
            }
          }

          .card-body {
            margin-bottom: 15px;

            .instance-info {
              .info-item {
                display: flex;
                margin-bottom: 12px;

                .info-label {
                  width: 80px;
                  font-weight: 500;
                  color: var(--el-text-color-secondary);
                  flex-shrink: 0;
                  font-size: 13px;
                }

                .info-value {
                  flex: 1;
                  color: var(--el-text-color-primary);
                  word-break: break-word;

                  .match-tag {
                    margin-right: 5px;
                    margin-bottom: 5px;
                  }

                  .score-progress {
                    width: 100%;
                    max-width: 150px;
                  }
                }
              }

              .info-item:last-child {
                margin-bottom: 0;
              }
            }
          }

          .card-footer {
            display: flex;
            justify-content: flex-end;
          }
        }
      }
    }

    .no-results {
      padding: 50px 0;
    }

    .initial-placeholder {
      text-align: center;
      padding: 50px 0;
      color: var(--el-text-color-secondary);

      p {
        margin-top: 15px;
        font-size: 16px;
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .cmdb-search-container {
    padding: 15px;

    .search-header {
      .search-card {
        .search-form {
          flex-direction: column;

          .search-input {
            max-width: 100%;
            width: 100%;
          }

          .search-button,
          .clear-button {
            width: 100%;
          }
        }

        .filter-section {
          .model-checkbox-group {
            flex-direction: column;
            gap: 10px;
          }
        }
      }
    }

    .search-results {
      .results-header {
        flex-direction: column;
        gap: 10px;
        align-items: flex-start;
      }

      .results-grid {
        grid-template-columns: 1fr;
      }
    }
  }
}
</style>