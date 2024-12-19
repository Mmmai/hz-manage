<template>
  <div class="card">
  <div class="user-header">
    <div>
      <el-button  type="primary" size="small" @click="handleAdd">新增</el-button>
      <!-- <el-button  type="primary" size="small" @click="insertDaemonData">插入样例数据</el-button> -->
      <el-button  v-if="multipleSelect.length == 0" disabled type="danger" size="small" @click="handleDeleteMore">批量删除</el-button>
      <el-button v-else type="danger" size="small" @click="handleDeleteMore">批量删除</el-button>

    </div>
    <el-form :inline="true" :model="filterObject" size="small" class="demo-form-inline">
    <el-form-item label="用户名检索">
      <el-input v-model="filterObject.search" placeholder="请输入用户名" clearable />
    </el-form-item>

    <el-form-item>
      <el-button type="primary" size="small" @click="hanldeSearch">查询</el-button>
    </el-form-item>
  </el-form>
  </div>
  <!-- 表格内容 -->
  <div>
    <el-table 
      border
      v-loading="loading"
      :data="userList" 
      style="width: 100%" 
      max-height="500px"
      :table-layout="tableLayout"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" :selectable="selectFilter"/>
      <el-table-column 
        v-for="item in userListCol"
        :key="item.prop" 
        :label="item.label"
        :prop="item.prop"
      >
      <template #default="scope" v-if="item.prop === 'roles'">
        <el-tag 

          v-for="xxx in scope.row.roles" 
          :key="xxx"
          class="el-tag-role-list"
        >
          {{ roleObject[xxx] }}
        </el-tag>
      </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="150">
        <template #default="scope">
          <el-button  type="primary" size="small" @click="handleEdit(scope.row)"
            >编辑</el-button
          >
          
          <el-button v-if="scope.row.username == 'admin'" type="danger" size="small" disabled @click="handleDelete(scope.row)">删除</el-button>
          <el-button v-else type="danger" size="small"  @click="handleDelete(scope.row)">删除</el-button>

        </template>
      </el-table-column>
    </el-table>
  </div>
  <div class="demo-pagination-block">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 30, 40]"
        :small="small"
        :disabled="disabled"
        :background="background"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalCount"
        :hide-on-single-page="isSinglePage"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
  </div>
</div>
  <!-- 新增的弹出框 -->
  <el-dialog
    v-model="dialogVisible"
    :title="action == 'add' ? '新增用户' : '编辑用户'"
    width="40%"
    :before-close="handleClose"
  >
  <el-form :inline="true" :model="formInline" class="demo-form-inline" ref="userFrom" status-icon>
    <el-row>
      <el-col :span="12">
        <el-form-item label="用户名称" prop="username"
          :rules="[{required:true}]"
        >
          
          <el-input v-model="formInline.username" placeholder="" clearable :disabled="isDisabled" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="真实名称" prop="real_name">
          <el-input v-model="formInline.real_name" placeholder="" clearable />
        </el-form-item>
      </el-col>

    </el-row>

    <!-- <el-form-item label="状态">
      <el-input v-model="formInline.status" placeholder="" clearable />
    </el-form-item> -->
    <el-row>
      <el-col :span="12">
        <el-form-item label="状态" prop="status">
          <!-- <el-radio-group v-model="formInline.status">
            <el-radio label=true />
            <el-radio label=false />
          </el-radio-group> -->
          <el-switch
            v-model="formInline.status"
            class="ml-2"
            inline-prompt
            style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949"
            active-text="Y"
            inactive-text="N"
            :disabled="isDisabled"
          />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="角色" prop="roles">
          <el-select
            v-model="formInline.roles"
            placeholder=""
            clearable
            multiple
            collapse-tags
            collapse-tags-tooltip
            :max-collapse-tags="3"
            :disabled="isDisabled"
            style="width: 120px"
          >
            <el-option 
              v-for="item in roleInfo" 
              :key="item.id"
              :label="item.role"
              :value="item.id"
            />
            <!-- <el-option label="禁用" value="False" /> -->
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>
    <el-form-item label="Password" prop="password">
      <el-input v-model="formInline.password" type="password" autocomplete="off" />
    </el-form-item>
    <el-row style="justify-content: flex-end;">
      <el-form-item>
      <el-button @click="cancelAdd">取消</el-button>
      <el-button type="primary" @click="handleCommit"> 确定</el-button>   
    </el-form-item>
    </el-row>
  <!-- </div> -->

  </el-form>
    <!-- <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addUser">
          新增
        </el-button>
      </span>
    </template> -->
  </el-dialog>
</template>

<script setup>
  import { getCurrentInstance, onMounted,ref,reactive, watch} from 'vue'
  const {proxy} = getCurrentInstance();
  // 搜素框变量
  const filterObject = reactive({
    search:""
  })
  // 表格变量
  const loading = ref(false)
  const userList = ref([])
  // const currentUserList = ref([])
  const tableLayout = ref('auto')
  const userListCol = ref([
    {
      prop:'username',
      label: '用户名称',
    },
    {
      prop:'real_name',
      label: '真实姓名',
    },
    {
      prop:'status',
      label: '状态',
    },
    {
      prop:'roles',
      label: '角色列表',
    },
    {
      prop:'update_time',
      label: '更新时间',
    },
    {
      prop:'create_time',
      label: '创建时间',
    }
    ])
  // 分页变量
  const currentPage = ref(1)
  const pageSize = ref(10)
  const small = ref(false)
  const background = ref(false)
  const disabled = ref(false)
  const totalCount = ref(0)
  const pageConfig = reactive({
    page:currentPage.value,
    size:pageSize.value,
    search:"",
    ordering:"id"
  })
  // 少于分页需求则不显示分页
  const isSinglePage=ref(false)

  // 角色列表
  const roleInfo = ref('') 
  const roleObject = ref({})
  // object反转
  function inverse(obj){
    var retobj = {};
    for(var key in obj){
    
      retobj[obj[key]] = key;
    }
  return retobj;
  }
  // cumputed 
  onMounted(() =>{
    // 初始化数据切片
    getRoleData(pageConfig);
    // api请求获取所有数据

    
  });
  // 获取角色数据
  const getRoleData = async(config) =>{
    let roleinfo = await proxy.$api.getRole(config)
    roleInfo.value = roleinfo.data.results
    // 将role列表转化为dict
    // console.log(roleInfo.value)
    for (let key in roleInfo.value){
      let rolename = roleInfo.value[key].role ;
      let roleid = roleInfo.value[key].id
      roleObject.value[roleid] = rolename
    }
    getUserData(pageConfig);
  }
  // 获取用户数据
  const getUserData = async(conf) => {
    loading.value = true
    // console.log('11111',pageConfig.value)
    let res = await proxy.$api.user(conf)
    console.log(conf)
    console.log(res)
    userList.value = res.data.results
    // 对数据做进一步处理
    // userList.value = res.data.map((item) => {
    //   // item.sex = item.sex === 0 ? '女':'男'
    //   let rolenameList = []
    //   for (let key in item.roles){
    //     // rolenameList.push(roleObject.value[item.roles[key]])
    //     rolenameList.push(item.roles[key])
    //   }
    //   // item.roles = rolenameList.toString()
    //   item.roles = rolenameList
    //   return item
    // })

    totalCount.value = res.data.count
    // if (totalCount.value <= pageSize.value){
    //   isSinglePage.value = true
    // }
    // getTableNowData(pageSize,currentPage);
    loading.value = false

    // userListCol.value = 
  }

  const handleSizeChange = (val) => {
    console.log(`${val} items per page`)
    pageConfig.size = val
    // getTableNowData(pageSize,currentPage);
    // if (totalCount.value <= pageSize.value){
    //   isSinglePage.value = true
    // }
    getUserData(pageConfig)

  }
  const handleCurrentChange = (val) => {
    pageConfig.page = val
    console.log(val)
    // getTableNowData(pageSize,currentPage);
    getUserData(pageConfig)
  }
  // 前端处理，数据切片
  // const getTableNowData = (pageSize,currentPage) => {
  //   let sindex = 0+pageSize.value*(currentPage.value - 1 )
  //   let eindex = pageSize.value + sindex
  //   currentUserList.value = userList.value.slice(sindex,eindex)
  // }
  // 弹出框

  // 新增按钮
  import {ElMessageBox,ElMessage} from 'element-plus'
  const dialogVisible = ref(false)
  // from表单数据
  const formInline = reactive({
    username: "",
    real_name: null,
    password:"",
    status:true,
    roles:[]
  })
  const action = ref('add')
  // 显示弹出框
  const handleAdd = () =>{
    action.value = 'add'
    dialogVisible.value = true

  }
  // 取消弹出框
  const cancelAdd = () =>{
    dialogVisible.value = false
      // 重置表单
    proxy.$refs.userFrom.resetFields();
  }
  // 关闭弹出框
  const handleClose = (done) => {
    ElMessageBox.confirm('是否确认关闭?')
      .then(() => {
        done()
        proxy.$refs.userFrom.resetFields();

      })
      .catch(() => {
        // catch error
      })
  }
  // 点击触发提交
  const handleCommit = () => {
    proxy.$refs.userFrom.validate(async(valid) =>{
      if (valid){
        // 新增接口
        if (action.value == 'add'){
          let res = await proxy.$api.useradd(formInline)
          console.log(res)
          if (res.status == 201){
            dialogVisible.value = false
            // 重置表单
            proxy.$refs.userFrom.resetFields();
            getUserData(pageConfig);
          }else{
            ElMessage({
              showClose: true,
              message: '添加失败:'+JSON.stringify(res.data),
              type: 'error',})
          }
        }
      // 编辑接口
        else{
          let res = await proxy.$api.userupdate(formInline)
          console.log(res)
          if (res.status == 200){
            dialogVisible.value = false
            // 重置表单
            console.log(formInline)
            proxy.$refs.userFrom.resetFields();
            console.log(formInline)
            getUserData(pageConfig);
          }
          else{
            console.log()
            ElMessage({
              showClose: true,
              message: '更新失败:'+JSON.stringify(res.data),
              type: 'error',})
          }
        }
      }else{
          ElMessage({
          showClose: true,
          message: '请输入正确内容.',
            type: 'error',})
      }
      console.log(formInline)
  })}
  
  // 编辑
  const handleEdit = (row) =>{
    action.value = 'edit'
    dialogVisible.value = true
    // 清除新增按钮会显示编辑按钮的记录
    proxy.$nextTick(() => {Object.assign(formInline,row)})
  }
  // 删除
  const handleDelete = (row) =>{  
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
      let res = await proxy.$api.userdel(row.id)
      if (res.status == 204){
        ElMessage({
          type: 'success',
          message: '删除成功',
        })
    
      }else{
        ElMessage({
          type: 'error',
          message: '删除失败',
        })
      }
      getUserData(pageConfig);
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: 'Delete canceled',
      })
    })
}
  // 批量删除
  // 获取勾选值
  
  const multipleSelect = ref([])
  // 按照返回条件禁止某些行变为可勾选的
  const selectFilter = (row,index) => {
    return row.username != 'admin'
  }
  const handleSelectionChange= (val) =>{
    multipleSelect.value = val
  }
  function sleep(delay) {
  var start = (new Date()).getTime();
  while ((new Date()).getTime() - start < delay) {
    continue;
  }
}

  const handleDeleteMore = () => {
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
      // await multipleSelect.value.forEach((row)=>{
      // const res =  proxy.$api.userdel(row.id)
      // let delList = multipleSelect.value.forEach((row)=>{
      let delList = []
      for (let row in multipleSelect.value){
        delList.push(multipleSelect.value[row].id)
      }
      console.log(delList)

      let res = await proxy.$api.usermuldel({pks:delList})
     
      if (res.status == 204){
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        
        }else{
          ElMessage({
            type: 'error',
            message: '删除失败',
          })
        }
      // sleep(20000)
      getUserData(pageConfig);
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: 'Delete canceled',
      })
    })

  }
  // 搜索框
  const hanldeSearch = async() =>{
    pageConfig.search = filterObject.search
    getUserData(pageConfig)
      }

  // 当编辑用户为admin时，禁用改登录名
  const isDisabled = ref(false)
  watch(()=> formInline.username,(n,) =>{
    if(n == 'admin'){
      isDisabled.value = true
    }else{
      isDisabled.value = false
    }
  })
</script>
<style scoped>

.el-pagination {
  justify-content: flex-end;
}
.user-header {
  display: flex;
  justify-content: space-between;
}
.el-tag-role-list {
  margin: 5px;
}

.el-form-button-add {
  display: flex;
  align-items: center;
}

</style>