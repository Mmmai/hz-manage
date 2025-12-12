<template>
  <div class="monitor-chart-container">
    <el-row :gutter="20" class="chart-row">
      <el-col :span="4">
        <div class="chart-card">
          <div ref="cpuUsageChart" class="chart-gauge"></div>
        </div>
      </el-col>

      <el-col :span="4">
        <div class="chart-card">
          <div ref="memoryChart" class="chart-gauge"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-card">
          <div ref="cpuChart" class="chart"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <div class="chart-card">
          <div ref="diskChart" class="chart"></div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, defineProps, nextTick } from "vue";
import * as echarts from "echarts";
import api from "@/api/index";

const props = defineProps({
  ip: {
    type: String,
    required: true,
  },
});

// refs
const cpuChart = ref(null);
const memoryChart = ref(null);
const diskChart = ref(null);
const cpuUsageChart = ref(null);

// 图表实例
let cpuChartInstance = null;
let cpuUsageChartInstance = null;
let memoryChartInstance = null;
let diskChartInstance = null;

// ResizeObserver 实例
let cpuObserver = null;
let memoryObserver = null;
let diskObserver = null;
let cpuUsageObserver = null;

// 定时器
let refreshTimer = null;

// 初始化单个图表
const initChart = (domRef, option) => {
  if (!domRef.value) return null;

  const chart = echarts.init(domRef.value);
  chart.setOption(option);

  // 创建 ResizeObserver
  const observer = new ResizeObserver(() => {
    if (
      domRef.value &&
      domRef.value.offsetWidth > 0 &&
      domRef.value.offsetHeight > 0
    ) {
      chart.resize();
    }
  });
  observer.observe(domRef.value);

  return { chart, observer };
};

// 各图表配置生成函数（添加数据验证）
const createCpuOption = (data) => {
  // ✅ 验证数据结构
  const validData = data || { time_labels: [], legend: [], series: [] };

  return {
    title: { text: "CPU负载", left: "center" },
    tooltip: { trigger: "axis" },
    legend: {
      data: Array.isArray(validData.legend) ? validData.legend : [],
      top: "5%",
    },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: Array.isArray(validData.time_labels) ? validData.time_labels : [],
    },
    yAxis: { type: "value", name: "负载" },
    series: Array.isArray(validData.series) ? validData.series : [],
  };
};

const createCpuUsageOption = (value) => ({
  title: {
    text: "CPU使用率",
    left: "center",
    top: "8%",
  },
  series: [
    {
      center: ["50%", "65%"],
      type: "gauge",
      axisLine: {
        lineStyle: {
          width: 30,
          color: [
            [0.3, "#67e0e3"],
            [0.7, "#37a2da"],
            [1, "#fd666d"],
          ],
        },
      },
      pointer: { itemStyle: { color: "auto" } },
      axisTick: {
        distance: -30,
        length: 8,
        lineStyle: { color: "#fff", width: 2 },
      },
      splitLine: {
        distance: -30,
        length: 30,
        lineStyle: { color: "#fff", width: 4 },
      },
      axisLabel: { color: "inherit", distance: -20, fontSize: 10 },
      detail: {
        valueAnimation: true,
        formatter: "{value} %",
        color: "inherit",
      },
      data: [{ value: value || 0, name: "使用率" }],
    },
  ],
});

const createMemoryOption = (value) => ({
  title: {
    text: "内存使用率",
    left: "center",
    top: "8%",
  },
  series: [
    {
      center: ["50%", "65%"],
      type: "gauge",
      axisLine: {
        lineStyle: {
          width: 30,
          color: [
            [0.3, "#67e0e3"],
            [0.7, "#37a2da"],
            [1, "#fd666d"],
          ],
        },
      },
      pointer: { itemStyle: { color: "auto" } },
      axisTick: {
        distance: -30,
        length: 8,
        lineStyle: { color: "#fff", width: 2 },
      },
      splitLine: {
        distance: -30,
        length: 30,
        lineStyle: { color: "#fff", width: 4 },
      },
      axisLabel: { color: "inherit", distance: -20, fontSize: 10 },
      detail: {
        valueAnimation: true,
        formatter: "{value} %",
        color: "inherit",
      },
      data: [{ value: value || 0, name: "使用率" }],
    },
  ],
});

const createDiskOption = (data) => {
  // ✅ 验证磁盘数据结构
  const validData = data || { yAxisData: [], seriesData: [] };

  return {
    title: { text: "文件系统空间使用率", left: "center" },
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    xAxis: {
      type: "value",
      name: "使用率 (%)",
      min: 0,
      max: 100,
      axisLabel: { formatter: "{value} %" },
    },
    yAxis: {
      type: "category",
      data: Array.isArray(validData.yAxisData) ? validData.yAxisData : [],
    },
    series: [
      {
        type: "bar",
        data: Array.isArray(validData.seriesData) ? validData.seriesData : [],
        label: {
          show: true,
          position: "insideRight",
          color: "#fff",
          fontWeight: "bold",
        },
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: "#5470c6" },
            { offset: 1, color: "#91cc75" },
          ]),
        },
      },
    ],
    grid: { left: "10%", right: "5%", top: "20%", bottom: "10%" },
  };
};

// 初始化所有图表
const initCharts = (monitorData) => {
  console.log("Initializing charts with data:", monitorData);

  // 销毁已存在的图表实例
  destroyCharts();
  console.log("Charts destroyed.", Object.values(monitorData.memoryUsage));
  // ✅ 确保只有在有数据时才初始化图表
  if (monitorData) {
    const cpu = initChart(cpuChart, createCpuOption(monitorData.cpuLoad));
    const memory = initChart(
      memoryChart,
      createMemoryOption(Object.values(monitorData.memoryUsage)[0].latest_value)
    );
    const disk = initChart(diskChart, createDiskOption(monitorData.diskUsage));
    const cpuUsage = initChart(
      cpuUsageChart,
      createCpuUsageOption(monitorData.cpuUsage)
    );

    if (cpu) {
      cpuChartInstance = cpu.chart;
      cpuObserver = cpu.observer;
    }
    if (cpuUsage) {
      cpuUsageChartInstance = cpuUsage.chart;
      cpuUsageObserver = cpuUsage.observer;
    }
    if (memory) {
      memoryChartInstance = memory.chart;
      memoryObserver = memory.observer;
    }
    if (disk) {
      diskChartInstance = disk.chart;
      diskObserver = disk.observer;
    }
  } else {
    // ✅ 没有数据时初始化空图表
    const cpu = initChart(cpuChart, createCpuOption(null));
    const memory = initChart(memoryChart, createMemoryOption(0));
    const disk = initChart(diskChart, createDiskOption(null));
    const cpuUsage = initChart(cpuUsageChart, createCpuUsageOption(0));

    if (cpu) cpuChartInstance = cpu.chart;
    if (cpuUsage) cpuUsageChartInstance = cpuUsage.chart;
    if (memory) memoryChartInstance = memory.chart;
    if (disk) diskChartInstance = disk.chart;
  }
};

// 更新数据（添加验证）
const updateChartData = (monitorData) => {
  if (!monitorData) return;

  if (cpuChartInstance && monitorData.cpuLoad) {
    cpuChartInstance.setOption(
      {
        xAxis: { data: monitorData.cpuLoad.time_labels || [] },
        legend: { data: monitorData.cpuLoad.legend || [] },
        series: monitorData.cpuLoad.series || [],
      },
      true
    ); // ✅ 使用 notMerge=true 确保完全替换
  }

  if (cpuUsageChartInstance && monitorData.cpuUsage !== undefined) {
    cpuUsageChartInstance.setOption(
      {
        series: [{ data: [{ value: monitorData.cpuUsage, name: "使用率" }] }],
      },
      true
    );
  }

  if (memoryChartInstance && monitorData.memoryUsage !== undefined) {
    memoryChartInstance.setOption(
      {
        series: [
          { data: [{ value: monitorData.memoryUsage, name: "使用率" }] },
        ],
      },
      true
    );
  }

  if (diskChartInstance && monitorData.diskUsage) {
    diskChartInstance.setOption(
      {
        yAxis: { data: monitorData.diskUsage.yAxisData || [] },
        series: [{ data: monitorData.diskUsage.seriesData || [] }],
      },
      true
    );
  }
};

// 加载监控数据
const loadMonitorData = async () => {
  try {
    console.log("Loading monitor data for IP:", props.ip);

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
    // ✅ 处理 Promise.allSettled 结果，避免单个请求失败影响整体
    const monitorData = {
      cpuLoad: cpuLoadRes.status === "fulfilled" ? cpuLoadRes.value.data : null,
      cpuUsage:
        cpuUsageRes.status === "fulfilled" ? cpuUsageRes.value.data?.value : 0,
      memoryUsage:
        memoryUsageRes.status === "fulfilled"
          ? memoryUsageRes.value.data?.value
          : 0,
      diskUsage:
        diskUsageRes.status === "fulfilled" ? diskUsageRes.value.data : null,
    };

    console.log("Processed monitor data:", monitorData);
    nextTick(() => {
      if (!cpuChartInstance) {
        initCharts(monitorData);
      } else {
        updateChartData(monitorData);
      }
    });

    return monitorData;
  } catch (error) {
    console.error("加载监控数据失败:", error);
    // 即使出错也确保图表初始化
    if (!cpuChartInstance) {
      initCharts(null);
    }
  }
};

// 定时刷新数据
const startAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }

  refreshTimer = setInterval(() => {
    loadMonitorData();
  }, 30000);
};

// 清理资源
const destroyCharts = () => {
  cpuChartInstance?.dispose();
  memoryChartInstance?.dispose();
  diskChartInstance?.dispose();
  cpuUsageChartInstance?.dispose();

  cpuObserver?.disconnect();
  cpuUsageObserver?.disconnect();
  memoryObserver?.disconnect();
  diskObserver?.disconnect();

  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }
};

// 生命周期
onMounted(async () => {
  await loadMonitorData();
  // startAutoRefresh(); // 如果需要自动刷新，取消注释
});

onUnmounted(() => {
  destroyCharts();
});
</script>

<style scoped>
.monitor-chart-container {
  padding: 20px;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.chart {
  width: 100%;
  height: 300px;
}

.chart-gauge {
  width: 100%;
  height: 300px;
}
</style>