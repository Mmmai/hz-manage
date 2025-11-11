<template>
  <div class="divVertical">
    <div class="card filter-card">
      <!-- 筛选区域 -->
      <div class="filter-container">
        <div class="filter-row filter-row-flex">
          <!-- 模型筛选 -->
          <div class="filter-item">
            <span class="filter-label">模型：</span>
            <el-select
              v-model="filters.model"
              placeholder="请选择模型"
              clearable
              style="width: 200px"
              @change="handleFilterChange"
            >
              <el-option
                v-for="model in modelOptions"
                :key="model.value"
                :label="model.label"
                :value="model.value"
              />
            </el-select>
          </div>

          <!-- 关系类型筛选 -->
          <div class="filter-item">
            <span class="filter-label">关系类型：</span>
            <el-select
              v-model="filters.relationType"
              placeholder="请选择关系类型"
              clearable
              style="width: 200px"
              @change="handleFilterChange"
            >
              <el-option
                v-for="relation in relationTypeOptions"
                :key="relation.id"
                :label="relation.name"
                :value="relation.id"
              />
            </el-select>
          </div>
          <!-- 实例名称筛选 -->
          <div class="filter-item">
            <span class="filter-label">实例名称：</span>
            <el-input
              v-model="filters.instance_name"
              placeholder="请输入实例名称"
              clearable
              style="width: 200px"
            />
          </div>
          <!-- 搜索按钮 -->
          <div class="filter-item">
            <el-button
              type="primary"
              :icon="Search"
              @click="handleFilterChange"
            >
              搜索
            </el-button>
            <el-button @click="resetFilters">重置</el-button>
          </div>
        </div>
      </div>
      <el-button type="primary" @click="handleAdd">新增关联</el-button>
    </div>

    <div class="card table-container" style="width: 100%">
      <el-table
        :data="relationList"
        stripe
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="definition.name" label="关系类型" width="150">
          <template #default="scope">
            {{ scope.row.relation?.name }}
          </template>
        </el-table-column>
        <el-table-column label="源实例">
          <template #default="scope">
            <div>
              <el-link
                :href="`/#/cmdb/cidata/${scope.row.source_instance?.id}`"
                >{{ scope.row.source_instance?.instance_name }}</el-link
              >
              <el-tag type="info" size="small">{{
                getModelName(scope.row.source_instance?.model)
              }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="源属性" prop="source_attributes" width="200">
          <template #default="scope">
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
          </template>
        </el-table-column>
        <el-table-column prop="relation" label="关联动作" width="100">
          <template #default="scope">
            <el-tag type="success">
              {{ scope.row.relation?.forward_verb }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="目标实例">
          <template #default="scope">
            <div>
              <el-link
                :href="`/#/cmdb/cidata/${scope.row.target_instance?.id}`"
                >{{ scope.row.target_instance?.instance_name }}</el-link
              >
              <el-tag type="info" size="small">{{
                getModelName(scope.row.target_instance?.model)
              }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="目标属性" prop="target_attributes" width="200">
          <template #default="scope">
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
          </template>
        </el-table-column>
        <el-table-column
          prop="relation_attributes"
          label="关系属性"
          width="250"
        >
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
        <el-table-column prop="id" label="关联动作描述">
          <template #default="scope">
            <div
              class="relation-description"
              v-html="generateStyledRelationDescription(scope.row)"
            ></div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button
              @click="handleViewDetail(scope.row)"
              type="primary"
              link
              :icon="View"
            >
            </el-button>
            <el-button
              @click="handleEdit(scope.row)"
              type="primary"
              link
              :icon="Edit"
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

      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: flex-end; display: flex"
      />
    </div>

    <!-- 关系详情抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      title="关系详情"
      direction="rtl"
      size="50%"
    >
      <div class="drawer-content">
        <json-viewer
          :value="currentRelationData"
          :expand-depth="10"
          copyable
          boxed
          sort
          expanded
        ></json-viewer>
      </div>
    </el-drawer>

    <!-- 编辑关系对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="'编辑关系'"
      width="600px"
      @close="resetEditForm"
    >
      <el-form ref="editFormRef" :model="editForm" label-width="120px">
        <el-form-item label="关系类型">
          <el-input v-model="editForm.relation.name" disabled />
        </el-form-item>

        <el-form-item label="源实例">
          <el-input v-model="editForm.source_instance.instance_name" disabled />
        </el-form-item>

        <el-form-item label="目标实例">
          <el-input v-model="editForm.target_instance.instance_name" disabled />
        </el-form-item>

        <!-- 动态生成attribute_schema相关表单项 -->
        <template v-if="editForm.relation?.attribute_schema">
          <!-- Source属性 -->
          <template
            v-for="(sourceField, sourceKey) in editForm.relation
              .attribute_schema.source"
            :key="'source_' + sourceKey"
          >
            <el-form-item
              :label="sourceField.verbose_name"
              :prop="'source_attributes.' + sourceKey"
            >
              <el-input
                v-model="editForm.source_attributes[sourceKey]"
                :placeholder="'请输入' + sourceField.verbose_name"
                style="width: 100%"
              />
            </el-form-item>
          </template>

          <!-- Target属性 -->
          <template
            v-for="(targetField, targetKey) in editForm.relation
              .attribute_schema.target"
            :key="'target_' + targetKey"
          >
            <el-form-item
              :label="targetField.verbose_name"
              :prop="'target_attributes.' + targetKey"
            >
              <el-input
                v-model="editForm.target_attributes[targetKey]"
                :placeholder="'请输入' + targetField.verbose_name"
                style="width: 100%"
              />
            </el-form-item>
          </template>

          <!-- Relation属性 -->
          <template
            v-for="(relationField, relationKey) in editForm.relation
              .attribute_schema.relation"
            :key="'relation_' + relationKey"
          >
            <el-form-item
              :label="relationField.verbose_name"
              :prop="'relation_attributes.' + relationKey"
            >
              <!-- 枚举类型 -->
              <el-select
                v-if="relationField.type === 'enum'"
                v-model="editForm.relation_attributes[relationKey]"
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
                v-model="editForm.relation_attributes[relationKey]"
                :placeholder="'请输入' + relationField.verbose_name"
                style="width: 100%"
                controls-position="right"
              />

              <!-- 默认文本类型 -->
              <el-input
                v-else
                v-model="editForm.relation_attributes[relationKey]"
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
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEditForm">保存</el-button>
        </div>
      </template>
    </el-dialog>
    <!-- 新增关系对话框 -->
    <el-dialog
      v-model="addRelationDialogVisible"
      :title="'新增关联关系'"
      width="60%"
      :before-close="resetAddRelationForm"
    >
      <el-form
        ref="addRelationFormRef"
        :model="addRelationForm"
        :rules="addRelationRules"
        label-width="120px"
      >
        <el-form-item label="源模型" prop="source_model">
          <el-select
            v-model="addRelationForm.source_model"
            placeholder="请选择源模型"
            style="width: 30%"
            filterable
            @change="handleSelectModelChange"
          >
            <el-option
              v-for="item in modelOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="源实例" prop="source_instance">
          <el-select
            v-model="addRelationForm.source_instance"
            placeholder="请选择源实例"
            style="width: 30%"
            filterable
            remote
            :remote-method="searchSourceInstances"
            :loading="sourceInstanceLoading"
          >
            <el-option
              v-for="item in sourceInstances"
              :key="item.id"
              :label="item.instance_name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="关系类型" prop="relation">
          <el-select
            v-model="addRelationForm.relation"
            placeholder="请选择关系类型"
            style="width: 30%"
            @change="handleRelationTypeChange"
          >
            <el-option
              v-for="item in relationDefineOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          label="目标模型"
          prop="target_instance"
          v-if="addRelationForm.relation"
        >
          <el-radio-group
            v-model="selectTargetModel"
            size="default"
            @change="targetModelChange"
          >
            <el-radio-button
              :label="item.label"
              :value="item.value"
              v-for="(item, index) in targetModelOptions"
              :key="index"
            />
          </el-radio-group>
        </el-form-item>
        <el-form-item
          label="关联动作"
          v-if="
            addRelationForm.source_model !== null && selectTargetModel !== null
          "
          ><div class="flexStart">
            <div
              v-if="
                addRelationForm.source_model === selectTargetModel &&
                relationDefineMap[addRelationForm.relation]?.forward_verb !==
                  relationDefineMap[addRelationForm.relation]?.reverse_verb
              "
            >
              <el-radio-group v-model="is_reverse">
                <el-radio :value="false" size="large">{{
                  relationDefineMap[addRelationForm.relation]?.forward_verb
                }}</el-radio>
                <el-radio :value="true" size="large">{{
                  relationDefineMap[addRelationForm.relation]?.reverse_verb
                }}</el-radio>
              </el-radio-group>
            </div>
            <el-text>{{ getRelationDescription }}</el-text>
          </div>
        </el-form-item>
        <el-form-item label="关联实例" v-if="addRelationForm.relation">
          <el-table
            :data="addRelationForm.relations"
            style="width: 100%; margin-top: 15px"
            border
          >
            <el-table-column
              prop="target_instance"
              label="目标实例"
              width="300"
            >
              <template #default="scope">
                <el-form-item
                  :prop="'relations.' + scope.$index + '.target_instance'"
                  required
                >
                  <el-select
                    v-model="scope.row.target_instance"
                    placeholder="请选择目标实例"
                    style="width: 100%"
                    filterable
                    remote
                    :remote-method="searchTargetInstances"
                    :loading="targetInstanceLoading"
                  >
                    <el-option
                      v-for="item in targetInstances"
                      :key="item.id"
                      :label="item.instance_name"
                      :value="item.id"
                    />
                  </el-select>
                </el-form-item>
              </template>
            </el-table-column>
            <el-table-column prop="source_attributes" label="源属性">
              <template #default="scope">
                <template v-if="scope.row.source_attributes">
                  <el-form-item
                    v-for="(sourceField, sourceKey) in relationDefineMap[
                      addRelationForm.relation
                    ]?.attribute_schema.source"
                    :key="'source_' + scope.$index + '.' + sourceKey"
                    :label="sourceField.verbose_name"
                    :prop="
                      'relations.' +
                      scope.$index +
                      '.source_attributes' +
                      sourceKey
                    "
                    :required="sourceField.required"
                    label-position="left"
                    label-width="100px"
                  >
                    <el-input
                      v-model="scope.row.source_attributes[sourceKey]"
                      :placeholder="'请输入' + sourceField.verbose_name"
                      style="width: 80%"
                    />
                  </el-form-item>
                </template>
              </template>
            </el-table-column>
            <el-table-column prop="target_attributes" label="目标属性">
              <template #default="scope">
                <template v-if="scope.row.target_attributes">
                  <el-form-item
                    v-for="(targetField, targetKey) in relationDefineMap[
                      addRelationForm.relation
                    ]?.attribute_schema.target"
                    :key="'source_' + scope.$index + '.' + targetKey"
                    :label="targetField.verbose_name"
                    :prop="
                      'relations.' +
                      scope.$index +
                      '.target_attributes.' +
                      targetKey
                    "
                    :required="targetField.required"
                    label-position="left"
                    label-width="100px"
                  >
                    <el-input
                      v-model="scope.row.target_attributes[targetKey]"
                      :placeholder="'请输入' + targetField.verbose_name"
                      style="width: 80%"
                    />
                  </el-form-item>
                </template>
              </template>
            </el-table-column>
            <el-table-column prop="relation_attributes" label="关系属性">
              <template #default="scope">
                <template v-if="scope.row.relation_attributes">
                  <el-form-item
                    v-for="(relationField, relationKey) in relationDefineMap[
                      addRelationForm.relation
                    ]?.attribute_schema.relation"
                    :key="'source_' + scope.$index + '.' + relationKey"
                    :label="relationField.verbose_name"
                    :prop="
                      'relations.' +
                      scope.$index +
                      '.relation_attributes.' +
                      relationKey
                    "
                    :required="relationField.required"
                    label-position="left"
                    label-width="100px"
                  >
                    <!-- <el-input
                      v-model="scope.row.relation_attributes[relationKey]"
                      :placeholder="'请输入' + relationField.verbose_name"
                      style="width: 100%"
                    /> -->
                    <!-- 枚举类型 -->
                    <el-select
                      v-if="relationField.type === 'enum'"
                      v-model="scope.row.relation_attributes[relationKey]"
                      :placeholder="'请选择' + relationField.verbose_name"
                      style="width: 80%"
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
                      v-else-if="
                        ['integer', 'float'].includes(relationField.type)
                      "
                      v-model="scope.row.relation_attributes[relationKey]"
                      :placeholder="'请输入' + relationField.verbose_name"
                      style="width: 80%"
                      controls-position="right"
                    />

                    <!-- 默认文本类型 -->
                    <el-input
                      v-else
                      v-model="scope.row.relation_attributes[relationKey]"
                      :placeholder="'请输入' + relationField.verbose_name"
                      style="width: 80%"
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
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="scope">
                <el-button
                  type="primary"
                  link
                  @click="copyTargetInstance(scope.row)"
                >
                  复制
                </el-button>
                <el-button
                  type="danger"
                  link
                  @click="removeTargetInstance(scope.$index)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <div style="width: 100%; margin-top: 10px" class="flexCenter">
            <el-button @click="addTargetInstance" type="primary"
              >新增</el-button
            >
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="resetAddRelationForm">取消</el-button>
          <el-button type="primary" @click="submitAddRelation">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>
           

<script setup>
import {
  ref,
  reactive,
  onMounted,
  computed,
  getCurrentInstance,
  watch,
} from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search, View, Edit, Delete } from "@element-plus/icons-vue";
import { JsonViewer } from "vue3-json-viewer";
import "vue3-json-viewer/dist/vue3-json-viewer.css";
import { useRoute } from "vue-router";
const route = useRoute();
import useModelStore from "@/store/cmdb/model";
const modelConfigStore = useModelStore();
const modelOptions = computed(() => modelConfigStore.modelOptions);
const modelObjectById = computed(() => modelConfigStore.modelObjectById);
const validationRulesEnumObject = computed(
  () => modelConfigStore.validationRulesEnumOptionsObject
);
const { proxy } = getCurrentInstance();

// 过滤条件
const filters = reactive({
  relationType: "",
  model: "",
  instance_name: "",
});

// 关系类型选项

// 关系列表
const relationList = ref([]);
const loading = ref(false);

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0,
});

// 抽屉相关
const drawerVisible = ref(false);
const currentRelationData = ref({});

// 编辑对话框相关
const editDialogVisible = ref(false);
const editFormRef = ref();
const currentEditId = ref(null);
const editForm = reactive({
  relation: {},
  source_instance: {},
  target_instance: {},
  source_attributes: {},
  target_attributes: {},
  relation_attributes: {},
});

// 新增关系对话框相关
const addRelationDialogVisible = ref(false);
const addRelationFormRef = ref();
const relationTypeOptions = ref([]); // 关系定义列表
const sourceInstances = ref([]); // 源实例列表
const targetInstances = ref([]); // 目标实例列表
const sourceInstanceLoading = ref(false);
const targetInstanceLoading = ref(false);
// 为目标实例存储独立的属性
const addTargetInstance = () => {
  addRelationForm.relations.push({
    target_instance: null,
    source_attributes: {},
    target_attributes: {},
    relation_attributes: {},
  });
};
const copyTargetInstance = (row) => {
  addRelationForm.relations.push({
    target_instance: null,
    source_attributes: { ...row.source_attributes },
    target_attributes: { ...row.target_attributes },
    relation_attributes: { ...row.relation_attributes },
  });
};
const removeTargetInstance = (index) => {
  addRelationForm.relations.splice(index, 1);
};
const addRelationForm = reactive({
  source_model: null,
  relation: null,
  source_instance: null,
  relations: [],
});

const targetModelOptions = ref([]);
const selectTargetModel = ref(null);
const targetModelChange = () => {
  if (selectTargetModel.value !== addRelationForm.source_model) {
    if (
      relationDefineMap.value[addRelationForm.relation]?.source_model.indexOf(
        selectTargetModel.value
      ) !== -1
    ) {
      is_reverse.value = true;
    } else {
      is_reverse.value = false;
    }
  }
};
// 模型关系map
const relationDefineMap = computed(() => {
  const map = {};
  relationTypeOptions.value.forEach((item) => {
    map[item.id] = item;
  });
  return map;
});
// 根据选择的源模型，过滤有被定义关联关系的选项
const relationDefineOptions = computed(() => {
  const map = {};
  relationTypeOptions.value.forEach((item) => {
    if (
      item.source_model.indexOf(addRelationForm.source_model) !== -1 ||
      item.target_model.indexOf(addRelationForm.source_model) !== -1
    ) {
      map[item.id] = item;
    }
  });
  return map;
});
const is_reverse = ref(false);

// watch(
//   () => addRelationForm.relation,
//   () => {
//     if (!addRelationForm.relation || !addRelationForm.source_model) return;
//     console.log("关联关系", relationDefineMap.value[addRelationForm.relation]);
//     let _sourceModelArr =
//       relationDefineMap.value[addRelationForm.relation]?.source_model;
//     let _targetModelArr =
//       relationDefineMap.value[addRelationForm.relation]?.target_model;
//     if (_sourceModelArr?.indexOf(addRelationForm.source_model) !== -1) {
//       // 源和目标都存在
//       if (_targetModelArr?.indexOf(addRelationForm.source_model) !== -1) {
//         targetModelOptions.value = modelOptions.value.filter((item) => {
//           return _targetModelArr.indexOf(item.value) !== -1;
//         });
//       } else {
//         targetModelOptions.value = modelOptions.value.filter((item) => {
//           return _targetModelArr.indexOf(item.value) !== -1;
//         });
//         is_reverse.value = false;
//       }
//     } else {
//       targetModelOptions.value = modelOptions.value.filter((item) => {
//         return _sourceModelArr.indexOf(item.value) !== -1;
//       });
//       is_reverse.value = true;
//     }
//     selectTargetModel.value = targetModelOptions.value[0].value;
//   },
//   { deep: true }
// );

// 表单验证规则
const addRelationRules = {
  relation: [{ required: true, message: "请选择关系类型", trigger: "change" }],
  source_instance: [
    { required: true, message: "请选择源实例", trigger: "change" },
  ],
  target_instances: [
    { required: true, message: "请选择目标实例", trigger: "change" },
  ],
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
// 表格列表的描述
const generateStyledRelationDescription = (row) => {
  if (!row) return "";
  const sourceName = row.source_instance.instance_name;
  const targetName = row.target_instance.instance_name;
  const relationName = row.relation.forward_verb;
  const sourceModelName =
    modelObjectById.value[row.source_instance.model].verbose_name;
  const targetModelName =
    modelObjectById.value[row.target_instance.model].verbose_name;
  // 根据instanceId所在位置决定使用哪一侧的属性
  let sourceAttributesName, targetAttributesName;
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
};
// 添加框的描述
const getRelationDescription = computed(() => {
  if (!selectTargetModel.value) return;
  let source_model_name =
    modelObjectById.value[addRelationForm.source_model]?.verbose_name;
  let target_model_name =
    modelObjectById.value[selectTargetModel.value]?.verbose_name;
  let source_instance_name =
    sourceInstanceMap.value[addRelationForm.source_instance]?.instance_name;
  let forward_verb =
    relationDefineMap.value[addRelationForm.relation]?.forward_verb;
  let reverse_verb =
    relationDefineMap.value[addRelationForm.relation]?.reverse_verb;
  if (is_reverse.value) {
    return `源实例: ${source_instance_name}(${source_model_name}) ${reverse_verb} ${target_model_name}`;
  } else {
    return `源实例: ${source_instance_name}(${source_model_name}) ${forward_verb} ${target_model_name}`;
  }
});
// 获取模型名称
const getModelName = (modelId) => {
  if (!modelId) return "";
  return modelObjectById.value[modelId]?.verbose_name || modelId;
};

// 处理筛选变化
const handleFilterChange = () => {
  pagination.currentPage = 1;
  fetchRelationData();
};

// 重置筛选
const resetFilters = () => {
  filters.relationType = "";
  filters.model = "";
  pagination.currentPage = 1;
  fetchRelationData();
};

// 处理分页大小变化
const handleSizeChange = (val) => {
  pagination.pageSize = val;
  pagination.currentPage = 1;
  fetchRelationData();
};

// 处理当前页变化
const handleCurrentChange = (val) => {
  pagination.currentPage = val;
  fetchRelationData();
};

// 查看详情
const handleViewDetail = (row) => {
  currentRelationData.value = row;
  drawerVisible.value = true;
};
const handleSelectModelChange = () => {
  // 清空之前选择的实例
  addRelationForm.source_instance = null;
  // 清空relation和targetModel
  addRelationForm.relation = null;
  targetModelOptions.value = [];
};
// 编辑关系
const handleEdit = (row) => {
  currentEditId.value = row.id;

  // 填充编辑表单数据
  editForm.relation = row.relation || {};
  editForm.source_instance = row.source_instance || {};
  editForm.target_instance = row.target_instance || {};
  editForm.source_attributes = { ...row.source_attributes } || {};
  editForm.target_attributes = { ...row.target_attributes } || {};
  editForm.relation_attributes = { ...row.relation_attributes } || {};

  editDialogVisible.value = true;
};

// 重置编辑表单
const resetEditForm = () => {
  currentEditId.value = null;
  editForm.relation = {};
  editForm.source_instance = {};
  editForm.target_instance = {};
  editForm.source_attributes = {};
  editForm.target_attributes = {};
  editForm.relation_attributes = {};
};

// 提交编辑表单
const submitEditForm = async () => {
  try {
    const params = {
      id: currentEditId.value,
      source_attributes: editForm.source_attributes,
      target_attributes: editForm.target_attributes,
      relation_attributes: editForm.relation_attributes,
    };

    const res = await proxy.$api.updateModelInstanceRelation(params);

    if (res.status === 200) {
      ElMessage.success("更新成功");
      editDialogVisible.value = false;
      resetEditForm();
      fetchRelationData(); // 刷新数据
    } else {
      ElMessage.error("更新失败");
    }
  } catch (error) {
    ElMessage.error("更新失败: " + error.message);
    console.error(error);
  }
};
// 新增关联
const handleAdd = async () => {
  addRelationDialogVisible.value = true;
  // await getRelationDefinitions();
  // 清空实例列表
  sourceInstances.value = [];
  targetInstances.value = [];
};
// 处理关系类型变更
const handleRelationTypeChange = () => {
  // 清空之前选择的实例
  // addRelationForm.source_instance = null;
  addRelationForm.target_instances = [];
  // sourceInstances.value = [];
  targetInstances.value = [];
  if (!addRelationForm.relation || !addRelationForm.source_model) return;
  let _sourceModelArr =
    relationDefineMap.value[addRelationForm.relation]?.source_model;
  let _targetModelArr =
    relationDefineMap.value[addRelationForm.relation]?.target_model;
  if (_sourceModelArr?.indexOf(addRelationForm.source_model) !== -1) {
    // 源和目标都存在
    if (_targetModelArr?.indexOf(addRelationForm.source_model) !== -1) {
      targetModelOptions.value = modelOptions.value.filter((item) => {
        return (
          _targetModelArr.indexOf(item.value) !== -1 ||
          _sourceModelArr.indexOf(item.value) !== -1
        );
      });
    } else {
      targetModelOptions.value = modelOptions.value.filter((item) => {
        return _targetModelArr.indexOf(item.value) !== -1;
      });
      is_reverse.value = false;
    }
  } else {
    targetModelOptions.value = modelOptions.value.filter((item) => {
      return _sourceModelArr.indexOf(item.value) !== -1;
    });
    is_reverse.value = true;
  }
  selectTargetModel.value = targetModelOptions.value[0].value;
};
// 重置新增关系表单
const resetAddRelationForm = () => {
  ElMessageBox.confirm("确定关闭添加对话框?", "Warning", {
    confirmButtonText: "确认",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(() => {
      addRelationFormRef.value?.resetFields();
      addRelationForm.source_model = null;
      addRelationForm.relation = null;
      addRelationForm.source_instance = null;
      addRelationForm.target_instances = [];
      // 清空目标实例属性映射
      addRelationForm.relations = [];
      sourceInstances.value = [];
      targetInstances.value = [];
      addRelationDialogVisible.value = false;
    })
    .catch(() => {
      ElMessage({
        type: "info",
        message: "取消关闭",
      });
    });
};
const sourceInstanceMap = ref({});
// 搜索源实例
const searchSourceInstances = async (query) => {
  // if (!addRelationForm.relation) {
  //   sourceInstances.value = [];
  //   return;
  // }
  sourceInstanceLoading.value = true;
  try {
    if (addRelationForm.source_model) {
      // 获取源模型
      const sourceModel = addRelationForm.source_model;
      const res = await proxy.$api.getCiModelInstance({
        model: sourceModel,
        search: query,
        page_size: 20,
      });
      sourceInstances.value = res.data.results;
      res.data.results.forEach((item) => {
        sourceInstanceMap.value[item.id] = item;
      });
    }
  } catch (error) {
    ElMessage.error("搜索源实例失败");
    console.error(error);
  } finally {
    sourceInstanceLoading.value = false;
  }
};

// 搜索目标实例
const searchTargetInstances = async (query) => {
  if (!addRelationForm.relation) {
    targetInstances.value = [];
    return;
  }

  targetInstanceLoading.value = true;
  try {
    // 获取当前选中关系类型
    const selectedRelation = relationTypeOptions.value.find(
      (item) => item.id === addRelationForm.relation
    );

    if (selectedRelation) {
      // 获取目标模型
      const res = await proxy.$api.getCiModelInstance({
        model: selectTargetModel.value,
        instance_name: query,
        page_size: 3,
      });
      targetInstances.value = res.data.results;
    }
  } catch (error) {
    ElMessage.error("搜索目标实例失败");
    console.error(error);
  } finally {
    targetInstanceLoading.value = false;
  }
};

// 提交新增关系
const submitAddRelation = async () => {
  await addRelationFormRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        const relations = [];

        // 为每个目标实例创建关系
        for (const _relation of addRelationForm.relations) {
          const params = {
            relation: addRelationForm.relation,
            source_instance: addRelationForm.source_instance,
            target_instance: _relation.target_instance,
            source_attributes: _relation.source_attributes || {},
            target_attributes: _relation.target_attributes || {},
            relation_attributes: _relation.relation_attributes || {},
          };
          relations.push(params);
        }
        console.log("提交的params", JSON.stringify({ relations: relations }));

        // 检查是否所有请求都成功
        const res = await proxy.$api.addRelations(relations);

        if (res.status == 200) {
          ElMessage.success("添加关联关系成功");
          addRelationDialogVisible.value = false;
          resetAddRelationForm();
          fetchRelationData(); // 刷新数据
        } else {
          ElMessage.error("部分关联关系添加失败");
        }
      } catch (error) {
        ElMessage.error("添加关联关系失败: " + error.message);
        console.error(error);
      }
    }
  });
};
// 获取关系类型数据
const fetchRelationTypes = async () => {
  try {
    const res = await proxy.$api.getModelRelationDefine();
    relationTypeOptions.value = res.data.results;
  } catch (error) {
    ElMessage.error("获取关系类型失败");
    console.error(error);
  }
};

// 获取关系数据
const fetchRelationData = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.currentPage,
      page_size: pagination.pageSize,
    };

    // 添加过滤条件
    if (filters.relationType) {
      params.relation = filters.relationType;
    }

    if (filters.model) {
      params.model = filters.model;
    }
    if (filters.instance_name) {
      params.instance_name = filters.instance_name;
    }
    const res = await proxy.$api.getModelInstanceRelation(params);
    relationList.value = res.data.results;
    pagination.total = res.data.count;
  } catch (error) {
    ElMessage.error("获取关系数据失败");
    console.error(error);
  } finally {
    loading.value = false;
  }
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
          fetchRelationData(); // 刷新数据
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

// 组件挂载时获取数据
onMounted(() => {
  modelConfigStore.getModel(); // 加载模型数据
  fetchRelationTypes(); // 加载关系类型
  fetchRelationData(); // 加载关系数据
});
</script>

<style scoped>
.filter-card {
  height: 55px;
  padding: 10px 15px;
  overflow-y: auto;
  flex: none;
  display: flex;
  justify-content: space-between;
}

.table-container {
  flex: 1;
  overflow: auto;
}

.filter-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 15px;
}

.filter-row-flex {
  display: flex;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.filter-label {
  white-space: nowrap;
}
</style>