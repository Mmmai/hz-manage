<template>
  <div class="edit-page">
    <div class="header">
      <el-page-header @back="goBack">
        <template #content>
          <span>编辑实例</span>
        </template>
      </el-page-header>
    </div>

    <div class="content">
      <el-tabs v-model="activeName" type="card" class="demo-tabs">
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
            <el-descriptions title="实例信息" :column="2">
              <el-descriptions-item label="唯一标识">
                {{ editForm.instance_name }}
              </el-descriptions-item>
              <el-descriptions-item label="所属分组">
                <el-text
                  :key="igIndex"
                  v-for="(igItem, igIndex) in instanceData?.instance_group"
                >
                  {{ igItem.group_path }}
                </el-text>
              </el-descriptions-item>
            </el-descriptions>

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
                style="width: 240px"
                :disabled="true"
              />
            </el-form-item>

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
                <el-row style="margin-left: 30px">
                  <el-col v-for="(fitem, findex) in item.fields" :span="12">
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
                      ></el-input>
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
                      ></el-input>
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
                      ></el-input>
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
                      />
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
                      ></el-input>
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
                      />
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
                      />
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
                      />
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
                        v-model="editForm[fitem.name]"
                        placeholder="请选择"
                        style="width: 240px"
                      >
                        <el-option
                          v-for="item in enumOptionObj[fitem.validation_rule]"
                          :key="item.value"
                          :label="item.label"
                          :value="item.value"
                        />
                      </el-select>
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
                      >
                        <el-option
                          v-for="(citem, cIndex) in modelRefOptions[fitem.name]"
                          :key="cIndex"
                          :label="citem.label"
                          :value="citem.value"
                        />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>
              </el-collapse-item>
            </el-collapse>
          </el-form>
        </el-tab-pane>

        <el-tab-pane
          label="变更记录"
          name="changelog"
          v-if="instanceData && instanceData.id"
        >
          <ciDataAudit ref="ciDataAuditRef" :instanceId="instanceData.id" />
        </el-tab-pane>
      </el-tabs>
    </div>

    <div class="footer">
      <el-button @click="goBack">取消</el-button>
      <el-button type="danger" @click="deleteInstance">删除</el-button>
      <el-button type="primary" @click="saveInstance">保存</el-button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, getCurrentInstance, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessageBox, ElMessage, ElLoading } from "element-plus";
import type { FormInstance } from "element-plus";
import { encrypt_sm4, decrypt_sm4 } from "@/utils/gmCrypto.ts";
import useConfigStore from "@/store/config";
import ciDataAudit from "./ciDataAudit.vue";

const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();
const configStore = useConfigStore();

// 表单相关
const editFormRef = ref<FormInstance>();
const editForm = reactive({
  instance_name: null,
});

const activeName = ref("modelField");
const activeArr = ref([0]);

// 数据
const instanceData = ref({});
const modelInfo = ref({});
const enumOptionObj = ref({});
const modelRefOptions = ref({});

// 获取路由参数
onMounted(() => {
  try {
    const data = JSON.parse(route.query.data);
    instanceData.value = data;

    modelInfo.value = JSON.parse(route.query.modelInfo);
    enumOptionObj.value = JSON.parse(route.query.enumOptionObj);
    modelRefOptions.value = JSON.parse(route.query.modelRefOptions);

    // 初始化表单
    initEditForm();
  } catch (e) {
    ElMessage.error("数据加载失败");
    router.back();
  }
});

// 初始化表单
const initEditForm = () => {
  Object.keys(instanceData.value).forEach((item) => {
    if (item === "id" || item === "instance_group") return;

    if (modelInfo.value.field_groups) {
      const modelFieldType = getModelFieldType();

      if (modelFieldType.model_ref.indexOf(item) !== -1) {
        if (instanceData.value[item] !== null) {
          editForm[item] = instanceData.value[item].id;
        } else {
          editForm[item] = instanceData.value[item];
        }
      } else if (modelFieldType.password.indexOf(item) !== -1) {
        if (configStore.showAllPass) {
          editForm[item] = decrypt_sm4(
            configStore.gmCry.key,
            configStore.gmCry.mode,
            instanceData.value[item]
          );
        } else {
          editForm[item] = instanceData.value[item];
        }
      } else {
        editForm[item] = instanceData.value[item];
      }
    }
  });
};

// 获取字段类型
const getModelFieldType = () => {
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
};

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
  let tmpObj = Object.assign({}, editForm);
  delete tmpObj.instance_name;

  const modelFieldType = getModelFieldType();

  for (let [ckey, cvalue] of Object.entries(tmpObj)) {
    if (cvalue === null || cvalue === "") continue;
    if (modelFieldType.password.indexOf(ckey) !== -1) {
      // 加密密码字段
      tmpObj[ckey] = encrypt_sm4(
        configStore.gmCry.key,
        configStore.gmCry.mode,
        cvalue
      );
    }
  }
  return tmpObj;
});

// 保存实例
const saveInstance = async () => {
  if (!editFormRef.value) return;

  await editFormRef.value.validate(async (valid, fields) => {
    if (valid) {
      const loading = ElLoading.service({
        lock: true,
        text: "保存中...",
        background: "rgba(0, 0, 0, 0.7)",
      });

      try {
        let res = await proxy.$api.updateCiModelInstance({
          id: instanceData.value.id,
          model: route.params.modelId,
          update_user: proxy.$store.state.username,
          fields: processFieldsForSubmit.value,
        });

        if (res.status == "200") {
          ElMessage({ type: "success", message: "保存成功" });
          router.back();
        } else {
          ElMessage({
            showClose: true,
            message: "保存失败:" + JSON.stringify(res.data),
            type: "error",
          });
        }
      } catch (error) {
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
          router.back();
        } else {
          ElMessage.error("删除失败");
        }
      } catch (error) {
        ElMessage.error("删除失败，请稍后重试");
      }
    })
    .catch(() => {
      // 取消删除
    });
};

// 返回
const goBack = () => {
  ElMessageBox.confirm("确定要离开页面吗？未保存的数据将会丢失", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(() => {
      window.close();
    })
    .catch(() => {
      // 取消
    });
};

// 暴露方法给父组件
defineExpose({
  initEditForm,
});
</script>

<style scoped lang="scss">
.edit-page {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.header {
  background: white;
  padding: 16px 24px;
  margin-bottom: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.content {
  background: white;
  padding: 24px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.footer {
  background: white;
  padding: 16px 24px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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