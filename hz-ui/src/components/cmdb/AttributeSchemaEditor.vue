<template>
  <div class="attribute-schema-editor">
    <el-table :data="attributes" style="width: 100%" v-if="editable">
      <el-table-column label="属性名" width="150">
        <template #default="scope">
          <el-input v-model="scope.row.key" placeholder="属性名"></el-input>
        </template>
      </el-table-column>
      <el-table-column label="类型" width="120">
        <template #default="scope">
          <el-select v-model="scope.row.value.type" placeholder="类型">
            <el-option label="字符串" value="string"></el-option>
          </el-select>
        </template>
      </el-table-column>

      <el-table-column label="显示名称" width="150">
        <template #default="scope">
          <el-input
            v-model="scope.row.value.verbose_name"
            placeholder="显示名称"
          ></el-input>
        </template>
      </el-table-column>
      <el-table-column
        prop="value.unit"
        label="单位"
        width="100"
        v-if="relation"
      >
        <template #default="scope">
          <el-input
            v-model="scope.row.value.unit"
            placeholder="单位"
          ></el-input> </template
      ></el-table-column>
      <el-table-column
        prop="value.default"
        label="默认值"
        width="120"
        v-if="relation"
      >
        <template #default="scope">
          <el-input v-model="scope.row.value.default" placeholder="单位" />
        </template>
      </el-table-column>
      <el-table-column label="必填" width="80">
        <template #default="scope">
          <el-checkbox v-model="scope.row.value.required"></el-checkbox>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="80">
        <template #default="scope">
          <el-button
            type="danger"
            :icon="Delete"
            link
            @click="removeAttribute(scope.$index)"
          ></el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-table :data="attributes" style="width: 100%" v-else>
      <el-table-column prop="key" label="属性名" width="150"></el-table-column>
      <el-table-column label="类型" width="120">
        <template #default="scope">
          {{ getTypeLabel(scope.row.value.type) }}
        </template>
      </el-table-column>

      <el-table-column
        prop="value.verbose_name"
        label="显示名称"
        width="150"
      ></el-table-column>
      <el-table-column
        prop="value.unit"
        label="单位"
        width="100"
        v-if="relation"
      ></el-table-column>
      <el-table-column
        prop="value.default"
        label="默认值"
        width="120"
        v-if="relation"
      ></el-table-column>
      <el-table-column label="必填" width="80">
        <template #default="scope">
          <el-tag v-if="scope.row.value.required" type="success">是</el-tag>
          <el-tag v-else>否</el-tag>
        </template>
      </el-table-column>
    </el-table>

    <div style="margin-top: 20px" v-if="editable">
      <el-button type="primary" @click="addAttribute">添加属性</el-button>
    </div>
  </div>
</template>

<script setup>
import { Delete } from "@element-plus/icons-vue";
import { useDebounceFn } from "@vueuse/core";
import { ref, watch, defineProps, defineEmits, defineModel } from "vue";
const schema = defineModel("schema");

const props = defineProps({
  editable: {
    type: Boolean,
    default: false,
  },
  relation: {
    type: Boolean,
    default: false,
  },
});

const attributes = ref([]);

const convertSchemaToArray = () => {
  attributes.value = Object.keys(schema.value).map((key) => ({
    key,
    value: { ...schema.value[key] },
  }));
};

const convertArrayToSchema = () => {
  const schema = {};
  attributes.value.forEach((attr) => {
    if (attr.key) {
      schema[attr.key] = { ...attr.value };
    }
  });
  return schema;
};

const addAttribute = () => {
  if (props.relation) {
    attributes.value.push({
      key: "",
      value: {
        type: "string",
        required: false,
        verbose_name: "",
        default: "",
      },
    });
  } else {
    attributes.value.push({
      key: "",
      value: {
        type: "string",
        required: false,
        verbose_name: "",
      },
    });
  }
};

const removeAttribute = (index) => {
  attributes.value.splice(index, 1);
};

const getTypeLabel = (type) => {
  const typeMap = {
    string: "字符串",
  };
  return typeMap[type] || type;
};
// 初始化attrributes
watch(
  () => schema.value,
  (newSchema, oldSchema) => {
    // 只有当 schema 真正发生变化时才更新 attributes
    if (JSON.stringify(newSchema) !== JSON.stringify(oldSchema)) {
      convertSchemaToArray();
    }
  },
  { deep: true, immediate: true }
);
// 父组件点击提交时，才更新schema
const updateSchema = () => {
  schema.value = convertArrayToSchema();
};
defineExpose({ updateSchema });
// const debouncedUpdateSchema = useDebounceFn(() => {
//   const newSchema = convertArrayToSchema();
//   if (JSON.stringify(newSchema) !== JSON.stringify(schema.value)) {
//     schema.value = newSchema;
//   }
// }, 900);
// // 监听 attributes 变化
// watch(
//   attributes,
//   (newAttributes, oldAttributes) => {
//     debouncedUpdateSchema();
//     console.log("222", newAttributes);
//   },
//   { deep: true }
// );
</script>

<style scoped>
.attribute-schema-editor {
  padding: 10px 0;
}
</style>