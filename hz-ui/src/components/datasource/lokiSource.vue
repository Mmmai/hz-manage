<template>
  <el-form
    :label-position="labelPosition"
    :model="formLabelAlign"
    label-width="auto"
    style="max-width: 400px"
    ref="formRef"
  >
  <el-form-item label="数据源名称" :rules="[{required:true}]">
    <el-input v-model="formLabelAlign.source_name" />
  </el-form-item>

    <el-form-item label="URL">
      <el-input v-model="formLabelAlign.url" />
    </el-form-item>
    <el-form-item label="认证">
      <el-switch
        v-model="formLabelAlign.isAuth"
        class="ml-2"
        style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949"
        />
    </el-form-item>
    <div v-if="formLabelAlign.isAuth">
      <el-form-item label="用户名">
        <el-input v-model="formLabelAlign.username" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="formLabelAlign.password" type="password"/>
      </el-form-item>
    </div>
    <el-form-item label="默认">
      <el-switch
        v-model="formLabelAlign.isDefault"
        class="ml-2"
        style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949"
      />
    </el-form-item>
    <el-form-item label="是否启用">
      <el-switch
        v-model="formLabelAlign.isUsed"
        class="ml-2"
        style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949"
        />
    </el-form-item>
  </el-form>
</template>
<script lang="ts" setup>
import { ref,reactive,getCurrentInstance, defineModel   } from 'vue'
const labelPosition = ref('right')
const formLabelAlign = defineModel("formData")
const { proxy } = getCurrentInstance();
const resetForm = ()=>{
  proxy.$refs.formRef.resetFields()
  console.log("test")
  console.log(formLabelAlign)
}
// const dialogVisible = ref(false)
// const formLabelAlign = reactive({
//   source_name: '',
//   url: '',
//   isAuth: false,
//   isDefault:false,
//   isUsed:true,
//   username:'',
//   password:''
// })
defineExpose({
  resetForm,
});
</script>