<template>
  <div class="tree-transfer">
    <div class="tree-transfer-panel">
      <!-- 左侧面板 -->
      <div class="panel left-panel">
        <div class="panel-header">
          <el-text tag="b">{{ titles[0] || "左侧列表" }}</el-text>
          <el-input
            v-model="leftFilterText"
            placeholder="输入关键字筛选"
            size="default"
            clearable
            class="filter-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
        <div class="panel-body">
          <el-tree
            ref="leftTreeRef"
            :data="leftTreeData"
            show-checkbox
            default-expand-all
            node-key="id"
            :props="treeProps"
            :filter-node-method="filterLeftNode"
            :check-strictly="checkStrictly"
            @check="handleLeftCheck"
            :default-checked-keys="leftCheckedKeys"
            :default-expanded-keys="defaultExpandedKeys"
            :expand-on-click-node="false"
          >
            <template #default="{ node, data }">
              <el-tooltip
                v-if="data.disabled"
                :content="data.disabledTooltip || '无法移动'"
                placement="top"
              >
                <span class="custom-tree-node">
                  <el-icon
                    class="node-icon"
                    v-if="node.childNodes && node.childNodes.length > 0"
                  >
                    <Folder />
                  </el-icon>
                  <span :class="{ 'node-disabled': data.disabled }">{{
                    node.label
                  }}</span>
                </span>
              </el-tooltip>
              <span v-else class="custom-tree-node">
                <el-icon
                  class="node-icon"
                  v-if="node.childNodes && node.childNodes.length > 0"
                >
                  <Folder />
                </el-icon>
                <span>{{ node.label }}</span>
              </span>
            </template>
          </el-tree>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="operation-buttons">
        <el-button
          type="primary"
          :icon="ArrowRight"
          circle
          size="default"
          :disabled="selectedLeftKeys.length === 0"
          @click="moveToRight"
        />
        <el-button
          type="primary"
          :icon="ArrowLeft"
          circle
          size="default"
          :disabled="selectedRightKeys.length === 0"
          @click="moveToLeft"
          style="margin-left: 0"
        />
      </div>

      <!-- 右侧面板 -->
      <div class="panel right-panel">
        <div class="panel-header">
          <el-text tag="b">{{ titles[1] || "右侧列表" }}</el-text>
          <el-input
            v-model="rightFilterText"
            placeholder="输入关键字筛选"
            size="default"
            clearable
            class="filter-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
        <div class="panel-body">
          <el-tree
            ref="rightTreeRef"
            :data="rightTreeData"
            show-checkbox
            default-expand-all
            node-key="id"
            :props="treeProps"
            :filter-node-method="filterRightNode"
            :check-strictly="checkStrictly"
            @check="handleRightCheck"
            :default-checked-keys="rightCheckedKeys"
            :default-expanded-keys="defaultExpandedKeys"
            :expand-on-click-node="false"
          >
            <template #default="{ node, data }">
              <el-tooltip
                v-if="data.disabled"
                :content="data.disabledTooltip || '无法移除'"
                placement="top"
              >
                <span class="custom-tree-node">
                  <el-icon class="node-icon">
                    <Folder
                      v-if="node.childNodes && node.childNodes.length > 0"
                    />
                    <Document v-else />
                  </el-icon>
                  <span :class="{ 'node-disabled': data.disabled }">{{
                    node.label
                  }}</span>
                </span>
              </el-tooltip>
              <span v-else class="custom-tree-node">
                <el-icon
                  class="node-icon"
                  v-if="node.childNodes && node.childNodes.length > 0"
                >
                  <Folder />
                </el-icon>
                <span>{{ node.label }}</span>
              </span>
            </template>
          </el-tree>
        </div>
      </div>
    </div>
  </div>
</template>
<script lang="ts" setup>
import { ref, computed, watch, nextTick, onMounted } from "vue";
import {
  ArrowLeft,
  ArrowRight,
  Search,
  Folder,
  Document,
} from "@element-plus/icons-vue";
import type { TreeInstance } from "element-plus";

// 定义组件属性
const props = defineProps({
  // 数据源
  data: {
    type: Array,
    default: () => [],
  },
  // 已选择的key值
  modelValue: {
    type: Array,
    default: () => [],
  },
  // 面板标题
  titles: {
    type: Array,
    default: () => ["左侧列表", "右侧列表"],
  },
  // 按钮文字
  buttonTexts: {
    type: Array,
    default: () => ["到左侧", "到右侧"],
  },
  // 是否严格模式（父子节点不互相关联）
  checkStrictly: {
    type: Boolean,
    default: false,
  },
  // 是否只返回叶子节点
  leafOnly: {
    type: Boolean,
    default: false,
  },
  // 树属性配置
  treeProps: {
    type: Object,
    default: () => ({
      children: "children",
      label: "label",
      disabled: "disabled",
    }),
  },
  // 默认展开的节点key
  defaultExpandedKeys: {
    type: Array,
    default: () => [],
  },
});

// 定义事件
const emit = defineEmits(["update:modelValue", "change"]);

// 树引用
const leftTreeRef = ref<TreeInstance>();
const rightTreeRef = ref<TreeInstance>();

// 筛选文本
const leftFilterText = ref("");
const rightFilterText = ref("");

// 选中的节点key
const selectedLeftKeys = ref([]);
const selectedRightKeys = ref([]);

// 处理左侧树选中事件
const handleLeftCheck = (data, info) => {
  selectedLeftKeys.value = info.checkedKeys;
};

// 处理右侧树选中事件
const handleRightCheck = (data, info) => {
  selectedRightKeys.value = info.checkedKeys;
};

// 获取所有叶子节点的key
const getLeafKeys = (data) => {
  const leafKeys = [];

  const traverse = (nodes) => {
    if (!nodes || !Array.isArray(nodes)) return;

    nodes.forEach((node) => {
      if (node.children && node.children.length > 0) {
        // 有子节点，继续遍历
        traverse(node.children);
      } else {
        // 叶子节点
        leafKeys.push(node.id);
      }
    });
  };

  traverse(data);
  return leafKeys;
};

// 获取所有节点的key（包括非叶子节点）
const getAllNodeKeys = (data) => {
  const allKeys = [];

  const traverse = (nodes) => {
    if (!nodes || !Array.isArray(nodes)) return;

    nodes.forEach((node) => {
      allKeys.push(node.id);
      if (node.children && node.children.length > 0) {
        // 有子节点，继续遍历
        traverse(node.children);
      }
    });
  };

  traverse(data);
  return allKeys;
};

// 过滤叶子节点（只保留叶子节点）
const filterLeafNodes = (keys, allData) => {
  // 构建完整树结构用于判断叶子节点
  const leafKeys = getLeafKeys(allData);
  return keys.filter((key) => leafKeys.includes(key));
};

// 左侧树数据（未选中的节点）
const leftTreeData = computed(() => {
  return filterTreeData(
    props.data,
    (item) => !props.modelValue.includes(item.id)
  );
});

// 右侧树数据（已选中的节点）
const rightTreeData = computed(() => {
  return filterTreeData(props.data, (item) =>
    props.modelValue.includes(item.id)
  );
});

// 左侧选中keys
const leftCheckedKeys = computed(() => {
  return selectedLeftKeys.value.filter(
    (key) => !props.modelValue.includes(key)
  );
});

// 右侧选中keys
const rightCheckedKeys = computed(() => {
  return selectedRightKeys.value.filter((key) =>
    props.modelValue.includes(key)
  );
});

// 过滤树数据
const filterTreeData = (data, filterFn) => {
  if (!data || !Array.isArray(data)) return [];

  const result = [];

  const processNode = (node) => {
    // 检查当前节点是否符合条件
    const nodeMatch = filterFn(node);

    // 创建当前节点的副本
    const newNode = { ...node };

    // 处理子节点
    let childrenMatch = false;
    if (node.children && node.children.length > 0) {
      // 递归处理子节点
      const filteredChildren = node.children
        .map((child) => processNode(child))
        .filter((child) => child !== null);
      if (filteredChildren.length > 0) {
        newNode.children = filteredChildren;
        childrenMatch = true;
      } else {
        delete newNode.children;
      }
    }

    // 如果当前节点匹配或者有子节点匹配，则保留该节点
    if (nodeMatch || childrenMatch) {
      return newNode;
    }

    // 如果当前节点和子节点都不匹配，返回null
    return null;
  };

  // 处理所有根节点
  data.forEach((node) => {
    const processedNode = processNode(node);
    if (processedNode !== null) {
      result.push(processedNode);
    }
  });

  return result;
};

// 左侧节点筛选
const filterLeftNode = (value, data) => {
  if (!value) return true;
  // 只筛选叶子节点
  if (data.children && data.children.length > 0) {
    return false;
  }
  return data.label.includes(value);
};

// 右侧节点筛选
const filterRightNode = (value, data) => {
  if (!value) return true;
  // 只筛选叶子节点
  if (data.children && data.children.length > 0) {
    return false;
  }
  return data.label.includes(value);
};
// 移动到右侧
const moveToRight = () => {
  if (selectedLeftKeys.value.length === 0) return;

  // 根据leafOnly属性决定是否只添加叶子节点
  let keysToAdd = selectedLeftKeys.value;
  if (props.leafOnly) {
    keysToAdd = filterLeafNodes(keysToAdd, props.data);
  }

  const newModelValue = [...new Set([...props.modelValue, ...keysToAdd])];
  emit("update:modelValue", newModelValue);
  emit("change", newModelValue, "right", keysToAdd);

  // 清空选中状态
  selectedLeftKeys.value = [];
  nextTick(() => {
    if (leftTreeRef.value) {
      leftTreeRef.value.setCheckedKeys([]);
    }
  });
};

// 移动到左侧
const moveToLeft = () => {
  if (selectedRightKeys.value.length === 0) return;

  // 根据leafOnly属性决定是否只移除叶子节点
  let keysToRemove = selectedRightKeys.value;
  if (props.leafOnly) {
    keysToRemove = filterLeafNodes(keysToRemove, props.data);
  }

  const newModelValue = props.modelValue.filter(
    (key) => !keysToRemove.includes(key)
  );
  emit("update:modelValue", newModelValue);
  emit("change", newModelValue, "left", keysToRemove);

  // 清空选中状态
  selectedRightKeys.value = [];
  nextTick(() => {
    if (rightTreeRef.value) {
      rightTreeRef.value.setCheckedKeys([]);
    }
  });
};

// 监听筛选文本变化
watch(leftFilterText, (val) => {
  if (leftTreeRef.value) {
    leftTreeRef.value.filter(val);
  }
});

watch(rightFilterText, (val) => {
  if (rightTreeRef.value) {
    rightTreeRef.value.filter(val);
  }
});

// 监听modelValue变化，更新选中状态
watch(
  () => props.modelValue,
  () => {
    nextTick(() => {
      if (leftTreeRef.value) {
        leftTreeRef.value.setCheckedKeys(leftCheckedKeys.value);
      }
      if (rightTreeRef.value) {
        rightTreeRef.value.setCheckedKeys(rightCheckedKeys.value);
      }
    });
  },
  { deep: true }
);

// 组件挂载后初始化
onMounted(() => {
  nextTick(() => {
    if (leftTreeRef.value) {
      leftTreeRef.value.setCheckedKeys(leftCheckedKeys.value);
    }
    if (rightTreeRef.value) {
      rightTreeRef.value.setCheckedKeys(rightCheckedKeys.value);
    }
  });
});
</script>
<style scoped>
.tree-transfer {
  width: 100%;
}

.tree-transfer-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.panel {
  flex: 1;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  height: 750px;
  background-color: var(--el-bg-color);
}

.panel-header {
  padding: 12px 15px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--el-bg-color);
}

.panel-header span {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.filter-input {
  width: 180px;
}

.panel-body {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
}

.operation-buttons {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 0 15px;
}

.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  font-size: 14px;
}

.node-icon {
  margin-right: 5px;
  width: 16px;
  height: 16px;
  color: #909399;
}

.node-disabled {
  color: #c0c4cc;
  cursor: not-allowed;
}

:deep(.el-tree-node__content) {
  height: 32px;
}

:deep(.el-tree-node__expand-icon) {
  padding: 4px;
}

:deep(.el-checkbox) {
  margin-right: 8px;
}
</style>