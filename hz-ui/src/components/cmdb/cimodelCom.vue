<template>
  <el-dialog v-model="ciModelDialog" title="新增模型" width="500" :before-close="handleClose">
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
      <!-- <el-form-item>
      <el-button type="primary" @click="submitForm(modelFormRef)">
        Create
      </el-button>
      <el-button @click="resetForm(modelFormRef)">Reset</el-button>
    </el-form-item> -->
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="addModelCance()">取消</el-button>
        <el-button type="primary" @click="modelCommit(modelFormRef)">
          确认
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>
<script lang="ts" setup>
import { ref, getCurrentInstance, onMounted, watch,defineExpose,defineModel, computed, reactive } from 'vue'
import { vDraggable } from 'vue-draggable-plus'
import { ElMessageBox, ElMessage } from 'element-plus'
import type { ComponentSize, FormInstance, FormRules } from 'element-plus'
import { fa } from 'element-plus/es/locale/index.mjs';
import iconSelectCom from '../components/iconSelectCom.vue';
const ciModelDialog = defineModel('isShow')
const grouplist = defineModel('grouplist')
const { proxy } = getCurrentInstance();
const isShow = ref(false)
const isShowIconSelect = () => {
  isShow.value = true
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
    {pattern: /^[a-z][a-z_]{3,20}$/ ,trigger: 'blur',message: '以英文字符开头,可以使用英文,下划线,长度3-20 ' ,required: true}

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
  await formEl.validate(async(valid, fields) => {
    if (valid) {
      if (modelAction.value) {
        // 添加
        let res = await proxy.$api.addCiModel(modelForm)
        console.log(res)
        // console.log(123)
        if (res.status == "200") {
          ElMessage({ type: 'success', message: '添加成功', });
          // 重置表单
          ciModelDialog.value = false
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
const resetForm = (formEl: FormInstance | undefined) => {
  if (!formEl) return
  formEl.resetFields()
}



</script>