<template>
  <div class="permission-container">
    <!-- <div class="header">
      <h2>CMDB权限管理</h2>
      <el-alert
        title="通过字段授权和实例授权来控制用户对CMDB资源的访问权限"
        type="info"
        :closable="false"
        class="header-alert"
      />
    </div> -->

    <div class="permission-content">
      <!-- 字段授权面板 -->
      <el-card class="permission-panel">
        <template #header>
          <div class="panel-header">
            <span class="panel-title"
              >字段授权
              <el-tooltip placement="top">
                <template #content>
                  如果勾选一个模型内字段组的所有字段，则添加的是此分组权限，后续此组有新增字段，也会有权限
                </template>
                <el-icon><InfoFilled /></el-icon> </el-tooltip
            ></span>
            <div class="panel-actions">
              <el-input
                v-model="fieldQuery"
                placeholder="输入关键字检索"
                clearable
                class="search-input"
                @input="onFieldQueryChanged"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
          </div>
        </template>

        <div class="tree-container">
          <el-tree-v2
            :data="modelTree"
            :props="treeProps"
            node-key="id"
            show-checkbox
            ref="fieldTreeRef"
            :filter-method="fieldFilterMethod"
            :height="850"
            class="permission-tree"
            @check="onTreeCheck"
            v-loading="loading"
          >
            <template #default="{ node, data }">
              <div class="custom-tree-node">
                <el-tag
                  size="small"
                  :type="
                    nodeTagType[data.type] ? nodeTagType[data.type] : 'info'
                  "
                  class="node-tag"
                >
                  {{ nodeTypeMap[data.type] }}
                </el-tag>
                <span class="node-label">{{ node.label }}</span>
              </div>
            </template>
          </el-tree-v2>
        </div>
      </el-card>

      <!-- 实例授权面板 -->
      <el-card class="permission-panel">
        <template #header>
          <div class="panel-header">
            <span class="panel-title"
              >实例授权
              <el-tooltip placement="top">
                <template #content>
                  如果勾选一个实例树内的所有实例，则添加的是此实例树权限，后续此组有新增实例，也会有权限
                </template>
                <el-icon><InfoFilled /></el-icon> </el-tooltip
            ></span>
            <div class="panel-actions">
              <el-input
                v-model="fieldQuery"
                placeholder="输入关键字检索"
                clearable
                class="search-input"
                @input="onFieldQueryChanged"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              <el-tooltip content="刷新实例" placement="top">
                <el-button
                  link
                  :icon="RefreshLeft"
                  @click="refreshCi"
                  class="refresh-btn"
                >
                </el-button>
              </el-tooltip>
            </div>
          </div>
        </template>

        <div class="tree-container">
          <el-tree-v2
            :data="modelCiTree"
            :props="treeProps"
            node-key="id"
            show-checkbox
            ref="instanceTreeRef"
            :height="850"
            class="permission-tree"
            @check="onTreeCheck"
            v-loading="loading"
          >
            <template #default="{ node, data }">
              <div class="custom-tree-node">
                <el-tag
                  size="small"
                  :type="
                    nodeTagType[data.type] ? nodeTagType[data.type] : 'info'
                  "
                  class="node-tag"
                >
                  {{ nodeTypeMap[data.type] }}
                </el-tag>
                <span class="node-label">{{ node.label }}</span>
                <span
                  v-if="data.instance_count !== undefined"
                  class="instance-count"
                >
                  ({{ data.instance_count }})
                </span>
              </div>
            </template>
          </el-tree-v2>
        </div>
      </el-card>
    </div>

    <div class="footer-actions">
      <el-button
        type="primary"
        size="large"
        @click="savePermissions"
        :disabled="!isDataChanged"
      >
        保存
      </el-button>
      <!-- <el-button size="large" @click="resetPermissions"> 重置 </el-button> -->
    </div>
  </div>
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
const { proxy } = getCurrentInstance();
import api from "@/api/index";
import useModelStore from "@/store/cmdb/model";
const modelConfigStore = useModelStore();
import type {
  FilterNodeMethodFunction,
  TreeV2Instance,
  TreeNodeData,
} from "element-plus";
import { InfoFilled, RefreshLeft, Search } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
const nowNodeObject = defineModel("nowNodeObject");
const getPermissionObj = defineModel("permissionObject");
const fieldQuery = ref("");
const instanceQuery = ref("");
const fieldTreeRef = ref<TreeV2Instance>();
const instanceTreeRef = ref<TreeV2Instance>();
const allModels = computed(() => modelConfigStore.allModels);
const allModelCiDataObj = computed(() => modelConfigStore.allModelCiDataObj);

// 新增：用于跟踪初始状态和当前状态
const initialFieldCheckedKeys = ref<string[]>([]);
const initialInstanceCheckedKeys = ref<string[]>([]);
const currentFieldCheckedKeys = ref<string[]>([]);
const currentInstanceCheckedKeys = ref<string[]>([]);

const treeProps = {
  label: "verbose_name",
  children: "children",
};

const nodeTypeMap = {
  modelgroups: "模型分组",
  models: "模型",
  modelfieldgroups: "字段组",
  modelfields: "字段",
  modelinstancegroup: "实例树",
  modelinstance: "实例",
};

const nodeTagType = {
  modelgroups: "primary",
  models: "success",
  modelfieldgroups: "warning",
  modelfields: "info",
  modelinstancegroup: "warning",
  modelinstance: "info",
};

// 新增：计算数据是否发生变化
const isDataChanged = computed(() => {
  // 比较字段树的选中状态
  const fieldChanged =
    initialFieldCheckedKeys.value.length !==
      currentFieldCheckedKeys.value.length ||
    initialFieldCheckedKeys.value.some(
      (key) => !currentFieldCheckedKeys.value.includes(key)
    ) ||
    currentFieldCheckedKeys.value.some(
      (key) => !initialFieldCheckedKeys.value.includes(key)
    );

  // 比较实例树的选中状态
  const instanceChanged =
    initialInstanceCheckedKeys.value.length !==
      currentInstanceCheckedKeys.value.length ||
    initialInstanceCheckedKeys.value.some(
      (key) => !currentInstanceCheckedKeys.value.includes(key)
    ) ||
    currentInstanceCheckedKeys.value.some(
      (key) => !initialInstanceCheckedKeys.value.includes(key)
    );

  return fieldChanged || instanceChanged;
});

const modelTree = computed(() => {
  // 先创建以groupList为第一层的树结构
  const tree = groupList.value.map((group) => ({
    id: group.id,
    name: group.name,
    verbose_name: group.verbose_name,
    description: group.description,
    type: "modelgroups", // 标识为分组节点
    parent_id: null, // 根节点没有父节点
    children: [],
  }));

  // 将模型按照model_group分配到对应的分组中
  allModels.value.forEach((model) => {
    const groupNode = tree.find((group) => group.id === model.model_group);
    if (groupNode) {
      // 创建模型节点
      const modelNode = {
        id: model.id,
        name: model.name,
        verbose_name: model.verbose_name,
        description: model.description,
        type: "models", // 标识为模型节点
        parent_id: groupNode.id, // 父节点为模型分组
        children: [],
      };

      // 处理 field_groups 作为模型的子节点
      if (model.field_groups && model.field_groups.length > 0) {
        modelNode.children = model.field_groups.map((group) => {
          const fieldGroupNode = {
            id: group.id,
            name: group.name,
            verbose_name: group.verbose_name,
            description: group.description,
            type: "modelfieldgroups", // 标识为字段组节点
            parent_id: modelNode.id, // 父节点为模型
            children: [],
          };

          // 处理 fields 作为 field_groups 的子节点
          if (group.fields && group.fields.length > 0) {
            fieldGroupNode.children = group.fields.map((field) => ({
              id: field.id,
              name: field.name,
              verbose_name: field.verbose_name,
              description: field.description,
              type: "modelfields", // 标识为字段节点
              parent_id: fieldGroupNode.id, // 父节点为字段组
            }));
          }

          return fieldGroupNode;
        });
      }

      groupNode.children.push(modelNode);
    }
  });

  return tree;
});

// 构建模型分组-模型-模型实例树-实例的完整树形结构
const modelCiTree = computed(() => {
  // 先创建以groupList为第一层的树结构
  const tree = groupList.value.map((group) => ({
    id: group.id,
    name: group.name,
    verbose_name: group.verbose_name,
    description: group.description,
    type: "modelgroups", // 标识为分组节点
    parent_id: null, // 根节点没有父节点
    children: [],
  }));

  // 将模型按照model_group分配到对应的分组中，并添加实例数据
  allModels.value.forEach((model) => {
    const groupNode = tree.find((group) => group.id === model.model_group);
    if (groupNode) {
      // 创建模型节点
      const modelNode = {
        id: model.id,
        name: model.name,
        verbose_name: model.verbose_name,
        description: model.description,
        type: "models", // 标识为模型节点
        parent_id: groupNode.id, // 父节点为模型分组
        children: [],
      };

      // 如果存在该模型的实例数据，则添加到模型节点下
      if (allModelCiDataObj.value[model.id]) {
        // 转换实例树结构
        const convertInstanceTree = (node, parentId) => {
          const instanceTreeNode = {
            id: node.id,
            name: node.label,
            verbose_name: node.label,
            instance_count: node.instances ? node.instances.length : 0,
            built_in: node.built_in,
            level: node.level,
            type: "modelinstancegroup", // 标识为实例树节点
            parent_id: parentId, // 父节点ID
            children: [],
          };

          // 处理子节点（实例树节点）
          if (node.children && node.children.length > 0) {
            instanceTreeNode.children = node.children.map((child) =>
              convertInstanceTree(child, instanceTreeNode.id)
            );
          }

          // 处理实例（作为子节点添加）
          if (node.instances && node.instances.length > 0) {
            node.instances.forEach((instance) => {
              instanceTreeNode.children.push({
                id: instance.id,
                name: instance.instance_name,
                verbose_name: instance.instance_name,
                type: "modelinstance", // 标识为实例节点
                parent_id: instanceTreeNode.id, // 父节点为实例树节点
              });
            });
          }

          return instanceTreeNode;
        };

        // 将实例树添加到模型节点下
        modelNode.children.push(
          convertInstanceTree(allModelCiDataObj.value[model.id], modelNode.id)
        );
      }

      groupNode.children.push(modelNode);
    }
  });
  return tree;
});

// 新增：处理树节点勾选变化
const onTreeCheck = () => {
  // 更新当前选中状态
  currentFieldCheckedKeys.value = fieldTreeRef.value?.getCheckedKeys() || [];
  currentInstanceCheckedKeys.value =
    instanceTreeRef.value?.getCheckedKeys() || [];
};

const onFieldQueryChanged = (query: string) => {
  fieldTreeRef.value!.filter(query);
};

const onInstanceQueryChanged = (query: string) => {
  instanceTreeRef.value!.filter(query);
};

const fieldFilterMethod = (query: string, node: TreeNodeData) =>
  node.verbose_name!.includes(query);

const instanceFilterMethod = (query: string, node: TreeNodeData) =>
  node.verbose_name!.includes(query);

// 获取模型组
const groupList = ref([]);
const getCiModelGroupList = async () => {
  let res = await api.getCiModelGroup();
  groupList.value = res.data.results;
};

const refreshCi = async () => {
  modelConfigStore.getAllModelTreeInstances(true);
};

const test = () => {
  fieldTreeRef.value!.setCheckedKeys(["f887f0ef-fc35-4fb2-9f47-5d35852be18b"]);
  console.log(fieldTreeRef.value);
};

// 处理字段权限树的勾选状态，按规则提取需要的ID
const handleFieldTreeCheck = () => {
  let params = [];
  const fieldCheckedNodes = fieldTreeRef.value?.getCheckedNodes(false);
  const fieldHalfCheckedNodes = fieldTreeRef.value?.getHalfCheckedNodes();
  // 获取半选的字段组节点
  const halfCheckedFieldGroupIds = fieldHalfCheckedNodes
    .filter((node) => node.type === "modelfieldgroups")
    .map((item) => item.id);
  // 获取全选节点,剔除模型分组和模型，得出全选的字段组
  const checkedFieldGroupIds = fieldCheckedNodes
    .filter((node) => node.type === "modelfieldgroups")
    .map((item) => item.id);
  // 提取半选的字段组id下属的字段id,因为字段组全选的字段，已经不需要处理了
  const checkFiledIds = fieldCheckedNodes
    .filter((node) => halfCheckedFieldGroupIds.includes(node.parent_id))
    .map((item) => item.id);
  // 添加字段组全选授权
  if (checkedFieldGroupIds.length > 0) {
    params.push({
      app_label: "cmdb",
      model: "modelfieldgroups",
      object_ids: checkedFieldGroupIds,
    });
  }
  // 添加字段组半选，字段授权
  if (checkFiledIds.length > 0) {
    params.push({
      app_label: "cmdb",
      model: "modelfields",
      object_ids: checkFiledIds,
    });
  }

  // 模型实例授权
  const instanceCheckedNodes = instanceTreeRef.value?.getCheckedNodes(false);
  const instanceHalfCheckedNodes = instanceTreeRef.value?.getHalfCheckedNodes();
  // 将全选的实例树和模型，添加到map中

  // 获取半选的实例树节点
  const halfCheckedInstanceGroupIds = instanceHalfCheckedNodes
    .filter((node) => node.type === "modelinstancegroup")
    .map((item) => item.id);
  // 获取全选的实例树节点,只选取最顶上的节点
  const checkedInstanceGroupIds = instanceCheckedNodes
    .filter((node) => {
      if (node.type === "modelinstancegroup") {
        // 判断父节点的类型
        const pNode = instanceTreeRef.value!.getNode(node.parent_id);
        if (pNode.data.type === "models") return true;
        if (halfCheckedInstanceGroupIds.includes(node.parent_id)) return true;
        return false;
      } else {
        return false;
      }
    })
    .map((item) => item.id);
  // 获取半选的实例树节点的实例节点
  const instanceCheckedIds = instanceCheckedNodes
    .filter(
      (node) =>
        halfCheckedInstanceGroupIds.includes(node.parent_id) &&
        node.type === "modelinstance"
    )
    .map((item) => item.id);
  // 添加全选的实例树授权
  if (checkedInstanceGroupIds.length > 0) {
    params.push({
      app_label: "cmdb",
      model: "modelinstancegroup",
      object_ids: checkedInstanceGroupIds,
    });
  }
  // 添加实例树半选，实例单独授权

  if (instanceCheckedIds.length > 0) {
    params.push({
      app_label: "cmdb",
      model: "modelinstance",
      object_ids: instanceCheckedIds,
    });
  }

  return params;
};

// 保存权限设置
const savePermissions = async () => {
  // 如果数据没有变化，则不提交
  if (!isDataChanged.value) {
    ElMessage.info("权限设置未发生变化，无需保存");
    return;
  }

  let params = handleFieldTreeCheck();
  console.log(params);
  let res = await api.setDataScope({
    scope_type: "filter",
    app_label: "cmdb",
    targets: params,
    ...nowNodeObject.value,
  });
  if (res.status == "201") {
    ElMessage.success("权限更新成功!");
    getDataScope();
  } else {
    ElMessage.error("保存失败," + JSON.stringify(res.data));
  }
  // 更新初始状态为当前状态
  initialFieldCheckedKeys.value = [...currentFieldCheckedKeys.value];
  initialInstanceCheckedKeys.value = [...currentInstanceCheckedKeys.value];
};

const filedCheckedKeys = ref([]);
const instanceCheckedKeys = ref([]);
const loading = ref(true);
const getDataScope = async () => {
  try {
    loading.value = true;
    let res = await api.getDataScope({
      ...nowNodeObject.value,
    });
    // 清空之前的数据，避免累积
    filedCheckedKeys.value = [];
    instanceCheckedKeys.value = [];

    res.data.results.forEach((item) => {
      if (item.scope_type == "filter") {
        Object.entries(item.targets_detail).forEach(([tkey, tvalue]) => {
          if (
            ["cmdb.modelfields", "cmdb.modelfieldgroups"].indexOf(tkey) !== -1
          ) {
            if (tvalue) {
              filedCheckedKeys.value.push(...tvalue);
            }
          } else if (
            ["cmdb.modelinstance", "cmdb.modelinstancegroup"].indexOf(tkey) !==
            -1
          ) {
            if (tvalue) {
              instanceCheckedKeys.value.push(...tvalue);
            }
          }
        });
      }
    });
    // 设置已配置的权限
    nextTick(() => {
      fieldTreeRef.value!.setCheckedKeys(filedCheckedKeys.value);
      instanceTreeRef.value!.setCheckedKeys(instanceCheckedKeys.value);

      // 初始化初始状态
      initialFieldCheckedKeys.value = [...filedCheckedKeys.value];
      initialInstanceCheckedKeys.value = [...instanceCheckedKeys.value];
      currentFieldCheckedKeys.value = [...filedCheckedKeys.value];
      currentInstanceCheckedKeys.value = [...instanceCheckedKeys.value];
    });
  } catch (error) {
    console.error("获取数据范围失败:", error);
    // 清空数据以防止使用旧数据
    filedCheckedKeys.value = [];
    instanceCheckedKeys.value = [];
    fieldTreeRef.value!.setCheckedKeys([]);
    instanceTreeRef.value!.setCheckedKeys([]);

    // 同样初始化初始状态
    initialFieldCheckedKeys.value = [];
    initialInstanceCheckedKeys.value = [];
    currentFieldCheckedKeys.value = [];
    currentInstanceCheckedKeys.value = [];
  } finally {
    setTimeout(() => {
      loading.value = false;
    }, 500);
  }
};

// 重置权限设置
const resetPermissions = () => {
  fieldTreeRef.value?.setCheckedKeys([], false);
  instanceTreeRef.value?.setCheckedKeys([], false);
  ElMessage.info("权限设置已重置");
};

onMounted(async () => {
  await modelConfigStore.getModel();
  await modelConfigStore.getAllModelTreeInstances();
  await getCiModelGroupList();
  await getDataScope();
});
</script>
<style scoped lang="scss">
.permission-container {
  // padding: 10px;
  // background-color: var(--el-bg-color-page);
  min-height: 100%;

  .header {
    margin-bottom: 20px;

    h2 {
      margin-bottom: 15px;
      color: var(--el-text-color-primary);
    }

    .header-alert {
      border-radius: 8px;
    }
  }

  .permission-content {
    height: 90%;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 20px;
  }

  .permission-panel {
    height: 100%;

    border-radius: 8px;
    box-shadow: var(--el-box-shadow-light);

    :deep(.el-card__header) {
      padding: 15px 20px;
      border-bottom: 1px solid var(--el-border-color-light);
    }

    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .panel-title {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        font-weight: 600;
        color: var(--el-text-color-primary);
      }

      .panel-actions {
        display: flex;
        align-items: center;
        gap: 10px;
      }

      .search-input {
        width: 150px;
      }

      .refresh-btn {
        color: var(--el-color-primary);
        font-weight: normal;
      }
    }

    .tree-container {
      height: 100%;
      overflow: auto;

      .permission-tree {
        :deep(.el-tree-node) {
          padding: 2px 0;
        }
      }
    }
  }

  .custom-tree-node {
    display: flex;
    align-items: center;
    flex: 1;
    padding: 5px 0;

    .node-tag {
      margin-right: 8px;
      border: none;
    }

    .node-label {
      flex: 1;
      font-size: 14px;
      color: var(--el-text-color-regular);
    }

    .instance-count {
      margin-left: 5px;
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
  }

  .footer-actions {
    display: flex;
    justify-content: center;
    gap: 20px;

    .el-button {
      padding: 12px 30px;
    }
  }

  @media (max-width: 1200px) {
    .permission-content {
      grid-template-columns: 1fr;
    }
  }
}
</style>