<template>
  <div class="card">
      <div class="user-header">
        <div>
          <el-button type="primary" size="small" @click="handleAdd">新增</el-button>
        </div>

      </div>
      <!-- 表格内容 -->
      <div>
        <el-table border v-loading="loading" :data="roleList" style="width: 100%" max-height="500px"
          highlight-current-row :table-layout="tableLayout" @selection-change="handleSelectionChange"
          @row-click="handleClick">
          <el-table-column type="selection" width="55" :selectable="selectFilter" />
          <el-table-column v-for="item in roleListCol" :key="item.prop" :label="item.label" :prop="item.prop">

          </el-table-column>
          <el-table-column fixed="right" label="操作" width="150">
            <template #default="scope">
              <el-button v-if="scope.row.role == '管理员'" type="primary" size="small" @click="handleEdit(scope.row)"
                disabled>编辑</el-button>
              <el-button v-else type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
              <el-button v-if="scope.row.role == '管理员'" type="danger" size="small" disabled
                @click="handleDelete(scope.row)">删除</el-button>
              <el-button v-else type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>

            </template>
          </el-table-column>
        </el-table>
        <!-- 分页 -->
      </div>
      <div class="demo-pagination-block">
        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 30, 40]"
          :small="small" :disabled="disabled" :background="background" layout="total, prev, pager, next"
          :total="totalCount" :hide-on-single-page="isSinglePage" @size-change="handleSizeChange"
          @current-change="handleCurrentChange" />
      </div>
  </div>
  <!-- 新增的弹出框 -->
  <el-dialog v-model="dialogVisible" :title="action == 'add' ? '新增角色' : '编辑角色'" width="25%" :before-close="handleClose">
    <el-form :inline="true" :model="formInline" class="demo-form-inline" label-position="right" label-width="80px"
      ref="userFrom" status-icon>
      <el-form-item label="角色名称" prop="role" :rules="[{ required: true }]">
        <el-input v-model="formInline.role" placeholder="" clearable :disabled="isDisabled" />
      </el-form-item>

      <el-form-item label="菜单授权" prop="roleMenus">
        <div style="border: 1px solid var(--el-border-color); width: 200px;">
          <el-tree ref="menuTreeRef" v-model="formInline.roleMenus" :data="dataSource" show-checkbox node-key="id"
            default-expand-all :expand-on-click-node="false">
          </el-tree>
        </div>
      </el-form-item>
      <el-row style="justify-content: space-around;">
        <el-form-item>
          <el-button @click="cancelAdd">取消</el-button>
          <el-button type="primary" @click="handleCommit"> 确定</el-button>

        </el-form-item>
      </el-row>
      <!-- </div> -->
    </el-form>

  </el-dialog>
</template>

<script lang="ts" setup>
import { getCurrentInstance, onMounted, computed, ref, reactive, watch, toRaw, nextTick } from 'vue'
const currentSelectRow = ref({})
const { proxy } = getCurrentInstance();
import { ElMessageBox, ElMessage } from 'element-plus'


// 搜素框变量
const filterObject = reactive({
  search: ""
})
// 表格变量
const loading = ref(false)
const roleList = ref([])
// const currentUserList = ref([])
const tableLayout = ref('auto')
const roleListCol = ref([
  {
    prop: 'role',
    label: '角色名称',
  },
  {
    prop: 'user_count',
    label: '用户数量',
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
  page: currentPage.value,
  size: pageSize.value,
  search: "",
  ordering: "id"
})
// 少于分页需求则不显示分页
const isSinglePage = ref(false)

// 角色列表
const roleObject = ref({})
// cumputed 
onMounted(async () => {
  // 初始化数据切片
  // api请求获取所有数据

  await getRoleData(pageConfig);
  getMenuListFunc();
  console.log(formInline)
  // selectFirst()
});
// 默认选中第1行
const selectFirst = () => {
  currentSelectRow.value = roleList.value[0]
}

// 获取角色数据
const getRoleData = async (config) => {
  let roleinfo = await proxy.$api.getRole(config)
  console.log(roleinfo)
  roleList.value = roleinfo.data.results.map((item) => {
    item.userinfo_set = item.userinfo_set.length
    return item
  })

  //   #roleList.value.length 
  totalCount.value = roleinfo.data.count
  // 隐藏下面的分页
  if (totalCount.value < pageSize.value) {
    isSinglePage.value = true
  }
  // 统计用户个数

  // 将role列表转化为dict
  // console.log(roleInfo.value)
  for (let key in roleList.value) {
    let rolename = roleList.value[key].role;
    let roleid = roleList.value[key].id
    roleObject.value[roleid] = rolename
  }
}

const handleSizeChange = (val) => {
  pageConfig.size = val
}
const handleCurrentChange = (val) => {
  pageConfig.page = val
}
// 点击表格行
// const currentSelectRow = ref({})

const handleClick = (val) => {
  // console.log(val)
  currentSelectRow.value = val
}

// 弹出框

// 新增按钮
const dialogVisible = ref(false)
// from表单数据
const formInline = reactive({
  role: "",
  roleMenus: []
})
const action = ref('add')
// 显示新增弹出框
const handleAdd = () => {
  action.value = 'add'
  dialogVisible.value = true
  console.log(formInline)

}
// 取消新增弹出框
const cancelAdd = () => {
  dialogVisible.value = false
  // 重置表单
  proxy.$refs.userFrom.resetFields();
  setCheckedKeys([])
}
// 关闭弹出框
const handleClose = (done) => {
  ElMessageBox.confirm('是否确认关闭?')
    .then(() => {
      proxy.$refs.userFrom.resetFields();
      setCheckedKeys([])

      done()

    })
    .catch(() => {
      // catch error
    })
}
// 点击触发提交
const handleCommit = () => {
  // let newMenuList = menuTreeRef.value.getCheckedKeys().concat(menuTreeRef.value.getHalfCheckedKeys())
  let newMenuList = menuTreeRef.value.getCheckedKeys()
  // 更新对应关系
  formInline.roleMenus = newMenuList
  // getCheckedKeys()
  console.log(formInline)

  proxy.$refs.userFrom.validate(async (valid) => {
    if (valid) {
      // 新增接口
      if (action.value == 'add') {
        console.log(formInline)
        let res = await proxy.$api.roleadd(formInline)
        if (res.status == 201) {
          dialogVisible.value = false
          ElMessage({
            type: 'success',
            message: '添加成功',
          })
          // 重置表单
          proxy.$refs.userFrom.resetFields();
          setCheckedKeys([])
          getRoleData(pageConfig);
        } else {
          ElMessage({
            showClose: true,
            message: '添加失败:' + JSON.stringify(res.data),
            type: 'error',
          })
        }
      }
      // 编辑接口
      else {
        console.log(formInline)
        let res = await proxy.$api.roleupdate({ id: formInline.id, role: formInline.role, menu: formInline.roleMenus })
        console.log(res)
        if (res.status == 200) {
          dialogVisible.value = false
          // 重置表单
          proxy.$refs.userFrom.resetFields();
          setCheckedKeys([])
          getRoleData(pageConfig);
          ElMessage({
            type: 'success',
            message: '更新成功',
          })
        }
        else {
          ElMessage({
            showClose: true,
            message: '更新失败:' + JSON.stringify(res.data),
            type: 'error',
          })
        }
      }
      getRoleData(pageConfig);
    } else {
      ElMessage({
        showClose: true,
        message: '请输入正确内容.',
        type: 'error',
      })
    }
    console.log(formInline)
  })
}

// 编辑
const handleEdit = (row) => {
  action.value = 'edit'
  dialogVisible.value = true
  // 清除新增按钮会显示编辑按钮的记录
  proxy.$nextTick(() => { Object.assign(formInline, row) })
  // setCheckedKeys(row.menu)
  setCheckedKeys(row.menu)
  console.log(formInline)

  // formInline.roleMenus = row.menu
}
// 删除
const handleDelete = (row) => {
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
    .then(async () => {
      // 发起删除请求
      let res = await proxy.$api.roledel(row.id)
      if (res.status == 204) {
        ElMessage({
          type: 'success',
          message: '删除成功',
        })
        await getRoleData(pageConfig);
        // selectFirst()
      } else {
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

const multipleSelect = ref([])
// 按照返回条件禁止某些行变为可勾选的
const selectFilter = (row, index) => {
  return row.role != '管理员'
}
const handleSelectionChange = (val) => {
  multipleSelect.value = val
}

// 搜索框
// const hanldeSearch = async() =>{
//   pageConfig.search = filterObject.search
//     }
// 弹出框中的tree
import { ElTree } from 'element-plus'

import type Node from 'element-plus/es/components/tree/src/model/node'

const menuTreeRef = ref<InstanceType<typeof ElTree>>()
interface Tree {
  id: number
  label: string
  children?: Tree[]
}
const dataSource = ref([])
const getMenuListFunc = (async () => {
  let res = await proxy.$api.getMenuList()
  console.log(res)
  dataSource.value = res.data.results
})


const setCheckedKeys = (val) => {
  nextTick().then(() => {
    menuTreeRef.value?.setCheckedKeys(val, false)
  })
}

const isDisabled = ref(false)
watch(() => formInline.role, (n,) => {
  if (n == '管理员') {
    isDisabled.value = true
  } else {
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
  margin: 10px 0px;
}

.el-tag-role-list {
  margin: 5px;
}

.el-form-button-add {
  display: flex;
  align-items: center;
}

.role-menu {
  display: flex;
  align-items: flex-start;

}
</style>