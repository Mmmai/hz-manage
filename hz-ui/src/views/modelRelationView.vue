<template>
  <div class="card divVertical">
    <div class="table-header">
      <div class="header-button-lf">
        <el-button type="primary" @click="handleAdd">新增关系</el-button>
      </div>
    </div>
    <div class="card table-container" style="width: 100%">
      <el-table :data="relationList" stripe style="width: 100%">
        <el-table-column
          prop="name"
          label="关系名称"
          width="200"
        ></el-table-column>
        <el-table-column prop="topology_type" label="拓扑类型" width="150">
          <template #default="scope">
            <el-tag :type="getTopologyTypeTagType(scope.row.topology_type)">
              {{ getTopologyTypeLabel(scope.row.topology_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source_model" label="源模型" width="300">
          <template #default="scope">
            <el-space wrap :size="10">
              <el-tag
                v-for="(item, index) in scope.row.source_model"
                :key="index"
                >{{ modelObjectById[item]?.verbose_name }}</el-tag
              >
            </el-space>
          </template>
        </el-table-column>
        <el-table-column prop="target_model" label="目标模型" width="300">
          <template #default="scope">
            <el-space wrap :size="10">
              <el-tag
                v-for="(item, index) in scope.row.target_model"
                :key="index"
                >{{ modelObjectById[item]?.verbose_name }}</el-tag
              >
            </el-space>
          </template></el-table-column
        >
        <el-table-column
          prop="forward_verb"
          label="正向动词"
          width="200"
        ></el-table-column>
        <el-table-column
          prop="reverse_verb"
          label="反向动词"
          width="200"
        ></el-table-column>
        <el-table-column
          prop="description"
          label="描述"
          min-width="200"
        ></el-table-column>
        <!-- <el-table-column prop="create_time" label="创建时间" width="280">
          <template #default="scope">
            {{ formatDate(scope.row.create_time) }}
          </template>
        </el-table-column> -->
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-tooltip content="查看详情" placement="top">
              <el-button
                @click="handleEdit(scope.row)"
                type="primary"
                link
                :icon="View"
              ></el-button>
            </el-tooltip>
            <el-tooltip
              :content="
                scope.row.built_in ? '内置关联关系，无法删除!' : '删除关联关系'
              "
              placement="top"
            >
              <el-button
                type="danger"
                link
                :icon="Delete"
                :disabled="scope.row.built_in"
                @click="handleDelete(scope.row)"
              ></el-button>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: flex-end; display: flex"
      >
      </el-pagination>
    </div>
  </div>
</template>

<script setup>
import {
  ref,
  reactive,
  onMounted,
  computed,
  watch,
  getCurrentInstance,
} from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { Delete, View } from "@element-plus/icons-vue";

import useModelStore from "@/store/cmdb/model";
const modelConfigStore = useModelStore();
const modelOptions = computed(() => modelConfigStore.modelOptions);
const modelObjectById = computed(() => modelConfigStore.modelObjectById);
const { proxy } = getCurrentInstance();
watch(
  () => modelObjectById,
  () => {
    console.log(modelObjectById.value);
  },
  { deep: true, immediate: true }
);
const router = useRouter();
const route = useRoute();
const relationList = ref([]);
// 模拟数据
const relationList1 = ref([
  {
    id: "e307f2ad-12e6-49ac-8215-e6c29aa5f58e",
    name: "主机-交换机",
    topology_type: "directed",
    forward_verb: "上联",
    reverse_verb: "下联",
    attribute_schema: {
      source: {
        port: {
          type: "string",
          required: false,
          verbose_name: "端口",
        },
      },
      target: {
        port: {
          type: "string",
          required: false,
          verbose_name: "端口",
        },
      },
      relation: {
        speed: {
          type: "float",
          unit: "Mbps",
          default: "20000",
          required: true,
          verbose_name: "速率",
        },
      },
    },
    description: null,
    create_time: "2025-10-31T17:42:59.661169",
    update_time: "2025-10-31T17:42:59.661210",
    create_user: "admin",
    update_user: "admin",
    source_model: "8103d7da-ede7-4416-9b77-f19a81a4d671",
    target_model: "1394f70d-ade6-4548-aa6a-13f9b8296b35",
  },
  {
    id: "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
    name: "应用-服务器",
    topology_type: "undirected",
    forward_verb: "部署于",
    reverse_verb: "承载",
    attribute_schema: {
      source: {},
      target: {},
      relation: {
        deploy_path: {
          type: "string",
          required: false,
          verbose_name: "部署路径",
        },
      },
    },
    description: "应用与服务器的关系",
    create_time: "2025-11-01T09:15:30.123456",
    update_time: "2025-11-01T09:15:30.123456",
    create_user: "admin",
    update_user: "admin",
    source_model: "abcd1234-ef56-7890-ghij-klmn12345678",
    target_model: "8103d7da-ede7-4416-9b77-f19a81a4d671",
  },
  {
    id: "b2c3d4e5-f6g7-8901-h2i3-j4k5l6m7n8o9",
    name: "服务依赖",
    topology_type: "daggered",
    forward_verb: "依赖",
    reverse_verb: "被依赖",
    attribute_schema: {
      source: {},
      target: {},
      relation: {
        weight: {
          type: "integer",
          required: false,
          verbose_name: "权重",
        },
      },
    },
    description: "服务间依赖关系",
    create_time: "2025-11-02T14:20:45.987654",
    update_time: "2025-11-02T14:20:45.987654",
    create_user: "admin",
    update_user: "admin",
    source_model: "defg5678-hijk-9012-lmno-345678901234",
    target_model: "ghij9012-klmn-3456-opqr-789012345678",
  },
]);

const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: null,
});

const getTopologyTypeLabel = (type) => {
  const typeMap = {
    directed: "有向图",
    undirected: "无向图",
    daggered: "有向无环图",
  };
  return typeMap[type] || type;
};

const getTopologyTypeTagType = (type) => {
  const tagTypeMap = {
    directed: "danger",
    undirected: "success",
    daggered: "warning",
  };
  return tagTypeMap[type] || "info";
};

// const formatDate = (dateString) => {
//   if (!dateString) return "";
//   const date = new Date(dateString);
//   return date.toLocaleString("zh-CN");
// };

const handleEdit = (row) => {
  // 跳转到详情页面
  router.push({
    path: route.path + "/" + row.id,
  });
};

const handleAdd = () => {
  // 跳转到新建页面（也可以是同一个详情页面，但传入特殊ID标识为新增）
  router.push({ path: route.path + "/new" });
};

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确认删除关系 "${row.name}" 吗？此操作不可恢复！`,
    "警告",
    {
      confirmButtonText: "确认",
      cancelButtonText: "取消",
      type: "warning",
    }
  )
    .then(async () => {
      // 执行删除操作
      // 这里应该是调用API删除
      let res = await proxy.$api.deleteModelRelationDefine(row.id);
      if (res.status == 204) {
        ElMessage.success("删除成功");
        getRelationData();
      } else {
        ElMessage.error(`删除失败: ${JSON.stringify(res.data)}`);
      }
      // 从列表中移除
    })
    .catch(() => {
      // 用户取消删除
    });
};

const handleSizeChange = (val) => {
  pagination.pageSize = val;
  // 重新加载数据
};

const handleCurrentChange = (val) => {
  pagination.currentPage = val;
  // 重新加载数据
};
const getRelationData = async () => {
  const res = await proxy.$api.getModelRelationDefine();
  relationList.value = res.data.results;
  pagination.total = res.data.count;
};
onMounted(() => {
  // 页面加载时可以请求API获取数据
  // 执行模型数据加载
  modelConfigStore.getModel();
  getRelationData();
  // console.log(modelConfigStore.modelOptions);
  // fetchData()
});
</script>

<style scoped>
.model-relation-view {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: calc(100vh - 60px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>