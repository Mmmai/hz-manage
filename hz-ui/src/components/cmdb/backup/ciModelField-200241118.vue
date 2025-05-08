<template>
  <!-- 获取模型详细信息的接口在这里调度 -->
  <div>
    <el-collapse v-model="activeArr">
      <el-collapse-item :name="fieldGroup.verbose_name" v-for="fieldGroup, index in ciModelFieldsList" :key="index">
        <template #title class="groupClass">
          <!-- <el-icon class="header-icon">
            <info-filled />
          </el-icon> -->
          <el-text tag="b" size="large">{{ fieldGroup.verbose_name }}</el-text>
          <div class="operation_show">
            <el-space v-if="!fieldGroup.built_in">
              <!-- <el-icon :size="20" @click="addModelFromGroup(fieldGroup.id)">
              <CirclePlusFilled />
            </el-icon> -->
              <el-tooltip class="box-item" effect="dark" content="编辑" placement="top">
                <!-- <el-icon  size="large" @click.stop="editModelFieldGroup(fieldGroup)">
              <Edit />
            </el-icon> -->
                <el-button size="small" @click.stop="editModelFieldGroup(fieldGroup)" :icon="Edit" circle></el-button>
              </el-tooltip>
              <el-tooltip class="box-item" effect="dark" content="删除" placement="top">
                <el-button size="small" @click.stop="deleteModelFieldGroup(fieldGroup.id)" :icon="Delete"
                  circle></el-button>
              </el-tooltip>
              <!-- 
            <el-icon size="large" @click.stop="deleteModelFieldGroup(fieldGroup.id)">
              <DeleteFilled />
            </el-icon> -->
            </el-space>
          </div>
        </template>
        <div>
          <el-space wrap :size="10" alignment="flex-start">

            <div v-for="data, index in fieldGroup.fields" :key="index">
              <el-tooltip effect="light" content="点击编辑字段" placement="top">

                <el-card shadow="hover" class="modelFieldCard" :class="data.built_in ? 'isBuiltClass' : ''" 
                  @click="editModelField(data)"
                >
                  <el-text tag="b">
                    {{ data.verbose_name }}
                  </el-text>
                  <el-row justify="space-between">
                    <el-tooltip class="box-item" effect="light" :content="data.name" placement="bottom">

                      <el-col :span="16" class="describe-class"><el-text> {{ data.name }} </el-text></el-col>
                    </el-tooltip>
                    <el-col :span="7"><el-text> {{ data.type }} </el-text></el-col>
                  </el-row>
                </el-card>
              </el-tooltip>

            </div>
            <div>
              <el-card class="modelFieldCard " style="align-items: center;justify-content: center;" @click="addModelField(fieldGroup)">
                <el-text type="primary" >+ 添加字段</el-text>

              </el-card>
            </div>
          </el-space>
        </div>
      </el-collapse-item>
    </el-collapse>
    <el-row style="margin-top: 10px;">
      <el-col>
        <el-button bg text @click="addModelFieldGroup(modelInfo)">添加分组</el-button>

      </el-col>

    </el-row>
  </div>
  <!-- 模型字段分组弹窗 -->
  <el-dialog v-model="isModelFieldGroup" :title="diaName + '字段分组'" width="500" :before-close="handleCloseModelFieldGroup">
    <el-form ref="groupFormRef" style="max-width: 600px" :model="modelFieldGroupForm"
      :rules="modelFieldGroupRules" label-width="auto" class="demo-modelForm" status-icon>
      <el-form-item label="字段组标识" prop="name">
        <el-input v-model="modelFieldGroupForm.name" :disabled="!modelFieldGroupAction" />
      </el-form-item>
      <el-form-item label="字段分组名称" prop="verbose_name">
        <el-input v-model="modelFieldGroupForm.verbose_name" />
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="modelFieldGroupCance(groupFormRef)">取消</el-button>
        <el-button type="primary" @click="modelFieldGroupCommit(groupFormRef)">
          确认
        </el-button>
      </div>
    </template>
  </el-dialog>


  <!-- 模型字段弹窗 -->
   
  <el-drawer
    v-model="modelFieldDrawer"
    title="模型字段"
    :before-close="modelFielHandleClose"
    direction="rtl"
    class="demo-drawer"
  >
    <div class="demo-drawer__content">
      <el-form :model="modelFieldForm" ref="modelFieldFormRef" label-width="auto" label-position="right"
        :rules="modelFieldFormRules"
      >
        <el-form-item label="唯一标识" prop="name" >
          <el-input v-model="modelFieldForm.name" autocomplete="off"  :disabled="nowModelField.built_in || isEdit ?  true : false"/>
        </el-form-item>
        <el-form-item label="显示名称" prop="verbose_name" >
          <el-input v-model="modelFieldForm.verbose_name" autocomplete="off" :disabled="nowModelField.built_in" />
        </el-form-item>
        <el-form-item label="字段类型" prop="type" >
          <el-input v-model="modelFieldForm.type" autocomplete="off" :disabled="nowModelField.built_in || isEdit ?  true : false" />
        </el-form-item>
        <el-form-item label="可编辑" prop="editable" >
          <el-switch v-model="modelFieldForm.editable" style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949" :disabled="nowModelField.built_in" />
        </el-form-item>
        <el-form-item label="必填" prop="required" >
          <el-switch v-model="modelFieldForm.required" style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949" />
        </el-form-item>
        <el-form-item label="正则表达式" prop="validation_rule" v-if="modelFieldForm.type === 'string'">
          <el-input v-model="modelFieldForm.validation_rule" autocomplete="off" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="modelFieldForm.description"  type="textarea" />
        </el-form-item>
        <!-- <el-form-item  prop="built_in"></el-form-item>
        <el-form-item  prop="model"></el-form-item>
        <el-form-item  prop="model_group"></el-form-item>
        <el-form-item  prop="create_user"></el-form-item>
        <el-form-item  prop="update_user"></el-form-item> -->
        </el-form>
      <div class="demo-drawer__footer">
        <el-button @click="modelFieldFormCancel(modelFieldFormRef)">取消</el-button>
        <el-button type="primary"  @click="modelFieldFormCommit(modelFieldFormRef)">
         确定
        </el-button>
      </div>
    </div>
  </el-drawer>

</template>
<script lang="ts" setup>
import { da, fa } from 'element-plus/es/locale/index.mjs';
import { ref, reactive, watch, getCurrentInstance, nextTick, onActivated,computed, onMounted } from 'vue'
// import { Delete, Filter,CirclePlus } from '@element-plus/icons-vue'
const { proxy } = getCurrentInstance();
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import type { ComponentSize, FormInstance, FormRules } from 'element-plus'
import {
  Check,
  Delete,
  Edit,
  Message,
  Search,
  Star,
} from '@element-plus/icons-vue'
import { useStore } from 'vuex'
import { value } from 'lodash-es';
const store = useStore()

const route = useRoute();
// const router = useRouter();
const modelInfo = ref({})
const ciModelFieldsList = ref([])
const activeArr = ref([])

// const ciModelFieldsList = defineModel("ciModelFieldsList")
// const activeArr = computed(()=>{
//   let _tempArr = []
//   ciModelFieldsList.value.forEach((item,index)=>{
//     console.log(123)
//     _tempArr.push(item.verbose_name)
//   })
//   return _tempArr
// })
// 获取模型字段信息
const getModelField = async () => {
  let res = await proxy.$api.getCiModel(route.query, route.query.id + '/with_fields')
  console.log(res)
  modelInfo.value = res.data
  ciModelFieldsList.value = res.data.field_groups
  ciModelFieldsList.value.forEach((item, index) => {
    activeArr.value.push(item.verbose_name)
  })
}

onActivated(async()=>{
  console.log("onActivated", "getModelField")
  // await getCiModelInfo(route.query, route.query.id);
  // await getCiModelGroupList();
  // await getModelField();
  getModelField();

})
onMounted(() => {
  console.log('field mount')
  // getModelField()
})
// const ciModelFieldsListAdd = computed(()=>{
//   ciModelFieldsList.push()
// })


// 字段分组
interface ModelFieldGroupForm {
  name: string,
  verbose_name: string,
  // model: string,
  // built_in: boolean,
  // create_user: string,
  // update_user: string,
}
// console.log( 'admin')
const modelFieldGroupForm = reactive<ModelFieldGroupForm>({
  name: '',
  verbose_name: '',
  // model: '',
  // // built_in: false,
  // // create_user: 'admin',
  // // update_user: 'admin',
})
const modelFieldGroupRules = reactive<FormRules<ModelFieldGroupForm>>({
  name: [
    { required: true, message: '请输入唯一标识', trigger: 'blur' },
    { pattern: /^[a-z][\w\d]{4,20}$/, trigger: 'blur', message: '以英文字符开头,可以使用英文,数字,下划线,长度4-20 ', required: true }

  ],
  verbose_name: [
    { required: true, message: '请输入组名称', trigger: 'blur' },
  ],

})
const groupFormRef = ref<FormInstance>()

const isModelFieldGroup = ref(false)
const modelFieldGroupCance = (formEl: FormInstance | undefined) => {
  isModelFieldGroup.value = false
  resetForm(formEl);
}
const modelFieldGroupAction = ref(false)

const nowGroupId = ref('')
const modelFieldGroupCommit = async (formEl: FormInstance | undefined) => {
  // 提交表单
  if (!formEl) return
  await formEl.validate(async (valid, fields) => {
    if (valid) {
      if (modelFieldGroupAction.value) {
        // 添加
        console.log(modelFieldGroupForm)
        let res = await proxy.$api.addCiModelFieldGroup({model:modelInfo.value.id,create_user:store.state.username,
                                                        update_user:store.state.username
                                                        ,...modelFieldGroupForm})
        console.log(res)
        // console.log(123)
        if (res.status == "201") {
          ElMessage({ type: 'success', message: '添加成功', });
          // 重置表单
          isModelFieldGroup.value = false
          resetForm(formEl);
          getModelField();
          // 获取数据源列表        
        } else {
          ElMessage({ showClose: true, message: '添加失败:' + JSON.stringify(res.data), type: 'error', })
        }
      } else {
        let res = await proxy.$api.updateCiModelFieldGroup({ id: nowGroupId.value, update_user:store.state.username,...modelFieldGroupForm })
        console.log(res)
        // console.log(123)
        if (res.status == "200") {
          ElMessage({ type: 'success', message: '更新成功', });
          // 重置表单
          isModelFieldGroup.value = false
          resetForm(formEl);
          getModelField();
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

const handleCloseModelFieldGroup = (done: () => void) => {
  ElMessageBox.confirm('是否确认关闭?')
    .then(() => {
      done()
      resetForm(groupFormRef.value);

    })
    .catch(() => {
      // catch error
    })
}



// 模型组悬停时的图标操作
// 新增模型
const diaName = ref('新增')
const addModelFieldGroup = (config) => {
  // modelFieldGroupForm.model_group = params
  diaName.value = '新增'
  nextTick(()=>{
  })
  isModelFieldGroup.value = true
  modelFieldGroupAction.value = true

}
// 修改
const editModelFieldGroup = (config) => {
  // ElMessage({
  //   message: '修改组名.',
  //   type: 'warning',
  // })
  // 打开弹窗
  diaName.value = '修改'
  isModelFieldGroup.value = true
  // 编辑模式
  nextTick(()=>{
    modelFieldGroupAction.value = false
  modelFieldGroupForm.name = config.name
  modelFieldGroupForm.verbose_name = config.verbose_name
  // modelFieldGroupForm.model = modelInfo.value.model.id
  nowGroupId.value = config.id

  })


  // modelFieldGroupCommit(groupFormRef.value)


}
// 删除组
const deleteModelFieldGroup = (config) => {
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

    // 发起删除请求
    let res = await proxy.$api.deleteCiModelFieldGroup(config)
    // 
    // let res = {status:204}
    if (res.status == 204 || res.status == 200) {
      ElMessage({
        type: 'success',
        message: '删除成功',
      })
      // 重新加载页面数据
      await getModelField();
    } else {
      ElMessage({
        type: 'error',
        message: '删除失败',
      })
    }

    // console.log(1111)
  })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '取消删除',
      })
    })

}

// 添加组
// const addModelFieldGroup = ()=>{

// }
// 动态样式绑定
// const isBuiltClass = (boolean)=>{
//   if (!boolean) return  
//   // return
// }

// 模型字段组


// 模型字段功能
const modelFieldDrawer = ref(false)
interface ModelFieldForm {
  name: string,
  verbose_name: string,
  // model: string,
  // model_field_group:string,
  // built_in: boolean,
  type:string,
  required:boolean,
  editable:boolean,
  validation_rule:string,
  description:string,
  // create_user: string,
  // update_user: string,
}
// console.log( 'admin')
const modelFieldForm = reactive<ModelFieldForm>({
  name: '',
  verbose_name: '',
  // model: '',
  // model_field_group:'',
  // built_in: false,
  type:'string',
  required:false,
  editable:true,
  validation_rule:'',
  description:'',
  // create_user: 'admin',
  // update_user: 'admin',
})
const modelFieldFormRules = reactive<FormRules<ModelFieldForm>>({
  name: [
    { required: true, message: '请输入唯一标识', trigger: 'blur' },
    { pattern: /^[a-z][\w\d]{4,20}$/, trigger: 'blur', message: '以英文字符开头,可以使用英文,数字,下划线,长度4-20 ', required: true }

  ],
  verbose_name: [{ required: true, message: '请输入字段显示名称', trigger: 'blur' },],
  type:[{ required: true, message: '字段类型', trigger: 'blur' },]
})
const modelFieldFormRef = ref<FormInstance>()

const isDisabled = ref(false)
const isEdit = ref(false)
const nowModelField = ref({})
const modelFieldAction = ref(true)
// 点击弹窗
const editModelField = (params) =>{
  modelFieldDrawer.value = true
  diaName.value = '修改'
  isEdit.value = true
  console.log(params)
  nowModelField.value = params
  modelFieldAction.value = false
  nextTick(() => {
    Object.keys(params).forEach(item=>{
        if (modelFieldForm.hasOwnProperty(item))  modelFieldForm[item] = params[item]
          } // isDisabled.value = params.built_in
      )
    // 替换当前用户名
    // modelFieldForm.update_user = store.state.username
  })

}

const modelFieldFormCancel = (formEl)=>{

  resetForm(formEl)
  modelFieldDrawer.value = false
}
const addModelField = (params)=>{
  diaName.value = '新增'
  nowModelField.value = {}
  modelFieldDrawer.value = true
  modelFieldAction.value = true
  isEdit.value = false

  nextTick(() => {
  // modelFieldForm.model = params.model
  // modelFieldForm.model_field_group = params.id
  // modelFieldForm.update_user = store.state.username
  nowGroupId.value = params.id
  console.log(nowGroupId.value)
  })

}

// 字段新增/编辑
const modelFieldFormCommit = async (formEl: FormInstance | undefined) => {
  // 提交表单
  if (!formEl) return
  await formEl.validate(async (valid, fields) => {
    if (valid) {
      if (modelFieldAction.value) {
        // 添加
        console.log(nowGroupId.value.id)
        let res = await proxy.$api.addCiModelField({model:modelInfo.value.model.id,model_field_group:nowGroupId.value,
                                                    create_user:store.state.username,update_user:store.state.username
                                                        ,...modelFieldForm})
        console.log(res)
        // console.log(123)
        if (res.status == "201") {
          ElMessage({ type: 'success', message: '添加成功', });
          // 重置表单
          modelFieldDrawer.value = false
          resetForm(formEl);
          getModelField();
          // 获取数据源列表        
        } else {
          ElMessage({ showClose: true, message: '添加失败:' + JSON.stringify(res.data), type: 'error', })
        }
      } else {
        let res = await proxy.$api.updateCiModelField({ id: nowModelField.value.id, update_user:store.state.username,...modelFieldForm })
        console.log(res)
        // console.log(123)
        if (res.status == "200") {
          ElMessage({ type: 'success', message: '更新成功', });
          // 重置表单
          modelFieldDrawer.value = false
          resetForm(formEl);
          getModelField();
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

// 取消弹窗
const modelFielHandleClose = (done: () => void) => {
  ElMessageBox.confirm('是否确认关闭?')
    .then(() => {
      done()
      // modelFieldFormRef.value.resetFields();
      resetForm(modelFieldFormRef.value);
      modelFieldDrawer.value = false
      // console.log(modelFieldForm)
      // resetForm(modelFieldFormRef.value)
    })
    .catch(() => {
      // catch error
      console.log(123)
    })

}

// 重置表单
const resetForm = (formEl: FormInstance | undefined) => {
  if (!formEl) return
  formEl.resetFields()
}

</script>
<style lang="less" scoped>
.modelFieldCard {
  max-width: 200px;
  width: 300px;
  height: 90px;
  display: flex;
  flex-direction: column;

}

.describe-class {
  white-space: nowrap;
  /*强制单行显示*/
  text-overflow: ellipsis;
  /*文本超出部分省略号表示*/
  overflow: hidden;
  /*文本超出部分隐藏*/
  max-width: 200px;
  /*设置文本显示的最大宽度*/
  display: inline-block
    /*设为行内块元素*/
  ;
  vertical-align: top;
  width: 200px;
}

.isBuiltClass {
  background-color: var(--el-color-info-light-8);
}

.operation_show {
  margin-left: 10px;
  display: none;
}

.el-collapse-item__header:hover .operation_show {
  display: flex;
}
.demo-drawer__footer {
  display: flex;
  justify-content:flex-end;
}
</style>