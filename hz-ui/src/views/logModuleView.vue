<template>
  <div class="card">
    <el-row class="row-bg" justify="space-between">
      <el-col :span="23">
        <span style="display: flex; align-items: center; margin-right: 10px"
          >分组</span
        >

        <el-segmented v-model="group" :options="groupOptions" size="large" />
      </el-col>
      <el-col :span="1">
        <el-button
          v-permission="`${route.name?.replace('_info', '')}:add`"
          type="primary"
          @click="addModule"
          >添加</el-button
        ></el-col
      >
    </el-row>

    <el-divider />
    <!-- 数据源列表展示 -->
    <el-table :data="showDataList" style="width: 100%" table-layout="auto">
      <!-- <el-table-column fixed prop="date" label="Date" width="150" /> -->
      <el-table-column prop="module_name" label="环节名称" />
      <el-table-column prop="label_name" label="标签名称" />
      <el-table-column prop="label_match" label="匹配方式" />
      <el-table-column prop="label_value" label="标签值" />
      <el-table-column prop="status" label="状态">
        <template #default="scope" prop="status">
          <el-switch
            v-permission="{
              id: `${route.name?.replace('_info', '')}:edit`,
              action: 'disabled',
            }"
            v-model="scope.row.status"
            class="ml-2"
            style="
              --el-switch-on-color: #13ce66;
              --el-switch-off-color: #ff4949;
            "
            @change="updateStatus(scope.row)"
          />
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作">
        <template #default="scope">
          <el-button
            v-permission="`${route.name?.replace('_info', '')}:edit`"
            link
            type="primary"
            size="small"
            @click="edit(scope.row)"
          >
            编辑
          </el-button>
          <el-button
            v-permission="`${route.name?.replace('_info', '')}:delete`"
            link
            type="primary"
            size="small"
            @click="deleteModule(scope.row)"
          >
            删除
          </el-button>
          <!-- <el-button link type="primary" size="small">Edit</el-button> -->
        </template>
      </el-table-column>
    </el-table>
  </div>
  <!-- 弹出框 -->
  <el-dialog
    v-model="dialogVisible"
    title="环节配置"
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
      :rules="rules"
    >
      <el-form-item label="数据源" prop="datasource">
        <!-- <el-input v-model="formLabelAlign.module_name" style="width:220px"/> -->
        <el-select
          v-model="formLabelAlign.data_source"
          filterable
          clearable
          allow-create
          placeholder="标签"
          style="width: 180px"
        >
          <el-option
            v-for="labelItem in dataSourceOptions"
            :key="labelItem.value"
            :label="labelItem.label"
            :value="labelItem.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="环节名称" prop="module_name">
        <el-input v-model="formLabelAlign.module_name" style="width: 220px" />
      </el-form-item>

      <el-form-item label="标签" prop="label_name">
        <!-- app = '123' -->
        <el-select
          v-model="formLabelAlign.label_name"
          filterable
          clearable
          allow-create
          placeholder="标签"
          style="width: 180px"
          @click="getLabels"
        >
          <el-option
            v-for="labelItem in labelList"
            :key="labelItem.value"
            :label="labelItem.label"
            :value="labelItem.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="标签值" prop="label_value">
        <el-input
          v-model="formLabelAlign.label_value"
          placeholder="支持模糊匹配"
        />
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
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button
          type="danger"
          @click="deleteAction"
          v-if="isAdd == false"
          v-permission="`${route.name?.replace('_info', '')}:delete`"
          >删除</el-button
        >
        <el-button type="primary" @click="updateAction" v-if="isAdd == false"
          >更新</el-button
        >
        <el-button type="primary" @click="submitAction" v-else>添加</el-button>
      </div>
    </template>
  </el-dialog>
</template>
<script lang="ts" setup>
import {
  ref,
  reactive,
  shallowRef,
  watch,
  getCurrentInstance,
  onMounted,
  computed,
} from "vue";
const { proxy } = getCurrentInstance();
import type { FormInstance, FormRules } from "element-plus";
import { useRoute } from "vue-router";
const route = useRoute();
import { ElMessageBox, ElMessage } from "element-plus";
import { filter, range } from "lodash-es";
import { RefSymbol } from "@vue/reactivity";
const getImgPath = (name: string): any => {
  return new URL(`/src/assets/images/${name}`, import.meta.url).href;
};
const formRef = ref<FormInstance>();
defineOptions({ name: "logModule" });

const rules = reactive<FormRules>({
  module_name: [{ required: true, message: "请填写名称", trigger: "blur" }],
  label_name: [{ required: true, message: "请添加匹配标签", trigger: "blur" }],
  label_value: [{ required: true, message: "请填写标签值", trigger: "blur" }],
});

const updateStatus = async (params) => {
  let res = await proxy.$api.updateLogModule(params);
  console.log(res);
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "更新成功",
    });
    // 重置表单，关闭弹出框,重新加载数据
    resetForm();
    dialogVisible.value = false;
    getLogModuleList();
  } else {
    ElMessage({
      type: "error",
      message: "更新失败",
    });
  }
};

const dialogVisible = ref(false);
const isAdd = ref(false);
const componentId = shallowRef("");
// 重置表单
const resetForm = () => {
  Object.keys(formLabelAlign).forEach((key) => {
    formLabelAlign[key] = initFormLabelAlign[key];
  });
};
// 关闭弹窗
const handleClose = (done: () => void) => {
  ElMessageBox.confirm("是否关闭?")
    .then(() => {
      resetForm();
      console.log(formLabelAlign);
      done();
    })
    .catch(() => {
      // catch error
    });
};
const defaultDataSource = ref({});

const initFormLabelAlign = {
  // module_name: '',
  data_source: defaultDataSource.value,
  label_name: "",
  label_value: "",
  label_match: "=~",
  group: "",
  status: true,
};
const formLabelAlign = reactive({
  // module_name: '',
  data_source: defaultDataSource.value,
  label_name: "",
  label_value: "",
  label_match: "=~",
  group: "",
  status: true,
});

// 添加按钮的动作
const addModule = () => {
  dialogVisible.value = true;
  isAdd.value = true;
};
const deleteModule = (params) => {
  nowId.value = params.id;
  deleteAction();
};

// 弹出框内容
// label来源于默认的loki
const dataSourceOptions = ref([]);
// 获取数据源列表
const getDataSource = async () => {
  let res = await proxy.$api.dataSourceGet();
  // dataSourceList.value = res.data
  res?.data.results.forEach((item) => {
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
        defaultDataSource.value = item;
      }
    }
  });
};
// 获取现有标签
const labelList = ref([]);
const getLabels = async () => {
  console.log(defaultDataSource.value);
  let res = await proxy.$api.lokiLabelGet({ url: defaultDataSource.value.url });
  labelList.value = res.data.data;
  // console.log(labelList.value)
};

const submitAction = () => {
  proxy.$refs.formRef.validate(async (valid) => {
    console.log(valid);
    if (valid) {
      let res = await proxy.$api.addLogModule(formLabelAlign);
      console.log(res);
      if (res.status == "201") {
        ElMessage({ type: "success", message: "添加成功" });
        // 重置表单
        resetForm();
        dialogVisible.value = false;
        getLogModuleList();
        // 获取数据源列表
      } else {
        ElMessage({
          showClose: true,
          message: "添加失败:" + JSON.stringify(res.data),
          type: "error",
        });
      }
    } else {
    }
  });
};
// 所属分组
const groupList = ref([]);
// 获取已添加的环节列表
const logModuleList = ref([]);
const groupCheckBox = ref([]);
const getLogModuleList = async () => {
  let res = await proxy.$api.getLogModule();
  // console.log(res)
  logModuleList.value = res.data.results;
  // 把已创建的分组罗列
  showDataList.value = res.data.results;
};
// const groupSelectOptions = ref([])
const groupSelectOptions = computed(() => {
  let tempList = [];
  logModuleList.value.forEach((item) => {
    if (!tempList.includes({ value: item.group, label: item.group }))
      tempList.push({ value: item.group, label: item.group });
  });
  return tempList;
});
const groupOptions = computed(() => {
  let tempList = ["所有"];
  logModuleList.value?.forEach((item) => {
    if (!tempList.includes(item.group)) tempList.push(item.group);
  });
  return tempList;
});
// const groupOptions = ref(['所有'])
const group = ref("所有");
// 动态生成groupOptions
watch(
  () => group.value,
  (n) => {
    if (n === "所有") {
      showDataList.value = logModuleList.value;
    } else {
      showDataList.value = logModuleList.value.filter((item) => {
        return item.group === n;
      });
    }
  }
);
// 点击编辑时的按钮
const nowId = ref("");
const edit = (config) => {
  dialogVisible.value = true;
  isAdd.value = false;

  // formLabelAlign.
  nowId.value = config.id;
  let filterArray = ["id", "update_time", "create_time"];
  Object.keys(config).forEach((key) => {
    if (filterArray.indexOf(key) === -1) {
      formLabelAlign[key] = config[key];
    }
  });
};
// 更新按钮
const updateAction = () => {
  proxy.$refs.formRef.validate(async (valid) => {
    if (valid) {
      let res = await proxy.$api.updateLogModule({
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
        resetForm();
        dialogVisible.value = false;
        getLogModuleList();
      } else {
        ElMessage({
          type: "error",
          message: "更新失败",
        });
      }
      resetForm();
    } else {
    }
  });
};
// 删除按钮
const deleteAction = () => {
  ElMessageBox.confirm("是否确认删除?", "Warning", {
    confirmButtonText: "确认删除",
    cancelButtonText: "取消",
    type: "warning",
    draggable: true,
  })
    .then(async () => {
      // 发起删除请求
      let res = await proxy.$api.delLogModule(nowId.value);
      if (res.status == 204) {
        ElMessage({
          type: "success",
          message: "删除成功",
        });
        // 重置表单，关闭弹出框,重新加载数据
        resetForm();
        dialogVisible.value = false;
        getLogModuleList();
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

//渲染时加载
onMounted(async () => {
  await getDataSource();
  await getLogModuleList();
  //  await
});

const showDataList = ref([]);
</script>
<style scoped lang="less">
.context-body {
  height: 90%;
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  align-content: flex-start;
  align-items: flex-start;
}
.el-card-context {
  display: flex;
  justify-content: space-between;
}
.el-card-div {
  margin: 10px 10px 10px 10px;
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