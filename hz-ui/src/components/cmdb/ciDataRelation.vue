<template>
  <div class="relations-card">
    <div class="card-header">
      <div>
        <el-button
          type="primary"
          @click="openAddRelationDialog"
          v-permission="`${route.name?.replace('_info', '')}:add`"
        >
          添加关联
        </el-button>
      </div>
    </div>

    <!-- 关联关系表格 -->
    <el-table
      :data="relationsData"
      style="width: 100%"
      border
      v-loading="loading"
    >
      <el-table-column prop="source_instance" label="源实例" width="200">
        <template #default="scope">
          <el-tag>{{ scope.row.source_instance.instance_name }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="relation_definition" label="关系类型" width="150">
        <template #default="scope">
          <el-tag type="success">{{
            scope.row.relation_definition.name
          }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="target_instance" label="目标实例">
        <template #default="scope">
          <el-tag>{{ scope.row.target_instance.instance_name }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="180">
        <template #default="scope">
          {{ formatDate(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="scope">
          <el-button
            size="small"
            type="danger"
            @click="deleteRelation(scope.row.id)"
            v-permission="`${route.name?.replace('_info', '')}:delete`"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="pagination.currentPage"
      v-model:page-size="pagination.pageSize"
      :page-sizes="[10, 20, 50]"
      layout="total, sizes, prev, pager, next, jumper"
      :total="pagination.total"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      style="margin-top: 20px; justify-content: flex-end"
    />

    <!-- 添加关联关系对话框 -->
    <el-dialog
      v-model="addRelationDialogVisible"
      title="添加关联关系"
      width="600px"
      @close="resetAddRelationForm"
    >
      <el-form
        ref="addRelationFormRef"
        :model="addRelationForm"
        :rules="addRelationRules"
        label-width="120px"
      >
        <el-form-item label="关系类型" prop="relation_definition">
          <el-select
            v-model="addRelationForm.relation_definition"
            placeholder="请选择关系类型"
            style="width: 100%"
            @change="handleRelationTypeChange"
          >
            <el-option
              v-for="item in relationDefinitions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="目标实例" prop="target_instance">
          <el-select
            v-model="addRelationForm.target_instance"
            placeholder="请选择目标实例"
            style="width: 100%"
            filterable
            remote
            :remote-method="searchTargetInstances"
            :loading="searchLoading"
          >
            <el-option
              v-for="item in targetInstances"
              :key="item.id"
              :label="item.instance_name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addRelationDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitAddRelation">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted, getCurrentInstance } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import useConfigStore from "@/store/config";

const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();
const configStore = useConfigStore();

// 数据加载状态
const loading = ref(false);
const searchLoading = ref(false);

// 关联关系数据
const relationsData = ref([]);
const relationDefinitions = ref([]); // 关系定义列表
const targetInstances = ref([]); // 目标实例列表

// 分页参数
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0,
});

// 添加关联关系对话框
const addRelationDialogVisible = ref(false);
const addRelationFormRef = ref();
const addRelationForm = reactive({
  relation_definition: null,
  target_instance: null,
});

// 表单验证规则
const addRelationRules = {
  relation_definition: [
    { required: true, message: "请选择关系类型", trigger: "change" },
  ],
  target_instance: [
    { required: true, message: "请选择目标实例", trigger: "change" },
  ],
};

// 获取当前实例ID（从路由参数中）
const getInstanceId = () => {
  return route.params.id;
};

// 获取关联关系数据
const getRelationsData = async () => {
  loading.value = true;
  try {
    const res = await proxy.$api.getModelInstanceRelation({
      source_instance: getInstanceId(),
      page: pagination.currentPage,
      page_size: pagination.pageSize,
    });

    relationsData.value = res.data.results;
    pagination.total = res.data.count;
  } catch (error) {
    ElMessage.error("获取关联关系数据失败");
    console.error(error);
  } finally {
    loading.value = false;
  }
};

// 获取关系定义列表
const getRelationDefinitions = async () => {
  try {
    const res = await proxy.$api.getModelRelationDefine({
      // 可以根据需要添加过滤条件
    });
    relationDefinitions.value = res.data.results;
  } catch (error) {
    ElMessage.error("获取关系类型失败");
    console.error(error);
  }
};

// 搜索目标实例
const searchTargetInstances = async (query) => {
  if (!addRelationForm.relation_definition) {
    targetInstances.value = [];
    return;
  }

  searchLoading.value = true;
  try {
    // 获取当前选中关系类型
    const selectedRelation = relationDefinitions.value.find(
      (item) => item.id === addRelationForm.relation_definition
    );

    if (selectedRelation) {
      const res = await proxy.$api.getCiModelInstance({
        // 根据关系类型的目标模型搜索实例
        model_in: selectedRelation.target_model.join(","),
        search: query,
        page_size: 20,
      });
      targetInstances.value = res.data.results;
    }
  } catch (error) {
    ElMessage.error("搜索目标实例失败");
    console.error(error);
  } finally {
    searchLoading.value = false;
  }
};

// 处理关系类型变更
const handleRelationTypeChange = () => {
  // 清空之前选择的目标实例
  addRelationForm.target_instance = null;
  // 重新搜索目标实例
  searchTargetInstances("");
};

// 打开添加关联关系对话框
const openAddRelationDialog = () => {
  addRelationDialogVisible.value = true;
  // 获取最新的关系定义列表
  getRelationDefinitions();
};

// 重置添加关联表单
const resetAddRelationForm = () => {
  addRelationFormRef.value?.resetFields();
  addRelationForm.relation_definition = null;
  addRelationForm.target_instance = null;
  targetInstances.value = [];
};

// 提交添加关联关系
const submitAddRelation = async () => {
  await addRelationFormRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        const res = await proxy.$api.addModelInstanceRelation({
          source_instance: getInstanceId(),
          ...addRelationForm,
        });

        if (res.status === 201) {
          ElMessage.success("添加关联关系成功");
          addRelationDialogVisible.value = false;
          resetAddRelationForm();
          getRelationsData(); // 刷新数据
        } else {
          ElMessage.error("添加关联关系失败");
        }
      } catch (error) {
        ElMessage.error("添加关联关系失败: " + error.message);
        console.error(error);
      }
    }
  });
};

// 删除关联关系
const deleteRelation = (id) => {
  ElMessageBox.confirm("确定要删除这个关联关系吗？", "确认删除", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      try {
        const res = await proxy.$api.deleteModelInstanceRelation(id);
        if (res.status === 204) {
          ElMessage.success("删除成功");
          getRelationsData(); // 刷新数据
        } else {
          ElMessage.error("删除失败");
        }
      } catch (error) {
        ElMessage.error("删除失败: " + error.message);
        console.error(error);
      }
    })
    .catch(() => {
      // 用户取消删除
    });
};

// 处理分页变化
const handleSizeChange = (val) => {
  pagination.pageSize = val;
  getRelationsData();
};

const handleCurrentChange = (val) => {
  pagination.currentPage = val;
  getRelationsData();
};

// 格式化时间
const formatDate = (dateString) => {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date
    .toLocaleString("zh-CN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    })
    .replace(/\//g, "-");
};

// 组件挂载时获取数据
onMounted(() => {
  getRelationsData();
  getRelationDefinitions();
});
</script>

<style scoped>
.relations-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.dialog-footer {
  text-align: right;
}
</style>