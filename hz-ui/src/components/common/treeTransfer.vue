<template>
  <div class="tree-transfer">
    <div class="tree-transfer-panel">
      <!-- 左侧面板 -->
      <div class="panel left-panel">
        <div class="panel-header">
          <el-text tag="b"
            >{{ titles[0] || "左侧列表" }} ({{ leftTreeDataCount }})</el-text
          >
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
            :data="leftUniqueKeyTreeData"
            show-checkbox
            default-expand-all
            node-key="uniqueKey"
            :props="treeProps"
            :filter-node-method="filterLeftNode"
            :check-strictly="checkStrictly"
            @check="handleLeftCheck"
            :default-checked-keys="leftUniqueCheckedKeys"
            :default-expanded-keys="defaultExpandedKeys"
            :expand-on-click-node="false"
            :class="{ 'tree-disabled': disabled }"
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
          <el-text tag="b"
            >{{ titles[1] || "右侧列表" }} ({{ rightTreeDataCount }})</el-text
          >
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
            :data="rightUniqueKeyTreeData"
            show-checkbox
            default-expand-all
            node-key="uniqueKey"
            :props="treeProps"
            :filter-node-method="filterRightNode"
            :check-strictly="checkStrictly"
            @check="handleRightCheck"
            :default-checked-keys="rightUniqueCheckedKeys"
            :default-expanded-keys="defaultExpandedKeys"
            :expand-on-click-node="false"
            :class="{ 'tree-disabled': disabled }"
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
  hideFullyAssignedParents: {
    type: Boolean,
    default: false,
  },
  // 是否禁用整个组件
  disabled: {
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

// 选中的节点key（原始ID）
const selectedLeftKeys = ref([]);
const selectedRightKeys = ref([]);

// 生成具有唯一key的树数据
const generateUniqueKeyTreeData = (data, prefix = "") => {
  if (!data || !Array.isArray(data)) return [];

  const result = [];

  const processNode = (node, index, parentPath = "") => {
    // 创建当前节点的副本
    const newNode = { ...node };

    // 生成唯一key: 路径+索引+原始ID
    const uniqueKey = `${parentPath}${index}-${node.id}`;
    newNode.uniqueKey = uniqueKey;

    // 处理子节点
    if (node.children && node.children.length > 0) {
      newNode.children = node.children.map((child, childIndex) =>
        processNode(child, childIndex, `${uniqueKey}-`)
      );
    }

    return newNode;
  };

  // 处理所有根节点
  data.forEach((node, index) => {
    const processedNode = processNode(node, index, prefix);
    result.push(processedNode);
  });

  return result;
};

// 从唯一key树数据中提取原始ID
const extractOriginalIds = (uniqueKeys, uniqueKeyTreeData) => {
  const originalIds = [];

  // 遍历唯一key树数据，查找对应的原始ID
  const traverse = (nodes) => {
    if (!nodes || !Array.isArray(nodes)) return;

    nodes.forEach((node) => {
      if (uniqueKeys.includes(node.uniqueKey)) {
        originalIds.push(node.id);
      }

      if (node.children && node.children.length > 0) {
        traverse(node.children);
      }
    });
  };

  traverse(uniqueKeyTreeData);
  return [...new Set(originalIds)]; // 去重
};

// 获取所有叶子节点的唯一key
const getLeafUniqueKeys = (data) => {
  const leafKeys = [];

  const traverse = (nodes) => {
    if (!nodes || !Array.isArray(nodes)) return;

    nodes.forEach((node) => {
      if (!node.children || node.children.length === 0) {
        // 叶子节点
        leafKeys.push(node.uniqueKey);
      } else if (node.children && node.children.length > 0) {
        // 有子节点，继续遍历
        traverse(node.children);
      }
    });
  };

  traverse(data);
  return leafKeys;
};

// 获取所有非disabled的叶子节点key（去重）
const getUniqueNonDisabledLeafKeys = (data) => {
  const leafKeys = new Set();

  const traverse = (nodes) => {
    if (!nodes || !Array.isArray(nodes)) return;

    nodes.forEach((node) => {
      if (!node.children || node.children.length === 0) {
        // 叶子节点，且未被禁用
        if (!node.disabled) {
          leafKeys.add(node.id);
        }
      } else if (node.children && node.children.length > 0) {
        // 有子节点，继续遍历
        traverse(node.children);
      }
    });
  };

  traverse(data);
  return Array.from(leafKeys);
};

// 左侧唯一key树数据
const leftUniqueKeyTreeData = computed(() => {
  return generateUniqueKeyTreeData(leftTreeData.value, "left-");
});

// 右侧唯一key树数据
const rightUniqueKeyTreeData = computed(() => {
  return generateUniqueKeyTreeData(rightTreeData.value, "right-");
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

// 新增：过滤树数据（增强版）- 支持隐藏所有子节点都在右侧的父节点
const filterTreeDataAdvanced = (
  data,
  filterFn,
  hideFullyAssignedParents = false,
  modelValue = []
) => {
  if (!data || !Array.isArray(data)) return [];

  const result = [];

  // 获取所有叶子节点
  const leafKeys = getLeafKeys(data);

  const processNode = (node) => {
    // 检查当前节点是否符合条件
    const nodeMatch = filterFn(node);

    // 创建当前节点的副本
    const newNode = { ...node };
    // 处理子节点
    let childrenMatch = false;
    let allLeafChildrenInRight = false;

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
      // 检查是否所有叶子节点子节点都在右侧（即所有叶子节点都被选中）
      if (hideFullyAssignedParents) {
        // 只考虑叶子节点，因为非叶子节点是否在右侧不影响是否显示父节点
        const descendantLeafKeys = getLeafKeys([node]);
        // 确保descendantLeafKeys不为空再进行every检查
        allLeafChildrenInRight =
          descendantLeafKeys.length > 0 &&
          descendantLeafKeys.every((key) => modelValue.includes(key));
      }
    }
    // 如果启用了隐藏完全分配的父节点且所有叶子节点子节点都在右侧，则不显示该父节点
    if (hideFullyAssignedParents && allLeafChildrenInRight) {
      return null;
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

// 左侧树数据（未选中的节点）
const leftTreeData = computed(() => {
  // 使用新的高级过滤函数，传入props.hideFullyAssignedParents参数控制是否隐藏完全分配的父节点
  if (props.hideFullyAssignedParents) {
    return filterTreeDataAdvanced(
      props.data,
      (item) => !props.modelValue.includes(item.id),
      true,
      props.modelValue
    );
  } else {
    return filterTreeData(
      props.data,
      (item) => !props.modelValue.includes(item.id)
    );
  }
});

// 右侧树数据（已选中的节点）
const rightTreeData = computed(() => {
  // 右侧树数据不需要隐藏完全分配的父节点的功能，所以直接使用原始的filterTreeData
  return filterTreeData(props.data, (item) =>
    props.modelValue.includes(item.id)
  );
});

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

// 计算左侧树数据数量
const leftTreeDataCount = computed(() => {
  if (props.leafOnly) {
    // 只统计非disabled的叶子节点数量（去重）
    const uniqueLeafKeys = getUniqueNonDisabledLeafKeys(leftTreeData.value);
    return uniqueLeafKeys.length;
  } else {
    // 统计所有非disabled节点数量
    const countNodes = (nodes) => {
      if (!nodes || !Array.isArray(nodes)) return 0;
      return nodes.reduce((count, node) => {
        // 如果节点被禁用，则不计入统计
        if (node.disabled) return count + countNodes(node.children);
        return count + 1 + countNodes(node.children);
      }, 0);
    };
    return countNodes(leftTreeData.value);
  }
});

// 计算右侧树数据数量
const rightTreeDataCount = computed(() => {
  if (props.leafOnly) {
    // 只统计非disabled的叶子节点数量（去重）
    const uniqueLeafKeys = getUniqueNonDisabledLeafKeys(rightTreeData.value);
    return uniqueLeafKeys.length;
  } else {
    // 统计所有非disabled节点数量
    const countNodes = (nodes) => {
      if (!nodes || !Array.isArray(nodes)) return 0;
      return nodes.reduce((count, node) => {
        // 如果节点被禁用，则不计入统计
        if (node.disabled) return count + countNodes(node.children);
        return count + 1 + countNodes(node.children);
      }, 0);
    };
    return countNodes(rightTreeData.value);
  }
});

// 左侧选中keys（唯一key）
const leftUniqueCheckedKeys = computed(() => {
  // 需要将原始ID转换为唯一key
  const uniqueKeys = [];
  const traverse = (nodes) => {
    if (!nodes || !Array.isArray(nodes)) return;

    nodes.forEach((node) => {
      if (selectedLeftKeys.value.includes(node.id)) {
        uniqueKeys.push(node.uniqueKey);
      }

      if (node.children && node.children.length > 0) {
        traverse(node.children);
      }
    });
  };

  traverse(leftUniqueKeyTreeData.value);
  return uniqueKeys;
});

// 右侧选中keys（唯一key）
const rightUniqueCheckedKeys = computed(() => {
  // 需要将原始ID转换为唯一key
  const uniqueKeys = [];
  const traverse = (nodes) => {
    if (!nodes || !Array.isArray(nodes)) return;

    nodes.forEach((node) => {
      if (selectedRightKeys.value.includes(node.id)) {
        uniqueKeys.push(node.uniqueKey);
      }

      if (node.children && node.children.length > 0) {
        traverse(node.children);
      }
    });
  };

  traverse(rightUniqueKeyTreeData.value);
  return uniqueKeys;
});

// 处理左侧树选中事件
const handleLeftCheck = (data, info) => {
  if (props.disabled) return;
  console.log(data);
  // 从唯一key提取原始ID
  selectedLeftKeys.value = extractOriginalIds(
    info.checkedKeys,
    leftUniqueKeyTreeData.value
  );
};

// 处理右侧树选中事件
const handleRightCheck = (data, info) => {
  if (props.disabled) return;
  console.log("handleRightCheck", rightTreeRef.value!.getCurrentNode());
  console.log(data);
  console.log(info);
  // 从唯一key提取原始ID
  selectedRightKeys.value = extractOriginalIds(
    info.checkedKeys,
    rightUniqueKeyTreeData.value
  );
};

// 过滤叶子节点（只保留叶子节点）
const filterLeafNodes = (keys, allData) => {
  // 构建完整树结构用于判断叶子节点
  const leafKeys = getLeafKeys(allData);
  return keys.filter((key) => leafKeys.includes(key));
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
        leftTreeRef.value.setCheckedKeys(leftUniqueCheckedKeys.value);
      }
      if (rightTreeRef.value) {
        rightTreeRef.value.setCheckedKeys(rightUniqueCheckedKeys.value);
      }
    });
  },
  { deep: true }
);

// 组件挂载后初始化
onMounted(() => {
  nextTick(() => {
    if (leftTreeRef.value) {
      leftTreeRef.value.setCheckedKeys(leftUniqueCheckedKeys.value);
    }
    if (rightTreeRef.value) {
      rightTreeRef.value.setCheckedKeys(rightUniqueCheckedKeys.value);
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
/* 添加禁用状态的样式 */
:deep(.tree-disabled .el-tree-node__content) {
  color: #c0c4cc;
  cursor: not-allowed;
  pointer-events: none;
}

:deep(.tree-disabled .el-checkbox) {
  pointer-events: none;
}

:deep(.tree-disabled .el-tree-node__expand-icon) {
  pointer-events: none;
}
</style>