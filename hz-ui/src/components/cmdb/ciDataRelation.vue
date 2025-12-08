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
      <el-table-column prop="source_instance" label="源实例">
        <template #default="scope">
          <el-tag v-if="scope.row.source_instance.id !== instanceId">{{
            scope.row.target_instance.instance_name
          }}</el-tag>
          <el-tag v-else>{{ scope.row.source_instance.instance_name }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="source_attributes" label="源属性" width="150">
        <template #default="scope">
          <div v-if="scope.row.source_instance.id === instanceId">
            <div
              v-for="(value, key) in scope.row.source_attributes"
              :key="key"
              style="font-size: 12px"
            >
              <el-text tag="b"
                >{{
                  getSourceAttributeLabel(scope.row.relation, key)
                }}:</el-text
              >
              {{ value }}
            </div>
          </div>
          <div v-else>
            <div
              v-for="(value, key) in scope.row.target_attributes"
              :key="key"
              style="font-size: 12px"
            >
              <el-text tag="b"
                >{{
                  getTargetAttributeLabel(scope.row.relation, key)
                }}:</el-text
              >
              {{ value }}
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="relation" label="关联动作" width="100">
        <template #default="scope">
          <el-tag type="success">
            {{ getRelationDisplayName(scope.row) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="source_instance" label="目标实例">
        <template #default="scope">
          <el-tag v-if="scope.row.source_instance.id !== instanceId">{{
            scope.row.source_instance.instance_name
          }}</el-tag>
          <el-tag v-else>{{ scope.row.target_instance.instance_name }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="target_attributes" label="目标属性" width="150">
        <template #default="scope">
          <div v-if="scope.row.source_instance.id !== instanceId">
            <div
              v-for="(value, key) in scope.row.source_attributes"
              :key="key"
              style="font-size: 12px"
            >
              <el-text tag="b"
                >{{
                  getSourceAttributeLabel(scope.row.relation, key)
                }}:</el-text
              >
              {{ value }}
            </div>
          </div>
          <div v-else>
            <div
              v-for="(value, key) in scope.row.target_attributes"
              :key="key"
              style="font-size: 12px"
            >
              <el-text tag="b"
                >{{
                  getTargetAttributeLabel(scope.row.relation, key)
                }}:</el-text
              >
              {{ value }}
            </div>
          </div>
        </template>
      </el-table-column>
      <!-- <el-table-column prop="target_instance" label="目标实例">
        <template #default="scope">
          <el-tag>{{ scope.row.target_instance.instance_name }}</el-tag>
        </template>
      </el-table-column> -->
      <el-table-column prop="relation_attributes" label="关系属性" width="150">
        <template #default="scope">
          <div
            v-for="(value, key) in scope.row.relation_attributes"
            :key="key"
            style="font-size: 12px"
          >
            <el-text tag="b"
              >{{
                getRelationAttributeLabel(scope.row.relation, key)
              }}:</el-text
            >
            {{ getRelationAttributeValue(scope.row.relation, key, value) }}
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="relation" label="关系类型" width="150">
        <template #default="scope">
          <el-tag type="info">{{ scope.row.relation.name }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="id" label="关联动作描述">
        <template #default="scope">
          <div
            class="relation-description"
            v-html="generateStyledRelationDescription(scope.row)"
          ></div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="scope">
          <el-button
            @click="editRelation(scope.row)"
            type="primary"
            :icon="Edit"
            link
            v-permission="`${route.name?.replace('_info', '')}:edit`"
          >
          </el-button>
          <el-button
            type="danger"
            link
            :icon="Delete"
            @click="deleteRelation(scope.row.id)"
            v-permission="`${route.name?.replace('_info', '')}:delete`"
          >
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
      :title="isEditMode ? '编辑关联关系' : '添加关联关系'"
      width="600px"
      @close="resetAddRelationForm"
    >
      <el-form
        ref="addRelationFormRef"
        :model="addRelationForm"
        :rules="addRelationRules"
        label-width="120px"
      >
        <el-form-item label="关系类型" prop="relation">
          <el-select
            v-model="addRelationForm.relation"
            placeholder="请选择关系类型"
            style="width: 100%"
            @change="handleRelationTypeChange"
            :disabled="isEditMode"
          >
            <el-option
              v-for="item in relationDefinitions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            >
              <span style="float: left">{{ item.name }}</span>
              <span
                style="
                  float: right;
                  color: var(--el-text-color-secondary);
                  font-size: 13px;
                "
              >
                {{
                  item.source_model?.indexOf(props.modelId) >>> -1
                    ? "目标实例"
                    : "源实例"
                }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="目标实例" prop="target_instance">
          <el-radio-group
            v-model="selectModel"
            size="default"
            @change="handleSelectModelChange"
          >
            <el-radio-button
              :disabled="isEditMode"
              :label="item.label"
              :value="item.value"
              v-for="(item, index) in selectModelOptions"
              :key="index"
            />
          </el-radio-group>
          <el-select
            v-model="addRelationForm.target_instance"
            placeholder="请选择关联实例"
            style="width: 100%; margin-top: 5px"
            filterable
            remote
            :remote-method="searchTargetInstances"
            :loading="searchLoading"
            :disabled="isEditMode"
          >
            <el-option
              v-for="item in targetInstances"
              :key="item.id"
              :label="item.instance_name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关联动作" v-if="selectModel === modelId">
          <el-radio-group v-model="is_reverse" :disabled="isEditMode">
            <el-radio :value="false" size="large">{{
              relationDefineMap[addRelationForm.relation]?.forward_verb
            }}</el-radio>
            <el-radio :value="true" size="large">{{
              relationDefineMap[addRelationForm.relation]?.reverse_verb
            }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <!-- 动态生成attribute_schema相关表单项 -->
        <template
          v-if="relationDefineMap[addRelationForm.relation]?.attribute_schema"
        >
          <!-- Source属性 -->
          <template
            v-for="(sourceField, sourceKey) in relationDefineMap[
              addRelationForm.relation
            ].attribute_schema.source"
            :key="'source_' + sourceKey"
          >
            <el-form-item
              :label="sourceField.verbose_name"
              :prop="'source_attributes.' + sourceKey"
              :required="sourceField.required"
            >
              <el-input
                v-model="addRelationForm.source_attributes[sourceKey]"
                :placeholder="'请输入' + sourceField.verbose_name"
                style="width: 100%"
              />
            </el-form-item>
          </template>

          <!-- Target属性 -->
          <template
            v-for="(targetField, targetKey) in relationDefineMap[
              addRelationForm.relation
            ].attribute_schema.target"
            :key="'target_' + targetKey"
          >
            <el-form-item
              :label="targetField.verbose_name"
              :prop="'target_attributes.' + targetKey"
              :required="targetField.required"
            >
              <el-input
                v-model="addRelationForm.target_attributes[targetKey]"
                :placeholder="'请输入' + targetField.verbose_name"
                style="width: 100%"
              />
            </el-form-item>
          </template>

          <!-- Relation属性 -->
          <template
            v-for="(relationField, relationKey) in relationDefineMap[
              addRelationForm.relation
            ].attribute_schema.relation"
            :key="'relation_' + relationKey"
          >
            <el-form-item
              :label="relationField.verbose_name"
              :prop="'relation_attributes.' + relationKey"
              :required="relationField.required"
            >
              <!-- 枚举类型 -->
              <el-select
                v-if="relationField.type === 'enum'"
                v-model="addRelationForm.relation_attributes[relationKey]"
                :placeholder="'请选择' + relationField.verbose_name"
                style="width: 100%"
              >
                <el-option
                  v-for="option in validationRulesEnumObject[
                    relationField.validation_rule
                  ]"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>

              <!-- 数字类型 -->
              <el-input-number
                v-else-if="['integer', 'float'].includes(relationField.type)"
                v-model="addRelationForm.relation_attributes[relationKey]"
                :placeholder="'请输入' + relationField.verbose_name"
                style="width: 100%"
                controls-position="right"
              />

              <!-- 默认文本类型 -->
              <el-input
                v-else
                v-model="addRelationForm.relation_attributes[relationKey]"
                :placeholder="'请输入' + relationField.verbose_name"
                style="width: 100%"
              />

              <!-- 单位显示 -->
              <div
                v-if="relationField.unit"
                style="font-size: 12px; color: #999; margin-top: 3px"
              >
                单位: {{ relationField.unit }}
              </div>
            </el-form-item>
          </template>
        </template>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addRelationDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitAddRelation">{{
            isEditMode ? "保存" : "添加"
          }}</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { Delete, Edit } from "@element-plus/icons-vue";
import {
  ref,
  reactive,
  onMounted,
  getCurrentInstance,
  computed,
  watch,
  nextTick,
} from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import useModelStore from "@/store/cmdb/model";
const props = defineProps({
  instanceId: {
    type: String,
    required: true,
  },
  modelId: {
    type: String,
    required: true,
  },
});
const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();
const modelConfigStore = useModelStore();
const modelOptions = computed(() => modelConfigStore.modelOptions);
const modelObjectById = computed(() => modelConfigStore.modelObjectById);
const validationRulesEnumObject = computed(
  () => modelConfigStore.validationRulesEnumOptionsObject
);
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
const isEditMode = ref(false); // 是否为编辑模式
const currentEditId = ref(null); // 当前编辑的记录ID
const addRelationForm = reactive({
  relation: null,
  source_instance: props.instanceId,
  target_instance: null,
  source_attributes: {},
  target_attributes: {},
  relation_attributes: {},
});

// 表单验证规则
const addRelationRules = {
  relation: [{ required: true, message: "请选择关系类型", trigger: "change" }],
  target_instance: [
    { required: true, message: "请选择目标实例", trigger: "change" },
  ],
  source_attributes: {},
  target_attributes: {},
  relation_attributes: {},
};

// 获取关联关系数据
const getRelationsData = async () => {
  loading.value = true;
  try {
    const res = await proxy.$api.getModelInstanceRelation({
      // source_instance: props.instanceId,
      instances: props.instanceId,
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
// 模型关系map
const relationDefineMap = computed(() => {
  const map = {};
  relationDefinitions.value.forEach((item) => {
    map[item.id] = item;
  });
  return map;
});
const selectModel = ref(null);
const selectModelOptions = ref([]);
const is_reverse = ref(false);
watch(
  () => addRelationForm.relation,
  () => {
    if (!addRelationForm.relation) return;
    let _sourceModelArr =
      relationDefineMap.value[addRelationForm.relation].source_model;
    let _targetModelArr =
      relationDefineMap.value[addRelationForm.relation].target_model;
    if (_sourceModelArr?.indexOf(props.modelId) !== -1) {
      // 源和目标都存在
      if (_targetModelArr?.indexOf(props.modelId) !== -1) {
        selectModelOptions.value = modelOptions.value.filter((item) => {
          return (
            _targetModelArr.indexOf(item.value) !== -1 ||
            _sourceModelArr.indexOf(item.value) !== -1
          );
        });
      } else {
        selectModelOptions.value = modelOptions.value.filter((item) => {
          return _targetModelArr.indexOf(item.value) !== -1;
        });
        is_reverse.value = false;
      }
    } else {
      selectModelOptions.value = modelOptions.value.filter((item) => {
        return _sourceModelArr.indexOf(item.value) !== -1;
      });
      is_reverse.value = true;
    }
    selectModel.value = selectModelOptions.value[0].value;
  },
  { deep: true }
);
// 切换时，清除已选择的目标实例
const handleSelectModelChange = () => {
  if (isEditMode.value) return;
  addRelationForm.target_instance = null;
};
// watch(
//   () => selectModel.value,
//   (newValue, oldValue) => {
//     console.log(selectModel.value);
//     console.log("新旧", oldValue, newValue);
//   }
// );
// 获取关系定义列表
const getRelationDefinitions = async () => {
  try {
    const res = await proxy.$api.getModelRelationDefine({
      // 可以根据需要添加过滤条件
      any_model: props.modelId,
    });
    relationDefinitions.value = res.data.results;
  } catch (error) {
    ElMessage.error("获取关系类型失败");
    console.error(error);
  }
};

// 搜索目标实例
const searchTargetInstances = async (query) => {
  if (!addRelationForm.relation) {
    targetInstances.value = [];
    return;
  }

  searchLoading.value = true;
  try {
    // 获取当前选中关系类型
    // const selectedRelation = relationDefinitions.value.find(
    //   (item) => item.id === addRelationForm.relation
    // );

    if (selectModel.value) {
      const res = await proxy.$api.getCiModelInstance({
        // 根据关系类型的目标模型搜索实例
        model: selectModel.value,
        search: query,
        page_size: 20,
      });
      // 去掉本身的实例
      targetInstances.value = res.data.results;
      targetInstances.value = targetInstances.value.filter(
        (item) => item.id !== props.instanceId
      );
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
  isEditMode.value = false;
  currentEditId.value = null;
  addRelationDialogVisible.value = true;

  // 获取最新的关系定义列表
  getRelationDefinitions();
};
// 编辑关联关系
const editRelation = async (row) => {
  isEditMode.value = true;
  currentEditId.value = row.id;
  addRelationDialogVisible.value = true;
  // 获取关系定义数据
  if (relationDefinitions.value.length === 0) {
    await getRelationDefinitions();
  }

  // 填充表单数据
  addRelationForm.relation = row.relation.id;

  // 填充属性数据
  addRelationForm.source_attributes = row.source_attributes || {};
  addRelationForm.target_attributes = row.target_attributes || {};
  addRelationForm.relation_attributes = row.relation_attributes || {};
  is_reverse.value = row.source_instance.id === props.instanceId ? false : true;
  nextTick(() => {
    selectModel.value = row.target_instance.model;
    targetInstances.value = [
      {
        id: row.source_instance.id,
        instance_name: row.source_instance.instance_name,
      },
      {
        id: row.target_instance.id,
        instance_name: row.target_instance.instance_name,
      },
    ];
    addRelationForm.target_instance = is_reverse.value
      ? row.source_instance.id
      : row.target_instance.id;

    // 获取目标实例列表
    // await searchTargetInstances("");
  });
};
// 重置添加关联表单
const resetAddRelationForm = () => {
  addRelationFormRef.value?.resetFields();
  addRelationForm.relation = null;
  addRelationForm.target_instance = null;
  // 重置attribute_schema相关字段
  addRelationForm.source_attributes = {};
  addRelationForm.target_attributes = {};
  addRelationForm.relation_attributes = {};
  targetInstances.value = [];
  isEditMode.value = false;
  is_reverse.value = false;
  currentEditId.value = null;
  selectModelOptions.value = [];
  selectModel.value = null;
};
// ... existing code ...
// 提交添加关联关系
const submitAddRelation = async () => {
  await addRelationFormRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        let res;
        let _addRelationForm = { ...addRelationForm };
        // 添加关系时，根据是否需要互换，将source_instance和target_instance的值互换
        if (is_reverse.value) {
          _addRelationForm.target_instance = addRelationForm.source_instance;
          _addRelationForm.source_instance = addRelationForm.target_instance;
        }
        if (isEditMode.value) {
          // 编辑模式
          res = await proxy.$api.updateModelInstanceRelation({
            id: currentEditId.value,
            ..._addRelationForm,
          });
        } else {
          // 新增模式
          // 将addRelationForm中的target_instance和source_instance的值互换

          res = await proxy.$api.addModelInstanceRelation({
            source_instance: props.instanceId,
            ..._addRelationForm,
          });
        }

        if (
          (res.status === 201 && !isEditMode.value) ||
          (res.status === 200 && isEditMode.value)
        ) {
          ElMessage.success(
            isEditMode.value ? "编辑关联关系成功" : "添加关联关系成功"
          );
          addRelationDialogVisible.value = false;
          resetAddRelationForm();
          getRelationsData(); // 刷新数据
        } else {
          ElMessage.error(
            isEditMode.value
              ? `编辑关联关系失败,${JSON.stringify(res.data)}`
              : `添加关联关系失败,${JSON.stringify(res.data)}}`
          );
        }
      } catch (error) {
        ElMessage.error(
          (isEditMode.value ? "编辑关联关系失败: " : "添加关联关系失败: ") +
            error.message
        );
        console.error(error);
      }
    }
  });
};
// ... existing code ...
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
// 获取关系显示名称（支持正向和反向）
const getRelationDisplayName = (row) => {
  if (!row) return "";
  if (row.source_instance.id === props.instanceId) {
    return row.relation.forward_verb;
  } else {
    return row.relation.reverse_verb;
  }
};

// 生成带样式的关联动作描述
const generateStyledRelationDescription = (row) => {
  if (!row) return "";
  const sourceName = row.source_instance.instance_name;
  const targetName = row.target_instance.instance_name;
  const relationName = getRelationDisplayName(row);
  const sourceModelName =
    modelObjectById.value[row.source_instance.model]?.verbose_name;
  const targetModelName =
    modelObjectById.value[row.target_instance.model]?.verbose_name;
  // 根据instanceId所在位置决定使用哪一侧的属性
  let sourceAttributesName, targetAttributesName;

  if (row.source_instance.id === props.instanceId) {
    // instanceId在source_instance中
    sourceAttributesName = Object.keys(row.source_attributes)
      .map(
        (key) =>
          `${getSourceAttributeLabel(
            row.relation,
            key
          )}: ${getRelationAttributeValue(
            row.relation,
            key,
            row.source_attributes[key],
            "source"
          )}`
      )
      .join(", ");
    targetAttributesName = Object.keys(row.target_attributes)
      .map(
        (key) =>
          `${getTargetAttributeLabel(
            row.relation,
            key
          )}: ${getRelationAttributeValue(
            row.relation,
            key,
            row.target_attributes[key],
            "target"
          )}`
      )
      .join(", ");

    // 构建描述文本，仅在属性存在时显示
    let description = `<span class="source-name">${sourceName}</span>(${sourceModelName})`;
    if (sourceAttributesName) {
      description += `的[${sourceAttributesName}]`;
    }
    description += ` - <span class="relation-name">${relationName}</span> - <span class="target-name">${targetName}</span>(${targetModelName})`;
    if (targetAttributesName) {
      description += `的[${targetAttributesName}]`;
    }
    return description;
  } else {
    // instanceId在target_instance中
    targetAttributesName = Object.keys(row.target_attributes)
      .map(
        (key) =>
          `${getTargetAttributeLabel(
            row.relation,
            key
          )}: ${getRelationAttributeValue(
            row.relation,
            key,
            row.target_attributes[key],
            "target"
          )}`
      )
      .join(", ");
    sourceAttributesName = Object.keys(row.source_attributes)
      .map(
        (key) =>
          `${getSourceAttributeLabel(
            row.relation,
            key
          )}: ${getRelationAttributeValue(
            row.relation,
            key,
            row.source_attributes[key],
            "source"
          )}`
      )
      .join(", ");

    // 构建描述文本，仅在属性存在时显示
    let description = `<span class="source-name">${targetName}</span>(${targetModelName})`;
    if (targetAttributesName) {
      description += `的[${targetAttributesName}]`;
    }
    description += ` - <span class="relation-name">${relationName}</span> - <span class="target-name">${sourceName}</span>(${sourceModelName})`;
    if (sourceAttributesName) {
      description += `的[${sourceAttributesName}]`;
    }
    return description;
  }
};

// 获取源属性标签
const getSourceAttributeLabel = (relation, attrKey) => {
  if (
    !relation ||
    !relation.attribute_schema ||
    !relation.attribute_schema.source
  )
    return attrKey;
  const field = relation.attribute_schema.source[attrKey];
  return field ? field.verbose_name : attrKey;
};

// 获取关系属性标签
const getRelationAttributeLabel = (relation, attrKey) => {
  if (
    !relation ||
    !relation.attribute_schema ||
    !relation.attribute_schema.relation
  )
    return attrKey;
  const field = relation.attribute_schema.relation[attrKey];
  return field ? field.verbose_name : attrKey;
};

// 获取目标属性标签
const getTargetAttributeLabel = (relation, attrKey) => {
  if (
    !relation ||
    !relation.attribute_schema ||
    !relation.attribute_schema.target
  )
    return attrKey;
  const field = relation.attribute_schema.target[attrKey];
  return field ? field.verbose_name : attrKey;
};
// 获取关系属性值（处理枚举和单位）
const getRelationAttributeValue = (relation, attrKey, value) => {
  if (
    !relation ||
    !relation.attribute_schema ||
    !relation.attribute_schema.relation
  )
    return value;

  const field = relation.attribute_schema.relation[attrKey];
  if (!field) return value;

  // 处理枚举类型
  if (field.type === "enum" && field.validation_rule) {
    const enumOptions = validationRulesEnumObject.value[field.validation_rule];
    if (enumOptions) {
      const option = enumOptions.find((option) => option.value === value);
      if (option) {
        return option.label;
      }
    }
  }

  // 添加单位
  if (field.unit) {
    return `${value} ${field.unit}`;
  }

  return value;
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

.target-name {
  font-weight: bold;
}

.relation-name {
  color: #409eff;
  font-weight: bold;
}
</style>