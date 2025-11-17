<template>
  <div class="divVertical">
    <div class="card flexJstart gap-5" style="height: 50px; flex: none">
      <el-tooltip
        class="box-item"
        effect="dark"
        content="返回proxy列表"
        placement="top"
      >
        <el-button @click="goBack()" :icon="Back" plain size="small">
        </el-button>
        <!-- <el-icon @click="goBack()">
          <Back />
        </el-icon> -->
      </el-tooltip>
      <el-text tag="b" size="large">{{
        `代理详情【${proxyForm.name}】`
      }}</el-text>
    </div>
    <div class="card" style="flex: none">
      <!-- proxy表单 -->
      <el-form
        ref="proxyFormRef"
        :model="proxyForm"
        :rules="proxyFormRules"
        label-width="100px"
        style="width: 100%; margin-top: 10px"
      >
        <el-row :gutter="20">
          <el-col :span="4">
            <el-form-item label="代理名称" prop="name">
              <el-input v-model="proxyForm.name" placeholder="请输入代理名称" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="中文名称" prop="verbose_name">
              <el-input
                v-model="proxyForm.verbose_name"
                placeholder="请输入中文名称"
              />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="代理类型" prop="proxy_type">
              <el-select
                v-model="proxyForm.proxy_type"
                placeholder="请选择代理类型"
                disabled
              >
                <el-option
                  v-for="item in proxyTypeOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                >
                  <span style="float: left">{{ item.label }}</span>
                  <span
                    style="
                      float: right;
                      color: var(--el-text-color-secondary);
                      font-size: 13px;
                    "
                  >
                    {{ item.description }}
                  </span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="是否启用" prop="enabled">
              <el-switch v-model="proxyForm.enabled" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="4">
            <el-form-item label="代理ip" prop="ip_address">
              <el-input
                v-model="proxyForm.ip_address"
                placeholder="请输入代理ip"
              />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="代理端口" prop="port">
              <el-input-number
                v-model="proxyForm.port"
                placeholder="请输入代理端口"
                :min="1"
                :max="65535"
                controls-position="right"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="认证用户" prop="auth_user">
              <el-input
                v-model="proxyForm.auth_user"
                placeholder="请输入认证用户"
              />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="用户密码" prop="auth_pass">
              <el-input
                v-model="proxyForm.auth_pass"
                type="password"
                placeholder="请输入用户密码"
                show-password
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="4">
            <el-form-item label="备注信息" prop="description">
              <el-input
                v-model="proxyForm.description"
                placeholder="请输入备注信息"
                :autosize="{ minRows: 2, maxRows: 4 }"
                type="textarea"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <el-row justify="center">
        <el-button type="primary" @click="updateAction()">更新</el-button>
      </el-row>
    </div>
    <div class="card">
      <el-tabs
        v-model="activeName"
        type="card"
        class="demo-tabs"
        @tab-click="handleClick"
      >
        <el-tab-pane
          :label="item.label"
          :name="item.name"
          :key="index"
          v-for="(item, index) in manageModelArr"
        >
        </el-tab-pane>
      </el-tabs>
      <el-row justify="center">
        <h3>节点关联配置</h3>
      </el-row>
      <div style="text-align: center">
        <!-- <el-transfer
          v-model="hasConfigNodes"
          style="text-align: left; display: inline-block"
          filterable
          :titles="['所有节点', '已配置节点']"
          :button-texts="['删除', '添加']"
          :format="{
            noChecked: '${total}',
            hasChecked: '${checked}/${total}',
          }"
          :data="allNodes"
          @change="handleChange"
        >
          <template #default="{ option }">
            <el-tooltip
              v-if="option.disabled"
              class="box-item"
              effect="dark"
              content="已被其它proxy关联"
              placement="top"
            >
              <span>{{ option.label }}</span>
            </el-tooltip>
            <span v-else>{{ option.label }}</span>
          </template>
        </el-transfer> -->
        <TreeTransfer
          v-model="selectedKeys"
          :data="treeData"
          :leaf-only="true"
          :hide-fully-assigned-parents="true"
          :titles="['可选节点', '已选节点']"
          :check-strictly="false"
          @change="handleChange"
        />
      </div>
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
import { Back } from "@element-plus/icons-vue";
import { ElMessageBox, ElMessage, ElNotification } from "element-plus";
import { useRoute, useRouter } from "vue-router";
import { has } from "lodash";
const router = useRouter();
const route = useRoute();
const { proxy } = getCurrentInstance();
import TreeTransfer from "@/components/common/treeTransfer.vue";

// proxyId
const proxyId = ref(null);

const goBack = () => {
  // if (route.name.includes("cmdb_only")) {
  //   router.push({
  //     path: "/cmdb_only/cmdb/cidata",
  //   });
  //   return;
  // }
  router.push({
    path: "/node_control/proxyManage",
  });
};
const resetForm = (formEl) => {
  if (!formEl) return;
  formEl.resetFields();
};
const formRef = ref("");
// 表单字段
const proxyForm = reactive({
  name: "",
  verbose_name: "",
  proxy_type: "all",
  enabled: true,
  ip_address: "",
  port: 22,
  auth_user: "",
  auth_pass: "",
  description: "",
});
// 代理类型选项
const proxyTypeOptions = [
  { label: "all", value: "all", description: "所有类型,支持zabbix和ansible" },
  { label: "zabbix", value: "zabbix", description: "zabbix代理" },
  { label: "ansible", value: "ansible", description: "ansible代理" },
];

// 表单验证规则
const proxyFormRules = {
  name: [
    { required: true, message: "请输入代理名称(不支持中文)", trigger: "blur" },
    {
      pattern:
        /^((\d{1,3}\.){1,3}\d{1,3})?[a-zA-Z0-9_-]{1,32}((\d{1,3}\.){1,3}\d{1,3})?$/,
      message: "请输入正确的代理名称,不支持中文等特殊符号",
      trigger: "blur",
    },
  ],

  proxy_type: [
    { required: true, message: "请选择代理类型", trigger: "change" },
  ],
  ip_address: [
    { required: true, message: "请输入代理IP", trigger: "blur" },
    {
      pattern: /^(\d{1,3}\.){3}\d{1,3}$/,
      message: "请输入正确的IP地址格式",
      trigger: "blur",
    },
  ],
  port: [
    { required: true, message: "请输入代理端口", trigger: "blur" },
    {
      //
      type: "number",
      min: 1,
      max: 65535,
      message: "端口号应在1-65535之间",
      trigger: "blur",
    },
  ],
  auth_user: [{ required: true, message: "请输入认证用户", trigger: "blur" }],
  auth_pass: [{ required: true, message: "请输入用户密码", trigger: "blur" }],
};

// 穿梭框
const allNodes = ref([]);
const hasConfigNodes = ref([]);
import type {
  TransferDirection,
  TransferKey,
  renderContent,
} from "element-plus";
import { ca } from "element-plus/es/locale/index.mjs";
// const handleChange = (
//   value: TransferKey[],
//   direction: TransferDirection,
//   movedKeys: TransferKey[]
// ) => {
//   console.log(value, direction, movedKeys);
//   if (direction == "right") {
//     // 添加关联
//     associate(movedKeys);
//   } else {
//     cancelAssociate(movedKeys);
//   }
// };
// 多模型管理
// 模型管理
const activeName = ref("hosts");
const manageModelArr = ref([]);
const manageModelNameMap = computed(() => {
  return manageModelArr.value.reduce((acc, cur) => {
    acc[cur.name] = cur;
    return acc;
  }, {});
});
const handleClick = (tab, event) => {
  // console.log(tab, event);
  nextTick(() => {
    getNodesData();
    getHostTreeData();
  });
};
// 请求
// 模型同步列表
const getMangeModel = async () => {
  let res = await proxy.$api.getModelConfig({ ordering: "create_time" });
  if (res.status == 200) {
    manageModelArr.value = res.data.results
      .filter((item) => item.is_manage === true)
      .map((item) => ({
        label: item.model_verbose_name || item.model_name,
        name: item.model_name,
        model_id: item.model,
      }));
  }
};
// 获取单个proxy信息
const getProxyData = async () => {
  let res = await proxy.$api.getProxyInfo(proxyId.value);
  if (res.status == 200) {
    // 赋值给表单
    proxyForm.name = res.data.name;
    proxyForm.verbose_name = res.data.verbose_name;
    proxyForm.proxy_type = res.data.proxy_type;
    proxyForm.enabled = res.data.enabled;
    proxyForm.ip_address = res.data.ip_address;
    proxyForm.port = res.data.port;
    proxyForm.auth_user = res.data.auth_user;
    proxyForm.auth_pass = res.data.auth_pass;
    proxyForm.description = res.data.description;
  }
  // 获取proxy已关联的node节点
  selectedKeys.value = res.data.nodes.map((item) => {
    // return {
    //   value: item.instance_name,
    //   key: item.id,
    //   disabled: false,
    // };
    return item.model_instance;
  });
  console.log("hasConfigNodes:", hasConfigNodes.value);
};
// 获取所有nodes
const getNodesData = async () => {
  let res = await proxy.$api.getNodesArray({
    model: manageModelNameMap.value[activeName.value]?.model_id,
  });
  if (res.status == 200) {
    allNodes.value = res.data.map((item) => {
      return {
        label: item.instance_name,
        id: item.id,
        instanceId: item.model_instance,
        disabled:
          item.proxy_id === proxyId.value || item.proxy_id == null
            ? false
            : true,
      };
    });
  }
  // console.log("allNodes:", allNodes.value);
};
const instanceNodeMap = computed(() => {
  let map = {};
  allNodes.value.forEach((item) => {
    map[item.instanceId] = item;
  });
  return map;
});
// 更新方法
const updateAction = async () => {
  let res = await proxy.$api.updateProxy({ id: proxyId.value, ...proxyForm });
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "更新成功",
    });
    getProxyData();
    resetForm(formRef.value);
  } else {
    ElMessage({
      type: "error",
      message: `更新失败: ${res.data}`,
    });
  }
};
// 节点关联
const associate = async (ids: TransferKey[]) => {
  let res = await proxy.$api.batchAssociateProxy({
    proxy_id: proxyId.value,
    ids: ids,
  });
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "关联成功",
    });
    // 获取已配置的nodes
    getProxyData();
  } else {
    ElMessage({
      type: "error",
      message: `关联失败: ${res.data}`,
    });
  }
};
// 节点取消关联
const cancelAssociate = async (ids: TransferKey[]) => {
  // 发起删除请求
  let res = await proxy.$api.batchDissociateProxy({
    ids: ids,
    proxy_id: proxyId.value,
  });
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "取消关联成功",
    });
    // 获取已配置的nodes
    getProxyData();
  } else {
    ElMessage({
      type: "error",
      message: `取消关联失败: ${res.data}`,
    });
  }
};

const treeData = ref([]);

const selectedKeys = ref([]);
function convertToTreeFormat(treeData) {
  /**
   * 递归转换节点
   * @param {Object} node - 原始节点
   * @returns {Object|null} 转换后的节点，如果应该被剔除则返回null
   */
  function convertNode(node) {
    const newNode = {
      id: node.id,
      label: node.label,
    };

    // 处理子节点
    let validChildren = [];
    if (node.children && node.children.length > 0) {
      validChildren = node.children
        .map(convertNode)
        .filter((child) => child !== null);
    }

    // 处理实例
    let instanceNodes = [];
    if (node.instances && node.instances.length > 0) {
      // 将instances转换为叶子节点
      instanceNodes = node.instances.map((instance) => ({
        id: instance.id,
        label: instance.instance_name,
        disabled: instanceNodeMap.value[instance.id]?.disabled || false,
        disabledTooltip:
          instanceNodeMap.value[instance.id]?.disabledTooltip ||
          "已被其它proxy关联",
      }));
    }

    // 合并子节点和实例节点
    const allChildren = [...validChildren, ...instanceNodes];

    if (allChildren.length > 0) {
      newNode.children = allChildren;
    } else if (
      (!node.instances || node.instances.length === 0) &&
      (!node.children || node.children.length === 0)
    ) {
      // 如果既没有子节点也没有实例，则剔除此节点
      return null;
    }

    return newNode;
  }

  // 处理根节点数组并过滤掉null节点
  const result = treeData.map(convertNode).filter((node) => node !== null);
  return result;
}

// 获取主机模型
// const hostModel = ref(null);
// const getCiModel = async () => {
//   let res = await proxy.$api.getCiModel({
//     name: "hosts",
//   });
//   hostModel.value = res.data.results[0];
// };

// 获取主机树数据
const getHostTreeData = async () => {
  let res = await proxy.$api.getCiModelTreeNode({
    model: manageModelNameMap.value[activeName.value]?.model_id,
  });
  treeData.value = convertToTreeFormat(res.data);
  // treeData.value = res.data;
};

//
const handleChange = (newVal, direction, movedKeys) => {
  // console.log("值变化:", newVal);
  // console.log("移动方向:", direction);
  // console.log("移动的keys:", movedKeys);
  if (direction == "right") {
    // 添加
    associate(movedKeys);
  } else {
    // 删除
    cancelAssociate(movedKeys);
  }
};
onMounted(async () => {
  proxyId.value = route.path.split("/").at(-1);
  // console.log("proxyId:", proxyId.value);
  await getMangeModel();
  await getProxyData();
  await getNodesData();
  await getHostTreeData();
  // await updateTreeDataWithDisabledStatus(treeData.value, allNodes.value);
});
onMounted(() => {
  // 截取路由的id
  // console.log(route.path);
  // console.log(route.path.split("/"));
});
</script>
<style scoped lang="scss">
:deep(.el-transfer-panel) {
  width: 500px;
  // height: auto;
}
:deep(.el-transfer) {
  --el-transfer-panel-body-height: 700px;
}
</style>