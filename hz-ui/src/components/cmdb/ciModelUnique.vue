<template>
  <div style="width: 100%">
    <div class="table-header">
      <div class="header-button-lf">
        <el-button type="primary" @click="addData">添加</el-button>
      </div>
    </div>
    <el-table
      ref="multipleTableRef"
      :data="tableData"
      style="width: 100%"
      border
    >
      <el-table-column prop="fields" label="校验规则">
        <template #default="scope">
          <span> {{ showName[scope.row.fields.join("+")] }}</span>
          <!-- <span> {{ scope.row.fields }}</span> -->
        </template>
      </el-table-column>
      <el-table-column prop="validate_null" label="空值校验">
        <template #default="scope">
          <el-switch
            v-permission="{
              id: `${route.name?.replace('_info', '')}:edit`,
              action: 'disabled',
            }"
            v-model="scope.row.validate_null"
            class="ml-2"
            style="
              --el-switch-on-color: #13ce66;
              --el-switch-off-color: #ff4949;
            "
            @change="
              updateCiData({
                id: scope.row.id,
                validate_null: scope.row.validate_null,
              })
            "
            :disabled="scope.row.built_in"
          />
          <!-- <span> {{ scope.row.fields }}</span> -->
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" />
      <el-table-column fixed="right" width="100" label="操作">
        <template #default="scope">
          <el-tooltip
            class="box-item"
            effect="dark"
            content="编辑"
            placement="top"
          >
            <el-button
              v-permission="`${route.name?.replace('_info', '')}:edit`"
              link
              type="primary"
              :icon="Edit"
              @click="editRow(scope.row)"
            ></el-button>
          </el-tooltip>
          <el-tooltip
            class="box-item"
            effect="dark"
            content="删除"
            placement="top"
          >
            <el-button
              link
              v-permission="`${route.name?.replace('_info', '')}:delete`"
              type="danger"
              :icon="Delete"
              :disabled="scope.row.built_in"
              @click="deleteRow(scope.row.id)"
            ></el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="dialogVisible"
      title="唯一校验配置"
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
        <el-form-item label="唯一校验组合" prop="fields">
          <el-select
            v-model="formInline.fields"
            fields="选择字段组合"
            multiple
            :multiple-limit="5"
            clearable
            filterable
            style="width: 240px"
            :disabled="nowRow.built_in || !isAdd ? true : false"
          >
            <el-option
              :label="data.verbose_name"
              :value="data.name"
              :key="index"
              v-for="(data, index) in modelFieldLists"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="空置校验" prop="validate_null">
          <el-switch
            v-model="formInline.validate_null"
            class="ml-2"
            style="
              --el-switch-on-color: #13ce66;
              --el-switch-off-color: #ff4949;
            "
            :disabled="nowRow.built_in"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formInline.description"
            style="width: 240px"
            :autosize="{ minRows: 2, maxRows: 4 }"
            type="textarea"
          />
        </el-form-item>
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

<script lang="ts" setup>
import { Delete, Edit } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  ref,
  computed,
  watch,
  getCurrentInstance,
  onMounted,
  reactive,
  nextTick,
  onActivated,
} from "vue";
import { useRoute } from "vue-router";
const route = useRoute();
const { proxy } = getCurrentInstance();
import { useStore } from "vuex";
const store = useStore();
const tableData = ref([]);
const props = defineProps(["modelId", "modelFieldLists"]);
const addData = () => {
  console.log(props.modelFieldLists);
  dialogVisible.value = true;
  isAdd.value = true;
};
const modelFieldNameObj = computed(() => {
  let tmpObj = {};
  props.modelFieldLists.forEach((item) => {
    tmpObj[item.name] = item.verbose_name;
  });
  return tmpObj;
});

const formRef = ref("");
const formInline = reactive({
  fields: [],
  validate_null: false,
  description: null,
});
const dialogVisible = ref(false);
const handleClose = () => {
  dialogVisible.value = false;
  resetForm(formRef.value);
  console.log(formInline);
};
const isAdd = ref(true);
// const addData = () => {
//   dialogVisible.value = true
//   isAdd.value = true
// }
const nowRow = ref({});
const editRow = (row) => {
  nowRow.value = row;
  dialogVisible.value = true;
  isAdd.value = false;
  nextTick(() => {
    Object.keys(row).forEach((item) => {
      if (item === "id") return;
      if (Object.keys(formInline).indexOf(item) === -1) return;
      formInline[item] = row[item];
    });
  });
};

const resetForm = (formEl) => {
  if (!formEl) return;
  console.log(formInline);
  formEl.resetFields();
  nowRow.value = {};
  console.log(formInline);
};

const submitAction = async (formEl) => {
  await formEl.validate(async (valid, fields) => {
    if (valid) {
      if (isAdd.value) {
        // 添加请求
        let res = await proxy.$api.addCiModelUnique({
          create_user: store.state.username,
          update_user: store.state.username,
          ...formInline,
          model: props.modelId,
        });
        // console.log(res)
        // console.log(123)
        if (res.status == "201") {
          ElMessage({ type: "success", message: "添加成功" });
          // 重置表单
          dialogVisible.value = false;
          resetForm(formEl);
          // getModelField();
          getTableData({ model: props.modelId });
          // 刷新页面
        } else {
          ElMessage({
            showClose: true,
            message: "添加失败:" + JSON.stringify(res.data),
            type: "error",
          });
        }
      } else {
        let res = await proxy.$api.updateCiModelUnique({
          id: nowRow.value.id,
          update_user: store.state.username,
          ...formInline,
        });
        console.log(res);
        // console.log(123)
        if (res.status == "200") {
          ElMessage({ type: "success", message: "更新成功" });
          // 重置表单
          dialogVisible.value = false;
          resetForm(formEl);
          getTableData({ model: props.modelId });
        } else {
          ElMessage({
            showClose: true,
            message: "更新失败:" + JSON.stringify(res.data),
            type: "error",
          });
        }
      }
    }
  });
};

const updateCiData = async (params) => {
  let res = await proxy.$api.updateCiModelUnique({
    update_user: store.state.username,
    ...params,
  });
  // console.log(123)
  if (res.status == "200") {
    ElMessage({ type: "success", message: "更新成功" });
    // 重置表单
    resetForm(formRef.value);
    getTableData({ model: props.modelId });
  } else {
    ElMessage({
      showClose: true,
      message: "更新失败:" + JSON.stringify(res.data),
      type: "error",
    });
  }
};

const deleteRow = (params) => {
  ElMessageBox.confirm("是否确认删除?", "删除", {
    confirmButtonText: "确认删除",
    cancelButtonText: "取消",
    type: "warning",
    draggable: true,
  })
    .then(async () => {
      // 发起删除请求
      let res = await proxy.$api.deleteCiModelUnique(params);
      //
      // let res = {status:204}
      if (res.status == 204) {
        ElMessage({
          type: "success",
          message: "删除成功",
        });
        // 重新加载页面数据
        getTableData({ model: props.modelId });
        resetForm(formRef.value);
        dialogVisible.value = false;
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
        message: "取消删除",
      });
    });
};

const showName = computed(() => {
  let tmpObj = {};
  tableData.value.forEach((item) => {
    let nameArr = item.fields.map((item2) => modelFieldNameObj.value[item2]);
    tmpObj[item.fields?.join("+")] = nameArr.join("+");
  });
  return tmpObj;
});

const getTableData = async (params) => {
  let res = await proxy.$api.getCiModelUnique(params);
  tableData.value = res.data.results;
  // console.log(res.data);
};
defineExpose({
  getTableData,
});
// onMounted(() => {
//   getTableData();
// })
// onActivated(async () => {
//   console.log("onActivated", "唯一校验")
//   // await getCiModelInfo(route.query, route.query.id);
//   // await getCiModelGroupList();
//   // await getModelField();
//   await getTableData();

// })
</script>
<style scoped lang="scss"></style>