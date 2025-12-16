// src/composables/useECharts.js
import { onUnmounted, watch } from 'vue';
import * as echarts from 'echarts';

/**
 * 安全初始化 ECharts 实例
 * @param {Ref<HTMLElement | null>} domRef - 图表容器的 ref
 * @param {Object | Ref<Object>} option - ECharts 配置项（支持响应式）
 * @param {number} retryDelay - 尺寸为 0 时的重试间隔（ms）
 * @param {number} maxRetries - 最大重试次数
 * @returns {{ chart: Ref<echarts.ECharts | null> }}
 */
export function useECharts(domRef, option, retryDelay = 100, maxRetries = 10) {
  let chart = null;
  let observer = null;
  let retryCount = 0;

  const initChart = () => {
    if (!domRef.value) return;

    const dom = domRef.value;
    if (dom.offsetWidth <= 0 || dom.offsetHeight <= 0) {
      if (retryCount < maxRetries) {
        retryCount++;
        setTimeout(initChart, retryDelay);
      } else {
        console.warn('ECharts 容器尺寸始终为 0，放弃初始化', dom);
      }
      return;
    }

    // 如果已有实例，先销毁
    if (chart) {
      chart.dispose();
    }

    chart = echarts.init(dom);

    // 处理 option 是响应式 ref 的情况
    const currentOption = typeof option === 'function' ? option() : option;
    chart.setOption(currentOption, true);

    // 监听 resize
    observer?.disconnect();
    observer = new ResizeObserver(() => {
      if (dom.offsetWidth > 0 && dom.offsetHeight > 0) {
        chart?.resize();
      }
    });
    observer.observe(dom);
  };

  // 初始尝试初始化
  initChart();

  // 如果 option 是 ref 或 reactive，监听变化
  if (option && typeof option === 'object' && 'value' in option) {
    watch(
      option,
      (newOpt) => {
        if (chart && newOpt) {
          chart.setOption(newOpt, true);
        }
      },
      { deep: true }
    );
  }

  // 清理
  onUnmounted(() => {
    if (chart) {
      chart.dispose();
      chart = null;
    }
    if (observer) {
      observer.disconnect();
      observer = null;
    }
  });

  return {
    chart: chart, // 注意：这里不是 ref，是普通变量（但已足够）
    // 如果你需要在外部调用 resize/setOption，可暴露方法
    getChartInstance: () => chart,
    updateOption: (newOption) => {
      if (chart) {
        chart.setOption(newOption, true);
      }
    },
  };
}