<template>
  <el-row :gutter="10">
    <el-col :span="6">
      <el-button type="primary" @click="addModel = true; modelAction = true">新增模型</el-button>
      <el-button type="default" @click="isModelGroup = true; modelGroupAction = true">新增分组</el-button>
    </el-col>
  </el-row>
  <!-- <el-divider /> -->

  <div v-for="gd, index in grouplist" :key="index" class="groupClass">

    <el-row>
      <!-- <el-icon>
        <Guide />
      </el-icon> -->

      <h2>{{ gd.name }}</h2>
      <div class="groupCountClass">
        <span class="number">{{ groupCardCount[gd.id] }}</span>
        <div class="operation_show groupCountClass">
          <el-space v-if="!gd.built_in">
            <el-icon :size="20" @click="addModelFromGroup(gd.id)">
              <CirclePlusFilled />
            </el-icon>
            <el-icon :size="20" @click="editModelGroup(gd)">
              <Edit />
            </el-icon>
            <el-icon :size="20" @click="deleteModelGroup(gd.id)">
              <DeleteFilled />
            </el-icon>
          </el-space>
          <el-tooltip effect="dark" content="内置分组无法修改" placement="right" v-else>
            <el-icon :size="20">
              <InfoFilled />
            </el-icon>
          </el-tooltip>

        </div>

      </div>


    </el-row>
    <!-- <el-divider /> -->

    <!-- <el-row> -->
    <el-space wrap :size="30" alignment="flex-start">

      <el-card shadow="hover" v-for="data, index in groupModel[gd.id]" :key="index" class="modelCard"
        @click="goToModelInfo(data)">
        <el-space size="large">
          <el-icon :size="30">
            <component :is="data.icon" />
          </el-icon>
          <el-space direction="vertical" size="small">
            <el-text tag="b">
              {{ data.verbose_name }}
            </el-text>

            <el-text>

              {{ data.name }}
            </el-text>

          </el-space>
        </el-space>
      </el-card>

    </el-space>

    <!-- </el-row> -->

    <!-- 新增模型的对话框 -->

    <!-- <el-icon><Ticket /></el-icon> -->

  </div>
  <!-- <el-dialog v-model="addModel" title="新增模型" width="500" :before-close="handleClose">
    <el-form ref="modelFormRef" style="max-width: 600px" :model="modelForm" :rules="rules" label-width="auto"
      class="demo-modelForm" status-icon>

      <el-form-item label="模型图标" prop="icon">
        <el-button @click="isShowIconSelect" :icon="modelForm.icon"></el-button>
        <iconSelectCom v-model:isShow="isShow" v-model:iconName="modelForm.icon" />

      </el-form-item>
      <el-form-item label="唯一标识" prop="obj_id">
        <el-input v-model="modelForm.obj_id" placeholder="请输入模型的唯一标识" />
      </el-form-item>
      <el-form-item label="模型名称" prop="name">
        <el-input v-model="modelForm.name" />
      </el-form-item>
      <el-form-item label="所属分组" prop="cgroup">
        <el-select v-model="modelForm.cgroup" placeholder="选择分组">
          <el-option :label="data.name" :value="data.id" v-for="data, index in grouplist" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="addModelCance()">取消</el-button>
        <el-button type="primary" @click="modelCommit(modelFormRef)">
          确认
        </el-button>
      </div>
    </template>
</el-dialog> -->
  <!-- 模型组 -->
  <el-dialog v-model="isModelGroup" title="新增模型组" width="500" :before-close="handleCloseModelGroup">
    <el-form ref="modelGroupFormRef" style="max-width: 600px" :model="modelGroupForm" :rules="modelGroupRules"
      label-width="auto" class="demo-modelForm" status-icon>
      <el-form-item label="模型组标识" prop="obj_id">
        <el-input v-model="modelGroupForm.obj_id" :disabled="!modelGroupAction" />
      </el-form-item>
      <el-form-item label="分组名称" prop="name">
        <el-input v-model="modelGroupForm.name" />
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="modelGroupCance()">取消</el-button>
        <el-button type="primary" @click="modelGroupCommit(modelGroupFormRef)">
          确认
        </el-button>
      </div>
    </template>
  </el-dialog>

</template>

<script setup lang="ts">
import { ref, getCurrentInstance, onMounted, watch, computed, reactive } from 'vue'
import { vDraggable } from 'vue-draggable-plus'
import { ElMessageBox, ElMessage } from 'element-plus'
import type { ComponentSize, FormInstance, FormRules } from 'element-plus'
import { fa } from 'element-plus/es/locale/index.mjs';
import iconSelectCom from '../../components/iconSelectCom.vue';

const { proxy } = getCurrentInstance();
const modelGroupAction = ref(false)
const modelAction = ref(false)

// const iconName = ref('ElemeFilled')

// const grouplist = ref([
//   { id: 1, obj_id: 'hostmanage', name: '主机管理' ,edit:false},
//   { id: 2, obj_id: 'network', name: '网络设备',edit:false },
//   { id: 3, obj_id: 'other', name: '其他',edit:true}
// ])

// const modelist = ref([
//   { id: 1, obj_id: "host", isDelete: false, group: 1, name: "主机" ,icon:"Box" },

//   { id: 2, obj_id: "switch", isDelete: false, group: 2, name: "交换机" ,icon:"Box"},
//   { id: 3, obj_id: "security", isDelete: false, group: 2, name: "安全设备",icon:"Box" },

//   { id: 4, obj_id: "other", isDelete: true, group: 3, name: "其他" ,icon:"Box"}
// ])

const groupCardCount = computed(() => {
  let _tempGroupCardCount = {}
  modelist.value.forEach(item => {
    if (_tempGroupCardCount[item.model_group]) {
      _tempGroupCardCount[item.model_group] += 1
    } else {
      _tempGroupCardCount[item.model_group] = 1
    }
  })
  // console.log(_tempGroupCardCount)
  return _tempGroupCardCount
})
const groupModel = computed(() => {
  let _tempGroupCardCount = {}
  modelist.value.forEach(item => {
    if (_tempGroupCardCount[item.model_group]) {
      _tempGroupCardCount[item.model_group].push(item)
    } else {
      _tempGroupCardCount[item.model_group] = [item]
    }
  })
  // console.log(_tempGroupCardCount)
  return _tempGroupCardCount
})

const addModel = ref(false)
const addModelCance = () => {
  addModel.value = false
  modelFormRef.value.resetFields();
}
// 获取模型组
const grouplist = ref([])
const getCiModelGroupList = async () => {

  let res = await proxy.$api.getCiModelGroup()
  console.log(res)
  grouplist.value = res.data.results
  console.log(grouplist.value)
}
// 获取模型CI
const modelist = ref([])
const getCiModelList = async () => {
  let res = await proxy.$api.getCiModel()
  console.log(res)
  modelist.value = res.data.results
}

// 模型表单
interface ModelForm {
  obj_id: string,
  name: string,
  cgroup: string,
  icon: string,
  edit: boolean
}
const modelForm = reactive<ModelForm>({
  obj_id: '',
  name: '',
  cgroup: '',
  icon: 'ElemeFilled',
  edit: true

})
const modelFormRef = ref<FormInstance>()

const rules = reactive<FormRules<ModelForm>>({
  obj_id: [
    { required: true, message: '请输入模型标识', trigger: 'blur' },
    { pattern: /^[a-z][a-z_]{3,20}$/, trigger: 'blur', message: '以英文字符开头,可以使用英文,下划线,长度3-20 ', required: true }

    // { min: 3, max: 5, message: 'Length should be 3 to 5', trigger: 'blur' },
  ],
  name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' },

  ],
  cgroup: [
    { required: true, message: '请选择分组', trigger: 'blur' },

  ]
})
// 模型动作

const modelCommit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate(async (valid, fields) => {
    if (valid) {
      if (modelAction.value) {
        // 添加
        let res = await proxy.$api.addCiModel(modelForm)
        console.log(res)
        // console.log(123)
        if (res.status == "200") {
          ElMessage({ type: 'success', message: '添加成功', });
          // 重置表单
          addModel.value = false
          resetForm(formEl);
          getCiModelList();
          // 获取数据源列表        
        } else {
          ElMessage({ showClose: true, message: '添加失败:' + JSON.stringify(res.data), type: 'error', })
        }
      } else {
        console.log('不在这里更新')
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
    } else {
      console.log('error submit!', fields)
    }
  })
}

const handleClose = (done: () => void) => {
  ElMessageBox.confirm('是否确认关闭?')
    .then(() => {
      done()
      resetForm(modelFormRef.value);
    })
    .catch(() => {
      // catch error
    })
}


// 模型组
interface ModelGroupForm {
  obj_id: string,
  name: string,
  edit: boolean
}
const modelGroupForm = reactive<ModelGroupForm>({
  obj_id: '',
  name: '',
  edit: true
})
const modelGroupRules = reactive<FormRules<ModelGroupForm>>({
  obj_id: [
    { required: true, message: '请输入唯一标识', trigger: 'blur' },
    { pattern: /^[a-z][\w\d]{4,20}$/, trigger: 'blur', message: '以英文字符开头,可以使用英文,数字,下划线,长度4-20 ', required: true }

  ],
  name: [
    { required: true, message: '请输入组名称', trigger: 'blur' },
  ],

})
const modelGroupFormRef = ref<FormInstance>()

const isModelGroup = ref(false)
const modelGroupCance = () => {
  isModelGroup.value = false
  modelGroupFormRef.value.resetFields();
}

const nowGroupId = ref('')
const modelGroupCommit = async (formEl: FormInstance | undefined) => {
  // 提交表单
  if (!formEl) return
  await formEl.validate(async (valid, fields) => {
    if (valid) {
      if (modelGroupAction.value) {
        // 添加
        let res = await proxy.$api.addCiModelGroup(modelGroupForm)
        console.log(res)
        // console.log(123)
        if (res.status == "201") {
          ElMessage({ type: 'success', message: '添加成功', });
          // 重置表单
          isModelGroup.value = false
          resetForm(formEl);
          getCiModelGroupList();
          // 获取数据源列表        
        } else {
          ElMessage({ showClose: true, message: '添加失败:' + JSON.stringify(res.data), type: 'error', })
        }
      } else {
        let res = await proxy.$api.updateCiModelGroup({ id: nowGroupId.value, ...modelGroupForm })
        console.log(res)
        // console.log(123)
        if (res.status == "200") {
          ElMessage({ type: 'success', message: '更新成功', });
          // 重置表单
          isModelGroup.value = false
          resetForm(formEl);
          getCiModelGroupList();
          // 获取数据源列表        
        } else {
          ElMessage({ showClose: true, message: '更新失败:' + JSON.stringify(res.data), type: 'error', })
        }
      }
      // console.log('submit!')

    } else {
      console.log('error submit!', fields)
    }
  })


}

const handleCloseModelGroup = (done: () => void) => {
  ElMessageBox.confirm('是否确认关闭?')
    .then(() => {
      done()
      modelGroupFormRef.value.resetFields();
    })
    .catch(() => {
      // catch error
    })
}

// 重置表单
const resetForm = (formEl: FormInstance | undefined) => {
  if (!formEl) return
  formEl.resetFields()
}


// 模型组悬停时的图标操作
// 新增模型
const addModelFromGroup = (params) => {
  modelForm.cgroup = params
  addModel.value = true
}
// 修改
const editModelGroup = (config) => {
  // ElMessage({
  //   message: '修改组名.',
  //   type: 'warning',
  // })
  // 打开弹窗
  isModelGroup.value = true
  // 编辑模式
  modelGroupAction.value = false
  modelGroupForm.obj_id = config.obj_id
  modelGroupForm.name = config.name
  nowGroupId.value = config.id
  // modelGroupCommit(modelGroupFormRef.value)


}
// 删除组
const deleteModelGroup = (config) => {
  // ElMessage({
  //   message: '删除组.',
  //   type: 'error',
  // })
  ElMessageBox.confirm(
    '是否确认删除?',
    '删除组',
    {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning',
      draggable: true,

    }
  ).then(async () => {
    console.log(config)

    console.log(groupCardCount.value[config])
    // 判断是否有模型，有则不能删除
    if (groupCardCount.value[config] === 0) {
      ElMessage({
        type: 'error',
        message: '请先删除模型组内的模型后再删除组！',
      })
      return
    }
    // 发起删除请求
    let res = await proxy.$api.deleteCiModelGroup(config)
    // 
    // let res = {status:204}
    if (res.status == 204 || res.status == 200) {
      ElMessage({
        type: 'success',
        message: '删除成功',
      })

    } else {
      ElMessage({
        type: 'error',
        message: '删除失败',
      })
    }
    // 重新加载页面数据
    getCiModelGroupList();
    console.log(1111)
  })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '取消删除',
      })
    })

}
// 模型图标选择
const isShow = ref(false)

const isShowIconSelect = () => {
  isShow.value = true
}

import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
const router = useRouter();
const store = useStore()
const route = useRoute()
console.log(route)
// 跳转路由详情
const goToModelInfo = (params) => {
  console.log(params)
  // console.log(store.state.getMenuInfo())
  // // 获取详情页面的菜单信息
  // let res = proxy.$api.getMenuList()
  let modelInfoParam = {
    obj_id_id: params.id,
    label: store.state.currentMenu + '-' + params.name,
    name: route.name + "_info",
    path: route.path + '/' + params.obj_id,
    is_info: true,
    // query:{id:params.id,tab:'field'}
    query: { id: params.id, tab: 'field' }
  }
  console.log(modelInfoParam)
  // 路由跳转
  router.push({
    path: route.path + '/' + params.obj_id,
    query: { id: params.id, tab: 'field' }
  });
  // store更新

  store.commit("selectMenu", modelInfoParam)
}




// onmunt
onMounted(() => {
  getCiModelGroupList();
  getCiModelList();
})
</script>

<style scoped>
.modelCard {
  width: 160px;
}

.number {
  display: block;
  border-radius: 30px;
  background-color: var(--el-color-primary-light-3);
  width: 20px;
  height: 20px;
  line-height: 20px;
  text-align: center;
  vertical-align: middle;
  color: #fff;

}

.groupCountClass {
  display: flex;
  align-items: center;
  align-content: center;
  margin-left: 10px;
}

.operation_show {
  display: none;
}

.groupClass:hover .operation_show {
  display: flex;
}
</style>
