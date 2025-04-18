<template>
  <div class="card">
    <div class="table-header">
      <div class="header-button-lf">
        <el-button
          v-permission="`${route.name?.replace('_info', '')}:add`"
          type="primary"
          @click="addData"
          >添加</el-button
        >
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
          @clear="getRules()"
          @keyup.enter.native="getRules()"
        />
        <!-- <el-button :icon="Refresh" circle @click="reloadWind" /> -->
      </div>
    </div>
    <el-table
      ref="multipleTableRef"
      :data="validationRules"
      style="width: 100%"
      border
      @sort-change="sortMethod"
    >
      <el-table-column property="name" label="规则名" sortable="custom" />
      <el-table-column property="verbose_name" label="规则名称" />
      <el-table-column
        property="field_type"
        label="字段类型"
        sortable="custom"
      />
      <el-table-column property="type" label="规则类型" sortable="custom" />
      <el-table-column property="rule" label="规则内容" show-overflow-tooltip />
      <el-table-column property="description" label="描述" />
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
              v-permission="`${route.name?.replace('_info', '')}:delete`"
              link
              type="danger"
              :icon="Delete"
              :disabled="scope.row.built_in"
              @click="deleteRow(scope.row.id)"
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
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      style="margin-top: 5px; justify-content: flex-end"
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
import { Delete, Edit, CircleClose, CirclePlus } from "@element-plus/icons-vue";
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
const validationRules = ref([]);
import { useRoute } from "vue-router";
const route = useRoute();
const colValue = ref("verbose_name");
const filterValue = ref<string>("");
const filterParam = computed(() => {
  return { [colValue.value]: filterValue.value };
});
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
    label: "规则名",
    sort: true,
    filter: true,
    type: "string",
    required: true,
  },
  {
    value: "verbose_name",
    label: "规则名称",
    sort: false,
    filter: true,
    type: "string",
    required: true,
  },
  {
    value: "field_type",
    label: "字段类型",
    sort: true,
    filter: true,
    type: "object",
    required: true,
  },
  {
    value: "type",
    label: "规则类型",
    sort: true,
    filter: true,
    type: "object",
  },
  {
    value: "rule",
    label: "规则内容",
    sort: false,
    filter: true,
    type: "string",
  },
  {
    value: "description",
    label: "描述",
    sort: false,
    filter: false,
    type: "text",
  },
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
const handleSizeChange = () => {
  getRules();
};
const handleCurrentChange = () => {
  getRules();
};

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
  getRules();
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

const editRow = (row) => {
  nowRow.value = row;
  dialogVisible.value = true;
  isAdd.value = false;
  nextTick(() => {
    Object.keys(row).forEach(
      (item) => {
        // if (formInline.hasOwnProperty(item)) formInline[item] = params[item]
        if (item === "id") return;
        // if (item === "rule" && row.field_type === "enum") {
        //   formInline[item] = JSON.parse(row[item]);
        // } else {
        //   formInline[item] = row[item];

        // }
        formInline[item] = row[item];
      } // isDisabled.value = params.built_in
    );
    if (row.field_type === "enum") {
      let tmpArr = [];
      Object.keys(JSON.parse(row.rule)).forEach((item) => {
        tmpArr.push({ name: item, value: JSON.parse(row.rule)[item] });
      });
      tmpFormData.value = tmpArr;
    }
    // formInline = params
    beforeEditFormData.value = JSON.parse(JSON.stringify(formInline));
    console.log(beforeEditFormData.value);
  });
};

const resetForm = (formEl) => {
  if (!formEl) return;
  formEl.resetFields();
  tmpFormData.value = [{ name: "", value: "" }];
};
// 获取字段类型字典
const fieldOptions = ref([]);
const validate_type = ref([]);
// 后端请求

const getRules = async (params = null) => {
  let res = await proxy.$api.getValidationRules({
    page: currentPage.value,
    page_size: pageSize.value,
    ...filterParam.value,
    ...sortParam.value,
    ...params,
  });
  validationRules.value = res.data.results;
  totalCount.value = res.data.count;
};
const getModelFieldType = async () => {
  let res = await proxy.$api.getCiModelFieldType();
  validate_type.value = res.data.field_validations;
  let fieldTypeObj = res.data.field_types;
  Object.keys(fieldTypeObj).forEach((item) => {
    fieldOptions.value.push({ value: item, label: fieldTypeObj[item] });
  });
};
const updateParams = ref({});
const submitAction = async (formEl) => {
  await formEl.validate(async (valid, fields) => {
    if (valid) {
      console.log(isUniq.value);
      if (isUniq.value) {
        ElMessage({ type: "error", message: "有重复值！" });
        return;
      }
      if (isAdd.value) {
        // 添加请求
        let res = await proxy.$api.addValidationRules({
          create_user: store.state.username,
          update_user: store.state.username,
          ...formInline,
        });
        // console.log(res)
        // console.log(123)
        if (res.status == "201") {
          ElMessage({ type: "success", message: "添加成功" });
          // 重置表单
          dialogVisible.value = false;
          resetForm(formEl);
          // getModelField();
          // 刷新页面
          await getRules();
        } else {
          ElMessage({
            showClose: true,
            message: "添加失败:" + JSON.stringify(res.data),
            type: "error",
          });
        }
      } else {
        if (
          JSON.stringify(beforeEditFormData.value) ===
          JSON.stringify(formInline)
        ) {
          dialogVisible.value = false;
          resetForm(formEl);
          ElMessage({
            showClose: true,
            message: "无更新,关闭窗口",
            type: "info",
          });
          return;
        } else {
          // 判断此次用户操作的字段
          // 通过entires转为键值对数组
          const arr1 = Object.entries(beforeEditFormData.value);
          const arr2 = Object.entries(formInline);
          //拼接后推入set中，但是需要将数组转为json字符串否则无法对比值的一致性
          const arr = arr1.concat(arr2).map((item) => JSON.stringify(item));
          const result = Array.from(new Set(arr)).map((item) =>
            JSON.parse(item)
          );
          //裁剪掉第一个对象占用掉的部分，剩下就是第二个对象与其不同的属性部分
          result.splice(0, arr1.length);
          //将键值对数组转为正常对象
          const obj = Object.fromEntries(result);
          let tmpObj = {};
          Object.keys(obj).forEach((item) => {
            if (obj[item] != "") {
              tmpObj[item] = obj[item];
            }
          });
          updateParams.value = tmpObj;

          if (Object.keys(updateParams.value).length === 0) {
            dialogVisible.value = false;
            resetForm(formEl);
            ElMessage({
              showClose: true,
              message: "无更新,关闭窗口",
              type: "info",
            });
            return;
          }
          // return
        }
        console.log(updateParams.value);
        console.log(formInline);
        let res = await proxy.$api.updateValidationRules({
          id: nowRow.value.id,
          update_user: store.state.username,
          ...updateParams.value,
        });
        console.log(res);
        // console.log(123)
        if (res.status == "200") {
          ElMessage({ type: "success", message: "更新成功" });
          // 重置表单
          dialogVisible.value = false;
          resetForm(formEl);
          getRules();
          // 获取数据源列表
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
const deleteRow = (params) => {
  ElMessageBox.confirm("是否确认删除?", "删除", {
    confirmButtonText: "确认删除",
    cancelButtonText: "取消",
    type: "warning",
    draggable: true,
  })
    .then(async () => {
      // 发起删除请求
      let res = await proxy.$api.deleteValidationRules(params);
      //
      // let res = {status:204}
      if (res.status == 204) {
        ElMessage({
          type: "success",
          message: "删除成功",
        });
        // 重新加载页面数据
        await getRules();
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

onMounted(() => {
  getRules();
  getModelFieldType();
});
</script>

<style scoped></style>
