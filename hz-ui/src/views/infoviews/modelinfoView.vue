<template>
  <div class="card">
    <el-scrollbar>
      <el-row class="cimodelinfo" justify="space-between">
        <el-col :span="20">
          <el-space :size="30" style="width: 40%">
            <el-button size="large" circle disabled style="margin: 10px">
              <!-- <Icon :icon="ciModelInfo.icon"></Icon> -->
              <iconifyOffline :icon="ciModelInfo?.icon" />
            </el-button>

            <!-- </div> -->

            <el-text
              >唯一标识: &nbsp;&nbsp;<el-text tag="b">
                {{ ciModelInfo.name }}</el-text
              >
            </el-text>

            <el-text
              >名称:&nbsp;&nbsp;
              <el-text tag="b">{{ ciModelInfo.verbose_name }}</el-text>
            </el-text>

            <el-text
              >实例数:&nbsp;&nbsp;
              <el-link type="primary" tag="b" disabled href="/#/cmdb/cidata">{{
                ciModelInfo.instance_count
              }}</el-link>
            </el-text>
          </el-space>
        </el-col>
        <el-col
          :span="2"
          style="display: flex; align-items: center; justify-content: center"
        >
          <el-space alignment="flex-end">
            <el-button
              v-permission="`${route.name?.replace('_info', '')}:delete`"
              :disabled="ciModelInfo.built_in"
              icon="Delete"
              @click="deleteCiModel(ciModelInfo.id)"
              circle
            />
            <el-button
              v-permission="`${route.name?.replace('_info', '')}:edit`"
              :disabled="ciModelInfo.built_in"
              icon="Edit"
              @click="editCiModel(ciModelInfo)"
              circle
            />

            <!-- <el-icon :size="20" :disabled="ciModelInfo.built_in" ><Delete /></el-icon>
        <el-icon :size="20"  ><Edit /></el-icon> -->
          </el-space>
        </el-col>
      </el-row>
      <el-tabs
        v-model="tabName"
        type="card"
        class="demo-tabs"
        @tab-click="handleClick"
      >
        <el-tab-pane label="模型字段" name="field">
          <ciModelField ref="ciModelFieldRef" />
          <!-- @getModelField="setModelField" -->
        </el-tab-pane>
        <el-tab-pane label="唯一校验" name="verification">
          <ciModelUnique
            :modelId="modelId"
            :modelFieldLists="modelFieldLists"
            ref="ciModelUniqueRef"
          />
        </el-tab-pane>
        <!-- <el-tab-pane label="Role" verbose_name="third">Role</el-tab-pane>
    <el-tab-pane label="Task" verbose_name="fourth">Task</el-tab-pane> -->
      </el-tabs>
    </el-scrollbar>
  </div>

  <el-dialog
    v-model="addModel"
    title="编辑模型"
    width="500"
    :before-close="handleClose"
  >
    <el-form
      ref="modelFormRef"
      style="max-width: 600px"
      :model="modelForm"
      :rules="rules"
      label-width="auto"
      class="demo-modelForm"
      status-icon
    >
      <el-form-item label="模型图标" prop="icon">
        <el-button @click="isShowIconSelect" :icon="modelForm.icon"></el-button>
        <iconSelectCom
          v-model:isShow="isShow"
          v-model:iconName="modelForm.icon"
        />
      </el-form-item>
      <el-form-item label="唯一标识" prop="name">
        <el-input
          v-model="modelForm.name"
          placeholder="请输入模型的唯一标识"
          disabled
        />
      </el-form-item>
      <el-form-item label="模型名称" prop="verbose_name">
        <el-input v-model="modelForm.verbose_name" />
      </el-form-item>
      <el-form-item label="所属分组" prop="model_group">
        <el-select v-model="modelForm.model_group" placeholder="选择分组">
          <el-option
            :label="data.verbose_name"
            :value="data.id"
            :key="index"
            v-for="(data, index) in grouplist"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="addModelCance(modelFormRef)">取消</el-button>
        <el-button type="primary" @click="modelCommit(modelFormRef)">
          确认
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import * as ElIcons from "@element-plus/icons-vue";
import {
  onMounted,
  reactive,
  getCurrentInstance,
  ref,
  toRefs,
  onActivated,
  watch,
  onUnmounted,
  onBeforeMount,
  computed,
} from "vue";
import iconSelectCom from "../../components/iconSelectCom.vue";
import { useStore } from "vuex";
import { useRouter, useRoute } from "vue-router";
const route = useRoute();
import useTabsStore from "@/store/tabs";
const tabsStore = useTabsStore();
import type { ComponentSize, FormInstance, FormRules } from "element-plus";
import ciModelField from "../../components/cmdb/ciModelField.vue";
import ciModelUnique from "../../components/cmdb/ciModelUnique.vue";

const ciModelUniqueRef = ref("");
const ciModelFieldRef = ref("");
const router = useRouter();
const store = useStore();
const { proxy } = getCurrentInstance();
import type { TabsPaneContext } from "element-plus";
const input = ref("");
// const addModel = ref(false)
// 获取模型组
const grouplist = ref([]);
const getCiModelGroupList = async () => {
  let res = await proxy.$api.getCiModelGroup();
  console.log(res);
  grouplist.value = res.data.results;
  console.log(grouplist.value);
};
const ciModelInfo = ref({});
const getModelInfo = async () => {
  let res = await proxy.$api.getCiModel(route.query, route.query.id);
  ciModelInfo.value = res.data.model;
};
// 子组件传递模型字段给父组件
const modelFieldLists = ref([]);
const setModelField = (params) => {
  modelFieldLists.value = params;
};

const handleClick = (tab: TabsPaneContext, event: Event) => {
  // console.log(tab)
  // console.log(tab.props.verbose_name)
  // console.log(route.path)
  // console.log(tabName.value)
  // 路由切换显示路由参数
  // router.push({ path: route.path, query: { id: route.query.id, verbose_name: route.query.verbose_name, tab: tab.props.name } })
  // 获取详情
  if (tab.props.name === "verification") {
    ciModelUniqueRef.value!.getTableData({ model: modelId.value });
  } else if (tab.props.name === "field") {
    // ciModelFieldRef.value!.getModelField();
  }
};
const tabName = ref("field");
// 监听路由的query，解决切换后停留在之前的标签页问题，现在默认让他显示field字段的页面，后续再优化把
// watch(route, (n) => {
//   // console.log(1111)
//   // console.log(222)
//   // console.log(n.query)
//   tabName.value = n.query.tab

// }, { deep: true })
// watch(() => route.query, (n) => {
//   if (n.query.tab) {
//     tabName.value = n.query.tab
//   }
// })
console.log(route);
const isShow = ref(false);

const isShowIconSelect = () => {
  isShow.value = true;
};
const iconName = ref("ElemeFilled");

const modelId = computed(() => {
  return ciModelInfo.value?.id;
});

// 获取CI模型属性
// const getCiModelInfo = async (params, id) => {
//   let res = await proxy.$api.getCiModel(params, id)
//   modelId.value = id
//   console.log(res)
//   ciModelInfo.value = res.data.model
//   console.log(ciModelInfo.value)

// }

// onActivated(()=>{
//   console.log('activated')
//   getCiModelInfo(route.query,route.query.id);

// })
// router.beforeRouteEnter((to, from, next) => {
//   // ...
//   console.log(111);
// }
// )

// 模型编辑和删除
// 模型表单
interface ModelForm {
  name: string;
  verbose_name: string;
  model_group: string;
  icon: string;
  built_in: boolean;
  // create_user: string,
  update_user: string;
}
const modelForm = reactive<ModelForm>({
  name: "",
  verbose_name: "",
  model_group: "",
  icon: "ElemeFilled",
  built_in: false,
  // create_user: 'admin',
  update_user: "admin",
});
const modelFormRef = ref<FormInstance>();

const rules = reactive<FormRules<ModelForm>>({
  name: [
    { required: true, message: "请输入模型标识", trigger: "blur" },
    {
      pattern: /^[a-z][a-z_]{3,20}$/,
      trigger: "blur",
      message: "以英文字符开头,可以使用英文,下划线,长度3-20 ",
      required: true,
    },

    // { min: 3, max: 5, message: 'Length should be 3 to 5', trigger: 'blur' },
  ],
  verbose_name: [
    { required: true, message: "请输入模型名称", trigger: "blur" },
  ],
  model_group: [{ required: true, message: "请选择分组", trigger: "blur" }],
});
// 模型动作
import { ElMessageBox, ElMessage } from "element-plus";
const modelAction = ref(false);

const addModel = ref(false);
const addModelCance = (formEl) => {
  addModel.value = false;
  resetForm(formEl);
};
const modelCommit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return;
  await formEl.validate(async (valid, fields) => {
    if (valid) {
      let res = await proxy.$api.updateCiModel({
        id: nowModelId.value,
        ...modelForm,
      });
      console.log(res);
      // console.log(123)
      if (res.status == "200") {
        ElMessage({ type: "success", message: "更新成功" });
        // 重置表单
        addModel.value = false;
        resetForm(formEl);
        getCiModelInfo(route.query, route.query.id);
        // 获取数据源列表
      } else {
        ElMessage({
          showClose: true,
          message: "添加失败:" + JSON.stringify(res.data),
          type: "error",
        });
      }
      // let res = await proxy.$api.updateCiModel({ id: nowGroupId.value, ...modelGroupForm })
      // console.log(res)
      // // console.log(123)
      // if (res.status == "200") {
      //   ElMessage({ type: 'success', message: '更新成功', });
      //   // 重置表单
      //   isModelGroup.value = false
      //   resetForm(formEl);
      //   getCiModelGroupList();
      //   // 获取数据源列表
      // } else {
      //   ElMessage({ showClose: true, message: '更新失败:' + JSON.stringify(res.data), type: 'error', })
      // }
    }
  });
};

const handleClose = (done: () => void) => {
  ElMessageBox.confirm("是否确认关闭?")
    .then(() => {
      done();
      resetForm(modelFormRef.value);
    })
    .catch(() => {
      // catch error
    });
};
// 重置表单
const resetForm = (formEl: FormInstance | undefined) => {
  if (!formEl) return;
  formEl.resetFields();
};

const deleteCiModel = (params) => {
  ElMessageBox.confirm("是否确认删除?", "删除组", {
    confirmButtonText: "确认删除",
    cancelButtonText: "取消",
    type: "warning",
    draggable: true,
  })
    .then(async () => {
      // 判断是否有模型，有则不能删除
      // if (groupCardCount.value[params] >>> 0) {
      //   ElMessage({
      //     type: 'error',
      //     message: '请先删除模型组内的模型后再删除组！',
      //   })
      //   return
      // }
      // 发起删除请求
      let res = await proxy.$api.deleteCiModel(params);
      //
      // let res = {status:204}
      if (res.status == 204) {
        ElMessage({
          type: "success",
          message: "删除成功",
        });
        // 刷新页面
        tabsStore.removeTabs(route.path, true);
        // router.push({ name: "model" });
        // router.go(-1)

        // nextTick(() => {
        //   location.reload();
        // });
        //
      } else {
        ElMessage({
          type: "error",
          message: "删除失败",
        });
      }
      // 重新加载页面数据
      // getCiModelGroupList();

      // console.log(1111)
    })
    .catch(() => {
      ElMessage({
        type: "info",
        message: "取消删除",
      });
    });
};

const nowModelId = ref("");
// 点击编辑按钮
const editCiModel = (params) => {
  console.log(params);
  modelForm.icon = params.icon;
  modelForm.verbose_name = params.verbose_name;
  modelForm.name = params.name;
  modelForm.model_group = params.model_group;
  modelForm.update_user = store.state.username;
  console.log(modelForm);
  addModel.value = true;
  nowModelId.value = params.id;
  getCiModelGroupList();
};

// 模型字段
// const ciModelFieldsRes = ref([])
const getModelField = async () => {
  let res = await proxy.$api.getCiModel(
    route.query,
    route.query.id + "/with_fields"
  );
  console.log(res);
  ciModelFieldsRes.value = res.data.field_groups;
};

// watch(route,async(n,o)=>{
//   console.log(n.fullPath,o.fullPath)
//   if (n.name == "model_info"){
//     await getCiModelInfo(route.query, route.query.id);
//     // await getCiModelGroupList();
//   // await getModelField();
//   }

// })

onMounted(async () => {
  console.log("onMount");
  // await getCiModelInfo(route.query, route.query.id)
  await getModelInfo();
  await ciModelFieldRef.value!.getModelField();
  await ciModelFieldRef.value!.getCiModelList();
  await ciModelFieldRef.value!.getRules();
  await ciModelFieldRef.value!.getModelFieldType();
  // modelForm.update_user = store.state.username
  // modelForm.create_user = store.state.username

  // await getCiModelInfo(route.query, route.query.id);
  // await getCiModelGroupList();
  // await getModelField();
});
// onActivated(async () => {
//   console.log("onActivated", route.path);
//   await getCiModelInfo(route.query, route.query.id);
//   // await getCiModelGroupList();
//   // await getModelField();
// })
// // onUpdated(async()=>{
//   console.log("onUpdated")
//   await getCiModelInfo(route.query, route.query.id);
//   await getCiModelGroupList();
//   await getModelField();

// })
onUnmounted(() => {
  console.log("onUnmounted");
});
onBeforeMount(() => {
  console.log("onBeforeMount");
});
</script>

<style scoped>
.el-descriptions {
  margin-top: 20px;
}

.cell-item {
  display: flex;
  align-items: center;
}

.margin-top {
  margin-top: 20px;
}

.iconStyle {
  margin-right: 8px;
}

.cimodelinfo {
  background-color: var(--el-color-primary-light-9);
  /* margin: 0 10px 0 10px; */
}

.ciIcon {
  margin: 20px;
  /* display: block; */
  border-radius: 30px;
  background-color: var(--el-color-primary-light-3);
}
</style>