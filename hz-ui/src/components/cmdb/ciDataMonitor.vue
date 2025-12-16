<template>
  <div class="monitor-chart-container">
    <el-row :gutter="20" class="chart-row" justify="space-between">
      <el-col :span="4">
        <div class="chart-card">
          <div ref="cpuUsageChartRef" class="chart-gauge"></div>
        </div>
      </el-col>

      <el-col :span="4">
        <div class="chart-card">
          <div ref="memoryChartRef" class="chart-gauge"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-card">
          <div ref="cpuChartRef" class="chart"></div>
        </div>
      </el-col>
    </el-row>

    <!-- <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <div class="chart-card">
          <div ref="diskChartRef" class="chart"></div>
        </div>
      </el-col>
    </el-row> -->
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, Ref, nextTick } from "vue";
import { useLineChart } from "@/composables/echarts/useLineChart";
import { useGaugeChart } from "@/composables/echarts/useGaugeChart";
import { useBarChart } from "@/composables/echarts/useBarChart";
import type {
  LineChartData,
  GaugeChartData,
  BarChartData,
} from "@/composables/echarts/types";
import api from "@/api/index";
const props = defineProps<{ ip: string }>();

// 图表容器 refs
const cpuChartRef = ref<HTMLElement | null>(null);
const cpuUsageChartRef = ref<HTMLElement | null>(null);
const memoryChartRef = ref<HTMLElement | null>(null);
const diskChartRef = ref<HTMLElement | null>(null);

// 响应式数据
const cpuData = ref<LineChartData | null>(null);
const cpuUsageData = ref<GaugeChartData>({ value: 0, title: "CPU使用率" });
const memoryData = ref<GaugeChartData>({ value: 0, title: "内存使用率" });
const diskData = ref<BarChartData | null>(null);

// 初始化图表（自动监听数据变化）
useLineChart(cpuChartRef, cpuData);
useGaugeChart(cpuUsageChartRef, cpuUsageData);
useGaugeChart(memoryChartRef, memoryData);
useBarChart(diskChartRef, diskData);

// 加载数据并更新 option
const loadMonitorData = async () => {
  const [cpuLoadRes, cpuUsageRes, memoryUsageRes, diskUsageRes] =
    await Promise.allSettled([
      api.getZabbixHistory({ ip: props.ip, keys: "system.cpu.load" }),
      api.getZabbixHistory({
        ip: props.ip,
        keys: "system.cpu.util",
        chart_type: "gauge",
      }),
      api.getZabbixHistory({
        ip: props.ip,
        keys: "vm.memory.size\\[pavailable\\]",
        chart_type: "gauge",
      }),
      api.getZabbixHistory({ ip: props.ip, keys: "vfs.fs.size" }),
    ]);
  cpuData.value =
    cpuLoadRes.status === "fulfilled" ? cpuLoadRes.value.data : null;
  cpuUsageData.value =
    cpuUsageRes.status === "fulfilled"
      ? { value: 11, title: "CPU使用率" }
      : { value: 0, title: "CPU使用率" };
  memoryData.value =
    memoryUsageRes.status === "fulfilled"
      ? { value: 22, title: "内存使用率" }
      : { value: 0, title: "内存使用率" };
  diskData.value =
    diskUsageRes.status === "fulfilled" ? diskUsageRes.value.data : null;
  console.log(diskData.value);
};

// 自动刷新（可选）
let refreshTimer = null;
const startAutoRefresh = () => {
  clearInterval(refreshTimer);
  refreshTimer = setInterval(loadMonitorData, 30000);
};

onMounted(async () => {
  await nextTick(); // 确保 DOM 渲染完成
  loadMonitorData();
});

// 清理定时器
onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer);
});
</script>

<style scoped>
/* 保持不变，但建议加 min-height */
.monitor-chart-container {
  padding: 20px;
}
.chart-row {
  margin-bottom: 20px;
}
/* 确保图表容器无论如何都有尺寸 */
.chart,
.chart-gauge {
  width: 100%;
  height: 300px;
  min-width: 180px; /* 仪表盘至少需要一点宽度 */
  min-height: 300px;
  box-sizing: border-box; /* 防止 padding 影响尺寸 */
}

/* 确保卡片容器不塌陷 */
.chart-card {
  width: 100%;
  min-width: 0; /* 关键！允许 flex/grid 子项 shrink */
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  display: flex;
  flex-direction: column;
}
</style>