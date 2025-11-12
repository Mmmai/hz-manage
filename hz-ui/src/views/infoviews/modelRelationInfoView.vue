<template>
  <div class="relation-type-view">
    <el-card class="relation-card">
      <template #header>
        <div class="card-header">
          <el-page-header @back="goBack">
            <template #content>
              <span>关系类型详情</span>
            </template>
          </el-page-header>
          <div>
            <el-tooltip
              content="
                  
                  编辑关联关系
              "
              placement="top"
            >
              <el-button
                type="primary"
                @click="editMode = true"
                v-if="!editMode"
                >编辑</el-button
              >
            </el-tooltip>

            <el-button type="success" @click="saveRelationType" v-if="editMode"
              >保存</el-button
            >
            <el-button @click="cancelEdit" v-if="editMode">取消</el-button>
          </div>
        </div>
      </template>

      <el-form
        :model="relationData"
        label-width="120px"
        :disabled="!editMode"
        ref="formRef"
      >
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="名称">
              <el-input
                v-model="relationData.name"
                :disabled="!editMode || !isAdd"
                style="max-width: 300px"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="拓扑关系">
              <el-select
                v-model="relationData.topology_type"
                :disabled="!editMode"
                style="max-width: 300px"
              >
                <el-option label="有向" value="directed"></el-option>
                <el-option label="无向" value="undirected"></el-option>
                <el-option label="有向无环" value="daggered"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="源模型">
              <el-select
                v-model="relationData.source_model"
                :disabled="!editMode"
                clearable
                multiple
                collapse-tags
                collapse-tags-tooltip
                :max-collapse-tags="3"
                style="max-width: 300px"
              >
                <el-option
                  v-for="item in modelOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                ></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="目标模型">
              <el-select
                v-model="relationData.target_model"
                :disabled="!editMode"
                clearable
                multiple
                collapse-tags
                collapse-tags-tooltip
                :max-collapse-tags="3"
                style="max-width: 300px"
              >
                <el-option
                  v-for="item in modelOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                ></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="正向动词">
              <el-input
                v-model="relationData.forward_verb"
                :disabled="!editMode"
                style="max-width: 300px"
              ></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="反向动词">
              <el-input
                v-model="relationData.reverse_verb"
                :disabled="!editMode"
                style="max-width: 300px"
              ></el-input> </el-form-item
          ></el-col>
        </el-row>

        <el-form-item label="描述">
          <el-input
            v-model="relationData.description"
            type="textarea"
            :disabled="!editMode"
            style="max-width: 1000px"
          >
          </el-input>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 属性模式部分 -->
    <el-card class="attribute-card">
      <template #header>
        <div class="card-header">
          <span>属性模式</span>
        </div>
      </template>

      <el-tabs type="card">
        <el-tab-pane label="源属性">
          <AttributeSchemaEditor
            ref="sourceSchemaRef"
            v-model:schema="relationData.attribute_schema.source"
            :editable="editMode"
          >
          </AttributeSchemaEditor>
        </el-tab-pane>
        <el-tab-pane label="目标属性">
          <AttributeSchemaEditor
            ref="targetSchemaRef"
            v-model:schema="relationData.attribute_schema.target"
            :editable="editMode"
          >
          </AttributeSchemaEditor>
        </el-tab-pane>
        <el-tab-pane label="关系属性">
          <AttributeSchemaEditor
            :schema="relationData.attribute_schema.relation"
            ref="relationSchemaRef"
            v-model:schema="relationData.attribute_schema.relation"
            :editable="editMode"
            :relation="true"
          >
          </AttributeSchemaEditor>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import {
  ref,
  reactive,
  watch,
  onMounted,
  getCurrentInstance,
  computed,
  nextTick,
} from "vue";
import AttributeSchemaEditor from "@/components/cmdb/AttributeSchemaEditor.vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import useModelStore from "@/store/cmdb/model";
const modelConfigStore = useModelStore();
const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();
const modelOptions = computed(() => modelConfigStore.modelOptions);
const goBack = () => {
  router.push({ path: "/cmdb/cimodelManage/modelRelation" });
};
const formRef = ref(null);
const sourceSchemaRef = ref(null);
const targetSchemaRef = ref(null);
const relationSchemaRef = ref(null);

const editMode = ref(false);
const originalData = ref({});
const relationData = reactive({
  name: "",
  topology_type: "directed",
  forward_verb: "",
  reverse_verb: "",
  attribute_schema: {
    source: {},
    target: {},
    relation: {},
  },
  description: null,
  source_model: "",
  target_model: "",
});

const saveRelationType = () => {
  sourceSchemaRef.value.updateSchema();
  targetSchemaRef.value.updateSchema();
  relationSchemaRef.value.updateSchema();
  nextTick(() => {
    if (isAdd.value) {
      addRelationData();
    } else {
      updateRelationData();
    }
  });
};

const cancelEdit = () => {
  editMode.value = false;
  Object.assign(relationData, originalData.value);
};

// watch(
//   () => relationData,
//   (newVal) => {
//     Object.assign(relationData, newVal);
//   },
//   { deep: true }
// );
const relationId = ref("");
const isAdd = ref(false);
// 请求
const getRelationData = async () => {
  const res = await proxy.$api.getModelRelationDefineInfo(relationId.value);
  if (res.status === 200) {
    originalData.value = res.data;
    // Object.assign(relationData, res.data);
    // relation赋值
    relationData.name = res.data.name;
    relationData.topology_type = res.data.topology_type;
    relationData.forward_verb = res.data.forward_verb;
    relationData.reverse_verb = res.data.reverse_verb;
    relationData.attribute_schema = res.data.attribute_schema;
    relationData.description = res.data.description;
    relationData.source_model = res.data.source_model;
    relationData.target_model = res.data.target_model;
  }
};
const updateRelationData = async () => {
  const res = await proxy.$api.updateModelRelationDefine({
    id: relationId.value,
    ...relationData,
  });
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "更新成功",
    });
    editMode.value = false;
    nextTick(() => {
      getRelationData();
    });
  } else {
    ElMessage({
      type: "error",
      message: `更新失败:  ${JSON.stringify(res.data)}`,
    });
  }
};
const addRelationData = async () => {
  const res = await proxy.$api.addModelRelationDefine(relationData);
  if (res.status == 201) {
    ElMessage.success("添加成功");
    editMode.value = false;
    formRef.value.resetFields();
    nextTick(() => {
      goBack();
    });
  } else {
    ElMessage({
      type: "error",
      message: `添加失败: ${JSON.stringify(res.data)}`,
    });
  }
};
onMounted(() => {
  relationId.value = route.path.split("/").at(-1);
  if (relationId.value.includes("new")) {
    isAdd.value = true;
    editMode.value = true;
  } else {
    getRelationData();
  }
});
</script>

<style scoped>
.relation-type-view {
  padding: 5px;
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.relation-card,
.attribute-card {
  margin-bottom: 20px;
}
</style>