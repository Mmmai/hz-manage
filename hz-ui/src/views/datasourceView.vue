<template>
  <!-- <el-button type="primary" @click="dialogVisible = true;componentId = lokiSource;isAdd = true">添加  </el-button> -->
  <div class="card">
    <el-dropdown
      style="margin-left: 15px; margin-right: 15px"
      @command="handleCommand"
    >
      <el-button
        type="primary"
        v-permission="`${route.name?.replace('_info', '')}:add`"
      >
        添加<el-icon class="el-icon--right"><arrow-down /></el-icon>
      </el-button>

      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="loki">loki</el-dropdown-item>
          <el-dropdown-item command="zabbix">zabbix</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <el-divider />
    <!-- 数据源列表展示 -->
    <div class="context-body">
      <div class="el-card-div" v-for="(v, i) in dataSourceList" :key="i">
        <el-card style="width: 250px" shadow="hover" @click="edit(v)">
          <div class="el-card-context">
            <div
              style="
                display: flex;
                justify-content: space-between;
                align-content: center;
              "
            >
              <img
                :src="getImgPath('loki_source.svg')"
                alt="Icon"
                style="width: 30px; height: 30px"
                v-if="v.source_type == 'loki'"
              />
              <img
                :src="getImgPath('zabbix_source.svg')"
                alt="Icon"
                style="width: 30px; height: 30px"
                v-else-if="v.source_type == 'zabbix'"
              />
              <span style="margin: 10px 0px 0px 10px">
                {{ v.source_name }}</span
              >
            </div>

            <!-- <el-icon v-if="v.isDefault"><Flag /></el-icon> -->
            <el-button type="success" size="small" round v-if="v.isDefault"
              >默认</el-button
            >
          </div>
        </el-card>
      </div>
    </div>
  </div>
  <!-- 弹出框 -->
  <el-dialog
    v-model="dialogVisible"
    :title="dataSourceType"
    width="500"
    :before-close="handleClose"
  >
    <!-- <span @click=changeCom>This is a message</span> -->

    <component
      :is="componentId"
      v-model:formData="formLabelAlign"
      ref="childRef"
    ></component>

    <template #footer>
      <div class="dialog-footer" v-if="!isAdd">
        <el-button type="danger" @click="deleteAction">删除</el-button>
        <el-button
          type="success"
          @click="testDataSource"
          v-loading="testLoading"
          >测试</el-button
        >

        <el-button type="primary" @click="updateAction">更新</el-button>
      </div>
      <div class="dialog-footer" v-else>
        <el-button type="success" @click="testDataSource">测试</el-button>
        <el-button type="primary" @click="submitAction">添加</el-button>
      </div>
    </template>
  </el-dialog>
  <!-- <el-select v-model="value" filterable reserve-keyword placeholder="Please enter a keyword" style="width: 240px" remote
    :remote-method="remoteSearch" :loading="searchLoading">
    <el-option v-for="item in renderOptions" :key="item.value" :label="item.label" :value="item.value" />
    <template v-if="needShowMore" #footer>
      <div class="show-more" @click="showMore">
        加载更多
      </div>
    </template>
  </el-select> -->
  <!-- <el-select v-model="value" filterable remote clearable     placeholder="Select"
    reserve-keyword  style="width: 240px" 
    :remote-method="remoteSearch(value)" >
    <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value" />
    </el-select> -->

  <!-- <template v-if="needShowMore" #footer>
      <div class="show-more" @click="showMore">
        加载更多
      </div>
    </template> -->
</template>
<script lang="ts" setup>
import {
  ref,
  reactive,
  shallowRef,
  getCurrentInstance,
  onMounted,
  defineAsyncComponent,
  computed,
  nextTick,
} from "vue";
// import { Delete, Filter,CirclePlus } from '@element-plus/icons-vue'
import lokiSource from "@/components/datasource/lokiSource.vue";
import zabbixSource from "../components/datasource/zabbixSource.vue";
import { debounce, method } from "lodash";
import { ElMessageBox, ElMessage } from "element-plus";
defineOptions({ name: "datasource" });

// const ComponentA = defineAsyncComponent(() => import("../components/datasource/lokiSource.vue"))
const { proxy } = getCurrentInstance();
import { useRoute } from "vue-router";
import { RefSymbol } from "@vue/reactivity";
const route = useRoute();
const testLoading = ref(false);
const getImgPath = (name: string): any => {
  return new URL(`/src/assets/images/${name}`, import.meta.url).href;
};
// const components = import.meta.glob('../components/datasource/*.vue')
// const componentList: Record<string, any> = reactive({});
// Object.entries(components).forEach(async ([key, val]) => {
//   console.log(key)
//   console.log(val)
//   componentList[key] = defineAsyncComponent(val);
//   });

const dialogVisible = ref(false);
const isAdd = ref(false);
const componentId = shallowRef("");
// 重置表单
const resetForm = () => {
  Object.keys(formLabelAlign).forEach((key) => {
    formLabelAlign[key] = initFormLabelAlign[key];
  });
};
// 关闭弹窗
const handleClose = (done: () => void) => {
  ElMessageBox.confirm("是否关闭?")
    .then(() => {
      resetForm();
      console.log(formLabelAlign);
      done();
    })
    .catch(() => {
      // catch error
    });
};
const initFormLabelAlign = {
  source_name: "",
  source_type: "",
  url: "",
  isAuth: false,
  isDefault: false,
  isUsed: true,
  username: "",
  password: "",
};
const formLabelAlign = reactive({
  source_name: "",
  source_type: "",
  url: "",
  isAuth: false,
  isDefault: false,
  isUsed: true,
  username: "",
  password: "",
});

const dataSourceType = ref("Loki");
// 添加按钮的动作
const handleCommand = (command) => {
  if (command == "loki") {
    componentId.value = lokiSource;
    formLabelAlign.source_type = "loki";
    dataSourceType.value = "Loki";
  } else if (command == "zabbix") {
    componentId.value = zabbixSource;
    formLabelAlign.source_type = "zabbix";
    dataSourceType.value = "Zabbix";
  }
  dialogVisible.value = true;
  isAdd.value = true;
};
const submitAction = async () => {
  let res = await proxy.$api.dataSourceAdd(formLabelAlign);
  console.log(res);
  if (res.data.code == "200") {
    ElMessage({
      type: "success",
      message: "添加成功",
    });
    // 重置表单
    resetForm();
    dialogVisible.value = false;
    getDataSource();
    // 获取数据源列表
  } else {
    ElMessage({
      showClose: true,
      message: "添加失败:" + JSON.stringify(res.data),
      type: "error",
    });
  }
};
const testDataSource = async () => {
  testLoading.value = true;

  let res = await proxy.$api.lokiLabelGet({ url: formLabelAlign.url });
  console.log(res);
  if (res.timeout) {
    ElMessage({
      message: `数据源异常，${res.message}`,
      type: "error",
    });
  } else {
    if (res.status == 200) {
      ElMessage({
        message: "数据源可用~",
        type: "success",
      });
    } else {
      ElMessage({
        message: `数据源异常，${res.statusText}`,
        type: "error",
      });
    }
  }
  nextTick(() => {
    testLoading.value = false;
  });
};
// 获取已添加的数据源
const dataSourceList = ref([]);
const getDataSource = async () => {
  let res = await proxy.$api.dataSourceGet();
  console.log(res);
  dataSourceList.value = res.data.results;
};
// 点击编辑时的按钮
const nowId = ref("");
const edit = (config) => {
  dialogVisible.value = true;
  isAdd.value = false;
  if (config.source_type == "loki") {
    componentId.value = lokiSource;
    dataSourceType.value = "Loki";
  } else if (config.source_type == "zabbix") {
    componentId.value = zabbixSource;
    dataSourceType.value = "Zabbix";
  }
  // formLabelAlign.
  nowId.value = config.id;
  console.log(nowId.value);
  let filterArray = ["id", "update_time", "create_time"];
  Object.keys(config).forEach((key) => {
    if (filterArray.indexOf(key) === -1) {
      formLabelAlign[key] = config[key];
    }
  });
};
// 更新按钮
const updateAction = async () => {
  let res = await proxy.$api.dataSourceUpdate({
    id: nowId.value,
    ...formLabelAlign,
  });
  console.log(res);
  if (res.status == 200) {
    ElMessage({
      type: "success",
      message: "更新成功",
    });
    // 重置表单，关闭弹出框,重新加载数据
    resetForm();
    dialogVisible.value = false;
    getDataSource();
  } else {
    ElMessage({
      type: "error",
      message: "更新失败",
    });
  }
  resetForm();
};
// 删除按钮
const deleteAction = (row) => {
  ElMessageBox.confirm("是否确认删除?", "Warning", {
    confirmButtonText: "确认删除",
    cancelButtonText: "取消",
    type: "warning",
    draggable: true,
  })
    .then(async () => {
      // 发起删除请求
      let res = await proxy.$api.dataSourceDel(nowId.value);
      if (res.status == 204) {
        ElMessage({
          type: "success",
          message: "删除成功",
        });
        // 重置表单，关闭弹出框,重新加载数据
        resetForm();
        dialogVisible.value = false;
        getDataSource();
      } else {
        ElMessage({
          type: "error",
          message: "删除失败",
        });
      }
    })
    .catch(() => {
      ElMessage({
        type: "info",
        message: "Delete canceled",
      });
    });
};
//渲染时加载
onMounted(async () => {
  await getDataSource();
  //  await
});
</script>
<style scoped>
.context-body {
  height: 90%;
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  align-content: flex-start;
  align-items: flex-start;
}

.el-card-context {
  display: flex;
  justify-content: space-between;
}

.el-card-div {
  margin: 10px 10px 10px 10px;
}

.show-more {
  display: flex;
  height: 24px;
  align-items: center;
  justify-content: center;
  color: #888888;
  cursor: pointer;
}
</style>