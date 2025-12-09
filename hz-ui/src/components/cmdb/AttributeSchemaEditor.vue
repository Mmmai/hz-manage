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
            <el-option label="浮点数" value="float"></el-option>
            <el-option label="整数" value="integer"></el-option>
            <el-option label="枚举类" value="enum" v-if="relation"></el-option>
          </el-select>
        </template>
      </el-table-column>

      <el-table-column label="显示名称" width="200">
        <template #default="scope">
          <el-input
            v-if="scope.row.value.type !== 'enum'"
            v-model="scope.row.value.verbose_name"
            placeholder="显示名称"
          ></el-input>
          <el-select
            v-else
            v-model="scope.row.value.verbose_name"
            placeholder="选择枚举规则"
          >
            <el-option
              v-for="(item, index) in props.validationRulesOptions"
              :key="item.index"
              :label="item.label"
              :value="item.label"
            ></el-option>
          </el-select>
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
        width="150"
        v-if="relation"
      >
        <template #default="scope">
          <el-input
            v-model="scope.row.value.default"
            placeholder="默认值"
            v-if="scope.row.value.type !== 'enum'"
          />
          <el-select
            v-else
            v-model="scope.row.value.default"
            placeholder="默认值"
          >
            <el-option
              v-for="(item, index) in props.validationRulesEnumOptionsObject[
                findLabelFromRules(scope.row.value.verbose_name)
              ]"
              :key="item.index"
              :label="item.label"
              :value="item.value"
            ></el-option>
          </el-select>
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
      >
        <template #default="scope">
          <span v-if="scope.row.value.type !== 'enum'">{{
            scope.row.value.default
          }}</span>
          <span v-else>{{ formatDefaultValue(scope.row) }}</span>
        </template>
      </el-table-column>
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
  validationRulesOptions: {
    type: Array,
    default: () => [],
  },
  validationRulesEnumOptionsObject: {
    type: Object,
    default: () => {},
  },
  validationRulesObjectById: {
    type: Object,
    default: () => {},
  },
});

const attributes = ref([]);

const findLabelFromRules = (rules) => {
  if (rules === undefined) return "";
  return props.validationRulesOptions.filter((item) => item.label === rules)[0]
    ?.value;
};
const formatDefaultValue = (row) => {
  try {
    const validationRule = row.value.validation_rule;
    const ruleObj = props.validationRulesObjectById[validationRule];
    // 检查规则对象和rule属性是否存在
    if (!ruleObj || !ruleObj.rule) {
      return undefined;
    }

    // 解析JSON并获取默认值
    const parsedRule = JSON.parse(ruleObj.rule);
    return parsedRule[row.value.default];
  } catch (error) {
    // 如果解析失败或其他错误，返回undefined
    console.warn("Failed to parse validation rule:", error);
    return undefined;
  }
};
const convertSchemaToArray = () => {
  if (schema.value === undefined && !schema) return;
  attributes.value = Object.keys(schema.value).map((key) => {
    if (props.relation && schema.value[key].type == "enum") {
      // 确保即使第一次也能正确获取 validation_rule
      const validationRule = findLabelFromRules(schema.value[key].verbose_name);
      return {
        key,
        value: {
          ...schema.value[key],
          validation_rule: validationRule,
        },
      };
    } else
      return {
        key,
        value: { ...schema.value[key] },
      };
  });
};

const convertArrayToSchema = () => {
  const _newSchema = {};
  attributes.value.forEach((attr) => {
    if (attr.key) {
      _newSchema[attr.key] = { ...attr.value };
    }
  });
  return _newSchema;
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
    convertSchemaToArray();
  },
  { deep: true, immediate: true }
);

// 监听验证规则的变化，确保 enum 类型字段能及时更新
watch(
  () => props.validationRulesOptions,
  (newVal, oldVal) => {
    if (props.relation && newVal && newVal.length > 0) {
      // 更新现有的 enum 属性的 validation_rule
      attributes.value = attributes.value.map((attr) => {
        if (attr.value.type === "enum") {
          const validationRule = findLabelFromRules(attr.value.verbose_name);
          return {
            ...attr,
            value: {
              ...attr.value,
              validation_rule: validationRule,
            },
          };
        }
        return attr;
      });
    }
  },
  { deep: true }
);

// 父组件点击提交时，才更新schema
const updateSchema = () => {
  // 在更新前再次确保所有 enum 类型都有正确的 validation_rule
  if (props.relation) {
    attributes.value = attributes.value.map((attr) => {
      if (attr.value.type === "enum" && !attr.value.validation_rule) {
        const validationRule = findLabelFromRules(attr.value.verbose_name);
        return {
          ...attr,
          value: {
            ...attr.value,
            validation_rule: validationRule,
          },
        };
      }
      return attr;
    });
  }

  schema.value = convertArrayToSchema();
};

defineExpose({ updateSchema });
</script>

<style scoped>
.attribute-schema-editor {
  padding: 10px 0;
}
</style>