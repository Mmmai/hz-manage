<template>
  <div
    style="
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      width: 100%;
      gap: 10px;
    "
  >
    <!-- 日志检索表单 -->
    <div class="card" style="flex: 0.3">
      <el-form
        :inline="true"
        :model="formInline"
        class="demo-form-inline"
        ref="formRef"
      >
        <el-form-item label="数据源">
          <el-select
            v-model="formInline.dataSourceUrl"
            placeholder="Select"
            size="large"
            style="width: 180px"
          >
            <el-option
              v-for="(dv, di) in dataSourceOptions"
              :key="di"
              :label="dv.label"
              :value="dv.value"
              :disabled="dv.disabled"
            />
          </el-select>
        </el-form-item>
        <div>
          <el-form-item label="过滤器" prop="labelValue">
            <div v-for="(value, key, index) in labelObject" :key="index">
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
                style="width: 65px"
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
              <!-- 具体标签可选值                          v-model="labelObject[key].labelValue"       allow-create-->
              <el-select
                filterable
                clearable
                reserve-keyword
                :loading="loading"
                remote-show-suffix
                v-model="labelObject[key].labelValue"
                :multiple="
                  multipleList.includes(labelObject[key].matchMethod)
                    ? false
                    : true
                "
                style="width: 240px"
                remote
                @click="getLabelValue(key)"
                :remote-method="remoteSearch"
              >
                <el-option
                  v-for="labelOptionItem in labelObject[key].labelValueList"
                  :key="labelOptionItem.value"
                  :label="labelOptionItem.label"
                  :value="labelOptionItem.value"
                />
              </el-select>
              <el-button
                v-if="Object.keys(labelObject).length >> 1"
                size="small"
                :icon="Delete"
                circle
                style="margin: 0 5px 0px 5px"
                @click="resetFilter(key)"
              />
              <!-- <Delete v-if="Object.keys(labelObject).length >> 1 " style="width: 1em; height: 1em; margin-right: 4px;margin-left: 4px;" @click="resetFilter(key)"/> -->
            </div>
            <el-button
              type="primary"
              :icon="CirclePlus"
              circle
              size="small"
              style="margin: 0 5px 0px 5px"
              @click="addFilter"
            />

            <!-- <el-icon @click="addFilter"><CirclePlus /></el-icon> -->
          </el-form-item>
        </div>
        <el-row justify="space-between">
          <el-col :span="12">
            <el-form-item label="条数">
              <el-input-number
                v-model="formInline.limit"
                :step="100"
                :min="1"
                :max="5000"
                width="20"
              />
            </el-form-item>

            <el-form-item label="关键字">
              <el-select
                v-model="formInline.matchKeyMethod"
                style="width: 60px"
              >
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
            <el-form-item
              label="时间范围"
              prop="dateValue"
              :rules="[{ required: true }]"
            >
              <el-date-picker
                v-model="formInline.dateValue"
                type="datetimerange"
                :shortcuts="shortcuts"
                range-separator="To"
                start-placeholder="Start date"
                end-placeholder="End date"
                value-format="x"
                @visible-change="getShortCuts()"
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                :loading="onSubmitIsLoading"
                @click="onSubmit"
                >检索</el-button
              >
              <el-button type="primary" @click="reloadFilter">重置</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>
    <!-- <el-divider /> -->
    <!-- 文件导出 -->
    <div class="card">
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
            <el-table :data="dataExpandInfo" border :show-header="false">
              <el-table-column fixed="left" label="Operations" width="45">
                <template #default="scope">
                  <el-button
                    :icon="Filter"
                    link
                    type="primary"
                    size="small"
                    @click="addLabelToFilter(scope.row)"
                  >
                  </el-button>
                </template>
              </el-table-column>
              <el-table-column label="label" prop="label" width="120px" />
              <el-table-column label="value" prop="value" />
            </el-table>
          </template>
        </el-table-column>
        <el-table-column
          label="日志时间"
          prop="logTime"
          sortable
          width="200px"
        />
        <el-table-column
          label="日志等级"
          prop="level"
          width="100px"
          :filters="logLevelOption"
          :filter-method="filterTag"
          filter-placement="bottom-end"
        >
          <template #default="scope">
            <el-tag
              v-if="scope.row.level == 'DEBUG'"
              type="primary"
              effect="light"
              >DEBUG</el-tag
            >
            <el-tag
              v-else-if="scope.row.level == 'INFO'"
              type="success"
              effect="light"
              >INFO</el-tag
            >
            <el-tag
              v-else-if="scope.row.level == 'WARN'"
              type="warning"
              effect="light"
              >WARN</el-tag
            >
            <el-tag
              v-else-if="scope.row.level == 'ERROR'"
              type="danger"
              effect="light"
              >ERROR</el-tag
            >
            <el-tag
              v-else-if="scope.row.level == 'FATAL'"
              type="danger"
              effect="light"
              >FATAL</el-tag
            >
            <el-tag v-else type="info" effect="light">UNKNOWN</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="日志内容">
          <template #header>
            <div
              style="
                display: flex;
                justify-content: space-between;
                align-items: center;
              "
            >
              <el-text style="color: var(--el-table-header-text-color)"
                >日志内容</el-text
              >
              <!-- <el-input v-model="search" size="small" placeholder="Type to search" /> -->
              <el-button
                type="primary"
                plain
                v-if="isDownload"
                @click="downloadResLog(resultLogs?.queryResult)"
                >下载日志</el-button
              >
            </div>
          </template>
          <template #default="{ row }">
            <span v-html="highlight(row.logLine, highlightKey)"> </span>
            <!-- <el-button v-show="showContext == row.lokiTime">查看上下文</el-button>   -->
            <div class="operation_show">
              <el-button @click="clickToShowNearLog(row)">查看上下文</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
  <nearLogCom
    v-model:isShow="isShowNearLog"
    :highlightKey="formInline.matchKey"
    :url="formInline.dataSourceUrl"
    ref="childRef"
  />
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
    <el-icon>
      <Top />
    </el-icon>
  </el-backtop>
</template>

<script lang="ts" setup>
import {
  ref,
  reactive,
  onMounted,
  watch,
  getCurrentInstance,
  computed,
  nextTick,
  onActivated,
} from "vue";
import { Delete, Filter, CirclePlus } from "@element-plus/icons-vue";
const { proxy } = getCurrentInstance();
import { ElMessageBox, ElMessage } from "element-plus";
import nearLogCom from "@/components/loki/nearLogCom.vue";

interface User {
  lokiTime: string;
  logTime: string;
  logLine: string;
  level: string;
}
const labelObject = reactive({
  "0": {
    labelName: "",
    matchMethod: "=",
    labelValue: "",
    isMultiple: false,
    labelValueList: [],
    initLabelValueList: [],
  },
});
const formInline = reactive({
  dataSourceUrl: "",
  labelFilters: {},
  matchKey: "",
  matchKeyMethod: "|=",
  limit: 200,
  dateValue: [],
});
//
const labelList = ref([]);
const matchOptions = [
  {
    value: "=",
    label: "=",
    text: "等于",
  },
  {
    value: "=~",
    label: "=~",
    text: "包含(支持多个)",
  },
  {
    value: "!=",
    label: "!=",
    text: "不等于",
  },
  {
    value: "!~",
    label: "!~",
    text: "不包含(支持多个)",
  },
];
// 关键字匹配选项
const matchKeyOptions = [
  {
    value: "|=",
    label: "=",
    text: "包含",
  },
  {
    value: "|~",
    label: "~",
    text: "正则匹配",
  },
  {
    value: "!=",
    label: "!=",
    text: "不包含",
  },
  {
    value: "!~",
    label: "!~",
    text: "反向正则",
  },
];
const resultLogs = ref<any>({});
const isDownload = ref(false);
const logData = ref([]);
const onSubmitIsLoading = ref(false);
const logLevelOption = ref([]);
// 获取结果
const onSubmit = async () => {
  onSubmitIsLoading.value = true;
  proxy.$refs.formRef.validate(async (valid) => {
    console.log(valid);
    if (valid) {
      console.log(formInline);
      let res = await proxy.$api.lokiQuery(formInline);
      console.log(res.data);
      resultLogs.value = res.data;
      logData.value = res.data.queryResult;
      // seeMore
      // if (res.data.queryResult.length >>> moreNumber.value){
      //   isSeeMore.value = true
      //   showData.value = res.data.queryResult.slice(0,moreNumber.value)
      // }
      // console.log(res.data.queryLogLevel.length)
      // 动态获取返回的level列表
      if (res.data.queryLogLevel.length >= 1) {
        res.data.queryLogLevel.forEach((item) => {
          logLevelOption.value.push({ text: item, value: item });
        });
      }
      console.log(logLevelOption.value);

      if (logData.value.length >>> 1) {
        isDownload.value = true;
      } else {
        ElMessage({
          showClose: true,
          message: "无结果返回",
          type: "info",
        });
      }
      onSubmitIsLoading.value = false;
    } else {
      onSubmitIsLoading.value = false;
      ElMessage({
        showClose: true,
        message: "请输入正确内容.",
        type: "error",
      });
    }
  });
};
// const value1 = ref(''  )
// const value3 = ref('')
// const defaultTime = new Date(2000, 1, 1, 12, 0, 0)

const shortcuts_tmp = [
  {
    text: "Last 1 hours",
    value: [new Date(new Date().getTime() - 1 * 60 * 60 * 1000), new Date()],
  },
  {
    text: "Last 2 hours",
    value: [new Date(new Date().getTime() - 2 * 60 * 60 * 1000), new Date()],
  },
  {
    text: "Last 6 hours",
    value: [new Date(new Date().getTime() - 6 * 60 * 60 * 1000), new Date()],
  },
  {
    text: "Last 12 hours",
    value: [new Date(new Date().getTime() - 12 * 60 * 60 * 1000), new Date()],
  },
  {
    text: "Last 24 hours",
    value: [new Date(new Date().getTime() - 24 * 60 * 60 * 1000), new Date()],
  },
  {
    text: "Today",
    value: [
      new Date(new Date().setHours(0, 0, 0, 0)),
      new Date(new Date().setHours(23, 59, 59, 999)),
    ],
  },
  {
    text: "Yesterday",
    value: () => {
      const start = new Date(new Date().getTime() - 1 * 60 * 60 * 1000);
      const end = new Date();
      return [start, end];
    },
  },
  {
    text: "A week ago",
    value: () => {
      const date = new Date();
      date.setDate(date.getDate() - 7);
      return [date.setDate(date.getDate() - 7), new Date()];
    },
  },
];
const getShortCuts = () => {
  shortcuts.value = [
    {
      text: "Last 1 hours",
      value: [new Date(new Date().getTime() - 1 * 60 * 60 * 1000), new Date()],
    },
    {
      text: "Last 2 hours",
      value: [new Date(new Date().getTime() - 2 * 60 * 60 * 1000), new Date()],
    },
    {
      text: "Last 6 hours",
      value: [new Date(new Date().getTime() - 6 * 60 * 60 * 1000), new Date()],
    },
    {
      text: "Last 12 hours",
      value: [new Date(new Date().getTime() - 12 * 60 * 60 * 1000), new Date()],
    },
    {
      text: "Last 24 hours",
      value: [new Date(new Date().getTime() - 24 * 60 * 60 * 1000), new Date()],
    },
    {
      text: "Today",
      value: [
        new Date(new Date().setHours(0, 0, 0, 0)),
        new Date(new Date().setHours(23, 59, 59, 999)),
      ],
    },
    {
      text: "Yesterday",
      value: () => {
        const start = new Date(new Date().getTime() - 1 * 60 * 60 * 1000);
        const end = new Date();
        return [start, end];
      },
    },
    {
      text: "A week ago",
      value: () => {
        const date = new Date();
        date.setDate(date.getDate() - 7);
        return [date.setDate(date.getDate() - 7), new Date()];
      },
    },
  ];
};

const shortcuts = ref([]);
// 监听选择的标签，动态获取标签值

// const isMultiple = ref(false)
const multipleList = ref(["=", "!="]);
// 清除标签具体值,
const clearLabelValue = (key) => {
  labelObject[key].labelValue = "";
};
// 监听标签过滤条件 labelObject
watch(
  () => labelObject,
  (n) => {
    formInline.labelFilters = n;
  },
  { deep: true }
);

const getLabels = async () => {
  let res = await proxy.$api.lokiLabelGet({ url: formInline.dataSourceUrl });
  console.log(res);
  labelList.value = res.data.data;
  // console.log(labelList.value)
};
const nowKey = ref("");
// 动态标签获取
const getLabelValue = async (key) => {
  nowKey.value = key;
  labelObject[key].labelValue = "";
  let labelFilterObject = labelObject[key];
  if (labelFilterObject.labelName == "") {
    return;
  } else {
    let res = await proxy.$api.lokiLabelValueGet({
      url: formInline.dataSourceUrl,
      label: labelFilterObject.labelName,
    });
    //console.log(res)

    labelObject[key].initLabelValueList = res.data.data;
    // labelObject[key].labelValueList = res.data.data
  }
};

// 展开行
const dataExpandInfo = ref([]);
const expandChange = (row) => {
  console.log(row.stream);
  // console.log(expandedRows)
  dataExpandInfo.value = [];
  Object.keys(row.stream).forEach((key) => {
    let tempData = {};
    tempData["label"] = key;
    tempData["value"] = row.stream[key];
    dataExpandInfo.value.push(tempData);
  });
  console.log(dataExpandInfo.value);
};
// 展开行后，可点击添加条件
const addLabelToFilter = (row) => {
  if (Object.keys(labelObject).includes(row.label)) {
    return;
  } else {
    labelObject[row.label] = {
      labelName: row.label,
      matchMethod: "=",
      labelValue: row.value,
      isMultiple: false,
      labelValueList: [],
    };
  }
};
// 匹配值高亮
const highlight = (content, keyword) => {
  let resultContent = content.replace(/</g, "&lt;").replace(/>/g, "&gt;");
  if (!keyword) {
    return resultContent;
  } else {
    const regex = new RegExp(keyword, "gi");
    // return content.replace(regex, match => `${match}`.replace(gi, m => `<span class="${highlightClass}">${m}</span>`));
    const res = resultContent.replace(
      regex,
      `<span style="background-color: #FFFF00;">$&</span>`
    );
    return res;
  }
};
import { debounce } from "lodash";
// const debouncedRemoteMethod = debounce(()=>{

// },1000)
// select 防抖
// const debouncedRemoteMethod = proxy.$commonFunc.debounceFunc((key)=> {
const loading = ref(false);
const remoteSearch = debounce((query) => {
  loading.value = true;
  if (query === "" || query === undefined || query instanceof Object) {
    // console.log(111)
    labelObject[nowKey.value].labelValueList =
      labelObject[nowKey.value].initLabelValueList;
    loading.value = false;
  } else {
    labelObject[nowKey.value].labelValueList = labelObject[
      nowKey.value
    ].initLabelValueList.filter((item) => {
      return item.label.includes(query);
    });
    loading.value = false;
  }
}, 500);

// this.fetchOptions(query);
// }, 10)
// level过滤功能
// const logLevelOption = computed(()=>{
//   let tempOption = []
//   logData.value.forEach(item=>{
//     if (tempOption.indexOf(item.level) === -1){
//       tempOption.push(item.level)
//     }
//   })
//   let tempObj = []
//   tempOption.forEach(item=>{
//     tempObj.push({text:item,value:item})
//   })
//   return tempObj
// })
const filterTag = (value: string, row: User) => {
  return row.level === value;
};

// 监听matchMethod,实现匹配高亮,加入防抖
const highlightKey = ref("");
watch(
  () => formInline.matchKey,
  proxy.$commonFunc.debounceFunc((n) => {
    highlightKey.value = n;
  }),
  { deep: true }
);

// 标签条件删除
const resetFilter = (key) => {
  Reflect.deleteProperty(labelObject, key);
};
const labelCount = ref(1);
const addFilter = () => {
  labelCount.value += 1;
  labelObject[labelCount.value] = {
    labelName: "",
    matchMethod: "=",
    labelValue: "",
    isMultiple: false,

    labelValueList: [],
  };
  console.log(labelObject);
};

const childRef = ref("");
const isShowNearLog = ref(false);
const clickToShowNearLog = (config) => {
  isShowNearLog.value = true;
  console.log(formInline);
  // let res = await proxy.$api.dataSourceGet(dataSourceId.value)
  // dataSourceUrl.value = res.data.url
  // childRef.value.showNearLog(formInline.dataSourceUrl, config);
  childRef.value.showNearLog(config);
};
// 下载日志文件
// 防止多次点击
const downloadResLog = (logList) => {
  let exportArray = [];
  logList.forEach((item) => {
    // console.log(`${item.logTime},${item.level},${item.logLine}`)
    exportArray.push(`${item.logTime},${item.level},${item.logLine}\n`);
    // exportArray.push(`${item.logTime},${item.level},1111\n`)
  });
  let nowTimeStr = proxy.$commonFunc.getCurrentTimeString(
    "-",
    "-",
    "_",
    ":",
    ":"
  );
  console.log(nowTimeStr);
  proxy.$commonFunc.downloadArray(`export-log-${nowTimeStr}`, exportArray);
};
const dataSourceList = ref([]);
const dataSourceOptions = ref([]);
// 获取数据源列表
const getDataSource = async () => {
  let res = await proxy.$api.dataSourceGet({ page: 1, page_size: 1000 });
  dataSourceList.value = res.data.results;
  res.data.results.forEach((item) => {
    if (item.source_type == "loki") {
      if (item.isUsed) {
        dataSourceOptions.value.push({
          label: item.source_name,
          value: item.url,
          disabled: false,
        });
      } else {
        dataSourceOptions.value.push({
          label: item.source_name,
          value: item.url,
          disabled: true,
        });
      }
      if (item.isDefault) {
        formInline.dataSourceUrl = item.url;
      }
    }
  });
};

// 查看更多
const moreNumber = ref(100);
const isSeeMore = ref(false);
const showData = ref([]);
// watch(() => moreNumber.value,(n,) => {
//   if (showData.value.length << n){
//     showData.value =
//   }
// },{deep:true})
const seeMore = () => {
  moreNumber.value += 100;
  console.log(moreNumber.value);
  console.log("resutl");
  console.log(resultLogs.value.queryResult.length);
  if (resultLogs.value.queryResult.length >>> moreNumber.value) {
    showData.value = resultLogs.value.queryResult.slice(0, moreNumber.value);
    console.log("show");
    console.log(showData.value.length);
    isSeeMore.value = true;
  } else {
    showData.value = resultLogs.value.queryResult;
    isSeeMore.value = false;
  }
};

const reloadFilter = () => {
  window.location.reload();
};
//渲染时加载
onMounted(async () => {
  console.log("in loki mounted");
  await getDataSource();
  //  await
});
//
// onActivated(()=>{
//   getShortCuts()
// })
</script>

<style scoped>
:deep(.highlight-class) {
  background-color: yellow;
  /* 高亮行的背景色 */
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
  background-color: yellow;
  /* 高亮颜色 */
}

/* 悬停显示查看上下文 */

.operation_show {
  display: none;
}

.el-table__body tr:hover > td .operation_show {
  display: block;
}
</style>