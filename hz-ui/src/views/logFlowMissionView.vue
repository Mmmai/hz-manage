<template>
  <div class="card">
    <el-table
      :data="tableData"
      :default-sort="{ prop: 'create_time', order: 'descending' }"
    >
      <!-- :row-class-name="tableRowClassName" -->

      <!-- <el-table-column type="index" label="ID" width="50" /> -->
      <el-table-column
        v-for="(v, i) in missionObject"
        :key="i"
        :prop="v.prop"
        :label="v.label"
        :width="v.width"
        :sortable="v.sortable"
        :fixed="v.fixed"
      >
        <!-- <template #default="scope" v-if="v.prop === 'flow_id'">
        {{ logFlowObjects[scope.row.flow_id].name }}
      </template>
<template #default="scope" v-if="v.prop === 'username'">
        {{ userObjects[scope.row.user_id].username }}
      </template> -->
        <template #default="scope" v-if="v.prop === 'status'">
          <el-tag round :type="missionStatus(scope.row.status)">{{
            missionStatusObject[scope.row.status]
          }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" width="80">
        <!-- <template #header>
        <el-input v-model="search" size="small" placeholder="Type to search" />
      </template> -->
        <template #default="scope">
          <el-link
            :href="
              '/#/log/logFlowMission/' +
              scope.row.mission_id +
              '?mission_id=' +
              scope.row.mission_id +
              '&verbose_name=' +
              scope.row.flow_name
            "
            type="primary"
            >查看结果</el-link
          >
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
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      style="margin-top: 5px; justify-content: flex-end"
    >
    </el-pagination>
  </div>
</template>
<script setup lang="ts">
import { reactive, ref, watch, getCurrentInstance, onMounted } from "vue";
const { proxy } = getCurrentInstance();
defineOptions({ name: "logFlowMission" });

import { ElMessageBox, ElMessage } from "element-plus";
import { Failed } from "@element-plus/icons-vue";
const missionObject = reactive([
  { label: "用户", prop: "username", width: "90" },
  { label: "日志流程", prop: "flow_name" },
  // {label:'请求ID',prop:'mission_id',width:'360'},
  { label: "分析ID", prop: "search_key" },
  { label: "数据源", prop: "dataSource_name", width: "120" },
  { label: "创建时间", prop: "create_time", width: "220", sortable: true },

  { label: "状态", prop: "status", width: "100", fixed: "right" },
]);
const missionStatus = (param) => {
  if (param == "Success") {
    return "success";
  } else if (param === "Failed") {
    return "error";
  } else {
    return "info";
  }
};
const missionStatusObject = {
  Pending: "运行中",
  Success: "成功",
  Failed: "失败",
  Unknown: "未知",
};
const tableData = ref([]);
const getLogMission = async () => {
  let res = await proxy.$api.getLogFlowMission({
    page: currentPage.value,
    page_size: pageSize.value,
  });
  tableData.value = res.data.results;
  totalCount.value = res.data.count;
};
const userObjects = reactive({});
const getUser = async () => {
  let res = await proxy.$api.user();
  res.data.results.forEach((item) => {
    userObjects[item.id] = item;
  });
};
// 获取日志流程的信息
// const logFlowObjects = reactive({})
// const getLogFlowList = async () => {
//   let res = await proxy.$api.getLogFlow()
//   // console.log(res)
//   res.data.data.forEach(item => {
//     logFlowObjects[item.id] = item
//   })
//   console.log(logFlowObjects)
//   }
// 分页
// 分页
const currentPage = ref(1);
const pageSize = ref(10);
const size = ref("default");
const disabled = ref(false);
const totalCount = ref(0);
const handleSizeChange = () => {
  getLogMission();
};
const handleCurrentChange = () => {
  getLogMission();
};
onMounted(async () => {
  // await getUser();
  // await getLogFlowList();
  await getLogMission();
});
</script>
<style scoped></style>