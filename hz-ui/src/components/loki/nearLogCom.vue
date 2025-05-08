<template>
  <el-dialog
    v-model="isShow"
    title="日志上下文"
    width="95%"
    top="9vh"
    @close="closeDialog"
  >
    <template #header="{ close, titleId, titleClass }">
      <div class="my-header">
        <div
          :id="titleId"
          :class="titleClass"
          style="display: flex; justify-content: space-between"
        >
          <span>日志上下文</span>
          <el-button
            type="primary"
            @click="downloadResLog(nearLogData)"
            style="margin-right: 20px"
          >
            下载日志
          </el-button>
        </div>
      </div>
    </template>
    <el-table
      :data="nearLogData"
      ref="nearLogRef"
      style="width: 100%"
      height="600"
      :row-class-name="highlightRow"
    >
      <el-table-column type="index" width="50" />

      <el-table-column label="日志时间" prop="logTime" width="200px" />
      <el-table-column label="日志等级" prop="level" width="100px">
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
        <template #default="{ row }">
          <span v-html="highlight(row.logLine, props.highlightKey)"> </span>
        </template>
      </el-table-column>
    </el-table>
    <template #footer>
      <div class="dialog-footer">
        <el-button type="primary" @click="changeBackwardLimit"
          >往前翻</el-button
        >
        <el-button type="primary" @click="changeForwardLimit">往后翻</el-button>
        <el-button type="primary" @click="toNowRow">跳转到分析行</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import {
  ref,
  reactive,
  onMounted,
  watch,
  getCurrentInstance,
  nextTick,
} from "vue";
import { Delete, Filter, CirclePlus } from "@element-plus/icons-vue";
const { proxy } = getCurrentInstance();
import { ElMessageBox, ElMessage } from "element-plus";
// 匹配值高亮
const highlight = (content, keyword) => {
  if (!keyword) {
    return content;
  } else {
    const regex = new RegExp(keyword, "gi");
    // return content.replace(regex, match => `${match}`.replace(gi, m => `<span class="${highlightClass}">${m}</span>`));
    const res = content.replace(
      regex,
      `<span style="background-color: #ff9b2d;">$&</span>`
    );
    return res;
  }
};
// 显示查看上下文的按钮
const isShow = defineModel("isShow");
const props = defineProps(["url", "highlightKey"]);
const backwardLimit = ref(10);
const forwardLimit = ref(10);
// 往前看
const changeBackwardLimit = async () => {
  backwardLimit.value += 10;
  await getNearLog(nowRow.value);
  // 跳转到第一行
  tableScrollToRow(proxy.$refs.nearLogRef, 0);
};
// 往后看
const changeForwardLimit = async () => {
  forwardLimit.value += 10;
  await getNearLog(nowRow.value);
  // 跳转到最后一行
  tableScrollToRow(proxy.$refs.nearLogRef, nearLogData.value.length);
};
const closeDialog = () => {
  backwardLimit.value = 10;
  forwardLimit.value = 10;
  nowRowIndex.value = 0;
};
const nearLogData = ref([]);
const nowRow = ref("");
// 上下文日志请求
const getNearLog = async (row) => {
  let beforeRes = await proxy.$api.lokiNearQuery({
    url: props.url,
    targetLog: row,
    limit: backwardLimit.value,
    direction: "backward",
  });
  let beforeLogList = beforeRes.data.queryResult;
  // console.log(beforeLogList);
  let afterRes = await proxy.$api.lokiNearQuery({
    url: props.url,
    targetLog: row,
    limit: forwardLimit.value,
    direction: "forward",
  });
  let afterLogList = afterRes.data.queryResult;
  // console.log(afterLogList);
  nearLogData.value = [...beforeLogList, ...afterLogList];
};
const showNearLog = async (row) => {
  nowRow.value = row;
  isShow.value = true;
  // let res = await
  // console.log(afterLogList)
  // console.log(nearLogData.value)
  await getNearLog(row);
  nextTick(() => {
    tableScrollToRow(proxy.$refs.nearLogRef, nowRowIndex.value);
  });
};
// 定位到表格滚动条的位置
function tableScrollToRow(tableElement, rowindex, isPrecise = true) {
  const theTableRows = tableElement.$el.querySelectorAll(
    ".el-table__body tbody .el-table__row"
  );
  let scrollTop = 0;
  for (let i = 0; i < theTableRows.length; i++) {
    if (i === rowindex) {
      break;
    }
    scrollTop += theTableRows[i].offsetHeight;
    if (!isPrecise) {
      scrollTop *= rowindex - 2;
      break;
    }
  }
  tableElement.scrollTo(0, scrollTop);
}
// const nowRowIndex = computed(()=>{
//   console.log("计算数学")
//   console.log(nearLogData.value)
//   console.log(nowRow.value)
//    return nearLogData.value.indexOf(nowRow.value)+1
// })
const nowRowIndex = ref(0);
watch(
  () => nearLogData.value,
  (n) => {
    // console.log(n)
    nowRowIndex.value = n.findIndex(
      (item) => item.lokiTime === nowRow.value.lokiTime
    );
    // console.log("当前行", nowRowIndex.value);
  }
);
const toNowRow = () => {
  tableScrollToRow(proxy.$refs.nearLogRef, nowRowIndex.value);
};
//   const nearLogRef = ref(null)
//   onMounted(() => {
//   // 方法一：尝试使用 Element Plus 提供的方法（如果存在）
//   if (nearLogRef.value && nearLogRef.value.scrollBarRef) {
//     console.log('xxxxx')
//     nearLogRef.value.scrollBarRef.setScrollTop(30);
//   }
// })
// 高亮显示上下文界面的匹配行
const highlightRow = ({ row }) => {
  if (row.lokiTime == nowRow.value["lokiTime"]) {
    return "highlight-class";
  }
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
defineExpose({
  showNearLog,
});
</script>

<style scoped>
.highlight {
  background-color: yellow;
  /* 高亮颜色 */
}
:deep(.highlight-class) {
  background-color: yellow;
  /* 高亮行的背景色 */
}
</style>