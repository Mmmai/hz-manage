<template>
  <TreeTransfer
    v-model="selectedKeys"
    :data="treeDataFinal"
    :leaf-only="true"
    :hide-fully-assigned-parents="true"
    :titles="['可选权限', '已选权限']"
    :check-strictly="false"
    @change="handleChange"
  />
</template>

<script lang="ts" setup>
import {
  ref,
  computed,
  watch,
  getCurrentInstance,
  onMounted,
  reactive,
  nextTick,
} from "vue";
import TreeTransfer from "@/components/common/treeTransfer.vue";

const { proxy } = getCurrentInstance();
import { ElMessage } from "element-plus";
const nowNodeObject = defineModel("nowNodeObject");
// 权限树数据
const treeData = ref([]);

// 选中的权限keys
const selectedKeys = ref([]);
const allPermissionKeys = ref([]);
const getPermissionObj = defineModel("permissionObject");
const treeDataFinal = computed(() => {
  // 深拷贝treeData以避免修改原始数据
  const treeDataCopy = JSON.parse(JSON.stringify(treeData.value));

  // 如果没有权限数据或没有选中的对象，直接返回原始数据
  if (!allPermissionKeys.value || !getPermissionObj.value) {
    console.log("没有权限数据或没有选中的对象", getPermissionObj.value);
    return treeDataCopy;
  }
  console.log("treeDataFinal");
  // 创建一个映射，方便快速查找权限信息
  const permissionMap = new Map();
  allPermissionKeys.value.forEach((item) => {
    permissionMap.set(item.button_id, item);
  });

  // 递归处理树节点
  const processNodes = (nodes) => {
    return nodes.map((node) => {
      // 创建节点副本
      const newNode = { ...node };

      // 检查该节点是否在权限列表中
      const permissionInfo = permissionMap.get(newNode.id);

      // 如果找到了权限信息且source_type不等于getPermissionObj的值
      if (
        permissionInfo &&
        permissionInfo.source_type !== getPermissionObj.value
      ) {
        // 设置节点为禁用状态
        newNode.disabled = true;
        // 添加提示信息
        newNode.disabledTooltip = `权限来源于${getSourceTypeName(
          permissionInfo.source_type
        )}:${permissionInfo.source_name}，无法在此处修改`;
      }

      // 递归处理子节点
      if (newNode.children && newNode.children.length > 0) {
        newNode.children = processNodes(newNode.children);
      }

      return newNode;
    });
  };

  return processNodes(treeDataCopy);
});

// 辅助函数：获取权限来源类型的中文名称
const getSourceTypeName = (sourceType) => {
  switch (sourceType) {
    case "user":
      return "用户";
    case "role":
      return "角色";
    case "user_group":
      return "用户组";
    default:
      return "未知";
  }
};

// 获取权限树数据
const getPermissionTreeData = async () => {
  let res = await proxy.$api.getMenuTree();
  treeData.value = res.data.results;
};

const getPermissionOnRight = async () => {
  let res = await proxy.$api.getPermissionHas(nowNodeObject.value);
  allPermissionKeys.value = res.data.results;
  selectedKeys.value = res.data.results.map((item) => {
    return item.button_id;
  });
};

// 权限变更处理
const handleChange = (newVal, direction, movedKeys) => {
  if (direction == "right") {
    // 添加权限
    addPermissions(movedKeys);
  } else {
    // 删除权限
    removePermissions(movedKeys);
  }
};

// 添加权限
const addPermissions = async (buttonIds) => {
  // 构造请求参数，根据当前编辑对象的类型来构造
  const params = { ...nowNodeObject.value, button_ids: buttonIds };

  let res = await proxy.$api.addObjectPermissions(params);
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "权限添加成功",
    });
    nextTick(() => {
      getPermissionOnRight();
    });
  } else {
    ElMessage({
      type: "error",
      message: `权限添加失败: ${JSON.stringify(res.data)}`,
    });
  }
};

// 删除权限
const removePermissions = async (buttonIds) => {
  // 构造请求参数，根据当前编辑对象的类型来构造
  const params = { ...nowNodeObject.value, button_ids: buttonIds };

  let res = await proxy.$api.removeObjectPermissions(params);
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "权限删除成功",
    });
    nextTick(() => {
      getPermissionOnRight();
    });
  } else {
    ElMessage({
      type: "error",
      message: `权限删除失败: ${JSON.stringify(res.data)}`,
    });
  }
};

defineExpose({
  getPermissionTreeData,
  getPermissionOnRight,
});
</script>
<style scoped lang="scss">
</style>