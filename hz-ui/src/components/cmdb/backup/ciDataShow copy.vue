<template>

  <!-- <el-button @click="getHasConfigField">1111</el-button> -->

  <el-row>
    <el-col>
      <el-button type="primary" @click="addCiData">添加</el-button>
      <el-button @click="isShowUpload = true">导入</el-button>
      <el-button :disabled="!(multipleSelect.length >>> 0)">转移</el-button>

      <el-button :disabled="!(multipleSelect.length >>> 0)">导出</el-button>
      <el-button :disabled="!(multipleSelect.length >>> 0)" @click="multipleUpdate">批量更新</el-button>
    </el-col>
  </el-row>
  <el-table ref="ciDataTableRef" :data="ciDataList" @selection-change="handleSelectionChange" table-layout="fixed"
    highlight-current-row v-loading="tableLoading" v-if="reloadTable">
    <el-table-column type="selection" :selectable="selectable" width="55" />
    <!-- <el-table-column label="Date" width="120" @row-click="editCiData">
                  <template #default="scope">{{ scope.row.date }}</template>
</el-table-column> -->
    <el-table-column v-for="data, index in showTableField" :property="data.name" :label="data.verbose_name"
      show-overflow-tooltip sortable min-width="120">
      <!-- 列表显示布尔值按钮，以及模型关联、枚举类的label值 -->
      <template #default="scope" v-if="modelFieldType.boolean.indexOf(data.name) != -1">
        <el-switch v-model="scope.row[data.name]" class="ml-2"
          style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949"
          @change="updateCiData({ id: scope.row.id, fields: { [data.name]: scope.row[data.name] } })" />
      </template>
      <template #default="scope" v-if="modelFieldType.enum.indexOf(data.name) != -1">
        <span>{{ enumOptionNameObj[data.name][scope.row[data.name]] }}</span>
      </template>
    </el-table-column>
    <el-table-column fixed="right" label="Operations" width="80">
      <template #header>
        <el-button @click="editCol" :icon="Setting" circle />
      </template>
      <template #default="scope">
        <el-button link type="primary" size="small" @click="editCiData(scope.row)">
          查看详情
        </el-button>
        <!-- <el-button link type="primary" size="small">Edit</el-button> -->
      </template>
    </el-table-column>
  </el-table>


  <!-- 修改列模板 -->
  <el-drawer v-model="ciModelColDrawer" class="edit-drawer" direction="rtl" size="35%" @close="reloadWind">
    <template #header>
      <h4>列表显示属性配置</h4>
    </template>
    <template #default>
      <el-scrollbar>

        <el-transfer ref="sortableRef" v-model="hasConfigField" filterable :filter-method="filterMethod"
          filter-placeholder="请输入" :data="allModelField" @change="transferChange"
          :props="{ key: 'id', label: 'verbose_name' }" :titles="['模型字段', '已选字段']">
          <template #default="{ option }">

            <div class="transferLable" :draggable="hasConfigField.includes(option.id)"
              @dragstart="handleDragStart(option)" @dragenter="handleDragenter($event, option)"
              @dragend="handleDrop($event)">
              <span class="trnsferValue">{{ option.verbose_name }}</span>
              <span id="draggable" class="sort">
                <el-icon>
                  <Rank />
                </el-icon>
              </span>
            </div>

          </template>

        </el-transfer>
      </el-scrollbar>

    </template>

    <template #footer>
      <div style="flex: auto">
        <!-- <el-button @click="colCancel">取消</el-button> -->
        <el-button type="primary" @click="colCommit" v-throttle>确认</el-button>
      </div>
    </template>
  </el-drawer>

  <!-- 实例编辑的弹出框 -->

  <el-drawer v-model="ciDrawer" class="edit-drawer" direction="rtl" size="40%" :before-close="ciDataHandleClose">
    <template #header>
      <el-text tag="b" style="margin-bottom: 0;">添加实例</el-text>
    </template>
    <template #default>
      <el-scrollbar>

        <el-form ref="ciDataFormRef" style="max-width: 100%" :model="ciDataForm" label-width="auto" status-icon
          label-position="top" :disabled="false">

          <div v-for="item, index in modelInfo.field_groups">
            <h4>{{ item.verbose_name }}</h4>
            <!-- <el-row justify="space-evenly"> -->
            <el-row>

              <el-col v-for="fitem, findex in item.fields" :span="12">
                <!-- <span>{{ fitem.name  }}</span> -->

                <el-form-item :label="fitem.verbose_name" :prop="fitem.name" v-if="fitem.type === 'string'"
                  :required="fitem.required" :rules="setFormItemRule(fitem.validation_rule)">
                  <template #label>
                    <el-space :size="2">

                      <span>{{ fitem.verbose_name }}</span>
                      <el-tooltip :content="fitem.description" placement="right" effect="light"
                        v-if="fitem.description.length != 0 ? true : false">
                        <el-icon>
                          <Warning />
                        </el-icon>
                      </el-tooltip>
                    </el-space>

                  </template>
                  <div v-if="!isEdit">
                    <span v-if="ciDataForm[fitem.name] != null">{{ ciDataForm[fitem.name] }}</span>
                    <span v-else>--</span>
                  </div>
                  <!-- <el-input v-model="ciDataForm[fitem.name]" style="width: 240px" v-else-if=""></el-input> -->
                  <el-input v-model="ciDataForm[fitem.name]" style="width: 240px" v-else></el-input>

                </el-form-item>
                <el-form-item :label="fitem.verbose_name" :prop="fitem.name"
                  v-if="['text', 'json'].indexOf(fitem.type) >>> -1 ? false : true" :required="fitem.required">
                  <template #label>
                    <el-space :size="2">
                      <span>{{ fitem.verbose_name }}</span>
                      <el-tooltip :content="fitem.description" placement="right" effect="light"
                        v-if="fitem.description.length != 0 ? true : false">

                        <el-icon>
                          <Warning />
                        </el-icon>
                      </el-tooltip>
                    </el-space>

                  </template>
                  <div v-if="!isEdit">
                    <span v-if="ciDataForm[fitem.name] != null">{{ ciDataForm[fitem.name] }}</span>
                    <span v-else>--</span>
                  </div>
                  <el-input v-model="ciDataForm[fitem.name]" style="width: 240px" autosize type="textarea"
                    v-else></el-input>
                </el-form-item>
                <el-form-item :label="fitem.verbose_name" :prop="fitem.name" v-if="fitem.type === 'boolean'"
                  :required="fitem.required">
                  <!-- <span>{{ fitem.verbose_name }}</span> -->
                  <el-switch v-model="ciDataForm[fitem.name]"
                    style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949;" :disabled="!isEdit" />

                </el-form-item>
                <el-form-item :label="fitem.verbose_name" :prop="fitem.name"
                  v-if="['float'].indexOf(fitem.type) >>> -1 ? false : true" :required="fitem.required">
                  <template #label>
                    <el-space :size="2">
                      <span>{{ fitem.verbose_name }}</span>
                      <el-tooltip :content="fitem.description" placement="right" effect="light"
                        v-if="fitem.description.length != 0 ? true : false">

                        <el-icon>
                          <Warning />
                        </el-icon>
                      </el-tooltip>
                    </el-space>

                  </template>
                  <div v-if="!isEdit">
                    <span v-if="ciDataForm[fitem.name] != null">{{ ciDataForm[fitem.name] }}</span>
                    <span v-else>--</span>
                  </div>
                  <el-input-number v-model="ciDataForm[fitem.name]" :precision="2" :step="0.1" v-else />
                </el-form-item>
                <el-form-item :label="fitem.verbose_name" :prop="fitem.name"
                  v-if="['integer'].indexOf(fitem.type) >>> -1 ? false : true" :required="fitem.required">
                  <template #label>
                    <el-space :size="2">
                      <span>{{ fitem.verbose_name }}</span>
                      <el-tooltip :content="fitem.description" placement="right" effect="light"
                        v-if="fitem.description.length != 0 ? true : false">
                        <el-icon>
                          <Warning />
                        </el-icon>
                      </el-tooltip>
                    </el-space>

                  </template>
                  <div v-if="!isEdit">
                    <span v-if="ciDataForm[fitem.name] != null">{{ ciDataForm[fitem.name] }}</span>
                    <span v-else>--</span>
                  </div>
                  <el-input-number v-model="ciDataForm[fitem.name]" :step="1" v-else />
                </el-form-item>
                <el-form-item :label="fitem.verbose_name" :prop="fitem.name"
                  v-if="['date'].indexOf(fitem.type) >>> -1 ? false : true" :required="fitem.required">
                  <template #label>
                    <el-space :size="2">
                      <span>{{ fitem.verbose_name }}</span>
                      <el-tooltip :content="fitem.description" placement="right" effect="light"
                        v-if="fitem.description.length != 0 ? true : false">

                        <el-icon>
                          <Warning />
                        </el-icon>
                      </el-tooltip>
                    </el-space>

                  </template>
                  <div v-if="!isEdit">
                    <span v-if="ciDataForm[fitem.name] != null">{{ ciDataForm[fitem.name] }}</span>
                    <span v-else>--</span>
                  </div>
                  <el-date-picker v-else v-model="ciDataForm[fitem.name]" type="date" placeholder="Pick a Date"
                    format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
                </el-form-item>
                <el-form-item :label="fitem.verbose_name" :prop="fitem.name"
                  v-if="['datetime'].indexOf(fitem.type) >>> -1 ? false : true" :required="fitem.required">
                  <template #label>
                    <el-space :size="2">
                      <span>{{ fitem.verbose_name }}</span>
                      <el-tooltip :content="fitem.description" placement="right" effect="light"
                        v-if="fitem.description.length != 0 ? true : false">

                        <el-icon>
                          <Warning />
                        </el-icon>
                      </el-tooltip>
                    </el-space>

                  </template>
                  <div v-if="!isEdit">
                    <span v-if="ciDataForm[fitem.name] != null">{{ ciDataForm[fitem.name] }}</span>
                    <span v-else>--</span>
                  </div>
                  <el-date-picker v-else v-model="ciDataForm[fitem.name]" type="datetime" placeholder="Pick a Date"
                    format="YYYY/MM/DD hh:mm:ss" value-format="YYYY-MM-DD hh:mm:ss" />
                </el-form-item>
                <el-form-item :label="fitem.verbose_name" :prop="fitem.name"
                  v-if="['enum'].indexOf(fitem.type) >>> -1 ? false : true" :required="fitem.required">
                  <template #label>
                    <el-space :size="2">
                      <span>{{ fitem.verbose_name }}</span>
                      <el-tooltip :content="fitem.description" placement="right" effect="light"
                        v-if="fitem.description.length != 0 ? true : false">
                        <el-icon>
                          <Warning />
                        </el-icon>
                      </el-tooltip>
                    </el-space>

                  </template>
                  <div v-if="!isEdit">
                    <span v-if="ciDataForm[fitem.name] != null">{{
                      enumOptionNameObj[fitem.name][ciDataForm[fitem.name]] }}</span>
                    <span v-else>--</span>
                  </div>

                  <el-select v-else v-model="ciDataForm[fitem.name]" placeholder="请选择" style="width: 240px;">
                    <el-option v-for="item in enumOptionObj[fitem.validation_rule]" :key="item.value"
                      :label="item.label" :value="item.value" />
                  </el-select>
                </el-form-item>
              </el-col>

            </el-row>
            <!-- <el-form-item label="Activity name" prop="name">
                  <el-input v-model="ruleForm.name" />
                </el-form-item> -->
          </div>

        </el-form>
      </el-scrollbar>

    </template>
    <template #footer>
      <div style="flex: auto" class="footerButtonClass">
        <el-button @click="ciDataCancel(ciDataFormRef)">取消</el-button>
        <div v-if="commitActionAdd">
          <el-button type="primary" @click="ciDataCommit(ciDataFormRef)">添加</el-button>
        </div>
        <div v-else>
          <div v-if="isEdit">
            <el-button type="danger" @click="ciDataDelete">删除</el-button>
            <el-button type="primary" @click="ciDataCommit(ciDataFormRef)" v-throttle>保存</el-button>

          </div>
          <div v-else>
            <el-button type="primary" @click="isEdit = true">编辑</el-button>

          </div>

        </div>

        <!-- <el-button type="primary" @click="ciDataCommit(ciDataFormRef)" v-if="saveButtonShow">{{ postButtonLabel }}</el-button> -->
        <!-- <el-button type="primary" @click="isEdit = true" v-if="editButtonShow">编辑</el-button> -->
        <!-- <el-button type="primary" @click="ciDataCommit(ciDataFormRef)" v-else="commitActionAdd">提交</el-button> -->


        <!-- <el-button type="primary" @click="ciDrawer = false" v-else>确认</el-button> -->

      </div>
    </template>
  </el-drawer>

  <!-- 批量更新 -->
  <el-dialog v-model="multipleDia" title="批量更新" width="500" :before-close="handleClose">
    <el-form ref="multipleFormRef" style="max-width: 1000px" :model="multipleForm" label-width="auto">
      <el-form-item v-for="(item, index) in multipleForm.updateParams" :key="item.name" :label="'字段' + (index + 1)"
        :prop="'updateParams.' + index + '.value'"
        :rules="setUpdateFormItemRule(allModelFieldByNameObj[item.name]?.validation_rule)" :required="true">
        <!--       :rules="modelFieldFormItemRule"
        :rules="setUpdateFormItemRule(allModelFieldByNameObj[item.name]?.validation_rule)"
   :rules="setFormItemRule(item.name)"  -->
        <el-space>

          <el-select v-model="item.name" placeholder="选择字段" style="width: 120px" filterable>
            <el-option v-for="oitem in allModelFieldOptions" :key="oitem.value" :label="oitem.label"
              :value="oitem.value" :disabled="oitem.disable" />
          </el-select>
          <div v-if="item.name !== ''">
            <div v-if="['text', 'json'].indexOf(allModelFieldByNameObj[item.name].type) >>> -1 ? false : true">
              <el-input v-model="item.value" type="textarea" autosize style="width: 180px;" />
            </div>
            <div v-else-if="['string'].indexOf(allModelFieldByNameObj[item.name].type) >>> -1 ? false : true">
              <el-input v-model="item.value" style="width: 180px;" />
            </div>
            <div v-else-if="['enum'].indexOf(allModelFieldByNameObj[item.name].type) >>> -1 ? false : true">
              <el-select v-model="item.value" placeholder="请选择" style="width: 180px;">
                <el-option v-for="ritem in enumOptionObj[allModelFieldByNameObj[item.name].validation_rule]"
                  :key="ritem.value" :label="ritem.label" :value="ritem.value" />
              </el-select>
            </div>
            <div v-else-if="['boolean'].indexOf(allModelFieldByNameObj[item.name].type) >>> -1 ? false : true">
              <el-switch v-model="item.value" style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949;" />
            </div>
            <div v-else-if="['integer'].indexOf(allModelFieldByNameObj[item.name].type) >>> -1 ? false : true">
              <el-input-number v-model="item.value" :step="1" style="width: 180px;" />

            </div>
            <div v-else-if="['float'].indexOf(allModelFieldByNameObj[item.name].type) >>> -1 ? false : true">
              <el-input-number v-model="item.value" :precision="2" :step="0.1" style="width: 180px;" />
            </div>
            <div v-else-if="['date'].indexOf(allModelFieldByNameObj[item.name].type) >>> -1 ? false : true">
              <el-date-picker v-model="item.value" type="date" placeholder="Pick a Date" format="YYYY-MM-DD"
                value-format="YYYY-MM-DD" style="width: 180px;" />
            </div>
            <div v-else-if="['datetime'].indexOf(allModelFieldByNameObj[item.name].type) >>> -1 ? false : true">
              <el-date-picker v-model="item.value" type="datetime" placeholder="Pick a Date"
                format="YYYY/MM/DD hh:mm:ss" value-format="YYYY-MM-DD hh:mm:ss" style="width: 180px;" />
            </div>

            <div v-else>
              <el-input v-model="item.value" />

            </div>
          </div>
          <el-button class="mt-2" :icon="Delete" circle @click.prevent="removeUpdateParams(index)">

          </el-button>
        </el-space>

      </el-form-item>

    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="multipleDia = false">取消</el-button>
        <el-button @click.prevent="addUpdateParams(updateParams)">新增字段</el-button>
        <el-button v-throttle type="primary" @click="saveCommit">保存</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 实例导入 -->
  <ciDataUpload v-model:isShowUpload="isShowUpload" />
</template>

<script lang="ts" setup>
import ciDataUpload from '../ciDataUpload.vue'
import {
  Check,
  Delete,
  Setting,
  Message,
  Search,
  Star,
  Warning
} from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { Rank } from '@element-plus/icons-vue'
import { ref, reactive, watch, getCurrentInstance, nextTick, onActivated, computed, onMounted } from 'vue'
import { da, pa } from 'element-plus/es/locale/index.mjs';
const { proxy } = getCurrentInstance();
const isShowUpload = ref(false)

import { useStore } from 'vuex'
import type { FormInstance, FormRules } from 'element-plus'
const store = useStore()

// 批量更新
const multipleFormRef = ref('')
const multipleDia = ref(false)
const multipleUpdate = () => {
  multipleDia.value = true
}
const setUpdateFormItemRule = (params) => {
  // let regexp = 
  if (params === undefined) return
  if (validationRulesObj.value[params]?.field_type === 'string') {

    if (params == '' || params == null) return
    // proxy.$commonFunc.validateRegexp(regexp)
    return [{ pattern: new RegExp(validationRulesObj.value[params].rule), message: '不符合正则表达式', trigger: 'blur' }]
  }

}
const modelFieldFormItemRule = computed(() => {
  // let regexp = 
  let tempList = {}
  modelInfo.value?.field_groups?.forEach(item => {
    item.fields.forEach(field => {
      if (field.type === 'string' && field.validation_rule !== '' && field.validation_rule !== null) {
        tempList['updateParams.' + field.name] = [{ pattern: new RegExp(validationRulesObj.value[field.validation_rule]?.rule), message: '不符合正则表达式', trigger: 'blur' }]
      }
    });
  })
  return tempList
})

const multipleForm = reactive({
  updateParams: [
    { name: '', value: '' },

  ]
})
// 禁用已选择的
// const 
const addUpdateParams = () => {
  multipleForm.updateParams.push({ name: '', value: '' })
}
const removeUpdateParams = (index) => {
  multipleForm.updateParams.splice(index, 1)
  multipleFormRef.value?.clearValidate()
}
const saveCommit = () => {
  multipleFormRef.value!.validate(async (valid) => {
    console.log(valid)
    if (valid) {
      console.log(multipleForm)
      console.log(multipleFormRef.value)
      // 批量更新的方法
      let tempObj = {}
      multipleForm.updateParams?.forEach(item => {
        tempObj[item.name] = item.value
      })
      console.log(tempObj)
      // 发起更新请求

    } else {
      ElMessage({
        showClose: true,
        message: '请输入正确内容.',
        type: 'error',
      })
    }
  })

}
const updateParamsList = computed(() => {
  let tempArr = []
  multipleForm.updateParams.forEach((item) => {
    tempArr.push(item.name)
  })
  return tempArr
})
const allModelFieldOptions = computed<any>(() => {
  let tempList = []
  modelInfo.value?.field_groups?.forEach(item => {
    item.fields.forEach(field => {
      let isDisabled = false
      if (updateParamsList.value.indexOf(field.name) !== -1) {
        isDisabled = true
      }
      tempList.push({ value: field.name, label: field.verbose_name, disable: isDisabled })
    });
  })
  return tempList
})
const handleClose = () => {
  multipleDia.value = false
  resetForm(multipleFormRef.value)
}

const tableLoading = ref(true)
const setLoading = (boolean) => {
  tableLoading.value = boolean
}
const reloadTable = ref(true)
const isEdit = ref(false)
const ciModelColDrawer = ref(false)
const editCol = () => {
  ciModelColDrawer.value = true
}
// 更新

const updateCiData = async (params) => {
  setLoading(true)
  let res = await proxy.$api.updateCiModelInstance({ update_user: store.state.username, ...params })
  // console.log(123)
  if (res.status == "200") {
    ElMessage({ type: 'success', message: '更新成功', });
    // 重置表单
    ciDrawer.value = false
    resetForm(ciDataFormRef.value);
    await getCiData();
  } else {
    ElMessage({ showClose: true, message: '更新失败:' + JSON.stringify(res.data), type: 'error', })
  }
}
const selectable = () => true;


// 表格勾选
const multipleSelect = ref([])
const handleSelectionChange = (val) => {
  multipleSelect.value = val
}



// 穿梭框排序



// 表格显示内容
// 修改显示列的弹出框
// const allModelField = ref([])
const hasConfigField = ref([

])

const ciModelId = defineModel('ciModelId')
const modelInfo = ref({})
const allModelFieldInfo = computed<any>(() => {
  let tempList = {}
  modelInfo.value?.field_groups?.forEach(item => {
    item.fields.forEach(field => {
      tempList[field.id] = field
    });
  })
  return tempList
})
const allModelFieldByNameObj = computed<any>(() => {
  let tempList = {}
  modelInfo.value?.field_groups?.forEach(item => {
    item.fields.forEach(field => {
      tempList[field.name] = field
    });
  })
  return tempList
})
// 获取模型已配置的显示列
const ciModelCol = ref({})
const getHasConfigField = async () => {
  console.log(1111)
  console.log(ciModelId.value)
  let res = await proxy.$api.getCiModelCol({ model: ciModelId.value })
  // console.log(typeof res.data.fields_preferred)
  ciModelCol.value = res.data
  console.log(res.data)
  hasConfigField.value = res.data.fields_preferred
}
// const allModelFieldSort = computed(()=>{
//   let intersection = allModelField.value.filter(item => hasConfigField.value.includes(item.id));
//   let _tmpArr = []

// })
// 排序函数
const objSort = (a, b) => {

}
watch(() => hasConfigField.value, (n,) => {
  // 对列排序
  allModelField.value.sort((a, b) => {
    let indexA = n.indexOf(a.id)
    let indexB = n.indexOf(b.id)
    return indexA - indexB
  })
  // console.log(allModelField.value)
  // ciDataList.value 
  // let tempArr = ciDataList.value
  // ciDataList.value = []
  // nextTick(()=>{
  //   ciDataList.value = tempArr

  // })
}, { deep: true })
const hasNoConfigFieldList = computed(() => {
  return allModelField.value.filter(item => { return hasConfigField.value.indexOf(item) == -1 })
})
const colCommit = async () => {
  // 提交更新
  let res = await proxy.$api.updateCiModelCol({ id: ciModelCol.value.id, fields_preferred: hasConfigField.value })
  // hasConfigField.value =
  if (res.status == "200") {
    ElMessage({ type: 'success', message: '更新成功', });
    // 重置表单
    nextTick(() => {
      ciModelColDrawer.value = false
    })
    // 获取数据源列表        
  } else {
    ElMessage({ showClose: true, message: '更新失败:' + JSON.stringify(res.data), type: 'error', })
  }
}
// table显示的列名
const showTableField = computed(() => {
  let tempArr: any[] = []
  hasConfigField.value.forEach(item => {
    if (Object.keys(allModelFieldInfo.value).indexOf(item) === -1) return []
    tempArr.push({ name: allModelFieldInfo.value[item].name, verbose_name: allModelFieldInfo.value[item].verbose_name })
  })
  // console.log(tempArr)
  return tempArr
})
const reloadWind = () => {
  // window.location.reload();
  reloadTable.value = false
  setTimeout(() => {
    reloadTable.value = true
  }, 500)
}
// console.log(allModelFieldInfo.value)
// watch(() => hasConfigField.value, (n,) => {
// }, { deep: true })

// 枚举类的字段下拉框
// 获取所有枚举类的字典
const validationRulesObj = ref({})
const validationRulesByNameObj = ref({})
const getRules = async (params = null) => {
  let res = await proxy.$api.getValidationRules(params)
  // validationRules.value = res.data
  res.data.forEach(item => {
    validationRulesObj.value[item.id] = item
    // validationRulesByNameObj.value[item.name] = item
  })
}
// 生成以规则ID为key，枚举类的选项为value的对象字典
const enumOptionObj = computed(() => {
  let tempList = {}
  modelInfo.value.field_groups.forEach(item => {
    item.fields.forEach(field => {
      if (field.type === 'enum') {
        // let ruleObj = JSON.parse(validationRulesObj.value[params].rule)
        // JSON.parse(validationRulesObj.value[params].rule)
        let ruleObj = JSON.parse(validationRulesObj.value[field.validation_rule].rule)
        let tmpList = []
        Object.keys(ruleObj).forEach(ritem => {
          tmpList.push({ value: ritem, label: ruleObj[ritem] })
        })
        tempList[field.validation_rule] = tmpList
      }
    });
  })
  return tempList
})
const enumOptionNameObj = computed(() => {
  let tempList = {}
  modelInfo.value.field_groups.forEach(item => {
    item.fields.forEach(field => {
      if (field.type === 'enum') {
        // let ruleObj = JSON.parse(validationRulesObj.value[params].rule)
        // JSON.parse(validationRulesObj.value[params].rule)
        let ruleObj = JSON.parse(validationRulesObj.value[field.validation_rule].rule)
        let tmpList = {}
        Object.keys(ruleObj).forEach(ritem => {
          // tmpList.push({ value: ritem, label: ruleObj[ritem] })
          tmpList[ritem] = ruleObj[ritem]
        })
        tempList[field.name] = tmpList
      }
    });
  })
  return tempList
})

const setFormItemRule = (rule) => {
  // console.log(rule)
  // let regexp = 
  if (rule == '' || rule == null) return
  // proxy.$commonFunc.validateRegexp(regexp)
  return [{ pattern: new RegExp(validationRulesObj.value[rule].rule), message: '不符合正则表达式', trigger: 'blur' }]
}
// 初始化表单数据
const initCiDataForm = () => {
  // let initObj = {}
  modelInfo.value.field_groups.forEach((item) => {
    item.fields.forEach(item2 => {
      // console.log(item2)
      ciDataForm[item2.name] = item2.default
    })
  })
  // ciDataForm = initObj
}

// 获取模型实例字段和模型信息
const ciModel = ref({})
const modelFieldType = ref({
  enum: [],
  boolean: []
})
const allModelField = ref([])
const getModelField = async () => {
  // let res = await proxy.$api.getCiModel({ name: 'hosts' })
  // ciModel.value = res.data.results[0]
  let res2 = await proxy.$api.getCiModel({}, ciModelId.value)
  modelInfo.value = res2.data
  let tempArr = []
  modelInfo.value.field_groups?.forEach(item => {
    item.fields.forEach(field => {
      // 把字段类型是枚举类和boolean值的暂存，用于table显示枚举的原值
      if (field.type === 'enum') {
        modelFieldType.value.enum.push(field.name)

      } else if (field.type === 'boolean') {
        modelFieldType.value.boolean.push(field.name)
      }
      tempArr.push(field)
    });
  })
  allModelField.value = tempArr
  console.log(allModelField.value)
  // console.log()
}
// const allModelField = computed(() => {
//   let tempArr = []
//   modelInfo.value.field_groups?.forEach(item => {
//     item.fields.forEach(field => {
//       // 把字段类型是枚举类和boolean值的暂存，用于table显示枚举的原值
//       if (field.type === 'enum') {
//         modelFieldType.value.enum.push(field.name)

//       } else if (field.type === 'boolean') {
//         modelFieldType.value.boolean.push(field.name)
//       }
//       tempArr.push(field)
//     });
//   })
//   // console.log()
//   console.log(modelFieldType.value)
//   return tempArr
// })


// 获取ci数据
const ciDataList = ref([])
const getCiData = async () => {
  setLoading(true)
  let tmpList = []
  let res = await proxy.$api.getCiModelInstance({ model: ciModelId.value })
  res.data.results.forEach(item => {
    tmpList.push({ id: item.id, ...item.fields })
  })
  ciDataList.value = tmpList
  setLoading(false)

}
const getCiDataAsTree1 = async (params) => {
  // console.log("子组件调用的")
  // return
  setLoading(true)
  let tmpList = []
  let res = await proxy.$api.getCiDataFromModelTree(params)
  res.data.results.forEach(item => {
    tmpList.push({ id: item.id, ...item.fields })
  })
  ciDataList.value = tmpList
  setLoading(false)

}
const getCiDataAsTree = async (params) => {
  // console.log("子组件调用的")
  // return
  setLoading(true)
  let tmpList = []
  let res = await proxy.$api.getCiModelInstance(params)
  res.data.results.forEach(item => {
    tmpList.push({ id: item.id, ...item.fields })
  })
  ciDataList.value = tmpList
  setLoading(false)

}
import { ElLoading } from 'element-plus'
// const loadingInstance = ElLoading.service(options)

// setTimeout(() => {
//   loadingInstance.close()
//   }, 2000)
onMounted(async () => {
  // const loading = ElLoading.service({
  //   lock: true,
  //   text: 'Loading',
  //   background: 'rgba(0, 0, 0, 0.7)',
  // })
  await getRules();
  setLoading(false)

  // 依赖模型id
  // await getModelField();
  // await getHasConfigField();
  // await getCiData();
  // // getModelField()
  // await initCiDataForm();
  // setTimeout(() => {
  //   loading.close()
  // }, 2000)
  //   nextTick(() => {
  //   // Loading should be closed asynchronously
  //   loadingInstance.close()
  // })
})
// 监听子组件的modelid变化，再加载父组件数据
// watch(() => ciModel.value, async (n,) => {
//   console.log(modelInfo.value)
//   // await getModelField();
//   await getHasConfigField();
//   await getCiData();
//   // getModelField()
//   await initCiDataForm();
// }, { deep: true })


defineExpose({
  getHasConfigField, getCiData, initCiDataForm, getModelField, getCiDataAsTree, setLoading
})

// 实例编辑弹出框
const ciDrawer = ref(false)
const addCiData = () => {
  isEdit.value = true
  ciDrawer.value = true
  commitActionAdd.value = true
  // await initCiDataForm();

}


// 按钮显示

const currentRow = ref({})
const beforeEditCiDataForm = ref({})
const editCiData = (params) => {
  // console.log(params)
  // resetForm(ciDataFormRef.value);

  console.log(ciDataForm)
  ciDrawer.value = true
  commitActionAdd.value = false
  currentRow.value = params
  console.log(params)
  console.log(Object.keys(params))
  nextTick(() => {
    Object.keys(params).forEach(item => {
      // if (ciDataForm.hasOwnProperty(item)) ciDataForm[item] = params[item]
      if (item === 'id') return
      ciDataForm[item] = params[item]
    } // isDisabled.value = params.built_in
    )
    // ciDataForm = params
    beforeEditCiDataForm.value = JSON.parse(JSON.stringify(ciDataForm))
    console.log(beforeEditCiDataForm.value)
  })
  console.log(ciDataForm)

}

const ciDataFormRef = ref<FormInstance>()
const ciDataForm = reactive({})

const commitActionAdd = ref(true)
const updateParams = ref({})
const ciDataCommit = async (formEl: FormInstance | undefined, params = null) => {
  if (!formEl) return
  // 增加如果用户进入编辑模式后，没有更新，点击确认的话，就不会调度后端更新

  await formEl.validate(async (valid, fields) => {
    if (valid) {
      if (commitActionAdd.value) {
        // 添加
        let res = await proxy.$api.addCiModelInstance({
          model: ciModelId.value, create_user: store.state.username,
          update_user: store.state.username
          , fields: ciDataForm
        })
        // console.log(res)
        // console.log(123)
        if (res.status == "201") {
          ElMessage({ type: 'success', message: '添加成功', });
          // 重置表单
          ciDrawer.value = false
          resetForm(formEl);
          // getModelField();
          // 刷新页面
          await getCiData();
        } else {
          ElMessage({ showClose: true, message: '添加失败:' + JSON.stringify(res.data), type: 'error', })
        }
      } else {
        // console.log(111)
        if (JSON.stringify(beforeEditCiDataForm.value) === JSON.stringify(ciDataForm)) {
          isEdit.value = false
          ciDrawer.value = false
          resetForm(formEl);
          ElMessage({ showClose: true, message: '无更新,关闭窗口', type: 'info', })
          return
        } else {

          // 通过entires转为键值对数组
          const arr1 = Object.entries(beforeEditCiDataForm.value);
          const arr2 = Object.entries(ciDataForm);
          //拼接后推入set中，但是需要将数组转为json字符串否则无法对比值的一致性
          const arr = arr1.concat(arr2).map((item) => JSON.stringify(item));
          const result = Array.from(new Set(arr)).map((item) => JSON.parse(item));
          //裁剪掉第一个对象占用掉的部分，剩下就是第二个对象与其不同的属性部分
          result.splice(0, arr1.length);
          //将键值对数组转为正常对象
          const obj = Object.fromEntries(result);
          let tmpObj = {}
          Object.keys(obj).forEach(item => {
            if (obj[item] != '') {
              tmpObj[item] = obj[item]
            }
          })
          updateParams.value = tmpObj

          if (Object.keys(updateParams.value).length === 0) {
            isEdit.value = false
            ciDrawer.value = false
            resetForm(formEl);
            ElMessage({ showClose: true, message: '无更新,关闭窗口', type: 'info', })
            return
          }
          // return
        }
        let res = await proxy.$api.updateCiModelInstance({ id: currentRow.value.id, update_user: store.state.username, fields: updateParams.value })
        // console.log(123)
        console.log(store.state.username)
        if (res.status == "200") {
          ElMessage({ type: 'success', message: '更新成功', });
          // 重置表单
          ciDrawer.value = false
          isEdit.value = false
          resetForm(formEl);
          await getCiData();
        } else {
          ElMessage({ showClose: true, message: '更新失败:' + JSON.stringify(res.data), type: 'error', })
        }
      }
      // console.log('submit!')

    } else {
      console.log('error submit!', fields)
    }
  })
};
// 取消弹窗
const ciDataHandleClose = (done: () => void) => {
  ElMessageBox.confirm('是否确认关闭?')
    .then(() => {
      done()
      resetForm(ciDataFormRef.value);
      ciDrawer.value = false
      isEdit.value = false
    })
    .catch(() => {
      // catch error
    })

}
// 取消按钮
const ciDataCancel = (formEl) => {
  resetForm(formEl)
  ciDrawer.value = false
  isEdit.value = false
}
// 实例删除
const ciDataDelete = (params = null) => {
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

    // 发起删除请求
    let res = await proxy.$api.deleteCiModelInstance(currentRow.value.id)
    // 
    // let res = {status:204}
    if (res.status == 204) {
      ElMessage({
        type: 'success',
        message: '删除成功',
      })
      // 重新加载页面数据
      await getCiData();
      resetForm(ciDataFormRef.value);
      ciDrawer.value = false
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
        message: '取消删除',
      })
    })

}
// 重置表单
const resetForm = (formEl: FormInstance | undefined) => {
  if (!formEl) return
  formEl.resetFields()
}


const filterMethod = (query, item) => {
  if (!query) { return true }
  return item.verbose_name.includes(query)
}

// 往右侧添加时，手动添加头部
const transferChange = (_, direction, movedKeys) => {
  if (direction === 'right') {
    const arrList = allModelField.value.filter(item => !movedKeys.includes(item.id))
    const arrUnshift = allModelField.value.filter(item => movedKeys.includes(item.id))
    allModelField.value = [...arrUnshift, ...arrList]
  }
}

let dragTarget = null // 用于存储被拖动的目标项
let dragIndex = -1 // 被拖动项在数组中的原始索引
let targetOption = null// 拖动过程中停放目标

// 开始拖动
const handleDragStart = (option) => {
  dragTarget = option
  dragIndex = allModelField.value.findIndex(item => item === option)
  console.log(dragIndex)
}

// 放置时重新排序数组
const handleDragenter = (event, option) => {
  event.preventDefault()
  if (!dragTarget || !option) return
  targetOption = option
  if (event.target.draggable) {
    clearMovingDOM()
    const targetIndex = allModelField.value.findIndex(item => item.id === targetOption.id)
    if (targetIndex < dragIndex) { // 往上拖拽
      event.target.className = 'movingTop'
    } else { // 往下拖拽
      event.target.className = 'movingBottom'
    }
  }
}

// 鼠标放开--拖拽结束
const handleDrop = () => {
  const targetIndex = allModelField.value.findIndex(item => item.id === targetOption.id)
  // console.log(targetIndex)
  const newIndex = targetIndex

  // 更新数组顺序
  // let _tmeparr = allModelField.value
  // console.log(dragIndex)
  const [removed] = allModelField.value.splice(dragIndex, 1)
  console.log(removed)
  console.log(newIndex)
  // 添加移除都的元素到新位置
  allModelField.value.splice(newIndex, 0, removed)
  // console.log(_tmeparr)
  // allModelField.value = _tmeparr
  console.log(allModelField.value)
  // 触发hasConfigField更新
  let _tempArr = []
  allModelField.value.forEach(item => {
    if (hasConfigField.value.indexOf(item.id) !== -1) {
      _tempArr.push(item.id)
    }
  })
  hasConfigField.value = _tempArr
  // 重置拖动状态
  dragTarget = null
  targetOption = null
  dragIndex = -1
  clearMovingDOM()
  // console.log(hasConfigField.value)
}

// 清除moving Class名
const clearMovingDOM = () => {
  document.querySelectorAll('.movingBottom').forEach(Element => {
    Element.className = 'transferLable'
  })
  document.querySelectorAll('.movingTop').forEach(Element => {
    Element.className = 'transferLable'
  })
}





</script>
<style scoped lang="scss">
::v-deep(.el-transfer-panel__item).el-checkbox {
  margin-right: 10px;

  .transferLable {
    display: flex;
    justify-content: space-between !important;
  }
}

.el-transfer ::v-deep(.el-transfer-panel):first-child .sort {
  display: none;
}

:deep(.el-transfer-panel) {

  width: 35%;
  height: 500px;
}

// .el-transfer-panel__list.is-filterable{
//     height: 400px;
// }



.moving {
  border-bottom: 1px solid #409eff;
}

.movingTop {
  border-top: 1px solid #409eff;
}

.movingBottom {
  border-bottom: 1px solid #409eff;
}

:deep(.el-drawer__header) {
  margin-bottom: 0;
}



.ci_data_table {
  // width:80%;
  // height: $mainHeight - $headerHeight;
  // flex: 1;

}

.footerButtonClass {
  display: flex;
  justify-content: end;
  gap: 15px;
}

// .common-layout {
//   display: flex;
//   gap: 10px;
//   justify-content: space-between;
// }</style>