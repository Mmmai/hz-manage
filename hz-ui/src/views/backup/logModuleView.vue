<template>

    
  <el-row class="row-bg" justify="space-between">
    <el-col :span="23">
      <span style="display: flex;align-items: center;margin-right: 10px;">分组</span>
      <el-checkbox
        v-model="checkAll"
        :indeterminate="isIndeterminate"
        @change="handleCheckAllChange"
        style="padding-right: 6px;"
      >
        所有
      </el-checkbox>

      <el-checkbox-group
        v-model="selectGroup"
        @change="handleCheckedCitiesChange"
        class="group-check"
      >
        <el-checkbox v-for="group in groupList" :key="group" :label="group" :value="group" >
          {{ group }}
        </el-checkbox>
      </el-checkbox-group>

    </el-col>
    <el-col :span="1">  <el-button type="primary" @click="addModule">添加</el-button></el-col>
  </el-row>

  <el-divider />
  <!-- 数据源列表展示 -->
  <div class="context-body">

    <div class="el-card-div" 
      v-for="v,i in showDataList" 
      :key=i 
      >
      <el-tooltip
        class="box-item"
        effect="dark"
        content="点击编辑"
        placement="bottom"
      >
      <el-card 
        style="width: 200px" 
        shadow="hover" 
        @click="edit(v)"
        >
        <!-- <div class="el-card-context">
            <span> {{v.module_name}}</span>          
          <el-button type="success" size="small" round v-if="v.isDefault">默认</el-button>
        </div> -->
        <!-- <el-descriptions 
          :title="v.module_name" 
          size="small"  
          direction="vertical" 
          border
        >
          <el-descriptions-item label="标签">{{ v.label_name }}</el-descriptions-item>
          <el-descriptions-item label="标签值">{{ v.label_value }}</el-descriptions-item>

        </el-descriptions> -->
        <h4>{{ v.module_name }}</h4>
      </el-card>
    </el-tooltip>

    </div>
  </div>
  <!-- 弹出框 -->
  <el-dialog
    v-model="dialogVisible"
    title="环节配置"
    width="500"
    :before-close="handleClose"
    draggable
    overflow
    >
    <!-- <span @click=changeCom>This is a message</span> -->
    <el-form
      label-position="right"
      :model="formLabelAlign"
      label-width="auto"
      style="max-width: 400px"
      ref="formRef"
      :rules="rules"

     >
      <el-form-item label="环节名称" prop="module_name">
        <el-input v-model="formLabelAlign.module_name" style="width:220px"/>
      </el-form-item>

      <el-form-item label="标签" prop="label_name">
      <!-- app = '123' -->
      <el-select
        v-model="formLabelAlign.label_name"
        filterable
        clearable
        allow-create
        placeholder="标签"
        style="width: 180px"
        @click="getLabels"
        >       
          <el-option
            v-for="labelItem in labelList"
            :key="labelItem.value"
            :label="labelItem.label"
            :value="labelItem.value"
          />
      </el-select>
      </el-form-item>
      <el-form-item label="标签值" prop="label_value">
        <el-input v-model="formLabelAlign.label_value" placeholder="支持模糊匹配"/>
      </el-form-item>
      <el-form-item label="分组">
      <el-select
        v-model="formLabelAlign.group"
        filterable
        clearable
        allow-create
        placeholder="所属分组，支持新增"
        style="width: 180px"
        >       
          <el-option
            v-for="gItem in groupOptions"
            :key="gItem.value"
            :label="gItem.label"
            :value="gItem.value"
          />
      </el-select>
      </el-form-item>
      <el-form-item label="是否启用">
      <el-switch
        v-model="formLabelAlign.status"
        class="ml-2"
        style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button type="danger" @click="deleteAction" v-if="isAdd == false">删除</el-button>
          <el-button type="primary" @click="updateAction" v-if="isAdd == false">更新</el-button>
          <el-button type="primary" @click="submitAction" v-else >添加</el-button>
      </div>
    </template>
  </el-dialog>
</template>
<script lang="ts" setup>
  import { ref,reactive, shallowRef,watch,getCurrentInstance, onMounted, computed  } from 'vue'
  const { proxy } = getCurrentInstance();
  import  type { FormInstance, FormRules } from 'element-plus'

  import {ElMessageBox,ElMessage} from 'element-plus'
  import { filter, range } from 'lodash-es';
import { RefSymbol } from '@vue/reactivity';
  const getImgPath = (name: string): any => {
    return new URL(`/src/assets/images/${name}`, import.meta.url).href
    }  
  const formRef = ref<FormInstance>()
  

  const rules = reactive<FormRules>({
    module_name: [{ required: true, message: '请填写名称', trigger: 'blur' }],
    label_name: [{ required: true, message: '请添加匹配标签', trigger: 'blur' }],
    label_value: [{ required: true, message: '请填写标签值', trigger: 'blur' }],
  })


  const dialogVisible = ref(false)
  const isAdd = ref(false)
  const componentId = shallowRef('')
  // 重置表单
  const resetForm = ()=>{
    Object.keys(formLabelAlign).forEach(key =>{
      formLabelAlign[key] = initFormLabelAlign[key]
    })
  }
  // 关闭弹窗
  const handleClose = (done: () => void) => {
    ElMessageBox.confirm('是否关闭?')
    .then(() => {
      resetForm();
      console.log(formLabelAlign)
      done()
    })
    .catch(() => {
      // catch error
    })
  } 
  const initFormLabelAlign = {
    // module_name: '',
    label_name:'',
    label_value:'',
    label_match: '=~',
    group: '',
    status:true,
    }
  const formLabelAlign = reactive({
    // module_name: '',
    label_name:'',
    label_value:'',
    label_match: '=~',
    group: '',
    status:true,
  })

  // 添加按钮的动作
  const addModule = () =>{
    dialogVisible.value = true;
    isAdd.value = true
  }


  // 弹出框内容
  // label来源于默认的loki
  const defaultDataSource = ref({})
  const getDataSource = async()=>{
    let res = await proxy.$api.dataSourceGet()
    console.log(res)
    res.data.forEach(item => {
      if (item.isDefault){
        console.log(item)
        defaultDataSource.value = item
      }
    });
  }
  // 获取现有标签
  const labelList = ref([])
  const getLabels = async () => {
    console.log(defaultDataSource.value)
    let res = await proxy.$api.lokiLabelGet({'url':defaultDataSource.value.url})
    labelList.value = res.data.data
    // console.log(labelList.value)
  }


  const submitAction = ()=>{
    proxy.$refs.formRef.validate(async(valid)=>{
      console.log(valid)
      if (valid){
        let res = await proxy.$api.addLogModule(formLabelAlign)
        console.log(res)
        if (res.status == "201"){
          ElMessage({type: 'success',message: '添加成功',});
          // 重置表单
          resetForm();
          dialogVisible.value = false
          getLogModuleList();
          // 获取数据源列表        
        }else{
          ElMessage({showClose: true,message: '添加失败:'+JSON.stringify(res.data),type: 'error',})
        }
      }else{
  
      }
    })
  }
  // 所属分组
  const groupList = ref([])
  // 获取已添加的环节列表
  const logModuleList = ref([])
  const groupCheckBox = ref([])
  const getLogModuleList = async()=>{
    let res = await proxy.$api.getLogModule()
    // console.log(res)
    logModuleList.value = res.data
    // 把已创建的分组罗列
    let tempGroupList = []

    res.data.forEach(item=>{
      
      if (tempGroupList.indexOf(item.group) === -1){
        if (item.group != ''){
          // groupList.value.push({'label':item.group,'value':item.group})
          tempGroupList.push(item.group)
        }
      }
      // if (groupCheckBox.value.indexOf(item.group) === -1 ){
      //   groupCheckBox.value.push(item.group)
      // }

    })
    groupList.value = tempGroupList

    console.log(groupList.value)
  }
  const groupOptions = ref([])
  // 动态生成groupOptions
  watch(groupList,(n,)=>{
    let tempGroupList = []
    let tempGroupOptions = []
    n.forEach(item=>{
      tempGroupOptions.push({'label':item,'value':item})
      tempGroupList.push(item)
      
    })
    groupOptions.value = tempGroupOptions
    selectGroup.value = tempGroupList
    console.log(selectGroup.value)
    checkAll.value = true
  },{'deep':true})
  // 点击编辑时的按钮
  const nowId = ref('')
  const edit = (config)=>{
    dialogVisible.value = true
    isAdd.value = false
    
    // formLabelAlign.
    nowId.value = config.id
    let filterArray = ['id','update_time','create_time']
    Object.keys(config).forEach(key => {
      if (filterArray.indexOf(key) === -1){
        formLabelAlign[key] = config[key]
      }
      });
  }
  // 更新按钮
  const updateAction = ()=>{
    proxy.$refs.formRef.validate(async(valid)=>{
      if (valid){
        let res = await proxy.$api.updateLogModule({id:nowId.value,...formLabelAlign})
        console.log(res)
        if (res.status == 200){
          ElMessage({
            type: 'success',
            message: '更新成功',
          })
          // 重置表单，关闭弹出框,重新加载数据
          resetForm()
          dialogVisible.value = false
          getLogModuleList();

        }else{
          ElMessage({
            type: 'error',
            message: '更新失败',
          })
        }
          resetForm()
      }else{
      
      }
    })
  }
  // 删除按钮
  const deleteAction = (row)=>{
    ElMessageBox.confirm(
      '是否确认删除?',
      'Warning',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
        draggable: true,

      }
      )
    .then(async() => {
      // 发起删除请求
      let res = await proxy.$api.delLogModule(nowId.value)
      if (res.status == 204){
        ElMessage({
          type: 'success',
          message: '删除成功',
        })
        // 重置表单，关闭弹出框,重新加载数据
        resetForm()
        dialogVisible.value = false
        getLogModuleList();

      }else{
        ElMessage({
          type: 'error',
          message: '删除失败',
        })
      }
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: 'Delete canceled',
      })
    })
  }
  
  //渲染时加载
  onMounted(async ()=>{
    await getDataSource();
    await getLogModuleList();
  //  await 
  }) 
  // 分组过滤功能
  const checkAll = ref(true)
  const isIndeterminate = ref(false)
  // const selectGroup = ref([])
  const selectGroup = ref([])

  // const cities = ['Shanghai', 'Beijing', 'Guangzhou', 'Shenzhen']

  const handleCheckAllChange = (val: boolean) => {
    selectGroup.value = val ? groupList.value : []
    isIndeterminate.value = false
  }
  const handleCheckedCitiesChange = (value: string[]) => {
    const checkedCount = value.length
    checkAll.value = checkedCount === groupList.value.length
    isIndeterminate.value = checkedCount > 0 && checkedCount < groupList.value.length
  }
  const showDataList = ref([])
  watch(()=>selectGroup.value,(n)=>{
    // console.log(n)
    // groupList.value.forEach(item=>{
    //   if (item =)
    // })
    let tempDataList = []
    logModuleList.value.forEach(item=>{
      if (selectGroup.value.indexOf(item.group) !== -1){
        
        tempDataList.push(item)
      }
    })
    if (n.length == groupList.value.length){
      showDataList.value = logModuleList.value
    }else{
      showDataList.value = tempDataList
    }
  })
  // watch(()=>checkAll.value,(n)=>{
  //   if (n){
  //     console.log(logModuleList.value)
  //     showDataList.value = logModuleList.value
  //     console.log(logModuleList)

  //   }

    
  // })

</script>
<style scoped lang="less">

.context-body{
  height: 90%;
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  align-content: flex-start;
  align-items: flex-start;
}
.el-card-context{
  display: flex;
  justify-content: space-between;
}
.el-card-div {
  margin: 10px 10px 10px 10px;
}
:deep(.el-col-23) {
  display: flex;
  justify-content: flex-start;
  }
.group-check {
  :deep(.el-checkbox){
    margin-right: 15px
    }
  }
</style>