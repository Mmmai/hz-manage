<template>
  <!-- 展示查询条件 -->
  <el-divider>
    <!-- <el-icon><star-filled /></el-icon> -->
    分析结果
  </el-divider>
  <!-- direction="vertical" -->
  <el-steps style="max-width: 100%" :active="5" :space="800" align-center >
    <!-- <el-step title="Step 11112" description="Some description" />
      <el-step title="Step 2" description="Some description" /> -->
    <el-step v-for="v, k, index in allDataObj" :key="index" :title="logModuleObj[k].module_name"
      :status="v.queryInfo.errorCount >>> 0 ? 'error' : v.queryResult.length === 0 ? 'error' : 'success'">
      <template #description>
        <el-card class="result-card">
          <!-- <template #header>
                <span>日志下载</span>
              </template> -->
          <!-- {{ logModuleObj.k.module_name }}
              日志数量:{{ v.queryResult.length }},错误日志数:{{ v.queryInfo.errorCount }} -->
          <!-- <div style="width: 500px;height: 100px;"> -->
            
          <el-space wrap :size="50">
            <el-result
              icon="success"
              title="Success Tip"
              >

            </el-result>
            <el-space direction="vertical">
            <el-statistic :value="v.queryResult.length">
              <template #title>
                <div style="display: inline-flex; align-items: center">
                  匹配数
                  <el-tooltip effect="dark" content="分析ID返回的日志条数"
                    placement="top">
                    <el-icon style="margin-left: 4px" :size="12">
                      <Warning />
                    </el-icon>
                  </el-tooltip>
                </div>
              </template>
            </el-statistic>
            <el-statistic :value="v.queryInfo.errorCount">
              <template #title>
                <div style="display: inline-flex; align-items: center">
                  错误数
                  <el-tooltip effect="dark" content="匹配到的日志中,日志等级为ERROR及以上的数量" placement="top">
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
              <el-link type="primary" @click="downloadStepLog(v)">下载日志</el-link>
              <el-link type="primary" @click="showStepLog(v)">查看日志</el-link>
            </el-space>
          </template>
        </el-card>
      </template>
    </el-step>
  </el-steps>
</template>
<script setup lang="ts">
import { reactive, ref, watch, getCurrentInstance, onMounted } from 'vue'
import { Delete, Edit, CirclePlus } from '@element-plus/icons-vue'
const { proxy } = getCurrentInstance();
import { ElMessageBox, ElMessage, ElLoading } from 'element-plus'
const steps = ref([1, 2, 3, 4, 5])
import { useRoute } from 'vue-router'
const route = useRoute()
console.log(route.path)
console.log(route.query)
console.log(route.query.test)
const allDataObj = ref({})

const requestLokiLog = async (config) => {
  const loading = ElLoading.service({
    lock: true,
    text: 'Loading',
  })
  let res = await proxy.$api.getFlowLokiLog(config)
  console.log(res.data)
  allDataObj.value = res.data
  proxy.$nextTick(() => {
    loading.close()
  })
}
// 获取logModule
const logModuleObj = ref({})
const getLogModuleList = async () => {

  let res = await proxy.$api.getLogModule()
  // console.log(res)
  // logModuleList.value = res.data
  // 把已创建的分组罗列

  res.data.forEach(item => {
    logModuleObj.value[item.id] = item
  })
  console.log(logModuleObj.value)
}
onMounted(async () => {
  getLogModuleList()
  if (route.query) {
    // console.log('执行任务')
    // console.log(route.query)
    // 
    await requestLokiLog(route.query)
  } else {
    console.log('查看历史记录')
  }
})
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
  height: 300px;
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


</style>