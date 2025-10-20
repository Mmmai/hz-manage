<template>
  <div class="zt-tree-transfer">
    <!-- 左边 -->
    <div class="left-content">
      <div class="list">
        <div class="left_lowline">
          <el-checkbox
            v-model="isCheckedAllLeft"
            :disabled="isLeftCheckAllBoxDisabled"
            label=""
            size="large"
            @change="handleLeftAllCheck"
          />
          <p class="left_title">
            {{ leftTitle }}
          </p>
        </div>
        <!-- 搜索 -->
        <div class="left_input">
          <el-input
            v-model="leftFilterText"
            :prefix-icon="Search"
            class="w-50 m-2"
            placeholder="搜索"
            clearable
          />
        </div>
        <div class="left-tree">
          <el-tree
            ref="leftTreeRef"
            v-slot="{ node, data }"
            :check-on-click-node="checkOnClickNode"
            :data="leftTreeData"
            :default-expand-all="defaultExpandAll"
            :expand-on-click-node="expandOnClickNode"
            :filter-node-method="filterLeftNode"
            :lazy="lazy"
            :load="handleLoadNode"
            :node-key="nodeKey"
            :props="defaultProps"
            highlight-current
            show-checkbox
            @check-change="handleLeftCheckChange"
          />
        </div>
      </div>
    </div>
    <!-- 中间按钮 -->
    <div class="btn-div">
      <div class="btn-item" @click="toRight()">
        <el-button
          :disabled="!currentLeftUseableNodes.length"
          :icon="ArrowRight"
          size="large"
          type="primary"
        />
      </div>
      <div class="btn-item" @click="toLeft()">
        <el-button
          :disabled="isToLeftBtnDisabled"
          :icon="ArrowLeft"
          size="large"
          type="primary"
        />
      </div>
    </div>
    <!-- 右边 -->
    <div class="righ-content">
      <div class="list">
        <div class="left_lowline">
          <el-checkbox
            v-model="isCheckedAllRight"
            :disabled="isRightCheckAllBoxDisabled"
            label=""
            size="large"
            @change="handleRightAllCheck"
          />
          <p class="left_title">
            {{ rightTitle }}
          </p>
        </div>
        <!-- 搜索 -->
        <div class="left_input">
          <el-input
            v-model="rightFilterText"
            :prefix-icon="Search"
            class="w-50 m-2"
            placeholder="搜索"
            clearable
          />
        </div>

        <!--    右侧数据展示格式为list时    -->
        <div v-if="isToList">
          <!--   根据[props.nodeKey]排序  ；  根据rightFilterText进行过滤显示    -->
          <div
            v-for="(item, index) in sortRightListByKey().filter((item) =>
              item[defaultProps.label].includes(rightFilterText)
            )"
            v-if="
              sortRightListByKey().filter((item) =>
                item[defaultProps.label].includes(rightFilterText)
              ).length
            "
            :key="index"
            class="right_item"
          >
            <!-- 检查是否有名为 "right-item" 的插槽内容 -->
            <slot
              v-if="$slots['right-item']"
              :index="index"
              :item="item"
              name="right-item"
            ></slot>
            <!-- 如果没有，则显示默认内容 -->
            <div v-else>
              <el-checkbox
                v-model="item.checked"
                :false-label="false"
                :true-label="true"
                :value="item[nodeKey]"
              >
                {{ item[defaultProps.label] }}
              </el-checkbox>
            </div>
          </div>

          <div v-else style="padding: 10px">
            <el-text type="info"> 暂无数据 </el-text>
          </div>
        </div>

        <!--    右侧数据展示格式为tree时    -->
        <div v-else class="right-tree">
          <el-tree
            ref="rightTreeRef"
            v-slot="{ node, data }"
            :check-on-click-node="checkOnClickNode"
            :data="rightTreeData"
            :default-expand-all="defaultExpandAll"
            :expand-on-click-node="expandOnClickNode"
            :filter-node-method="filterRightNode"
            :node-key="nodeKey"
            :props="defaultProps"
            highlight-current
            show-checkbox
            @check-change="handleRightCheckChange"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed, nextTick, ref, watch } from "vue";
import { ArrowLeft, ArrowRight, Search } from "@element-plus/icons-vue";

/* 定义props */
const props: TreeTransferProps = defineProps({
  // 主键
  nodeKey: {
    type: String,
    default: "id",
  },
  // 左侧标题
  leftTitle: {
    type: String,
    default: () => {
      return "全部列表";
    },
  },
  // 右侧标题
  rightTitle: {
    type: String,
    default: () => {
      return "已选列表";
    },
  },
  // 是否开启懒加载
  lazy: { type: Boolean, default: false },
  // 懒加载时，加载数据的方法
  loadMethod: { type: Function, required: false },
  // tree绑定的props
  defaultProps: {
    type: Object,
    default: () => ({
      label: "label",
      children: "children",
      disabled: "disabled",
    }),
  },
  // 左侧树结构数据
  leftData: {
    type: Array,
    default: () => {
      return [];
    },
  },
  // 默认选中的数据的ids，显示在右侧列表
  defaultSelectionKeys: {
    type: Array,
    default: () => {
      return [];
    },
  },
  // 右侧数据是否按顺序排序 仅在平铺展开是有效  只支持按住键正序排序
  isSort: {
    type: Boolean,
  },
  defaultExpandAll: {
    type: Boolean,
    default: false,
  },
  // 是否在点击节点的时候选中节点，默认值为 false，即只有在点击复选框时才会选中节点。
  checkOnClickNode: {
    type: Boolean,
    default: false,
  },
  // 是否在点击节点的时候展开或者收缩节点， 默认值为 true，如果为 false，则只有点箭头图标的时候才会展开或者收缩节点。
  expandOnClickNode: {
    type: Boolean,
    default: true,
  },
  // 选择右侧所选数据的展示类型，默认是tree，true时为list
  isToList: {
    type: Boolean,
    default: false,
  },
}); // 又侧筛选条件

/* 定义emit */
const emit = defineEmits(["checkVal"]);

/**
 * 定义props类型
 */
export interface TreeTransferProps {
  nodeKey: any;
  leftTitle: any;
  rightTitle: any;
  defaultProps: any;
  leftData: any;
  defaultSelectionKeys: any;
  isSort: boolean;
  defaultExpandAll: Array<any>;
  checkOnClickNode: boolean;
  expandOnClickNode: boolean;
  isToList: any;
  loadMethod: Function;
  lazy: boolean;
}

const isCheckedAllLeft = ref(false); // 左侧全选框是否选中
const isCheckedAllRight = ref(false); // 右侧全选框是否选中

const isLeftCheckAllBoxDisabled = ref(false); // 左侧全选框是否禁用
const isRightCheckAllBoxDisabled = ref(false); // 右侧全选框是否禁用

const leftTreeRef = ref(); // 左侧树ref
const rightTreeRef = ref(); // 右侧树ref

const leftFilterText = ref(""); // 左侧筛选条件
const rightFilterText = ref("");
const leftTreeData = ref([]); // 左侧tree数据
// 用于在右侧显示的数据列表
const rightData = ref([]); // 右侧列表结构数据
const rightTreeData = ref([]); // 右侧树结构数据

// 数组打平
const flattenTree = (treeData: any[], defaultProps: any): any[] => {
  let flatData: any[] = [];
  treeData.forEach((node) => {
    flatData.push(node);
    if (node[defaultProps.children] && node[defaultProps.children].length) {
      flatData = flatData.concat(
        flattenTree(node[defaultProps.children], defaultProps)
      );
    }
  });
  return flatData;
};

// 校验树是否全选
const checkedAllTrue = (
  treeRef: any,
  treeData: any[],
  nodeKey: any,
  defaultProps: any
): boolean => {
  // 校验是否全选
  const allKeys: string[] = treeRef.getCheckedKeys();
  const allNodes: any[] = flattenTree(treeData, defaultProps);
  const allKeysSet: Set<string> = new Set(allKeys);
  const allNodesSet: Set<string> = new Set(
    allNodes.map((node) => node[nodeKey])
  );

  return (
    allKeysSet.size === allNodesSet.size &&
    [...allKeysSet].every((key) => allNodesSet.has(key))
  );
};

// 深拷贝
const deepClone = (obj: any): any => {
  // 判断拷贝的obj是对象还是数组
  const objClone: any = Array.isArray(obj) ? [] : {};
  if (obj && typeof obj === "object") {
    // obj不能为空，并且是对象或者是数组 因为null也是object
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        if (obj[key] && typeof obj[key] === "object") {
          // obj里面属性值不为空并且还是对象，进行深度拷贝
          objClone[key] = deepClone(obj[key]); // 递归进行深度的拷贝
        } else {
          objClone[key] = obj[key]; // 直接拷贝
        }
      }
    }
  }
  return objClone;
};

// 校验是否树节点是否全部禁用 nodes: []
const checkAllDisabled = (nodes: any[], defaultProps: any): boolean => {
  if (!(nodes && Array.isArray(nodes))) return false;

  for (const node of nodes) {
    // 如果当前节点的disabled不是true，则直接返回false
    if (!node[defaultProps.disabled]) {
      return false;
    }
    // 如果当前节点有子节点，则递归检查子节点
    if (node[defaultProps.children]?.length) {
      const childrenAreDisabled = checkAllDisabled(
        node[defaultProps.children],
        defaultProps
      );
      // 如果子节点中有任何disabled不是true，则返回false
      if (!childrenAreDisabled) {
        return false;
      }
    }
  }
  // 如果所有节点的disabled都是true，则返回true
  return true;
};

// 设置数组的某个字段值为某个参数
const setFieldValue = (
  array: any[],
  field: string,
  value: any,
  defaultProps: any
) => {
  // 遍历数组中的每个元素
  array.forEach((item) => {
    // 如果元素是对象且有属性，则设置字段值
    if (typeof item === "object" && item !== null) {
      item[field] = value;
      // 如果元素有子数组，递归调用函数
      if (Array.isArray(item[defaultProps.children])) {
        setFieldValue(item[defaultProps.children], field, value, defaultProps);
      }
    }
  });
};

// 设置禁用
const setTreeIsDisabled = (
  data: any[],
  nodeKeysToDisable: string[],
  nodeKey: string,
  defaultProps: any,
  flag = true
) => {
  if (!data || !data.length) return;
  data.forEach((item) => {
    if (
      nodeKeysToDisable &&
      nodeKeysToDisable.length &&
      nodeKeysToDisable.includes(item[nodeKey])
    ) {
      // 如果当前节点的id主键在要禁用的id主键列表中，设置disabled为true
      item[defaultProps.disabled] = flag;
    }
    // 如果当前节点有children，递归调用函数
    const itemChildren = item[defaultProps.children];
    if (itemChildren && Array.isArray(itemChildren)) {
      setTreeIsDisabled(
        itemChildren,
        nodeKeysToDisable,
        nodeKey,
        defaultProps,
        flag
      );
    }
  });
};

// 获取数组中disabled的节点的Ids
const getDisabledNodeIds = (
  nodes: any[],
  nodeKey: string,
  defaultProps: any
): string[] => {
  const disabledIds: string[] = [];

  function traverse(node: any) {
    if (node.disabled) {
      disabledIds.push(node[nodeKey]);
    }
    if (node[defaultProps.children]?.length) {
      node[defaultProps.children].forEach((child: any) => traverse(child));
    }
  }

  nodes.forEach((node) => traverse(node));
  return disabledIds;
};

// 递归校验 当子节点全部被禁用时 ，则设置其父节点也禁用
const updateDisabledStatus = (nodes: any[], defaultProps: any) => {
  nodes.forEach((node) => {
    // 首先检查当前节点是否有子节点
    if (node[defaultProps.children]?.length) {
      // 假设当前节点的所有子节点都是禁用的
      let allChildrenDisabled = true;

      // 递归检查所有子节点的disabled状态
      node[defaultProps.children].forEach((child: any) => {
        // 如果子节点有子节点，递归调用
        if (child[defaultProps.children]?.length) {
          updateDisabledStatus([child], defaultProps); // 递归更新子节点状态
        }
        // 更新子节点的disabled状态
        child[defaultProps.disabled] =
          child[defaultProps.children]?.length > 0
            ? child[defaultProps.children].every(
                (c: any) => c[defaultProps.disabled]
              )
            : child[defaultProps.disabled];

        // 如果发现任何一个子节点没有被禁用，更新假设
        if (!child[defaultProps.disabled]) {
          allChildrenDisabled = false;
        }
      });

      // 更新当前节点的disabled状态
      node[defaultProps.disabled] = allChildrenDisabled;
    }
  });
};

// 左侧输入框过滤事件
const filterLeftNode = (value, data) => {
  if (!value) return true;
  return data[props.defaultProps.label].includes(value);
};

// 右侧输入框过滤事件
const filterRightNode = (value, data) => {
  if (!value) return true;
  return data[props.defaultProps.label].includes(value);
};

// 右侧数据按顺序排序
const sortRightListByKey = () => {
  if (!props.isSort) return rightData.value;
  return rightData.value.sort((a, b) => a[props.nodeKey] - b[props.nodeKey]);
};

// 递归函数，用于构建只包含 ids 数组中 id 的树结构
const filterTreeByIds = (treeData, ids) => {
  return treeData
    .map((node) => {
      // 创建一个新节点对象，避免直接修改原始数据
      const newNode = { ...node };
      newNode[props.defaultProps.disabled] = false;

      // 如果当前节点的 id 在 ids 中，保留这个节点及其子节点
      if (ids.includes(node[props.nodeKey])) {
        // 递归地过滤子节点
        newNode[props.defaultProps.children] = filterTreeByIds(
          node[props.defaultProps.children] || [],
          ids
        );
      } else {
        // 如果当前节点的 id 不在 ids 中，但有子节点，递归地过滤子节点
        // 同时，如果子节点中有至少一个节点的 id 在 ids 中，保留当前节点
        newNode[props.defaultProps.children] = filterTreeByIds(
          node[props.defaultProps.children] || [],
          ids
        ).filter((child) => child !== null);
      }

      // 如果当前节点的 id 不在 ids 中，且没有子节点或子节点都不在 ids 中，则不保留这个节点
      if (
        !ids.includes(node[props.nodeKey]) &&
        (!newNode[props.defaultProps.children] ||
          newNode[props.defaultProps.children].length === 0)
      ) {
        return null;
      }

      // 返回新的节点对象
      return newNode;
    })
    .filter((node) => node !== null); // 过滤掉 null 节点
};

// 去右边
const toRight = () => {
  /*  右侧显示的数据获取 */
  rightTreeData.value = getRightTreeData();
  rightData.value = getRightListData();

  // 给父组件抛出已选择的数据
  checkVal();

  /*
   *  更新移动后的左侧树的节点状态 和全选按钮状态
   *    先给所有已右移的节点设置禁用
   *    再通过递归计算是否将子节点的父节点也设置禁用（子节点全部禁用时，将其父节点也禁用）
   *
   * */
  const rids = rightData.value.map((item) => item[props.nodeKey]);
  setTreeIsDisabled(
    leftTreeData.value,
    rids,
    props.nodeKey,
    props.defaultProps
  );
  updateDisabledStatus(leftTreeData.value, props.defaultProps);
  isLeftCheckAllBoxDisabled.value = checkAllDisabled(
    leftTreeData.value,
    props.defaultProps
  );
};
// 去左边
const toLeft = async () => {
  if (props.isToList) {
    // 获取当前右侧选中的数据，没有就return
    const listToLeftIds = rightData.value
      .filter((item) => item.checked)
      .map((item) => item[props.nodeKey]);
    if (!listToLeftIds.length) return;

    // 从右侧去掉选中的数据,并将所有数据的checked设为false，避免由索引变更导致的异常选中
    const unselectedList = rightData.value.filter((item) => !item.checked);
    rightData.value.map((item) => (item.checked = false));
    rightData.value = unselectedList;

    // 恢复选中数据在左侧的可选状态,并清除选中状态
    listToLeftIds.forEach((item) => leftTreeRef.value.setChecked(item, false));
    setTreeIsDisabled(
      leftTreeData.value,
      listToLeftIds,
      props.nodeKey,
      props.defaultProps,
      false
    );
    updateDisabledStatus(leftTreeData.value, props.defaultProps);

    checkVal();
    isLeftCheckAllBoxDisabled.value = checkAllDisabled(
      leftTreeData.value,
      props.defaultProps
    );
  } else {
    // 获取当前右侧选中的数据，没有就return
    const treeToLeftIds = getRightTReeCheckedNodeIds();
    if (!treeToLeftIds.length) return;

    // 恢复选中数据在左侧的可选状态,并清除选中状态
    setTreeIsDisabled(
      leftTreeData.value,
      treeToLeftIds,
      props.nodeKey,
      props.defaultProps,
      false
    );
    treeToLeftIds.forEach((item) => leftTreeRef.value.setChecked(item, false));
    updateDisabledStatus(leftTreeData.value, props.defaultProps);

    checkVal();
    isLeftCheckAllBoxDisabled.value = checkAllDisabled(
      leftTreeData.value,
      props.defaultProps
    );

    rightTreeData.value = [];
    rightTreeData.value = getRightTreeData();
    isCheckedAllRight.value = checkedAllTrue(
      rightTreeRef.value,
      rightTreeData.value,
      props.nodeKey,
      props.defaultProps
    );
  }
};

// 获取右侧树中选中节点的Ids
const getRightTReeCheckedNodeIds = () => {
  // 返回全部节点填false, false ；返回叶子结点填true,true
  const checkNodeIds = rightTreeRef.value.getCheckedKeys(true);
  if (!checkNodeIds.length) return [];

  return checkNodeIds;
};

// 左侧数据全选操作（全不选）
const handleLeftAllCheck = () => {
  const leftTree = leftTreeRef.value;
  const disabledIds = getDisabledNodeIds(
    leftTreeData.value,
    props.nodeKey,
    props.defaultProps
  );

  if (isCheckedAllLeft.value) {
    /*
     * 操作 ： 设置全选
     * 逻辑 ： 已经设置了disable的节点无法编辑选中，所以先获取所有设置了disable的节点的ids，然后将所有数据放开disable，设置全部选中，选中后再将ids中的节点设置禁用
     * */
    setFieldValue(
      leftTreeData.value,
      props.defaultProps.disabled,
      false,
      props.defaultProps
    );
    leftTree?.setCheckedNodes(leftTreeData.value);
    setTreeIsDisabled(
      leftTreeData.value,
      disabledIds,
      props.nodeKey,
      props.defaultProps
    );
    isCheckedAllLeft.value = true;
  } else {
    /*
     * 操作 ： 设置全不选
     * 逻辑 ： 已经设置disabled的节点不应该改变其选中和禁用状态 ，所以先获取所有禁用数据的ids（也就是checked=true的所有当前选中状态的数据），然后取消全部的选中状态，再将ids中的节点设置为选中状态
     * */
    leftTree?.setCheckedNodes([]);
    disabledIds.forEach((item) => leftTreeRef.value.setChecked(item, true));
    isCheckedAllLeft.value = false;
  }
};
// 左侧树节点checkbox被点击
const handleLeftCheckChange = () => {
  isCheckedAllLeft.value = checkedAllTrue(
    leftTreeRef.value,
    leftTreeData.value,
    props.nodeKey,
    props.defaultProps
  );
};

// 右侧树节点checkbox被点击
const handleRightCheckChange = () => {
  isCheckedAllRight.value = checkedAllTrue(
    rightTreeRef.value,
    rightTreeData.value,
    props.nodeKey,
    props.defaultProps
  );
};

// 右侧数据全选操作（全不选）
const handleRightAllCheck = () => {
  // list
  setFieldValue(
    rightData.value,
    "checked",
    isCheckedAllRight.value,
    props.defaultProps
  );
  // tree
  rightTreeRef.value.setCheckedNodes(
    isCheckedAllRight.value ? rightTreeData.value : []
  );
};

// 返回已选数据给父组件
const checkVal = () => {
  emit(
    "checkVal",
    props.isToList ? rightData.value : leftTreeRef.value.getCheckedNodes(true)
  );
};

const walkTreeData = (nodes, selectedKeys) => {
  const ret = [];
  nodes.forEach((node) => {
    const newNode = { ...node };
    newNode[props.defaultProps.disabled] = false;

    delete newNode[props.defaultProps.children];
    node[props.defaultProps.children] &&
      (newNode[props.defaultProps.children] = walkTreeData(
        node[props.defaultProps.children],
        selectedKeys
      ));
    if (
      selectedKeys.includes(newNode[props.nodeKey]) ||
      (newNode[props.defaultProps.children] &&
        newNode[props.defaultProps.children].length)
    ) {
      ret.push(newNode);
    }
  });

  return ret;
};

// 获取右侧list结构数据
const getRightListData = () => {
  /*  右侧list结构数据获取 */
  if (!currentLeftUseableNodes.value.length) return [];

  const newArr = rightData.value.concat(currentLeftUseableNodes.value);
  const obj: any = {};
  // 去重
  const peon: any = newArr.reduce((cur, next) => {
    obj[next[props.nodeKey]]
      ? ""
      : (obj[next[props.nodeKey]] = true && cur.push(next));
    cur.checked = false;
    return cur;
  }, []); // 设置cur默认类型为数组，并且初始值为空的数组

  return peon;
};

// 获取右侧树结构数据
const getRightTreeData = () => {
  if (!leftTreeRef.value || !rightTreeRef.value) return [];

  const checkedKeys = leftTreeRef.value.getCheckedKeys(false); // 当前选中节点 key 的数组
  const halfCheckedKeys = leftTreeRef.value.getHalfCheckedKeys(); // 目前半选中的节点的 key 所组成的数组
  const allCheckedKeys = halfCheckedKeys.concat(checkedKeys);
  if (allCheckedKeys && allCheckedKeys.length) {
    return walkTreeData(leftTreeData.value, allCheckedKeys);
  } else {
    return [];
  }
};

// 获取左侧树当前所选的可进行右移操作的数据
const currentLeftUseableNodes = computed(() => {
  if (!leftTreeRef.value) return [];

  // 返回全部节点填false ；返回叶子结点填true
  const checkNodes = leftTreeRef.value.getCheckedNodes(true); // 将返回当前选中节点的节点数组
  if (!checkNodes.length) return [];

  // 过滤当前已选，如果没有选择新的数据就return
  const useableNodes = checkNodes.filter(
    (item) => !item[props.defaultProps.disabled]
  );
  if (!useableNodes.length) return [];

  return useableNodes;
});

// 左移按钮disabled计算
const isToLeftBtnDisabled = computed(() => {
  let checkNodes = [];
  rightTreeRef.value &&
    (checkNodes = rightTreeRef.value.getCheckedNodes(false, false)); // tree选择的节点
  const listToLeftIds = rightData.value
    .filter((item) => item.checked)
    .map((item) => item[props.nodeKey]); // list选择的节点

  return !(listToLeftIds.length || checkNodes.length);
});

// 更新 treeData 中的指定节点，添加子节点
const updateTreeData = (targetNode: any, childNodes: any) => {
  const recursiveUpdate = (nodes: any) => {
    for (const node of nodes) {
      if (node[props.nodeKey] === targetNode[props.nodeKey]) {
        node[props.defaultProps.children] = childNodes; // 将子节点添加到目标节点
      } else if (node[props.defaultProps.children]) {
        recursiveUpdate(node[props.defaultProps.children]); // 递归查找目标节点
      }
    }
  };

  if (!Object.keys(leftTreeData.value).length) {
    leftTreeData.value = childNodes;
    return;
  }

  recursiveUpdate(leftTreeData.value);
};

//  懒加载方法
const handleLoadNode = (node: any, resolve: any) => {
  if (props.lazy) {
    const pid = node.level === 0 ? 0 : node.data[props.nodeKey];
    props
      .loadMethod(pid)
      .then((res: any) => {
        if (res || Array.isArray(res)) {
          // 更新 treeData，确保包含懒加载的节点
          // 在节点展开时，确保 treeData 是最新的完整结构
          resolve(res);
        } else {
          resolve([]);
        }
        updateTreeData(node.data, res);
      })
      .catch((err: any) => {
        console.error("Failed to load node data:", err);
        resolve([]);
      });
  } else {
    resolve(node.data[props.defaultProps.children] || []);
  }
};

// 监听右侧数据变化，判断右侧全选框是否选中
watch(
  () => rightData.value,
  (newData) => {
    if (!newData || !props.isToList) return;
    isCheckedAllRight.value =
      newData.length && newData.every((item) => item.checked);
  },
  {
    deep: true,
    immediate: true,
  }
);

// 初始化操作，将传参的默认选中节点传递并显示到右侧
watch(
  () => props.defaultSelectionKeys,
  (newKeys) => {
    if (props.lazy && props.loadMethod) return;
    if (!newKeys?.length) return;

    nextTick(async () => {
      // 设置目前选中的节点
      await leftTreeRef.value.setCheckedKeys(newKeys);
      toRight();
    });
  },
  {
    deep: true,
    immediate: true,
  }
);

// 初始化操作，将传参的默认选中节点传递并显示到右侧
watch(
  () => props.leftData,
  (newData) => {
    // 如果是懒加载，并且有loadMethod方法，直接return
    if (props.lazy && props.loadMethod) return;
    // 没有数据就return
    if (!newData?.length) return;
    leftTreeData.value = deepClone(newData);
    setFieldValue(
      leftTreeData.value,
      props.defaultProps.disabled,
      false,
      props.defaultProps
    );
  },
  {
    deep: true,
    immediate: true,
  }
);

watch(leftFilterText, (val) => {
  leftTreeRef.value!.filter(val);
});
watch(rightFilterText, (val) => {
  rightTreeRef.value!.filter(val);
});
</script>



<style lang="less" scoped>
.zt-tree-transfer {
  display: flex;
  height: 500px;
  width: 800px;
  box-sizing: border-box;

  .btn-div {
    flex: 1;
    height: 60%;
    margin: auto;
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
    align-items: center;

    .btn-item {
      :deep(svg),
      :deep(.el-icon) {
        height: 1.6em !important;
        width: 1.6em !important;
      }
    }
  }

  .left-content {
    width: 45%;
    border: 1px solid #dcdfe6;
    box-sizing: border-box;
    padding: 5px 10px;

    .list {
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      overflow: hidden;

      .left-tree {
        width: calc(100% - 5px);
        height: 100%;
        overflow: auto;
        margin-top: 10px;
        padding-right: 5px;
      }
    }
  }

  .righ-content {
    box-sizing: border-box;
    border: 1px solid #dcdfe6;
    padding: 5px 10px;
    width: 45%;
    overflow: auto;

    .right_item {
      text-align: left;
    }

    .list {
      height: 100%;
      display: flex;
      flex-direction: column;
    }
  }

  .left_lowline {
    display: flex;
    align-items: center;
  }

  .right_lowline {
    display: flex;
    align-items: center;
  }

  :deep(.el-input__wrapper) {
    position: relative;

    .el-input__inner {
      padding-right: 18px;
    }

    .el-input__suffix {
      position: absolute;
      right: 8px;
      top: 50%;
      transform: translateY(-50%);
    }
  }

  // 滚动条宽度
  ::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }

  // 滚动条轨道
  ::-webkit-scrollbar-track {
    background: rgb(239, 239, 239);
    border-radius: 2px;
  }

  // 小滑块
  ::-webkit-scrollbar-thumb {
    background: #40a0ff49;
    border-radius: 2px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: #40a0ff;
  }

  :deep(.el-button:focus) {
    outline: none;
  }

  :deep(.el-tree) {
    display: inline-block;
    min-width: 100%;

    .el-tree-node__content {
      //margin-right: 5px;
    }
  }
}
</style>

