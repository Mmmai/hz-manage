<template>
  <!-- 展示查询条件 -->
  <div class="card">
    <el-descriptions class="margin-top" title="查询条件" :column="4" border>
      <template #extra>
        <el-tooltip content="切换流程是否换行显示" placement="top">
          <el-button
            type="primary"
            @click="isWrap ? (isWrap = false) : (isWrap = true)"
            >切换</el-button
          >
        </el-tooltip>
        <el-tooltip content="返回任务列表" placement="top">
          <el-button type="primary" @click="goToMission">
            <el-icon><Back /></el-icon>
          </el-button>
        </el-tooltip>
      </template>
      <el-descriptions-item>
        <template #label>
          <div class="cell-item">
            <el-icon :style="iconStyle">
              <user />
            </el-icon>
            查询用户
          </div>
        </template>
        {{ currenUsername }}
      </el-descriptions-item>
      <el-descriptions-item>
        <template #label>
          <div class="cell-item">
            <el-icon :style="iconStyle">
              <iphone />
            </el-icon>
            请求ID
          </div>
        </template>
        {{ missionId }}
      </el-descriptions-item>
      <el-descriptions-item>
        <template #label>
          <div class="cell-item">
            <el-icon :style="iconStyle">
              <location />
            </el-icon>
            时间范围
          </div>
        </template>
        {{ logDate[0] }} - {{ logDate[1] }}
      </el-descriptions-item>
      <el-descriptions-item>
        <template #label>
          <div class="cell-item">
            <el-icon :style="iconStyle">
              <tickets />
            </el-icon>
            任务状态
          </div>
        </template>
        <el-tag :type="missionStatus.level"
          >{{ missionStatus.status }}
          <el-icon class="is-loading" v-show="missionStatus.isLoading">
            <Loading /> </el-icon
        ></el-tag>
      </el-descriptions-item>
      <el-descriptions-item>
        <template #label>
          <div class="cell-item">
            <el-icon :style="iconStyle">
              <tickets />
            </el-icon>
            数据源
          </div>
        </template>
        {{ dataSourceName }}
      </el-descriptions-item>
      <el-descriptions-item>
        <template #label>
          <div class="cell-item">
            <el-icon :style="iconStyle">
              <tickets />
            </el-icon>
            业务流
          </div>
        </template>
        {{ flowName }}
      </el-descriptions-item>
      <el-descriptions-item>
        <template #label>
          <div class="cell-item">
            <el-icon :style="iconStyle">
              <office-building />
            </el-icon>
            分析ID
          </div>
        </template>
        {{ matchKey }}
      </el-descriptions-item>
    </el-descriptions>
    <el-divider>
      <!-- <el-icon><star-filled /></el-icon> -->
      分析结果
    </el-divider>
    <!-- direction="vertical" -->

    <!-- <el-icon><Right /></el-icon> -->
    <!-- :style="{ width: '100%', display: 'flex' }" -->
    <div
      style="position: absolute; top: 50%; left: 50%"
      v-if="missionStatus.isLoading"
      v-loading="missionStatus.isLoading"
    ></div>
    <el-space :wrap="isWrap" :size="10" v-else>
      <div
        v-for="(v, index) in flowSort"
        :key="index"
        :style="{
          width: '100%',
          heigth: '320px',
          display: 'flex',
          'align-items': 'center',
        }"
      >
        <el-card class="result-card">
          <template #header>
            <span>环节{{ index + 1 }}: {{ logModuleObj[v].module_name }}</span>
          </template>
          <!-- {{ logModuleObj.k.module_name }}
              日志数量:{{ v.queryResult.length }},错误日志数:{{ v.queryInfo.errorCount }} -->
          <!-- <div style="width: 500px;height: 100px;"> -->

          <el-space wrap :size="50">
            <el-result
              :icon="reqStatus(allDataObj[v])"
              :title="resultTip(allDataObj[v])"
            >
            </el-result>
            <el-space direction="vertical">
              <el-statistic :value="allDataObj[v].queryResult.length">
                <template #title>
                  <div style="display: inline-flex; align-items: center">
                    匹配数
                    <el-tooltip
                      effect="dark"
                      content="分析ID返回的日志条数"
                      placement="top"
                    >
                      <el-icon style="margin-left: 4px" :size="12">
                        <Warning />
                      </el-icon>
                    </el-tooltip>
                  </div>
                </template>
              </el-statistic>
              <el-statistic :value="allDataObj[v].queryInfo.errorCount">
                <template #title>
                  <div style="display: inline-flex; align-items: center">
                    错误数
                    <el-tooltip
                      effect="dark"
                      content="匹配到的日志中,日志等级为ERROR及以上的数量"
                      placement="top"
                    >
                      <el-icon style="margin-left: 4px" :size="12">
                        <Warning />
                      </el-icon>
                    </el-tooltip>
                  </div>
                </template>
              </el-statistic>
            </el-space>
          </el-space>
          <template #footer>
            <el-space :style="{ width: '100%', justifyContent: 'flex-end' }">
              <el-link
                type="primary"
                @click="downloadStepLog(v, allDataObj[v])"
                :disabled="
                  allDataObj[v].queryResult.length === 0 ? true : false
                "
                >下载日志</el-link
              >
              <el-link
                type="primary"
                @click="showStepLog(v, allDataObj[v])"
                :disabled="
                  allDataObj[v].queryResult.length === 0 ? true : false
                "
                >查看日志</el-link
              >
            </el-space>
          </template>
        </el-card>
        <el-icon
          v-if="Object.keys(allDataObj).length === index + 1 ? false : true"
          ><Right
        /></el-icon>
      </div>
    </el-space>

    <!-- 点击查看详情，查看环节的详细日志 -->
  </div>
  <el-drawer v-model="drawer" size="80%" class="drawer">
    <template #header>
      <el-segmented v-model="nowStep" :options="hasLogModuleOptions" />
    </template>
    <template #default>
      <el-table
        :data="allDataObj[nowStep].queryResult"
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
        <el-table-column label="日志内容" prop="logLine">
          <template #default="{ row }">
            <span v-html="highlight(row.logLine, matchKey)"> </span>
            <!-- <el-button v-show="showContext == row.lokiTime">查看上下文</el-button>   -->
            <div class="operation_show">
              <el-link type="primary" @click="clickToShowNearLog(row)"
                >查看上下文
              </el-link>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </template>
    <template #footer>
      <div style="flex: auto">
        <!-- <el-button @click="cancelClick">cancel</el-button>
        <el-button type="primary" @click="confirmClick">confirm</el-button> -->
      </div>
    </template>
  </el-drawer>
  <el-backtop :bottom="50">
    <el-icon><Top /></el-icon>
  </el-backtop>
  <nearLogCom
    v-model:isShow="isShowNearLog"
    v-model:highlightKey="matchKey"
    v-model:url="dataSourceUrl"
    ref="childRef"
  />
</template>
<script setup lang="ts">
import {
  reactive,
  ref,
  watch,
  getCurrentInstance,
  onMounted,
  computed,
  onUnmounted,
} from "vue";
// import { Delete, Edit, CirclePlus } from '@element-plus/icons-vue'
const { proxy } = getCurrentInstance();
import { ElMessageBox, ElMessage, ElLoading } from "element-plus";
// 引入上下文组件
import nearLogCom from "@/components/loki/nearLogCom.vue";
// 引入pinia
import useTabsStore from "@/store/tabs";
const tabsStore = useTabsStore();
const loading = ref(true);
// showChild = !showChild
const steps = ref([1, 2, 3, 4, 5]);
import { useRoute, useRouter } from "vue-router";
const route = useRoute();
const router = useRouter();
import type { ComponentSize } from "element-plus";
const isWrap = ref(true);
const size = ref<ComponentSize>("default");
const goToMission = () => {
  router.push({ name: "logFlowMission" });
  // 删除现在的tabs
  console.log(route.fullPath);
  tabsStore.removeTabs(route.fullPath, false);
};
const isShowNearLog = ref(false);
const dataSourceUrl = ref("");
const childRef = ref("");
const clickToShowNearLog = async (config) => {
  isShowNearLog.value = true;
  let res = await proxy.$api.dataSourceGet(dataSourceId.value);
  dataSourceUrl.value = res.data.url;
  childRef.value.showNearLog(dataSourceUrl.value, config);
};
// 获取vuex中的username
// import {useStore} from 'vuex'
// let store = useStore()
// const currenUsername = computed(() => {
//     return store.state.username
//   })
const currenUsername = ref("");
const allDataObj = ref({});
const flowSort = ref([]);
// const logDate = computed(()=>{
//   console.log(route.query.dateValue[0])
//   let sdate = proxy.$commonFunc.timestampToDate(route.query.dateValue[0])
//   let edate = proxy.$commonFunc.timestampToDate(route.query.dateValue[1])
//   console.log(sdate)
//   return [sdate,edate]
// })
const logDate = ref([]);
// const matchKey = computed(()=>{
//   return route.query.matchKey
// })
const matchKey = ref("");
const dataSourceName = ref("");
const flowName = ref("");
const dataSourceId = ref("");
// const missionId = computed(()=>{
//       return route.query.missionId
//     })

const missionId = ref("");
const missionStatus = ref({
  level: "info",
  status: "运行中",
  isLoading: true,
});
// 任务状态常量

// 通过loki接口获取
const requestLokiLog = async (config) => {
  // const loading = ElLoading.service({
  //   lock: true,
  //   text: 'Loading',
  // })
  let sdate = proxy.$commonFunc.timestampToDate(config.dateValue[0]);
  let edate = proxy.$commonFunc.timestampToDate(config.dateValue[1]);
  logDate.value.push(sdate);
  logDate.value.push(edate);
  matchKey.value = config.matchKey;
  currenUsername.value = config.username;
  dataSourceName.value = config.dataSourceName;
  dataSourceId.value = config.dataSourceId;

  flowName.value = config.flowName;
  missionId.value = config.missionId;
  let res = await proxy.$api.getFlowLokiLog(config);
  console.log(res);
  if (!res) {
    missionStatus.value.level = "danger";
    missionStatus.value.status = "异常";
    loading.value = false;
    // return false;
  } else if (res.status == 200) {
    missionStatus.value.level = "success";
    missionStatus.value.status = "成功";
    // loading.value = false;
  } else {
    loading.value = false;
    missionStatus.value.level = "danger";
    missionStatus.value.status = "异常";
    // return false;
  }
  // loading.value = false

  allDataObj.value = res.data.info;
  flowSort.value = res.data.sort;
  proxy.$nextTick(() => {
    // loading.close()
  });
};
//
const iconStyle = computed(() => {
  const marginMap = {
    large: "8px",
    default: "6px",
    small: "4px",
  };
  return {
    marginRight: marginMap[size.value] || marginMap.default,
  };
});
// 获取logModule
const logModuleObj = ref({});
const hasLogModuleOptions = computed(() => {
  let tempObj = [];
  flowSort.value?.forEach((item) => {
    // console.log(item);
    if (
      allDataObj.value[item].status &&
      allDataObj.value[item].queryResult.length >>> 0
    ) {
      var status = false;
    } else {
      var status = true;
    }
    tempObj.push({
      label: logModuleObj.value[item].module_name,
      value: item,
      disabled: status,
    });
  });
  return tempObj;
});
const getLogModuleList = async () => {
  let res = await proxy.$api.getLogModule();
  // console.log(res)
  // logModuleList.value = res.data
  // 把已创建的分组罗列

  res?.data.results.forEach((item) => {
    logModuleObj.value[item.id] = item;
  });
  console.log(logModuleObj.value);
};

// const 下载日志
const downloadStepLog = (param1, param2) => {
  let module_name = logModuleObj.value[param1].module_name;
  let exportArray = [];
  param2.queryResult.forEach((item) => {
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

  proxy.$commonFunc.downloadArray(
    `${module_name}-export-log-${nowTimeStr}`,
    exportArray
  );
};
// 查看详细日志
const showStepLog = (param1, param2) => {
  drawer.value = true;
  nowStep.value = param1;
};
//
const dataExpandInfo = ref([]);
// 表格的展开行
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
const eventSource = ref(null);
const openSse = (params) => {
  // let eventSource = null;    "/api/v1/logFlowMission/get_lokiAnalysis_status/"

  eventSource.value = new EventSource(
    `/api/v1/log/logFlowMission/get_lokiAnalysis_status/${params}/`
  );
  eventSource.value.onmessage = (event) => {
    console.log(JSON.parse(event.data).is_finish);
    if (JSON.parse(event.data).is_finish) {
      closeSse();
      fromDatabase();
    }
    // result.value.push(event.data);
  };
};
const closeSse = () => {
  console.log("SSE 关闭");
  eventSource.value?.close();
};
// 通过历史数据获取结果
const fromDatabase = async () => {
  // 截取路由的最后一个位置,拿到missionId
  let _tempArr = route.path.split("/").filter((item) => {
    return item != "";
  });
  let id = _tempArr[_tempArr.length - 1];
  // console.log(route.query.mission_id);
  let res = await proxy.$api.getLogFlowMission(id);
  console.log(res);
  let config = res.data.mission_query;
  // missionStatus.value = config.status
  // missionStatus.value.level =
  if (res.data.status == "Success") {
    missionStatus.value.level = "success";
    missionStatus.value.status = "成功";
    missionStatus.value.isLoading = false;
    // loading.value = false;
  } else if (res.data.status == "Failed") {
    missionStatus.value.level = "danger";
    missionStatus.value.status = "失败";
    missionStatus.value.isLoading = false;
  } else if (res.data.status == "Pending") {
    missionStatus.value.level = "info";
    missionStatus.value.status = "运行中";
    missionStatus.value.isLoading = true;
    // 是Pending,则开启task的sse请求
    openSse(res.data.task_id);
  } else {
    missionStatus.value.level = "info";
    missionStatus.value.status = "未知";
    missionStatus.value.isLoading = false;
  }
  let sdate = proxy.$commonFunc.timestampToDate(config.dateValue[0]);
  let edate = proxy.$commonFunc.timestampToDate(config.dateValue[1]);
  logDate.value.push(sdate);
  logDate.value.push(edate);
  matchKey.value = res.data.search_key;
  currenUsername.value = res.data.username;
  missionId.value = res.data.mission_id;
  dataSourceName.value = res.data.dataSource_name;
  flowName.value = res.data.flow_name;
  dataSourceId.value = res.data.dataSource_id;
  // console.log((new Function('return' + res.data.results.replace(/True/g, "true").replace("False", "false")))())
  // console.log(res.data.results.replace(/True/g, "true").replace(/False/g, "false"))
  // allDataObj.value = (new Function('return' + res.data.results.replace(/True/g, "true").replace(/False/g, "false")))()
  // allDataObj.value = JSON.parse(res.data.results);
  allDataObj.value = res.data.results.info;
  flowSort.value = res.data.results.sort;
  // allDataObj.value = JSON.parse('\''+res.data.results.replace(/True/g, "true").replace(/False/g, "false")+'\'')
  console.log(allDataObj.value);
};
onMounted(async () => {
  getLogModuleList();
  // if (Object.keys(route.query).length != 0) {
  // if (route.query.missionId) {
  //   // console.log(route.query)
  //   //
  //   await requestLokiLog(route.query);
  // } else {
  //   fromDatabase();
  // }
  fromDatabase();
});
onUnmounted(() => {
  closeSse();
});
//
const resultTip = (params) => {
  if (params.status) {
    if (params.queryInfo.errorCount == 0 && params.queryResult.length >> 0) {
      return "日志正常";
    } else if (
      params.queryInfo.errorCount >> 0 &&
      params.queryResult.length >> 0
    ) {
      return "存在报错";
    } else {
      return "无请求信息";
    }
  } else {
    return "请求错误";
  }
};
// 根据返回值判断环节的状态
const reqStatus = (params) => {
  if (params.status) {
    if (params.queryInfo.errorCount == 0 && params.queryResult.length >> 0) {
      return "success";
    } else if (
      params.queryInfo.errorCount >> 0 &&
      params.queryResult.length >> 0
    ) {
      return "warning";
    } else {
      return "error";
    }
  } else {
    return "error";
  }
};

// 弹出框js
const drawer = ref(false);
const nowStep = ref("");
// 关闭弹窗
const handleClose = (done: () => void) => {
  ElMessageBox.confirm("是否关闭?")
    .then(() => {
      // resetForm();
      // resetForm();

      done();
    })
    .catch(() => {
      // catch error
    });
};
const highlight = (content, keyword) => {
  if (!keyword) {
    return content;
  } else {
    const regex = new RegExp(keyword, "gi");
    // return content.replace(regex, match => `${match}`.replace(gi, m => `<span class="${highlightClass}">${m}</span>`));
    const res = content.replace(
      regex,
      `<span style="background-color: #FFFF00;">$&</span>`
    );
    return res;
  }
};
const logLevelOption = [
  { text: "DEBUG", value: "DEBUG" },
  { text: "INFO", value: "INFO" },
  { text: "WARN", value: "WARN" },
  { text: "ERROR", value: "ERROR" },
  { text: "FATAL", value: "FATAL" },
  { text: "UNKNOWN", value: "UNKNOWN" },
];

import type { TableColumnCtx, TableInstance } from "element-plus";
import { RefSymbol } from "@vue/reactivity";
import { isUndefined } from "lodash-es";
interface User {
  lokiTime: string;
  logTime: string;
  logLine: string;
  level: string;
}
const filterTag = (value: string, row: User) => {
  return row.level === value;
};
</script>
<style scoped lang="less">
// 可以看下less或者scss，这个写样式方便点
// :deep(.el-step__main) {
//   display: flex;
//   flex-direction: column;
// }

// :deep(.el-step__description) {
//   flex: 1;
// }
// 可以合并写

:deep(.el-step__main) {
  display: flex;
  flex-direction: column;

  .el-step__description {
    flex: 1;
  }
}
:deep(.el-result) {
  --el-result-icon-font-size: 42px;
}
.result-card {
  width: 300px;
  // height: 100%;
  height: 310px;
  display: flex;
  flex-direction: column;
}

.result-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  justify-content: center;
  align-content: center;
  align-items: center;
}
:deep(.el-card__body) {
  padding: 20px 20px 20px 0;
}

.result-card :deep(.el-card__footer) {
  padding: calc(var(--el-card-padding) - 10px) var(--el-card-padding);
}
.result-card :deep(.el-card__header) {
  display: flex;
  justify-content: center;
}
:deep(.el-result__title p) {
  white-space: normal;
  max-width: 100px;
}
.operation_show {
  display: none;
}
.el-table__body tr:hover > td .operation_show {
  display: block;
}
</style>