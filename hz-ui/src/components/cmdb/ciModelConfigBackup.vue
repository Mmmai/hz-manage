<template>
  <div class="card">
    <!-- <div v-if="configData.length >>> 1">111</div> -->
    <!-- <div v-else>
    </div> -->
    <!-- <el-dialog v-model="dialogFormVisible" title="模型同步配置" width="600"> -->

    <el-form :model="formLine">
      <el-form-item label="启用管理">
        <el-switch
          :disabled="!isEdit"
          v-model="formLine.is_manage"
          class="ml-2"
          style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949"
        />
      </el-form-item>
      <el-table
        :data="formLine.zabbix_sync_info"
        style="width: 50%"
        border
        v-if="formLine.is_manage"
      >
        <el-table-column label="接口类型" width="150">
          <template #default="scope">
            <el-select
              v-model="scope.row.type"
              filterable
              placeholder="接口类型"
              style="width: 120px"
              v-if="scope.row.isEditing"
            >
              <el-option
                v-for="typeOption in getAvailableTypeOptions(scope.$index)"
                :key="typeOption.value"
                :label="typeOption.label"
                :value="typeOption.value"
                :disabled="typeOption.disabled"
              />
            </el-select>
            <span v-else>{{ scope.row.type }}</span>
          </template>
        </el-table-column>
        <el-table-column label="接口模板">
          <template #default="scope">
            <el-select
              v-model="scope.row.template"
              filterable
              placeholder="模板"
              style="width: 400px"
              v-if="scope.row.isEditing"
            >
              <el-option
                v-for="template in templateOptions"
                :key="template.value"
                :label="template.label"
                :value="template.value"
              />
            </el-select>
            <span v-else>{{ scope.row.template }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" v-if="isEdit">
          <template #header>
            <el-button @click="addZabbixSyncInfo" :icon="CirclePlus"
              >添加</el-button
            >
          </template>
          <template #default="scope">
            <div v-if="!scope.row.isEditing">
              <el-button
                type="primary"
                :icon="Edit"
                link
                @click="editRow(scope.$index)"
                >编辑</el-button
              >
              <el-button
                type="danger"
                :icon="Delete"
                link
                @click="removeZabbixSyncInfo(scope.$index)"
                :disabled="formLine.built_in"
                >删除</el-button
              >
            </div>
            <div v-else>
              <el-button
                type="primary"
                :icon="Check"
                link
                @click="saveRow(scope.$index)"
                >保存</el-button
              >
              <el-button
                type="primary"
                :icon="Close"
                link
                @click="cancelRow(scope.$index)"
                >取消</el-button
              >
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- <el-button @click="removeZabbixSyncInfo(index)">删除配置</el-button> -->
      <!-- <el-button
            type="danger"
            :icon="Delete"
            plain
            size="small"
            circle
            @click="removeZabbixSyncInfo(index)"
          /> -->
    </el-form>

    <!-- <div class="dialog-footer flexCenter" v-if="!isEdit">
      <el-button type="primary" @click="editConfig">编辑</el-button>
    </div>
    <div class="dialog-footer flexCenter" v-else>

    </div> -->
    <div v-if="isEdit">
      <el-button @click="cancelAction()">取消</el-button>
      <el-button
        type="primary"
        @click="saveAction()"
        :disabled="hasUnsavedEditingRows"
        >保存</el-button
      >
    </div>
    <div v-else>
      <el-button @click="editConfig()">编辑</el-button>
    </div>
    <!-- </el-dialog> -->
  </div>
</template>

<script lang="ts" setup>
import {
  Delete,
  Edit,
  Check,
  CirclePlus,
  Close,
} from "@element-plus/icons-vue";

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
const props = defineProps(["modelId", "modelFieldLists", "ciModelInfo"]);
import { ElMessageBox, ElMessage, ElNotification } from "element-plus";
import { get } from "lodash";

const configData = ref({});
const isEdit = ref(false);
const editConfig = () => {
  isEdit.value = true;
};
// 计算属性：检查是否有未保存的编辑行
const hasUnsavedEditingRows = computed(() => {
  return formLine.zabbix_sync_info.some((item) => item.isEditing);
});
const dialogFormVisible = ref(false);
interface zbxItem {
  type: string;
  template: string;
  isEditing?: boolean;
}
const formLine = reactive<{
  zabbix_sync_info: zbxItem[];
  is_manage: boolean;
  built_in: boolean;
}>({
  zabbix_sync_info: [],
  is_manage: false,
  built_in: false,
});
const typeOptions = ref([
  { value: "agent", label: "agent" },
  { value: "ipmi", label: "ipmi" },
  { value: "snmp", label: "snmp" },
]);
const templateOptions = ref([]);
// 获取可用的类型选项，已选择的类型会被禁用
const getAvailableTypeOptions = (currentIndex) => {
  // 获取已经选择的类型（排除当前编辑的行）
  const selectedTypes = formLine.zabbix_sync_info
    .filter((item, index) => {
      // 排除当前编辑的行
      if (index === currentIndex) return false;
      // 包括已保存的项（!item.isEditing）和已选择类型的编辑项（item.isEditing && item.type）
      return !item.isEditing || (item.isEditing && item.type);
    })
    .map((item) => item.type)
    .filter((type) => type); // 过滤掉空的type值

  // 返回更新后的选项列表，已选择的类型设置为禁用
  return typeOptions.value.map((option) => ({
    ...option,
    disabled: selectedTypes.includes(option.value),
  }));
};
const addZabbixSyncInfo = () => {
  // 检查是否还有可用的类型选项
  const availableTypes = getAvailableTypeOptions(-1).filter(
    (option) => !option.disabled
  );

  if (availableTypes.length === 0) {
    ElMessage({
      type: "warning",
      message: "所有接口类型都已配置，无法添加更多配置",
    });
    return;
  }

  formLine.zabbix_sync_info.push({
    type: "",
    template: "",
    isEditing: true,
  });
};
const removeZabbixSyncInfo = (index) => {
  formLine.zabbix_sync_info.splice(index, 1);
};
const editRow = (index) => {
  // 设置当前行进入编辑状态
  formLine.zabbix_sync_info[index].isEditing = true;
};
const cancelRow = (index) => {
  formLine.zabbix_sync_info[index].isEditing = false;
  // 判断是否有编辑，没有则删除
  if (formLine.zabbix_sync_info[index].type === "") {
    removeZabbixSyncInfo(index);
  }
  getConfigData();
};
const saveRow = (index) => {
  // 检查是否选择了类型
  if (!formLine.zabbix_sync_info[index].type) {
    ElMessage({
      type: "warning",
      message: "请选择接口类型",
    });
    return;
  }

  // 检查是否已存在相同类型的配置（排除当前正在编辑的项）
  const currentType = formLine.zabbix_sync_info[index].type;
  const isDuplicate = formLine.zabbix_sync_info.some((item, i) => {
    return i !== index && !item.isEditing && item.type === currentType;
  });

  if (isDuplicate) {
    ElMessage({
      type: "warning",
      message: `接口类型 "${currentType}" 已存在，请选择其他类型或编辑已有配置`,
    });
    return;
  }

  // 退出当前行的编辑状态
  formLine.zabbix_sync_info[index].isEditing = false;
};
const cancelAction = () => {
  isEdit.value = false;
  // 判断是否有编辑，没有则删除
  nextTick(() => {
    getConfigData();
  });
};
const modelConfigId = ref(null);
// 请求
const getConfigData = async () => {
  const res = await proxy.$api.getModelConfig({ model: props.modelId });
  if (res.status == 200) {
    configData.value = res.data.results;
    // 如果有返回数据，处理数据格式
    if (res.data.results && res.data.results.length > 0) {
      const config = res.data.results[0]; // 假设只有一条配置
      modelConfigId.value = config.id;
      formLine.is_manage = config.is_manage;
      formLine.built_in = config.built_in;
      formLine.zabbix_sync_info = config.zabbix_sync_info.map((item) => ({
        ...item,
        isEditing: false, // 默认不处于编辑状态
      }));
    }
  }
};
const getZabbixTemplates = async () => {
  let res = await proxy.$api.getZabbixTemplate();
  console.log(res);
  if (res.status == 200) {
    templateOptions.value = res.data.data;
  } else {
    ElMessage({
      type: "error",
      message: `添加失败: ${JSON.stringify(res.data)}`,
    });
  }
};
const saveAction = async () => {
  // 检查是否有未保存的编辑行
  if (hasUnsavedEditingRows.value) {
    ElMessage({
      type: "warning",
      message: "还有未保存的编辑行，请先保存或取消所有编辑行",
    });
    return;
  }
  console.log(modelConfigId.value);
  let res = await proxy.$api.updateModelConfig({
    id: modelConfigId.value,
    ...formLine,
  });
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "保存成功",
    });
    getConfigData();
  } else {
    ElMessage({
      type: "error",
      message: `保存失败: ${JSON.stringify(res.data)}`,
    });
  }
};

defineExpose({
  getConfigData,
  getZabbixTemplates,
});
</script>
<style scoped lang="scss">
</style>