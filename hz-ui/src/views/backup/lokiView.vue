<template>
  <div>
    <!-- 日志检索表单 -->
    <div>
      <el-form :inline="true" :model="formInline" class="demo-form-inline" ref="formRef">
        <el-form-item label="数据源">
          <el-select
            v-model="formInline.dataSourceUrl"
            placeholder="Select"
            size="large"
            style="width: 180px"
            >
              <el-option
                v-for="dv,di in dataSourceOptions"
                :key="di"
                :label="dv.label"
                :value="dv.value"
                :disabled="dv.disabled"
              />
          </el-select>
        </el-form-item>
        <div>
          <el-form-item label="过滤器">
            <div v-for="(value,key,index) in labelObject"
            :key="index"
              >
              <el-select
                v-model="labelObject[key].labelName"
                filterable
                clearable
                placeholder="标签"
                style="width: 120px"
                @click="getLabels"
                @change="clearLabelValue(key)"

                >       
                  <el-option
                    v-for="labelItem in labelList"
                    :key="labelItem.value"
                    :label="labelItem.label"
                    :value="labelItem.value"
                  />
              </el-select>
              <el-select
                v-model="labelObject[key].matchMethod"
                style="width: 60px"
                @change="clearLabelValue(key)"
              >
                <el-option
                  v-for="matchItem in matchOptions"
                  :key="matchItem.value"
                  :label="matchItem.label"
                  :value="matchItem.value"
                  >
                  <span style="float: left">{{ matchItem.label }}</span>
                    <span
                      style="
                        float: right;
                        color: var(--el-text-color-secondary);
                        font-size: 13px;
                      "
                    >
                      {{ matchItem.text }}
                  </span>
                </el-option>
              </el-select>
              <!-- 具体标签可选值 -->
              <el-select
                filterable
                clearable
                allow-create
                :multiple="multipleList.includes(labelObject[key].matchMethod) ? false : true"
                collapse-tags
                collapse-tags-tooltip
                v-model="labelObject[key].labelValue"
                @click="getLabelValue(key)"
                style="width: 240px"
              >
              <el-option
                v-for="labelOptionItem in labelObject[key].labelValueList"
                :key="labelOptionItem.value"
                :label="labelOptionItem.label"
                :value="labelOptionItem.value"
              />
              </el-select>
              <el-button  
                v-if="Object.keys(labelObject).length >> 1 "  
                size="small" 
                :icon="Delete" 
                circle
                style="margin: 0 5px 0px 5px;"
                @click="resetFilter(key)"
                />
              <!-- <Delete v-if="Object.keys(labelObject).length >> 1 " style="width: 1em; height: 1em; margin-right: 4px;margin-left: 4px;" @click="resetFilter(key)"/> -->
              </div>
            <el-button 
              type="primary" 
              :icon="CirclePlus" 
              circle 
              size="small" 
              style="margin: 0 5px 0px 5px;"
              @click="addFilter" 
            />

    <!-- <el-icon @click="addFilter"><CirclePlus /></el-icon> -->
      </el-form-item>
    </div>
    <el-row justify="space-between">
      <el-col :span="12">
    <el-form-item label="条数">
      <el-input-number v-model="formInline.limit" :step="1000" :min="1" :max="5000"/>
    </el-form-item>

    <el-form-item label="关键字">
      <el-select
      v-model="formInline.matchKeyMethod"
      style="width: 60px"
    >
    <!-- @change="clearLabelValue(key)" -->
    <el-option
      v-for="matchKeyItem in matchKeyOptions"
      :key="matchKeyItem.value"
      :label="matchKeyItem.label"
      :value="matchKeyItem.value"
    >
    <span style="float: left">{{ matchKeyItem.label }}</span>
      <span
        style="
          float: right;
          color: var(--el-text-color-secondary);
          font-size: 13px;
        "
      >
        {{ matchKeyItem.text }}
      </span>
    </el-option>
    </el-select>
      <el-input
        v-model="formInline.matchKey"
        style="width: 240px"
        autosize
        type="textarea"
        placeholder="请输入关键字"
      />
    </el-form-item>
  </el-col>
  <el-col :span="12">
      <el-form-item label="时间范围" :rules="[{required:true}]">
          <el-date-picker
          v-model="formInline.dateValue"
          type="datetimerange"
          :shortcuts="shortcuts"
          range-separator="To"
          start-placeholder="Start date"
          end-placeholder="End date"
          value-format="x"
            />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="onSubmitIsLoading" @click="onSubmit">检索</el-button>
      </el-form-item>
    </el-col>

    </el-row>

  </el-form>
    </div>
    <!-- <el-divider /> -->
    <!-- 文件导出 -->
    <el-row justify="end">   
      <el-button  type="primary" v-if="isDownload" @click="downloadResLog(resultLogs.queryResult)">下载日志</el-button>
    </el-row>
  <el-table 
      :data="resultLogs.queryResult"  
      style="width: 98%"
      @expand-change="expandChange"
      :default-sort="{ prop: 'logTime', order: 'descending' }"
    >
      <!-- @cell-mouse-enter="enterRow"	
      @cell-mouse-leave="leaveRow" -->
      <!-- 展开的详情，可以点击label添加到过滤条件 -->
    <el-table-column type="expand">
      <!-- <template #default="props"> -->
        <template #default="props">
        <el-table :data="dataExpandInfo" border :show-header="false" >
          <el-table-column fixed="left" label="Operations" width="45">
            <template #default="scope">
              <el-button :icon="Filter" link type="primary" size="small" @click="addLabelToFilter(scope.row)">
                
              </el-button>
            </template>
          </el-table-column>
          <el-table-column label="label" prop="label" width="120px"/>
          <el-table-column label="value" prop="value" />
        </el-table>
      </template>
    </el-table-column>
    <el-table-column label="日志时间" prop="logTime" sortable  width="200px"/>
    <el-table-column label="日志等级" prop="level" width="100px">
      <template #default="scope">
        <el-tag v-if="scope.row.level == 'DEBUG'" type="primary" effect="light">DEBUG</el-tag>
        <el-tag v-else-if="scope.row.level == 'INFO'" type="success" effect="light">INFO</el-tag>
        <el-tag v-else-if="scope.row.level == 'WARN'" type="warning" effect="light">WARN</el-tag>
        <el-tag v-else-if="scope.row.level == 'ERROR'" type="danger" effect="light">ERROR</el-tag>
        <el-tag v-else-if="scope.row.level == 'FATAL'" type="danger" effect="light">FATAL</el-tag>
        <el-tag v-else type="info" effect="light">UNKNOWN</el-tag>

      </template>

    </el-table-column>
    <el-table-column label="日志内容"    >

      <template #default="{ row }">
      <span v-html="highlight(row.logLine, highlightKey)"> </span>
        <!-- <el-button v-show="showContext == row.lokiTime">查看上下文</el-button>   -->
      <div class="operation_show">
        <el-button @click="showNearLog(row)">查看上下文</el-button>
      </div>
      </template>


    </el-table-column>
  </el-table>
<!-- 显示上下文弹窗 -->
<el-dialog v-model="dialogTableVisible" title="日志上下文" width="95%" top="9vh" @close="closeDialog">
  <template #header="{ close, titleId, titleClass }">
      <div class="my-header">
        <div :id="titleId" :class="titleClass" style="display: flex;justify-content: space-between;">
          <span>日志上下文</span>
          <el-button  type="primary" @click="downloadResLog(nearLogData)" style="margin-right: 20px;">
            下载日志
          </el-button>
        </div>
      </div>
    </template>
  <el-table :data="nearLogData" ref="nearLogRef" style="width: 100%" height="600" 
    :row-class-name="highlightRow"
  >
  <el-table-column type="index" width="50" />

    <el-table-column label="日志时间" prop="logTime"  width="200px"/>
      <el-table-column label="日志等级" prop="level" width="100px">
        <template #default="scope">
          <el-tag v-if="scope.row.level == 'DEBUG'" type="primary" effect="light">DEBUG</el-tag>
          <el-tag v-else-if="scope.row.level == 'INFO'" type="success" effect="light">INFO</el-tag>
          <el-tag v-else-if="scope.row.level == 'WARN'" type="warning" effect="light">WARN</el-tag>
          <el-tag v-else-if="scope.row.level == 'ERROR'" type="danger" effect="light">ERROR</el-tag>
          <el-tag v-else-if="scope.row.level == 'FATAL'" type="danger" effect="light">FATAL</el-tag>
          <el-tag v-else type="info" effect="light">UNKNOWN</el-tag>

        </template>

      </el-table-column>
      <el-table-column label="日志内容"    >
        <template #default="{ row }">
        <span v-html="highlight(row.logLine, highlightKey)"> </span>
        </template>

      </el-table-column>
  </el-table>
  <template #footer>
      <div class="dialog-footer">
        <el-button type="primary" @click="changeBackwardLimit">往前翻</el-button>
        <el-button type="primary" @click="changeForwardLimit">往后翻</el-button>
        <el-button type="primary" @click="toNowRow">跳转到分析行</el-button>

      </div>
    </template>
</el-dialog>

  </div>
  <el-backtop :bottom="50" target=".el-main">
    <!-- <div
      style="
        height: 100%;
        width: 100%;
        background-color: var(--el-bg-color-overlay);
        box-shadow: var(--el-box-shadow-lighter);
        text-align: center;
        line-height: 40px;
        color: #1989fa;
      "
    >
    </div> -->
    <el-icon><Top /></el-icon>

  </el-backtop>
  </template>
  
  <script lang="ts" setup>
  import { ref,reactive, onMounted,watch,getCurrentInstance, nextTick  } from 'vue'
  import { Delete, Filter,CirclePlus } from '@element-plus/icons-vue'
  const { proxy } = getCurrentInstance();
  import {ElMessageBox,ElMessage} from 'element-plus'

  const labelObject = reactive({
    "0":{
        "labelName":'',
        "matchMethod":'=',
        "labelValue":'',
        "isMultiple":false,
        "labelValueList":[]
        },
  })
  const formInline = reactive({
    dataSourceUrl:'',
    labelFilters:{},
    matchKey:"",
    matchKeyMethod:"|=",
    limit:1000,
    })
  // 
  const labelList = ref([])
  const matchOptions = [
    {
      value: '=',
      label: '=',
      text:"等于"
    },
    {
      value: '=~',
      label: '=~',
      text:"包含(支持多个)"
    },
    {
      value: '!=',
      label: '!=',
      text:"不等于"
    },
    {
      value: '!~',
      label: '!~',
      text:"不包含(支持多个)"
    },
    ]
  // 关键字匹配选项
  const matchKeyOptions = [
    {
      value: '|=',
      label: '=',
      text:"包含"
    },
    {
      value: '|~',
      label: '~',
      text:"正则匹配"
    },
    {
      value: '!=',
      label: '!=',
      text:"不包含"
    },
    {
      value: '!~',
      label: '!~',
      text:"反向正则"
    }
    ]
  const resultLogs = ref({})
  const isDownload = ref(false)
  const logData = ref([])
  const onSubmitIsLoading = ref(false)
  // 获取结果
  const onSubmit = async() => {
    onSubmitIsLoading.value = true
    proxy.$refs.formRef.validate(async(valid) =>{
      console.log(valid)
      if (valid){
        console.log(formInline)
        let res = await proxy.$api.lokiQuery(formInline)
        // console.log(res.data)
        resultLogs.value = res.data
        logData.value = res.data.queryResult
        if (logData.value.length >>> 1){
          isDownload.value = true
        }
        onSubmitIsLoading.value = false
      }else{
            ElMessage({
            showClose: true,
            message: '请输入正确内容.',
              type: 'error',})
        }
    })
  }
  // const value1 = ref(''  )
  // const value3 = ref('')
  // const defaultTime = new Date(2000, 1, 1, 12, 0, 0)

  const shortcuts = [
  {
      text: 'Last 1 hours',
      value: [new Date(new Date().getTime() - 1 * 60 * 60 * 1000),new Date()],
    },
    {
      text: 'Last 2 hours',
      value: [new Date(new Date().getTime() - 2 * 60 * 60 * 1000),new Date()],
    },
    {
      text: 'Last 6 hours',
      value: [new Date(new Date().getTime() - 6 * 60 * 60 * 1000),new Date()],
    },
    {
      text: 'Last 12 hours',
      value: [new Date(new Date().getTime() - 12 * 60 * 60 * 1000),new Date()],
    },
    {
      text: 'Last 24 hours',
      value: [new Date(new Date().getTime() - 24 * 60 * 60 * 1000),new Date()],
    },
    {
      text: 'Today',
      value: [new Date(new Date().setHours(0,0,0,0)),new Date(new Date().setHours(23, 59, 59, 999))]
    },
    {
      text: 'Yesterday',
      value: () => {
        const start = new Date(new Date().getTime() - 1 * 60 * 60 * 1000)
        const end = new Date()
        return [start,end]
      },
    },
    {
      text: 'A week ago',
      value: () => {
        const date = new Date()
        date.setDate(date.getDate() - 7)
        return [date.setDate(date.getDate() - 7),new Date()]
      },
    },
  ]
  // 监听选择的标签，动态获取标签值

  // const isMultiple = ref(false)
  const multipleList = ref(['=',"!="])
  // 清除标签具体值,
  const clearLabelValue = (key) => {
    labelObject[key].labelValue = ''
  }
  // 监听标签过滤条件 labelObject
  watch(() => labelObject,(n,) => {
    formInline.labelFilters = n
  },{deep:true})

  const getLabels = async () => {
    let res = await proxy.$api.lokiLabelGet({'url':formInline.dataSourceUrl})
    console.log(res)
    labelList.value = res.data.data
    // console.log(labelList.value)
  }
  // 动态标签获取
  const getLabelValue = async (key) => {
    let labelFilterObject = labelObject[key]
    if (labelFilterObject.labelName == ''){
      return
    }else{
    let res = await proxy.$api.lokiLabelValueGet({'url':formInline.dataSourceUrl,'label':labelFilterObject.labelName})
    //console.log(res)
    labelObject[key].labelValueList = res.data.data
  }
  }
  
  // 展开行
  const dataExpandInfo = ref([])
  const expandChange = (row) => {
    console.log(row.stream)
    // console.log(expandedRows)
    dataExpandInfo.value = []
    Object.keys(row.stream).forEach(key => {
      let tempData = {}
      tempData["label"] = key
      tempData["value"] = row.stream[key]
      dataExpandInfo.value.push(tempData) 
    });
    console.log(dataExpandInfo.value)
  }
  // 展开行后，可点击添加条件
  const addLabelToFilter = (row) => {
    if (Object.keys(labelObject).includes(row.label)){
      return
    }else{
    labelObject[row.label] = {
        "labelName":row.label,
        "matchMethod":'=',
        "labelValue":row.value,
        "isMultiple":false,
        "labelValueList":[]
        }
    }
  }
// 匹配值高亮
 const highlight = (content, keyword) => {
      if (!keyword) {
        return content;
      }else{
      const regex = new RegExp(keyword, 'gi');
      // return content.replace(regex, match => `${match}`.replace(gi, m => `<span class="${highlightClass}">${m}</span>`));
      const res = content.replace(regex,`<span style="background-color: #ff9b2d;">$&</span>`)
      return res;
      }
    }
 // 监听matchMethod,实现匹配高亮,加入防抖
 const highlightKey = ref('')
 watch(() => formInline.matchKey,proxy.$commonFunc.debounceFunc((n,)=> {
    highlightKey.value = n
  }),{deep:true})
  
  // 标签条件删除
  const resetFilter = (key) => {
    Reflect.deleteProperty(labelObject,key)
  }
  const labelCount = ref(1)
  const addFilter = () => {
    labelCount.value +=1
    labelObject[labelCount.value] = {
        "labelName":'',
        "matchMethod":'=',
        "labelValue":"",
        "isMultiple":false,

        "labelValueList":[]
        }
    console.log(labelObject)
  }
  // 显示查看上下文的按钮
  const dialogTableVisible = ref(false)
  const backwardLimit = ref(10)
  const forwardLimit = ref(10)
  // 往前看
  const changeBackwardLimit = async()=> {
    backwardLimit.value += 10
    await getNearLog(nowRow.value)
    // 跳转到第一行
    tableScrollToRow(proxy.$refs.nearLogRef,0)

  }
  // 往后看
  const changeForwardLimit = async()=> {
    forwardLimit.value += 10
    await getNearLog(nowRow.value)
    // 跳转到最后一行
    tableScrollToRow(proxy.$refs.nearLogRef,nearLogData.value.length)

  }
  const closeDialog = ()=>{
    backwardLimit.value = 10
    forwardLimit.value = 10
    nowRowIndex.value = 0

  }
  const nearLogData = ref([])
  const nowRow = ref('')
  // 上下文日志请求
  const getNearLog = async(row) => {
    let beforeRes = await proxy.$api.lokiNearQuery({'url':formInline.dataSourceUrl,"targetLog":row,"limit":backwardLimit.value,"direction":"backward"})
    let beforeLogList = beforeRes.data.queryResult
    console.log(beforeLogList)
    let afterRes = await proxy.$api.lokiNearQuery({'url':formInline.dataSourceUrl,"targetLog":row,"limit":forwardLimit.value,"direction":"forward"})
    let afterLogList = afterRes.data.queryResult
    console.log(afterLogList)
    nearLogData.value = [...beforeLogList,...afterLogList]
  }
  const showNearLog = async(row) => {
    nowRow.value = row
    dialogTableVisible.value = true
    // let res = await
    // console.log(afterLogList)
    // console.log(nearLogData.value)
    await getNearLog(row)
    nextTick(()=>{
      tableScrollToRow(proxy.$refs.nearLogRef,nowRowIndex.value)
    })
    
  }
  // 定位到表格滚动条的位置
  function tableScrollToRow(tableElement, rowindex, isPrecise = true) {
    const theTableRows = tableElement.$el.querySelectorAll('.el-table__body tbody .el-table__row')
    let scrollTop = 0;
    for (let i = 0; i < theTableRows.length; i++) {
      if (i === rowindex) {
        break
      }
      scrollTop += theTableRows[i].offsetHeight
      if (!isPrecise) {
        scrollTop *= (rowindex - 2);
        break;
      }
    
    }
    tableElement.scrollTo(0, scrollTop)
  }
  // const nowRowIndex = computed(()=>{
  //   console.log("计算数学")
  //   console.log(nearLogData.value)
  //   console.log(nowRow.value)
  //    return nearLogData.value.indexOf(nowRow.value)+1
  // })
  const nowRowIndex = ref(0)
  watch(() => nearLogData.value,(n,) => {
    // console.log(n)
    nowRowIndex.value = n.findIndex(item => item.lokiTime === nowRow.value.lokiTime)
  })
  const toNowRow = ()=>{
    tableScrollToRow(proxy.$refs.nearLogRef,nowRowIndex.value)
  }
//   const nearLogRef = ref(null)
//   onMounted(() => {
//   // 方法一：尝试使用 Element Plus 提供的方法（如果存在）
//   if (nearLogRef.value && nearLogRef.value.scrollBarRef) {
//     console.log('xxxxx')
//     nearLogRef.value.scrollBarRef.setScrollTop(30);
//   }
// })
// 高亮显示上下文界面的匹配行
const highlightRow = ({row,}) => {
  if (row.lokiTime == nowRow.value["lokiTime"]){
    return "highlight-class"
  }
}
// 下载日志文件
// 防止多次点击
const downloadResLog = (logList)=>{
  let exportArray = []
    logList.forEach(item => {
    // console.log(`${item.logTime},${item.level},${item.logLine}`)
    exportArray.push(`${item.logTime},${item.level},${item.logLine}\n`)
    // exportArray.push(`${item.logTime},${item.level},1111\n`)

  });
  let nowTimeStr = proxy.$commonFunc.getCurrentTimeString('-','-','_',':',':')
  console.log(nowTimeStr)
  proxy.$commonFunc.downloadArray(`export-log-${nowTimeStr}`,exportArray)
}
  const dataSourceList = ref([])
  const dataSourceOptions = ref([])
  // 获取数据源列表
  const getDataSource = async()=>{
    let res = await proxy.$api.dataSourceGet()
    dataSourceList.value = res.data
    res.data.forEach(item =>{
      if (item.source_type == 'loki'){
        if(item.isUsed){
          dataSourceOptions.value.push({"label":item.source_name,"value":item.url,"disabled":false})
        }else{
          dataSourceOptions.value.push({"label":item.source_name,"value":item.url,"disabled":true})
        }
        if (item.isDefault){
          formInline.dataSourceUrl = item.url
        }
      }
    })
  } 
  //渲染时加载
  onMounted(async ()=>{
   await getDataSource();
  //  await 
  }) 
  </script>

  <style scoped>
  :deep(.highlight-class){
  background-color: yellow; /* 高亮行的背景色 */
}
  .demo-datetime-picker {
    display: flex;
    width: 100%;
    padding: 0;
    flex-wrap: wrap;
  }
  .demo-datetime-picker .block {
    padding: 30px 0;
    text-align: center;
    border-right: solid 1px var(--el-border-color);
    flex: 1;
  }
  .demo-datetime-picker .block:last-child {
    border-right: none;
  }
  .demo-datetime-picker .demonstration {
    display: block;
    color: var(--el-text-color-secondary);
    font-size: 14px;
    margin-bottom: 20px;
  }
  .demo-form-inline .el-input {
  --el-input-width: 220px;
}

.demo-form-inline .el-select {
  --el-select-width: 220px;
}
/* .el-tag:hover {
  background-color: #6cc7f5;
  color: white;
} */
/* .log-res {
  overflow-y: scroll;
} */

/* 匹配值高亮 */
.highlight {
  background-color: yellow; /* 高亮颜色 */
}

/* 悬停显示查看上下文 */

.operation_show {
  display: none;
}
.el-table__body tr:hover > td .operation_show {
  display: block;
}

  </style>
  