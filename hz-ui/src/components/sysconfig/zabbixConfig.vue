<template>
  <div class="card">
    <el-button type="primary" @click="editAction" v-show="!isEdit"
      >编辑</el-button
    >
    <el-button @click="cancelAction" v-show="isEdit">取消</el-button>
    <el-button type="primary" @click="commit" v-show="isEdit">保存</el-button>
    <el-divider></el-divider>

    <el-form
      :model="paramForm"
      class="demo-form-inline"
      ref="formRef"
      label-width="auto"
      label-position="right"
      :rules="rules"
    >
      <!-- <el-form-item
        v-for="(item, index) in zabbixParamsArray"
        :key="index"
        :label="item.verbose_name"
        :prop="item.param_name"
      >
        <el-input v-if="isEdit" v-model="paramForm[item.param_name]"></el-input>
        <span v-else>{{ item.param_value }}</span>
      </el-form-item> -->
      <!-- <el-form-item
        v-for="(item, index) in zabbixParamsFormItem"
        :key="index"
        :label="zabbixParamsObjectByName[item]?.verbose_name"
        :prop="zabbixParamsObjectByName[item]?.param_name"
      >
        <div v-if="isEdit">
          <el-input
            v-model="paramForm[zabbixParamsObjectByName[item]?.param_name]"
            style="min-width: 120px; max-width: 400px"
          ></el-input>
        </div>

        <span v-else>{{ zabbixParamsObjectByName[item]?.param_value }}</span>
      </el-form-item> -->
      <el-form-item label="是否同步" prop="zabbix_is_sync">
        <el-switch
          style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949"
          :disabled="!isEdit"
          v-model="paramForm.zabbix_is_sync"
          active-value="1"
          inactive-value="0"
        />
      </el-form-item>
      <div v-if="paramForm.zabbix_is_sync === '1'">
        <el-form-item
          :prop="item"
          v-for="(item, index) in zabbixParamsFormItem"
          :key="index"
        >
          <template #label>
            <el-space :size="2">
              <el-text tag="b"
                >{{ zabbixParamsObjectByName[item]?.verbose_name }}:
              </el-text>
              <el-tooltip
                :content="zabbixParamsObjectByName[item]?.description"
                placement="right"
                effect="dark"
                v-if="
                  zabbixParamsObjectByName[item]?.description.length != 0
                    ? true
                    : false
                "
              >
                <el-icon>
                  <Warning />
                </el-icon>
              </el-tooltip>
            </el-space>
          </template>
          <el-input
            v-if="isEdit"
            v-model="paramForm[item]"
            style="min-width: 80px; max-width: 400px"
            :type="item.includes('password') ? 'password' : 'text'"
            :show-password="item.includes('password')"
          ></el-input>
          <div v-else>
            <span v-if="item.includes('password')">{{
              "*".repeat(zabbixParamsObjectByName[item]?.param_value.length)
            }}</span>
            <span v-else>{{
              zabbixParamsObjectByName[item]?.param_value
            }}</span>
          </div>
        </el-form-item>
        <!-- <el-form-item label="zabbix服务端ip" prop="zabbix_server">
          <el-input
            v-if="isEdit"
            v-model="paramForm.zabbix_server"
            style="min-width: 120px; max-width: 400px"
          ></el-input>
          <span v-else>{{
            zabbixParamsObjectByName?.zabbix_server?.param_value
          }}</span>
        </el-form-item>
        <el-form-item label="用户名" prop="zabbix_username">
          <el-input
            v-if="isEdit"
            v-model="paramForm.username"
            style="min-width: 120px; max-width: 400px"
          ></el-input>
          <span v-else>{{
            zabbixParamsObjectByName?.zabbix_username?.param_value
          }}</span>
        </el-form-item>

        <el-form-item label="密码" prop="zabbix_password">
          <el-input
            v-if="isEdit"
            v-model="paramForm.password"
            style="min-width: 120px; max-width: 400px"
          ></el-input>
          <span v-else>{{
            zabbixParamsObjectByName?.zabbix_password?.param_value
          }}</span>
        </el-form-item>

        <el-form-item label="主机模板" prop="zabbix_host_template">
          <el-input
            v-if="isEdit"
            v-model="paramForm.zabbix_host_template"
            style="min-width: 120px; max-width: 400px"
          ></el-input>
          <span v-else>{{
            zabbixParamsObjectByName?.zabbix_host_template?.param_value
          }}</span>
        </el-form-item>
        <el-form-item label="网络监控模板" prop="zabbix_network_template">
          <el-input
            v-if="isEdit"
            v-model="paramForm.zabbix_network_template"
            style="min-width: 120px; max-width: 400px"
          ></el-input>
          <span v-else>{{
            zabbixParamsObjectByName?.zabbix_network_template?.param_value
          }}</span>
        </el-form-item>
        <el-form-item label="token注销时间(s)" prop="zabbix_interval">
          <el-input
            v-if="isEdit"
            v-model="paramForm.zabbix_interval"
            style="min-width: 80px; max-width: 200px"
          ></el-input>
          <span v-else>{{
            zabbixParamsObjectByName?.zabbix_interval?.param_value
          }}</span>
        </el-form-item> -->
      </div>
      <!-- <el-form-item>
        <el-button type="primary" @click="onSubmit">更新</el-button>
      </el-form-item> -->
    </el-form>
  </div>
</template>

<script lang="ts" setup>
import { RefreshRight, Warning } from "@element-plus/icons-vue";
import {
  ref,
  computed,
  watch,
  getCurrentInstance,
  onMounted,
  reactive,
  nextTick,
} from "vue";
import { v1 as uuidv1, v4 as uuidv4 } from "uuid";
const { proxy } = getCurrentInstance();
import { useStore } from "vuex";
import { ElLoading, ElNotification, ElMessage } from "element-plus";

const store = useStore();
import useConfigStore from "@/store/config";
const configStore = useConfigStore();
const isEdit = ref(false);
const zabbixParamsArray = ref([]);
const zabbixParamsFormItem = [
  // "zabbix_is_sync",
  "zabbix_url",
  "zabbix_server",
  "zabbix_username",
  "zabbix_password",
  "zabbix_host_template",
  "zabbix_ipmi_template",
  "zabbix_network_template",
  "zabbix_interval",
];
const formRef = ref(null);
const paramForm = reactive({
  zabbix_is_sync: "0",
  zabbix_url: null,
  zabbix_server: null,
  zabbix_username: null,
  zabbix_password: null,
  zabbix_ipmi_template: null,
  zabbix_host_template: null,
  zabbix_network_template: null,
  zabbix_interval: 0,
});
const zabbixParamsObjectByName = computed(() => {
  let tmpObj = new Object();
  zabbixParamsArray.value?.forEach((item) => {
    tmpObj[item.param_name] = item;
  });
  return tmpObj;
});
// watch(zabbixParamsObjectByName, (n) => {
//   console.log(n);
// });
const getParams = async () => {
  let res = await proxy.$api.getSysConfig({ param_name: "zabbix" });
  console.log(res.data);
  zabbixParamsArray.value = res.data;
  res.data.forEach((item) => {
    paramForm[item.param_name] = item.param_value;
  });
};

const editAction = () => {
  isEdit.value = true;
  console.log(isEdit.value);
  nextTick(() => {
    zabbixParamsArray.value?.forEach((item) => {
      paramForm[item.param_name] = item.param_value;
    });
  });
};
const cancelAction = () => {
  isEdit.value = false;
  nextTick(() => {
    // formRef.value!.resetFields();
    getParams();
  });
};
const commit = async () => {
  await formRef.value!.validate(async (valid, fields) => {
    if (valid) {
      let res = await proxy.$api.updateZabbixConfig(paramForm);
      if (res.status == 200) {
        ElMessage({ type: "success", message: "更新成功" });
        nextTick(() => {
          isEdit.value = false;
          getParams();
        });
      } else {
        ElMessage({ type: "error", message: `${res.data}` });
      }
    }
  });
};
const validateUrl = (rule: any, value: any, callback: any) => {
  const urlRegex =
    /^(https?):\/\/((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))([\/\w .-]*)*\/?$/;
  if (value === "") {
    callback(new Error("url地址不正确"));
  } else if (!urlRegex.test(value)) {
    callback(new Error("url地址不符合正则表达式"));
  } else {
    callback();
  }
};
const validateInt = (rule: any, value: any, callback: any) => {
  const urlRegex = /^\d+$/;
  if (value === "") {
    callback(new Error("不能为空"));
  } else if (!urlRegex.test(value)) {
    callback(new Error("不符合正则表达式"));
  } else {
    callback();
  }
};
// 校验规则
const rules = reactive({
  zabbix_url: [
    {
      required: true,
      message: "请输入正确格式的zabbix接口地址",
      trigger: "blur",
    },
    { validator: validateUrl, trigger: "blur" },
  ],
  zabbix_server: [
    {
      required: true,
      message: "不能为空",
      trigger: "blur",
    },
  ],
  zabbix_username: [
    {
      required: true,
      message: "不能为空",
      trigger: "blur",
    },
  ],
  zabbix_password: [
    {
      required: true,
      message: "不能为空",
      trigger: "blur",
    },
  ],
  zabbix_interval: [
    {
      required: true,
      message: "不能为空",
      trigger: "blur",
    },
    { validator: validateInt, trigger: "blur" },
  ],
});

onMounted(() => {
  getParams();
});
</script>
<style scoped lang="scss">
</style>