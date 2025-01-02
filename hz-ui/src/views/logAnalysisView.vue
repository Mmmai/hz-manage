<template>
  <div class="card">
    <el-row class="row-bg" justify="space-between">
      <!-- <el-col :span="23">
      <span style="display: flex;align-items: center;margin-right: 10px;">分组</span>
      <el-checkbox
        v-model="checkAll"
        :indeterminate="isIndeterminate"
        @change="handleCheckAllChange"
        style="padding-right: 6px;"
      >
        所有
      </el-checkbox>

      <el-checkbox-group
        v-model="selectGroup"
        @change="handleCheckedCitiesChange"
        class="group-check"
      >
        <el-checkbox v-for="group in groupList" :key="group" :label="group" :value="group" >
          {{ group }}
        </el-checkbox>
      </el-checkbox-group>
    </el-col> -->
      <el-col :span="23">
        <span style="display: flex; align-items: center; margin-right: 10px"
          >分组</span
        >

        <el-segmented v-model="group" :options="groupOptions" size="large" />
      </el-col>
      <el-col :span="1">
        <el-button type="primary" @click="addLogFlow">添加</el-button></el-col
      >
    </el-row>
    <!-- <el-button type="primary" @click="addLogFlow">添加</el-button>     -->
    <el-divider />
    <el-space wrap>
      <!-- v-for="fItem,fIndex in showDataList"  -->

      <el-card
        v-for="(fItem, fIndex) in showDataList"
        :key="fIndex"
        class="box-card"
        style="width: 300px; height: 250px"
        shadow="hover"
        @click="cardClick(fItem)"
      >
        <!--  -->
        <template #header>
          <div class="card-header">
            <span>{{ fItem.group }}: {{ fItem.name }}</span>
            <!-- <el-button class="button" text>Operation button</el-button> -->
            <div style="display: flex; justify-content: space-between">
              <el-button
                type="primary"
                size="small"
                :icon="Edit"
                circle
                @click.stop="editLogFlow(fItem)"
              />
              <el-button
                type="danger"
                size="small"
                :icon="Delete"
                circle
                @click.stop="deleteAction(fItem)"
              />
            </div>
          </div>
        </template>
        <!-- ;overflow-y:auto -->
        <template #default>
          <el-scrollbar height="120px">
            <div v-for="(mv, mk) in fItem.steps" :key="mk" class="text item">
              <li>{{ logModuleObj[mv].module_name }}</li>
            </div>
          </el-scrollbar>
        </template>
      </el-card>
    </el-space>
  </div>
  <!-- 弹出框 -->
  <el-dialog
    v-model="dialogVisible"
    title="业务流程"
    width="500"
    :before-close="handleClose"
    draggable
    overflow
  >
    <!-- <span @click=changeCom>This is a message</span> -->
    <el-form
      label-position="right"
      :model="formLabelAlign"
      label-width="auto"
      style="max-width: 400px"
      ref="formRef"
    >
      <el-form-item
        label="流程名称"
        prop="name"
        :rules="[
          { required: true, message: '请输入流程名称', trigger: 'blur' },
        ]"
      >
        <el-input v-model="formLabelAlign.name" style="width: 220px" />
      </el-form-item>
      <el-form-item label="分组">
        <el-select
          v-model="formLabelAlign.group"
          filterable
          clearable
          allow-create
          placeholder="所属分组，支持新增"
          style="width: 180px"
        >
          <el-option
            v-for="gItem in groupSelectOptions"
            :key="gItem.value"
            :label="gItem.label"
            :value="gItem.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="是否启用">
        <el-switch
          v-model="formLabelAlign.status"
          class="ml-2"
          style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949"
        />
      </el-form-item>
      <!-- 动态表单 -->
      <div v-for="(item, index) in formLabelAlign.stepList" :key="index">
        <el-form-item
          :label="'环节' + (index + 1)"
          :prop="'stepList.' + index + '.step'"
          :rules="[{ required: true, message: '请选择环节', trigger: 'blur' }]"
        >
          <el-select
            v-model="item.step"
            filterable
            clearable
            placeholder="选择流程"
            style="width: 180px"
          >
            <el-option
              v-for="mItem in logModuleOptions"
              :key="mItem.value"
              :label="mItem.label"
              :value="mItem.value"
              :disabled="mItem.disabled"
            />
          </el-select>
          <!-- v-if="Object.keys(labelObject).length >> 1 "   -->
          <el-button
            v-if="formLabelAlign.stepList.length >> 1"
            size="small"
            :icon="Delete"
            circle
            style="margin: 0 5px 0px 5px"
            @click="deleteItem(index)"
          />
          <el-button
            v-if="index == formLabelAlign.stepList.length - 1"
            type="primary"
            :icon="CirclePlus"
            circle
            size="small"
            style="margin: 0 5px 0px 5px"
            @click="addItem"
          />
        </el-form-item>
      </div>

      <el-form-item label="描述" prop="describe">
        <el-input v-model="formLabelAlign.describe" type="textarea" />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button
          type="danger"
          @click="deleteAction({ id: nowId })"
          v-if="isAdd == false"
          >删除</el-button
        >
        <el-button type="primary" @click="updateAction" v-if="isAdd == false"
          >更新</el-button
        >
        <el-button type="primary" @click="submitAction" v-else>添加</el-button>
      </div>
    </template>
  </el-dialog>
  <!-- 检索的弹出框  :-->
  <el-dialog
    v-model="openSearch"
    title="查询条件"
    width="500"
    appendToBody
    :before-close="searchClose"
    draggable
    overflow
  >
    <el-form
      label-position="right"
      label-width="auto"
      :model="searchForm"
      style="max-width: 600px"
      ref="searchFormRef"
    >
      <el-form-item label="数据源">
        <el-select
          v-model="searchForm.dataSourceId"
          placeholder="Select"
          size="large"
          style="width: 180px"
        >
          <el-option
            v-for="(dv, di) in dataSourceOptions"
            :key="di"
            :label="dv.label"
            :value="dv.value"
            :disabled="dv.disabled"
          />
        </el-select>
      </el-form-item>
      <el-form-item
        label="业务流ID"
        prop="flowId"
        :rules="[
          { required: true, message: '请选择业务流ID', trigger: 'blur' },
        ]"
      >
        <el-select
          v-model="searchForm.flowId"
          placeholder="Select"
          size="large"
          style="width: 180px"
        >
          <el-option
            v-for="(dv, di) in logFlowOptions"
            :key="di"
            :label="dv.label"
            :value="dv.value"
            :disabled="dv.disabled"
          />
        </el-select>
      </el-form-item>
      <el-form-item
        label="关键字"
        prop="matchKey"
        :rules="[
          { required: true, message: '需要提供关键字!!!', trigger: 'blur' },
        ]"
      >
        <el-input
          v-model="searchForm.matchKey"
          autosize
          type="textarea"
          placeholder="请输入关键字"
        />
      </el-form-item>
      <el-form-item
        label="时间范围"
        prop="dateValue"
        :rules="[{ required: true, message: '选择时间范围', trigger: 'blur' }]"
      >
        <el-date-picker
          v-model="searchForm.dateValue"
          type="datetimerange"
          :shortcuts="shortcuts"
          range-separator="To"
          start-placeholder="Start date"
          end-placeholder="End date"
          value-format="x"
        />
      </el-form-item>
      <el-form-item label="分析ID" prop="uuid">
        <el-input v-model="searchForm.missionId" disabled />
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button type="primary" @click="searchSubmit">检索</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import {
  reactive,
  ref,
  watch,
  getCurrentInstance,
  computed,
  onMounted,
  onDeactivated,
  nextTick,
  onActivated,
} from "vue";
import { Delete, Edit, CirclePlus } from "@element-plus/icons-vue";
const { proxy } = getCurrentInstance();
import { ElMessageBox, ElMessage } from "element-plus";

const initFormLabelAlign = {
  name: "",
  group: "",
  describe: "",
  status: true,
  stepList: [{ step: "" }],
  steps: [],
};
const formLabelAlign = reactive({
  name: "",
  group: "",
  describe: "",
  status: true,
  stepList: [{ step: "" }],
  steps: [],
});
// 重置表单
const resetForm = () => {
  // 重置提交表单
  Object.keys(formLabelAlign).forEach((key) => {
    formLabelAlign[key] = initFormLabelAlign[key];
  });
  // 重置环节对象
  let tempLogModuleOptions = [];
  logModuleOptions.value.forEach((item) => {
    item.disabled = false;
    tempLogModuleOptions.push(item);
  });
  logModuleOptions.value = tempLogModuleOptions;
};
// 删除环节
const deleteItem = (key) => {
  formLabelAlign.stepList.splice(key, 1);
};
// 添加环节
const addItem = () => {
  formLabelAlign.stepList.push({ step: "" });
};
// 监听表单中的环节，追加到steps
watch(
  () => formLabelAlign.stepList,
  (n) => {
    if (n.length == 0) {
      return 111;
    }
    formLabelAlign.steps = [];
    let tempLogModuleOptions = [];
    let tempStepList = [];
    n.forEach((item) => {
      if (formLabelAlign.steps.indexOf(item.step) === -1 && item.step != "") {
        formLabelAlign.steps.push(item.step);
      }
      //
      if (item.step != "") {
        tempStepList.push(item.step);
      }
    });
    logModuleOptions.value.forEach((o) => {
      if (tempStepList.includes(o.value)) {
        o.disabled = true;
      } else {
        o.disabled = false;
      }
      tempLogModuleOptions.push(o);
    });
    logModuleOptions.value = tempLogModuleOptions;
  },
  { deep: true }
);
// 分组
// const groupSelectOptions = ref([])
// 获取日志流列表
const logFlowList = ref([]);
const logFlowOptions = ref([]);
// const groupList = ref([])
const showDataList = ref([]);

const getLogFlowList = async () => {
  let res = await proxy.$api.getLogFlow();
  console.log(res.data);
  logFlowList.value = res.data.data;
  showDataList.value = res.data.data;
  console.log(showDataList.value);
  // groupSelectOptions.value = []
  // groupOptions.value = ['所有']
  res.data.data.forEach((item) => {
    // if (groupOptions.value.indexOf(item.group) === -1){
    //   if (item.group != ''){
    //     // groupList.value.push({'label':item.group,'value':item.group})
    //     // tempGroupList.value.push({label:item.group,value:item.group})
    //     groupOptions.value.push(item.group)
    //   }
    // }
    // if (groupSelectOptions.value.indexOf(item.group) === -1){
    //   if (item.group != ''){
    //     // groupList.value.push({'label':item.group,'value':item.group})
    //     // tempGroupList.value.push({label:item.group,value:item.group})
    //     groupSelectOptions.value.push({label:item.group,value:item.group})
    //   }
    // }
    // flow列表分组
    logFlowOptions.value.push({
      label: item.name,
      value: item.id,
      disabled: !item.status,
    });
  });
  // groupList.value = tempGroupList
};
// const groupOptions = ref(['所有'])
const groupSelectOptions = computed(() => {
  let tempList = [];
  logFlowList.value.forEach((item) => {
    if (!tempList.includes({ value: item.group, label: item.group }))
      tempList.push({ value: item.group, label: item.group });
  });
  return tempList;
});
const groupOptions = computed(() => {
  let tempList = ["所有"];
  logFlowList.value.forEach((item) => {
    if (!tempList.includes(item.group)) tempList.push(item.group);
  });
  return tempList;
});
const group = ref("所有");
// 分组动态监测
// watch(groupList,(n,)=>{
//   let tempGroupList = []
//   let tempGroupOptions = []
//   n.forEach(item=>{
//     tempGroupOptions.push({'label':item,'value':item})
//     tempGroupList.push(item)

//   })
//   groupOptions.value = tempGroupOptions
//   selectGroup.value = tempGroupList
//   console.log(selectGroup.value)
//   checkAll.value = true
// },{'deep':true})
watch(
  () => group.value,
  (n) => {
    if (n === "所有") {
      console.log(n);
      showDataList.value = logFlowList.value;
    } else {
      showDataList.value = logFlowList.value.filter((item) => {
        return item.group === n;
      });
    }
    // console.log(11111)
  }
);
// 获取环节列表
const logModuleOptions = ref([]);
const logModuleObj = ref({});
const getLogModuleOptions = async () => {
  let res = await proxy.$api.getLogModule();
  // console.log(res)
  res.data.results.forEach((item) => {
    if (item.status) {
      logModuleOptions.value.push({ label: item.module_name, value: item.id });
      logModuleObj.value[item.id] = item;
    }
  });
};
const dialogVisible = ref(false);
const isAdd = ref(true);
// 添加按钮
const addLogFlow = () => {
  dialogVisible.value = true;
  isAdd.value = true;
  // proxy.$refs.formRef.resetFields();
};
// 提交新增
const submitAction = async () => {
  // console.log(formLabelAlign)
  // return 111
  proxy.$refs.formRef.validate(async (valid) => {
    if (valid) {
      let res = await proxy.$api.addLogFlow(formLabelAlign);
      if (res.status == "201") {
        ElMessage({ type: "success", message: "添加成功" });
        // 重置表单
        proxy.$refs.formRef.resetFields();
        // resetForm();
        dialogVisible.value = false;
        // 获取数据源列表
        getLogFlowList();
      } else {
        ElMessage({
          showClose: true,
          message: "添加失败:" + JSON.stringify(res.data),
          type: "error",
        });
      }
    } else {
      return;
    }
  });
};
// 编辑按钮
const nowId = ref("");
const editLogFlow = (row) => {
  console.log(row);
  dialogVisible.value = true;
  isAdd.value = false;
  nowId.value = row.id;
  let stepListTemp = [];
  row.steps.forEach((item) => {
    stepListTemp.push({ step: item });
  });
  // let filterArray = ['id','update_time','create_time']
  // Object.keys(row).forEach(key => {
  //   if (filterArray.indexOf(key) === -1){
  //     formLabelAlign[key] = row[key]
  //   }
  //   });
  proxy.$nextTick(() => {
    Object.assign(formLabelAlign, row);
  });
  formLabelAlign.stepList = stepListTemp;
  console.log(formLabelAlign);
};
// 更新按钮
const updateAction = () => {
  proxy.$refs.formRef.validate(async (valid) => {
    if (valid) {
      console.log(nowId.value);
      let res = await proxy.$api.updateLogFlow({
        id: nowId.value,
        ...formLabelAlign,
      });
      console.log(res);
      if (res.status == 200) {
        ElMessage({
          type: "success",
          message: "更新成功",
        });
        // 重置表单，关闭弹出框,重新加载数据
        // proxy.$refs.formRef.resetFields();
        resetForm();
        // resetForm();
        dialogVisible.value = false;
        // 获取数据源列表
        getLogFlowList();
      } else {
        ElMessage({
          type: "error",
          message: "更新失败",
        });
      }
      // 获取数据源列表
      getLogFlowList();
    } else {
    }
  });
};
// 删除按钮
const deleteAction = (row) => {
  ElMessageBox.confirm("是否确认删除?", "Warning", {
    confirmButtonText: "确认删除",
    cancelButtonText: "取消",
    type: "warning",
    draggable: true,
  })
    .then(async () => {
      // 发起删除请求
      let res = await proxy.$api.delLogFlow(row.id);
      if (res.status == 204) {
        ElMessage({
          type: "success",
          message: "删除成功",
        });
        // 重置表单，关闭弹出框,重新加载数据
        // proxy.$refs.formRef.resetFields();
        // resetForm();
        resetForm();
        dialogVisible.value = false;
        // 获取数据源列表
        getLogFlowList();
      } else {
        ElMessage({
          type: "error",
          message: "删除失败",
        });
      }
    })
    .catch(() => {
      ElMessage({
        type: "info",
        message: "Delete canceled",
      });
    });
};

onMounted(async () => {
  await getLogModuleOptions();
  await getLogFlowList();
  await getDataSource();
  //  await
});

// 关闭弹窗
const handleClose = (done: () => void) => {
  ElMessageBox.confirm("是否关闭?")
    .then(() => {
      // resetForm();
      resetForm();

      done();
    })
    .catch(() => {
      // catch error
    });
};
// 获取当前用户
import { useStore } from "vuex";
let store = useStore();
const currenUsername = computed(() => {
  return store.state.username;
});
// 日志分析功能代码
// 点击检索
const openSearch = ref(false);
window.__TestOpenSearch = openSearch;
const dataSourceOptions = ref([]);
const searchForm = reactive({
  dataSourceId: "",
  dataSourceName: "",
  matchKey: "",
  dateValue: [],
  username: currenUsername,
  flowName: "",
});
const shortcuts = [
  {
    text: "Last 1 hours",
    value: [new Date(new Date().getTime() - 1 * 60 * 60 * 1000), new Date()],
  },
  {
    text: "Last 2 hours",
    value: [new Date(new Date().getTime() - 2 * 60 * 60 * 1000), new Date()],
  },
  {
    text: "Last 6 hours",
    value: [new Date(new Date().getTime() - 6 * 60 * 60 * 1000), new Date()],
  },
  {
    text: "Last 12 hours",
    value: [new Date(new Date().getTime() - 12 * 60 * 60 * 1000), new Date()],
  },
  {
    text: "Last 24 hours",
    value: [new Date(new Date().getTime() - 24 * 60 * 60 * 1000), new Date()],
  },
  {
    text: "Today",
    value: [
      new Date(new Date().setHours(0, 0, 0, 0)),
      new Date(new Date().setHours(23, 59, 59, 999)),
    ],
  },
  {
    text: "Yesterday",
    value: () => {
      const start = new Date(new Date().getTime() - 1 * 60 * 60 * 1000);
      const end = new Date();
      return [start, end];
    },
  },
  {
    text: "A week ago",
    value: () => {
      const date = new Date();
      date.setDate(date.getDate() - 7);
      return [date.setDate(date.getDate() - 7), new Date()];
    },
  },
];
// 获取数据源列表
const getDataSource = async () => {
  let res = await proxy.$api.dataSourceGet();
  console.log(res);
  // dataSourceList.value = res.data
  res?.data?.results.forEach((item) => {
    if (item.source_type == "loki") {
      if (item.isUsed) {
        dataSourceOptions.value.push({
          label: item.source_name,
          value: item.id,
          disabled: false,
        });
      } else {
        dataSourceOptions.value.push({
          label: item.source_name,
          value: item.id,
          disabled: true,
        });
      }
      if (item.isDefault) {
        searchForm.dataSourceId = item.id;
        searchForm.dataSourceName = item.source_name;
      }
    }
  });
};
// 检索弹窗关闭
const searchClose = (done: () => void) => {
  console.log("in before search close");
  ElMessageBox.confirm("是否关闭?")
    .then(() => {
      // resetForm();
      proxy.$refs.searchFormRef.resetFields();

      done();
    })
    .catch(() => {
      // catch error
    });
};
// cardClick卡片点击事件
const cardClick = (conf) => {
  openSearch.value = true;
  searchForm.flowId = conf.id;
  console.log(conf);
  searchForm.flowName = conf.name;
  searchForm.missionId = proxy.$commonFunc.getUuid();
};
//
import { useRouter } from "vue-router";
const router = useRouter();
const searchSubmit = async () => {
  proxy.$refs.searchFormRef.validate((valid) => {
    if (valid) {
      proxy.$refs.searchFormRef.resetFields();
      openSearch.value = false;
      setTimeout(() => {
        router.push({
          path: "/log/logFlowMission/" + searchForm.uuid,
          query: searchForm,
        });
      });
      // resetForm();
    }
  });
};

onDeactivated(() => {
  console.log("onDeactivated!");
  openSearch.value = false;
});
onActivated(() => {
  console.log("onActivated", openSearch.value);
  nextTick(() => {
    console.log("onActivated nextTick", openSearch.value);
  });
});
watch(
  () => openSearch.value,
  (n) => {
    console.log(1111, n);
  }
);
</script>

<style scoped lang="less">
.card-header {
  display: flex;
  justify-content: space-between;
}

:deep(.el-col-23) {
  display: flex;
  justify-content: flex-start;
}

.group-check {
  :deep(.el-checkbox) {
    margin-right: 15px;
  }
}
</style>
