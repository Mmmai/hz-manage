<template>
  <div class="card">
    <div class="table-header">
      <div class="header-button-lf">
        <el-button
          v-permission="`${route.name?.replace('_info', '')}:add`"
          type="primary"
          @click="getZabbixStatus()"
          >可用性同步</el-button
        >
        <el-button
          v-permission="`${route.name?.replace('_info', '')}:add`"
          type="primary"
          :disabled="multipleSelection.length >>> 1 ? false : true"
          @click="installAgent()"
          >触发安装</el-button
        >
        <el-button
          v-permission="`${route.name?.replace('_info', '')}:add`"
          type="primary"
          @click="getZabbixStatus()"
        ></el-button>
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
      ref="multipleTableRef"
      :data="syncHosts"
      style="width: 100%"
      border
      @sort-change="sortMethod"
      @selection-change="handleSelectionChange"
      @filter-change="filterMethod"
    >
      <el-table-column type="selection" width="55" />

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
              @click="reInstall(scope.row)"
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

    <!-- 弹出框 -->
    <el-dialog
      v-model="dialogVisible"
      title="规则配置"
      width="500"
      :before-close="handleClose"
    >
      <el-form
        :inline="true"
        label-position="right"
        :model="formInline"
        label-width="auto"
        ref="formRef"
      >
        <el-form-item
          :label="item.label"
          :key="index"
          v-for="(item, index) in colLists"
          :required="item.required"
          :prop="item.value"
        >
          <div v-if="item.value === 'rule'">
            <div v-if="formInline.field_type === 'enum'">
              <div v-for="(item, index) in tmpFormData" :key="index">
                <li>
                  <el-input
                    v-model="item.name"
                    style="width: 90px; margin-right: 10px"
                  />
                  <el-input
                    v-model="item.value"
                    style="width: 160px; margin-right: 10px"
                  />
                  <el-button
                    circle
                    type="danger"
                    size="small"
                    :icon="CircleClose"
                    @click="rmField(index)"
                    v-if="tmpFormData.length !== 1"
                  ></el-button>
                  <el-button
                    circle
                    type="primary"
                    size="small"
                    :icon="CirclePlus"
                    @click="addField(index)"
                  ></el-button>
                </li>
              </div>
            </div>
            <el-input
              v-model="formInline[item.value]"
              type="textarea"
              clearable
              v-else
              style="width: 300px"
              :disabled="nowRow.built_in"
            />
          </div>

          <el-input
            v-model="formInline[item.value]"
            type="textarea"
            clearable
            v-else-if="item.value === 'description'"
            style="width: 300px"
          />

          <el-input
            v-model="formInline[item.value]"
            clearable
            v-else-if="item.value === 'name'"
            :disabled="nowRow.built_in || !isAdd ? true : false"
          />
          <el-input
            v-model="formInline[item.value]"
            clearable
            v-else-if="item.value === 'verbose_name'"
          />
          <div v-else>
            <el-select
              v-model="formInline.field_type"
              placeholder="Select"
              style="width: 120px"
              v-if="item.value === 'field_type'"
              :disabled="nowRow.built_in || !isAdd ? true : false"
            >
              <el-option
                v-for="fItem in fieldOptions"
                :key="fItem.value"
                :label="fItem.label"
                :value="fItem.value"
              />
            </el-select>
            <el-select
              v-model="formInline.type"
              placeholder="Select"
              style="width: 120px"
              v-else
              :disabled="nowRow.built_in || !isAdd ? true : false"
            >
              <el-option
                v-for="vItem in validate_type[formInline.field_type]"
                :key="vItem.type"
                :label="vItem.description"
                :value="vItem.type"
              />
            </el-select>
          </div>
        </el-form-item>
        <div v-if="formInline.type === 'regex'" class="flexJstart">
          <el-text>测试正则</el-text>
          <el-input
            v-model="testRegex"
            clearable
            style="width: 200px; margin: 0 10px"
          />
          <el-icon
            style="color: var(--el-color-success)"
            :size="20"
            v-if="testRegexRes"
          >
            <SuccessFilled />
          </el-icon>
          <el-icon style="color: var(--el-color-danger)" :size="20" v-else>
            <WarningFilled />
          </el-icon>
        </div>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleClose">取消</el-button>
          <el-button type="primary" @click="submitAction(formRef)">
            提交
          </el-button>
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
} from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  ref,
  computed,
  watch,
  getCurrentInstance,
  onMounted,
  reactive,
  nextTick,
} from "vue";
const { proxy } = getCurrentInstance();
import { useStore } from "vuex";
const store = useStore();
const syncHosts = ref([]);
import { useRoute } from "vue-router";
import { tr } from "element-plus/es/locale/index.mjs";
const route = useRoute();
const colValue = ref("name");
const filterValue = ref<string>("");
// const filterParam = computed(() => {
//   return { [colValue.value]: filterValue.value };
// });
// 正则测试
const testRegex = ref(null);
const testRegexRes = computed(() => {
  // 用户输入的正则表达式
  if (testRegex.value === null) return true;
  var regexString = RegExp(formInline.rule);
  if (regexString.test(testRegex.value)) {
    return true;
  } else {
    return false;
  }
});
const tmpFormData = ref([{ name: "", value: "" }]);
const arrayJson = computed(() => {
  let tempArr = {};
  tmpFormData.value.forEach((item) => {
    if (item.name !== "" && item.value !== "") {
      tempArr[item.name] = item.value;
    }
  });
  return tempArr;
});
// 重复
const isUniq = computed(() => {
  return (
    proxy.$commonFunc.hasDuplicates(Object.keys(arrayJson.value)) ||
    proxy.$commonFunc.hasDuplicates(Object.values(arrayJson.value))
  );
});
watch(
  () => arrayJson.value,
  (n) => {
    if (Object.keys(n).length === 0) return;
    formInline.rule = JSON.stringify(arrayJson.value);
  }
);
const addField = (index) => {
  tmpFormData.value.splice(index + 1, 0, { name: "", value: "" });
};
const rmField = (index) => {
  tmpFormData.value.splice(index, 1);
  console.log(tmpFormData.value);
};
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
  console.log(res);
  // syncHosts.value = res.data.results;
  syncHosts.value = res.data;
  totalCount.value = res.data.length;
};

onMounted(() => {
  getZabbixSyncHost();
});

const multipleSelection = ref([]);
const handleSelectionChange = (val) => {
  multipleSelection.value = val;
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
const filterParam = ref({
  [colValue.value]: filterValue.value,
});

const filterMethod = (filters: object) => {
  //
  // nextTick(() => {
  //   getZabbixSyncHost();
  // });
  // console.log(typeof filters);
  // console.log(Object.keys(filters)[0]);
  if (Object.values(filters)[0].length > 1) {
    filterParam.value[`${Object.keys(filters)[0]}__in`] =
      Object.values(filters)[0].join(",");
  } else {
    filterParam.value[Object.keys(filters)[0]] = Object.values(filters)[0];
  }
  // console.log(column);
  // console.log(filterParam.value);
  nextTick(() => {
    getZabbixSyncHost();
  });
};

const getZabbixStatus = async () => {
  let res = await proxy.$api.updateZabbixAvailability();
  console.log(res);
};
// 安装agent
const installAgent = async (params) => {
  let res = await proxy.$api.installAgent(params);
};
</script>

<style scoped></style>
