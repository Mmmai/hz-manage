<template>
  <div class="divVertical gap-5">
    <div class="header card">
      <el-page-header @back="goBack">
        <template #content>
          <span>{{
            `${modelInfo.model?.verbose_name}【${instanceData.instance_name}】`
          }}</span>
        </template>
      </el-page-header>
    </div>

    <div class="content card">
      <el-descriptions
        border
        :column="2"
        style="width: 40%; margin-bottom: 10px"
        label-width="100px"
      >
        <el-descriptions-item label="唯一标识">
          {{ instanceData.instance_name }}
        </el-descriptions-item>
        <el-descriptions-item label="所属分组" width="55%">
          <div
            :key="igIndex"
            v-for="(igItem, igIndex) in instanceData?.instance_group"
            class="group-item"
          >
            {{ igItem.group_path }}
          </div>
        </el-descriptions-item>
      </el-descriptions>

      <el-tabs
        v-model="activeName"
        type="card"
        class="demo-tabs"
        @tab-click="handleClick"
      >
        <el-tab-pane label="资产信息" name="modelField">
          <el-form
            ref="editFormRef"
            style="max-width: 100%"
            :model="editForm"
            label-width="auto"
            status-icon
            label-position="top"
            require-asterisk-position="right"
          >
            <el-row :gutter="20" justify="space-between">
              <el-form-item
                prop="instance_name"
                required
                style="margin-left: 30px"
              >
                <template #label>
                  <el-space :size="2">
                    <el-text tag="b">唯一标识</el-text>
                    <el-tooltip
                      content="唯一命名标识"
                      placement="right"
                      effect="dark"
                    >
                      <el-icon>
                        <Warning />
                      </el-icon>
                    </el-tooltip>
                  </el-space>
                </template>

                <el-input
                  v-model="editForm.instance_name"
                  style="min-width: 400px"
                  v-if="isEdit"
                />
                <el-text v-else>{{ editForm.instance_name }}</el-text>
              </el-form-item>
              <div
                style="
                  width: 200px;
                  display: flex;
                  justify-content: flex-end;
                  margin-right: 20px;
                "
              >
                <div v-if="!isEdit">
                  <el-button
                    type="primary"
                    @click="editAction"
                    v-permission="`${route.name?.replace('_info', '')}:edit`"
                    >编辑</el-button
                  >
                  <el-tooltip
                    :content="
                      !hasUnassignedPool
                        ? '实例不在空闲池，无法删除!'
                        : '删除实例'
                    "
                    placement="top"
                    effect="dark"
                  >
                    <el-button
                      type="danger"
                      @click="deleteInstance"
                      v-permission="
                        `${route.name?.replace('_info', '')}:delete`
                      "
                      :disabled="!hasUnassignedPool"
                      >删除</el-button
                    >
                  </el-tooltip>
                </div>
                <div v-else>
                  <el-button type="primary" @click="cancelAction"
                    >取消</el-button
                  >
                  <el-button type="primary" @click="submitAction"
                    >保存</el-button
                  >
                </div>
              </div>
            </el-row>

            <el-collapse v-model="activeArr">
              <el-collapse-item
                :name="index"
                v-for="(item, index) in modelInfo.field_groups"
                :key="index"
              >
                <template #title>
                  <el-text tag="b" size="large">{{
                    item.verbose_name
                  }}</el-text>
                </template>
                <el-row :gutter="20" style="margin-left: 30px">
                  <el-col
                    v-for="(fitem, findex) in item.fields"
                    :key="findex"
                    :xs="24"
                    :sm="24"
                    :md="12"
                    :lg="8"
                    :xl="6"
                  >
                    <el-form-item
                      :label="fitem.verbose_name"
                      :prop="fitem.name"
                      v-if="fitem.type === 'string'"
                      :required="fitem.required"
                      :rules="setFormItemRule(fitem.validation_rule)"
                    >
                      <template #label>
                        <el-space :size="2">
                          <el-text tag="b">{{ fitem.verbose_name }}</el-text>
                          <el-tooltip
                            :content="fitem.description"
                            placement="right"
                            effect="dark"
                            v-if="fitem.description.length != 0 ? true : false"
                          >
                            <el-icon>
                              <Warning />
                            </el-icon>
                          </el-tooltip>
                        </el-space>
                      </template>
                      <el-input
                        v-model="editForm[fitem.name]"
                        style="width: 240px"
                        :disabled="!fitem.editable"
                        v-if="isEdit"
                      ></el-input>
                      <el-text v-else>
                        {{ editForm[fitem.name] }}
                      </el-text>
                    </el-form-item>
                    <el-form-item
                      :label="fitem.verbose_name"
                      :prop="fitem.name"
                      v-if="fitem.type === 'json'"
                      :required="fitem.required"
                    >
                      <template #label>
                        <el-space :size="2">
                          <el-text tag="b">{{ fitem.verbose_name }}</el-text>
                          <el-tooltip placement="right" effect="dark">
                            <template #content>
                              json类型字段<br />请输入json格式数据!
                            </template>
                            <el-icon><InfoFilled /></el-icon>
                          </el-tooltip>
                          <el-tooltip
                            :content="fitem.description"
                            placement="right"
                            effect="dark"
                            v-if="fitem.description.length != 0 ? true : false"
                          >
                            <el-icon>
                              <Warning />
                            </el-icon>
                          </el-tooltip>
                        </el-space>
                      </template>
                      <el-input
                        v-model="editForm[fitem.name]"
                        style="width: 240px"
                        autosize
                        type="textarea"
                        v-if="isEdit"
                      ></el-input>
                      <el-text v-else>
                        {{ editForm[fitem.name] }}
                      </el-text>
                    </el-form-item>
                    <el-form-item
                      :label="fitem.verbose_name"
                      :prop="fitem.name"
                      v-if="['text'].indexOf(fitem.type) >>> -1 ? false : true"
                      :required="fitem.required"
                    >
                      <template #label>
                        <el-space :size="2">
                          <el-text tag="b">{{ fitem.verbose_name }}</el-text>
                          <el-tooltip
                            :content="fitem.description"
                            placement="right"
                            effect="dark"
                            v-if="fitem.description.length != 0 ? true : false"
                          >
                            <el-icon>
                              <Warning />
                            </el-icon>
                          </el-tooltip>
                        </el-space>
                      </template>
                      <el-input
                        v-model="editForm[fitem.name]"
                        style="width: 240px"
                        autosize
                        type="textarea"
                        v-if="isEdit"
                      ></el-input>
                      <el-text v-else> {{ editForm[fitem.name] }} </el-text>
                    </el-form-item>
                    <el-form-item
                      :label="fitem.verbose_name"
                      :prop="fitem.name"
                      v-if="fitem.type === 'boolean'"
                      :required="fitem.required"
                    >
                      <template #label>
                        <el-space :size="2">
                          <el-text tag="b">{{ fitem.verbose_name }}</el-text>
                          <el-tooltip
                            :content="fitem.description"
                            placement="right"
                            effect="dark"
                            v-if="fitem.description.length != 0 ? true : false"
                          >
                            <el-icon>
                              <Warning />
                            </el-icon>
                          </el-tooltip>
                        </el-space>
                      </template>
                      <el-switch
                        v-model="editForm[fitem.name]"
                        style="
                          --el-switch-on-color: #13ce66;
                          --el-switch-off-color: #ff4949;
                        "
                        :disabled="!isEdit"
                      />
                    </el-form-item>
                    <el-form-item
                      :label="fitem.verbose_name"
                      :prop="fitem.name"
                      v-if="['float'].indexOf(fitem.type) >>> -1 ? false : true"
                      :required="fitem.required"
                    >
                      <template #label>
                        <el-space :size="2">
                          <el-text
                            tag="b"
                            v-if="fitem.unit !== null ? true : false"
                            >{{
                              fitem.verbose_name + "(" + fitem.unit + ")"
                            }}</el-text
                          >
                          <el-text tag="b" v-else>{{
                            fitem.verbose_name
                          }}</el-text>
                          <el-tooltip
                            :content="fitem.description"
                            placement="right"
                            effect="dark"
                            v-if="fitem.description.length != 0 ? true : false"
                          >
                            <el-icon>
                              <Warning />
                            </el-icon>
                          </el-tooltip>
                        </el-space>
                      </template>
                      <el-input-number
                        v-model="editForm[fitem.name]"
                        :precision="2"
                        :step="1"
                        v-if="isEdit"
                      />
                      <el-text v-else>
                        {{ editForm[fitem.name] }}
                      </el-text>
                    </el-form-item>
                    <!-- 密码类型 -->
                    <el-form-item
                      :label="fitem.verbose_name"
                      :prop="fitem.name"
                      v-if="
                        ['password'].indexOf(fitem.type) >>> -1 ? false : true
                      "
                      :required="fitem.required"
                    >
                      <template #label>
                        <el-space :size="2">
                          <el-text tag="b">{{ fitem.verbose_name }}</el-text>
                          <el-tooltip
                            :content="fitem.description"
                            placement="right"
                            effect="dark"
                            v-if="fitem.description.length != 0 ? true : false"
                          >
                            <el-icon>
                              <Warning />
                            </el-icon>
                          </el-tooltip>
                        </el-space>
                      </template>
                      <el-input
                        v-model="editForm[fitem.name]"
                        style="width: 240px"
                        type="password"
                        auto-complete="new-password"
                        show-password
                        clearable
                        v-if="isEdit"
                      ></el-input>
                      <div v-else>
                        <el-text v-if="useConfigStore.isShowPass">
                          {{
                            decrypt_sm4(
                              gmConfig.key,
                              gmConfig.mode,
                              editForm[fitem.name]
                            )
                          }}
                        </el-text>
                        <div v-else>
                          <el-text v-if="editForm[fitem.name]?.length >> 0">{{
                            "*".repeat(editForm[fitem.name]?.length)
                          }}</el-text>
                          <el-text v-else></el-text>
                        </div>
                      </div>
                    </el-form-item>
                    <el-form-item
                      :label="fitem.verbose_name"
                      :prop="fitem.name"
                      v-if="
                        ['integer'].indexOf(fitem.type) >>> -1 ? false : true
                      "
                      :required="fitem.required"
                    >
                      <template #label>
                        <el-space :size="2">
                          <el-text
                            tag="b"
                            v-if="fitem.unit !== null ? true : false"
                            >{{
                              fitem.verbose_name + "(" + fitem.unit + ")"
                            }}</el-text
                          >
                          <el-text tag="b" v-else>{{
                            fitem.verbose_name
                          }}</el-text>
                          <el-tooltip
                            :content="fitem.description"
                            placement="right"
                            effect="dark"
                            v-if="fitem.description.length != 0 ? true : false"
                          >
                            <el-icon>
                              <Warning />
                            </el-icon>
                          </el-tooltip>
                        </el-space>
                      </template>
                      <el-input-number
                        v-model="editForm[fitem.name]"
                        :step="1"
                        v-if="isEdit"
                      />
                      <el-text v-else>
                        {{ editForm[fitem.name] }}
                      </el-text>
                    </el-form-item>
                    <el-form-item
                      :label="fitem.verbose_name"
                      :prop="fitem.name"
                      v-if="['date'].indexOf(fitem.type) >>> -1 ? false : true"
                      :required="fitem.required"
                    >
                      <template #label>
                        <el-space :size="2">
                          <el-text tag="b">{{ fitem.verbose_name }}</el-text>
                          <el-tooltip
                            :content="fitem.description"
                            placement="right"
                            effect="dark"
                            v-if="fitem.description.length != 0 ? true : false"
                          >
                            <el-icon>
                              <Warning />
                            </el-icon>
                          </el-tooltip>
                        </el-space>
                      </template>
                      <el-date-picker
                        v-model="editForm[fitem.name]"
                        type="date"
                        placeholder="Pick a Date"
                        format="YYYY-MM-DD"
                        value-format="YYYY-MM-DD"
                        v-if="isEdit"
                      />
                      <el-text v-else>
                        {{ editForm[fitem.name] }}
                      </el-text>
                    </el-form-item>
                    <el-form-item
                      :label="fitem.verbose_name"
                      :prop="fitem.name"
                      v-if="
                        ['datetime'].indexOf(fitem.type) >>> -1 ? false : true
                      "
                      :required="fitem.required"
                    >
                      <template #label>
                        <el-space :size="2">
                          <el-text tag="b">{{ fitem.verbose_name }}</el-text>
                          <el-tooltip
                            :content="fitem.description"
                            placement="right"
                            effect="dark"
                            v-if="fitem.description.length != 0 ? true : false"
                          >
                            <el-icon>
                              <Warning />
                            </el-icon>
                          </el-tooltip>
                        </el-space>
                      </template>
                      <el-date-picker
                        v-model="editForm[fitem.name]"
                        type="datetime"
                        placeholder="Pick a Date"
                        format="YYYY/MM/DD hh:mm:ss"
                        value-format="YYYY-MM-DD hh:mm:ss"
                        v-if="isEdit"
                      />
                      <el-text v-else>
                        {{ editForm[fitem.name] }}
                      </el-text>
                    </el-form-item>
                    <el-form-item
                      :label="fitem.verbose_name"
                      :prop="fitem.name"
                      v-if="['enum'].indexOf(fitem.type) >>> -1 ? false : true"
                      :required="fitem.required"
                    >
                      <template #label>
                        <el-space :size="2">
                          <el-text tag="b">{{ fitem.verbose_name }}</el-text>
                          <el-tooltip
                            :content="fitem.description"
                            placement="right"
                            effect="dark"
                            v-if="fitem.description.length != 0 ? true : false"
                          >
                            <el-icon>
                              <Warning />
                            </el-icon>
                          </el-tooltip>
                        </el-space>
                      </template>
                      <el-select
                        clearable
                        filterable
                        v-model="editForm[fitem.name]"
                        placeholder="请选择"
                        style="width: 240px"
                        v-if="isEdit"
                      >
                        <el-option
                          v-for="item in validationRulesEnumObject[
                            fitem.validation_rule
                          ]"
                          :key="item.value"
                          :label="item.label"
                          :value="item.value"
                        />
                      </el-select>
                      <el-text v-else>
                        {{ instanceData.fields[fitem.name]?.label }}
                      </el-text>
                    </el-form-item>
                    <el-form-item
                      :label="fitem.verbose_name"
                      :prop="fitem.name"
                      v-if="
                        ['model_ref'].indexOf(fitem.type) >>> -1 ? false : true
                      "
                      :required="fitem.required"
                    >
                      <template #label>
                        <el-space :size="2">
                          <el-text tag="b">{{ fitem.verbose_name }}</el-text>
                          <el-tooltip
                            :content="fitem.description"
                            placement="right"
                            effect="dark"
                            v-if="fitem.description.length != 0 ? true : false"
                          >
                            <el-icon>
                              <Warning />
                            </el-icon>
                          </el-tooltip>
                        </el-space>
                      </template>
                      <el-select
                        v-model="editForm[fitem.name]"
                        clearable
                        placeholder="请选择"
                        style="width: 240px"
                        filterable
                        remote
                        :remote-method="
                          (query) => filterModelRefCiData(query, fitem.name)
                        "
                        v-if="isEdit"
                      >
                        <el-option
                          v-for="(citem, cIndex) in modelRefOptions[fitem.name]"
                          :key="cIndex"
                          :label="citem.instance_name"
                          :value="citem.id"
                        />
                      </el-select>
                      <el-text v-else>
                        {{ instanceData.fields[fitem.name]?.instance_name }}
                      </el-text>
                    </el-form-item>
                  </el-col>
                </el-row>
              </el-collapse-item>
            </el-collapse>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="监控信息" name="monitor" disabled>111</el-tab-pane>
        <el-tab-pane label="关联关系" name="relations">
          <ciDataRelation
            ref="ciDataRelationRef"
            v-if="instanceData && instanceData.id"
            :instanceId="instanceData.id"
            :modelId="instanceData.model"
          />
        </el-tab-pane>
        <el-tab-pane label="变更记录" name="changelog">
          <ciDataAudit
            ref="ciDataAuditRef"
            v-if="instanceData && instanceData.id"
            :instanceId="instanceData.id"
          />
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- <div class="footer">
      <el-button @click="goBack">取消</el-button>
      <el-button type="danger" @click="deleteInstance">删除</el-button>
      <el-button type="primary" @click="saveInstance">保存</el-button>
    </div> -->
  </div>
</template>

<script lang="ts" setup>
import {
  ref,
  reactive,
  computed,
  getCurrentInstance,
  onMounted,
  nextTick,
} from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessageBox, ElMessage, ElLoading } from "element-plus";
import type { FormInstance } from "element-plus";
import { encrypt_sm4, decrypt_sm4 } from "@/utils/gmCrypto.ts";
import useConfigStore from "@/store/config";
import useModelStore from "@/store/cmdb/model";

import ciDataAudit from "@/components/cmdb/ciDataAudit.vue";
import ciDataRelation from "@/components/cmdb/ciDataRelation.vue";
const instanceId = ref(null);
const instanceData = ref({});

const modelConfigStore = useModelStore();

const modelInfo = ref({});
const validationRulesEnumObject = computed(
  () => modelConfigStore.validationRulesEnumOptionsObject
);
const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();
const configStore = useConfigStore();
const isEdit = ref(false);
const gmConfig = computed(() => configStore.gmCry);

// 表单相关
const editFormRef = ref<FormInstance>();
const editForm = reactive({
  id: null,
  instance_name: null,
});
const ciDataAuditRef = ref(null);
const activeName = ref("modelField");
const handleClick = (tab: TabsPaneContext, event: Event) => {
  if (tab.props.name == "changelog") {
    ciDataAuditRef.value!.getData();
  }
};
const activeArr = ref([0]);

// 数据
const modelRefOptions = ref({});
// const props = defineProps(["instanceId"])

// 初始化表单
const initEditForm = () => {
  editForm.id = instanceData.value.id;
  editForm.instance_name = instanceData.value.instance_name;
  Object.keys(instanceData.value.fields).forEach((item) => {
    if (modelFieldType.value.enum.includes(item)) {
      if (instanceData.value.fields[item] !== null) {
        editForm[item] = instanceData.value.fields[item].value;
      } else {
        editForm[item] = null;
      }
    } else if (modelFieldType.value.model_ref.includes(item)) {
      if (instanceData.value.fields[item] !== null) {
        // 未点击时，赋予实例初始值
        modelRefOptions.value[item] = [instanceData.value.fields[item]];
        editForm[item] = instanceData.value.fields[item].id;
      } else {
        editForm[item] = null;
      }
    } else if (modelFieldType.value.password.includes(item)) {
      if (configStore.showAllPass) {
        editForm[item] = decrypt_sm4(
          configStore.gmCry.key,
          instanceData.value.fields[item]
        );
      } else {
        editForm[item] = instanceData.value.fields[item];
      }
    } else {
      editForm[item] = instanceData.value.fields[item];
    }
  });
};
const hasUnassignedPool = computed(() => {
  return instanceData.value?.instance_group?.some((item) =>
    item.group_path.includes("空闲池")
  );
});

// 获取字段类型
const modelFieldType = computed(() => {
  let tempObj = {
    enum: [],
    boolean: [],
    model_ref: [],
    password: [],
  };

  if (modelInfo.value.field_groups) {
    modelInfo.value.field_groups.forEach((group) => {
      group.fields.forEach((field) => {
        if (field.type === "enum") {
          tempObj.enum.push(field.name);
        } else if (field.type === "boolean") {
          tempObj.boolean.push(field.name);
        } else if (field.type === "model_ref") {
          tempObj.model_ref.push(field.name);
        } else if (field.type === "password") {
          tempObj.password.push(field.name);
        }
      });
    });
  }

  return tempObj;
});
// 表单验证规则
const setFormItemRule = (rule) => {
  if (rule == "" || rule == null) return;
  // 这里需要根据实际的validationRulesObj来设置规则
  return [
    {
      pattern: new RegExp(".*"), // 简化处理，实际应使用传入的规则
      message: "不符合正则表达式",
      trigger: "blur",
    },
  ];
};

// 处理需要加密的字段
const processFieldsForSubmit = computed(() => {
  // 判断此次编辑有没有字段数据变更，只提交有变更的字段
  let tmpObj = {};

  // 遍历editForm中的所有字段
  for (let [key, value] of Object.entries(editForm)) {
    // 跳过id字段
    if (["id", "instance_name"].includes(key)) continue;

    // 比较当前值与原始值是否不同
    let originalValue = instanceData.value.fields[key];

    // 对于枚举类型字段，需要特殊处理
    if (modelFieldType.value.enum.includes(key)) {
      originalValue =
        instanceData.value.fields[key] === null
          ? null
          : instanceData.value.fields[key].value;
    }
    // 对于模型引用类型字段，需要特殊处理
    else if (modelFieldType.value.model_ref.includes(key)) {
      originalValue =
        instanceData.value.fields[key] === null
          ? null
          : instanceData.value.fields[key].id;
    }
    // 对于密码字段，如果显示的是解密后的值，则需要获取原始加密值进行比较
    else if (modelFieldType.value.password.includes(key)) {
      // 如果配置允许显示明文密码，则originalValue已经是解密后的值
      // 否则就是原始的加密值
      if (!configStore.showAllPass) {
        originalValue = instanceData.value.fields[key];
      }
    }

    // 比较值是否发生变化（考虑null、undefined和空字符串的情况）
    if (
      value !== originalValue ||
      (value === null &&
        originalValue !== null &&
        originalValue !== undefined) ||
      (value === "" &&
        originalValue !== "" &&
        originalValue !== null &&
        originalValue !== undefined)
    ) {
      // 只有当值发生变化时才添加到提交对象中
      // console.log(key, value, originalValue);

      // 如果是密码字段且有值，则进行加密
      if (
        modelFieldType.value.password.includes(key) &&
        value !== null &&
        value !== ""
      ) {
        tmpObj[key] = encrypt_sm4(
          configStore.gmCry.key,
          configStore.gmCry.mode,
          value
        );
      } else {
        tmpObj[key] = value;
      }
    }
  }

  return tmpObj;
});
const allModelFieldByNameObj = computed<any>(() => {
  return (modelInfo.value?.field_groups || []).reduce((acc, group) => {
    (group.fields || []).forEach((field) => {
      acc[field.name] = field;
    });
    return acc;
  }, {});
});
// model_ref过滤
const filterModelRefCiData = async (query, fieldName) => {
  // console.log(query, fieldName);
  const fieldConfig = allModelFieldByNameObj.value[fieldName];
  // if (query === "") return;
  // console.log(fieldConfig);

  if (!fieldConfig || !fieldConfig.ref_model) return;

  try {
    let res = await proxy.$api.getModelRefCi({
      model: fieldConfig.ref_model,
      instance_name: query ? query : undefined, // 搜索关键字
      page: 1,
      page_size: query ? 100 : 20,
    });

    // 更新对应字段的选项
    modelRefOptions.value[fieldName] = res.data.results;
  } catch (error) {
    console.error("获取model_ref数据失败:", error);
  }
};
// 编辑实例
const editAction = () => {
  isEdit.value = true;
};
const cancelAction = () => {
  isEdit.value = false;
  // 判断是否有编辑，没有则删除
  nextTick(() => {
    initEditForm();
  });
};
// 保存实例
const submitAction = async () => {
  if (!editFormRef.value) return;

  await editFormRef.value.validate(async (valid, fields) => {
    if (valid) {
      if (
        Object.keys(processFieldsForSubmit.value).length === 0 &&
        editForm.instance_name === instanceData.value.instance_name
      ) {
        ElMessage({
          showClose: true,
          message: "没有数据发生变更",
          type: "warning",
        });
        isEdit.value = false;
        return;
      }
      const loading = ElLoading.service({
        lock: true,
        text: "保存中...",
        background: "rgba(0, 0, 0, 0.7)",
      });

      try {
        let res = await proxy.$api.updateCiModelInstance({
          id: instanceData.value.id,
          model: modelInfo.value.id,
          instance_name:
            editForm.instance_name === instanceData.value.instance_name
              ? null
              : editForm.instance_name,
          fields: processFieldsForSubmit.value,
        });

        if (res.status == "200") {
          ElMessage({ type: "success", message: "保存成功" });
          isEdit.value = false;
          getCiDataInfo();
          // router.back();
        } else {
          console.log(res);
          ElMessage({
            showClose: true,
            message: "保存失败:" + JSON.stringify(res.data),
            type: "error",
          });
        }
      } catch (error) {
        console.log(error);
        ElMessage({
          showClose: true,
          message: "保存失败，请稍后重试",
          type: "error",
        });
      } finally {
        loading.close();
      }
    } else {
      ElMessage({
        showClose: true,
        message: "表单填写有误，请检查",
        type: "error",
      });
    }
  });
};

// 删除实例
const deleteInstance = () => {
  ElMessageBox.confirm("确定要删除该实例吗？此操作不可恢复", "删除实例", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      try {
        let res = await proxy.$api.deleteCiModelInstance(instanceData.value.id);
        if (res.status == 204) {
          ElMessage.success("删除成功");
          goBack();
        } else {
          ElMessage.error(`删除失败,${JSON.stringify(res.data)}`);
        }
      } catch (error) {
        ElMessage.error("删除失败，error");
      }
    })
    .catch(() => {
      // 取消删除
    });
};

// 返回
const goBack = () => {
  if (route.name.includes("cmdb_only")) {
    router.push({
      path: "/cmdb_only/cmdb/cidata",
    });
    return;
  }
  if (!isEdit.value) {
    router.push({
      path: "/cmdb/cidata",
    });
    return;
  }
  ElMessageBox.confirm("确定要离开页面吗？未保存的数据将会丢失", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(() => {
      router.push({
        path: "/cmdb/cidata",
      });
    })
    .catch(() => {
      // 取消
    });
};
// 请求
// 枚举类的字段下拉框
// 获取所有枚举类的字典
// const validationRulesObj = ref({});
// const getRules = async (params = null) => {
//   let res = await proxy.$api.getValidationRules({
//     ...params,
//     page: 1,
//     page_size: 10000,
//   });
//   // validationRules.value = res.data
//   res.data.results.forEach((item) => {
//     validationRulesObj.value[item.id] = item;
//     // validationRulesByNameObj.value[item.name] = item
//   });
//   // console.log(1111111);
//   // console.log(validationRulesObj.value);
// };
// 获取model_ref的信息
const getModelRefCiData = async (params) => {
  let res = await proxy.$api.getModelRefCi({
    model: params,
    page: 1,
    page_size: 10000,
  });
};
const getCiDataInfo = async () => {
  const res = await proxy.$api.getCiModelInstanceInfo(instanceId.value);
  if (res.status === 200) {
    instanceData.value = res.data;
  }
};
const getCiModelInfo = async () => {
  // console.log(instanceData.value.model);
  const res = await proxy.$api.getCiModel({}, instanceData.value.model);
  if (res.status === 200) {
    modelInfo.value = res.data;
  }
  // console.log(modelInfo.value);
};
const ciDataDelete = (params = null) => {
  ElMessageBox.confirm("是否确认删除?", "实例删除", {
    confirmButtonText: "确认删除",
    cancelButtonText: "取消",
    type: "warning",
    draggable: true,
  })
    .then(async () => {
      // 发起删除请求
      let res = await proxy.$api.deleteCiModelInstance(currentRow.value.id);
      //
      // let res = {status:204}
      if (res.status == 204) {
        ElMessage({
          type: "success",
          message: "删除成功",
        });
        goBack();
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
// 获取路由参数
onMounted(async () => {
  try {
    instanceId.value = route.path.split("/").at(-1);
    await getCiDataInfo();
    // 获取模型信息
    await getCiModelInfo();
    modelConfigStore.getModel();

    modelConfigStore.getValidationRules();
    // 初始化表单
    initEditForm();
  } catch (e) {
    console.log(e);
    ElMessage.error("数据加载失败", e);
    router.back();
  }
});
// 暴露方法给父组件
defineExpose({
  initEditForm,
});
</script>

<style scoped lang="scss">
.edit-page {
  padding: 20px;
  // background-color: #f5f5f5;
  min-height: 100vh;
}

.header {
  // background: white;
  flex: none;
  padding: 10px 20px;
  // margin-bottom: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.content {
  // background: white;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  // margin-bottom: 20px;
  height: 100%;
}

.footer {
  // background: white;
  padding: 10px 20px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
.group-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.group-item {
  line-height: 1.5;
}
.el-drawer__header {
  margin-bottom: 0px !important;
}

:deep(.el-transfer-panel__item).el-checkbox {
  margin-right: 10px;

  .transferLable {
    display: flex;
    justify-content: space-between !important;
  }
}

.el-transfer ::v-deep(.el-transfer-panel):first-child .sort {
  display: none;
}

.moving {
  border-bottom: 1px solid #409eff;
}

.movingTop {
  border-top: 1px solid #409eff;
}

.movingBottom {
  border-bottom: 1px solid #409eff;
}

:deep(.el-drawer__header) {
  margin-bottom: 0;
}

.footerButtonClass {
  display: flex;
  justify-content: end;
  gap: 15px;
}

.demo-tabs > .el-tabs__content {
  padding: 32px;
  color: #6b778c;
  font-size: 32px;
  font-weight: 600;
}
</style>