// src/composables/echarts/useEChartsBase.ts
import { onUnmounted, watch, Ref, ref } from 'vue';
import * as echarts from 'echarts';
import type { ECharts, EChartsOption } from 'echarts';
import { MONITOR_THEME } from './theme';

export interface UseEChartsBaseReturn {
  chart: Ref<ECharts | null>;
  setOption: (option: EChartsOption, notMerge?: boolean) => void;
  resize: () => void;
}

export function useEChartsBase(
  domRef: Ref<HTMLElement | null>,
  initialOption: EChartsOption = {},
  retryDelay = 1000,
  maxRetries = 10
): UseEChartsBaseReturn {
  const chartInstance = ref<ECharts | null>(null);
  let resizeObserver: ResizeObserver | null = null;



  const attemptInit = (dom: HTMLElement, retryCount: number) => {
    // 先清理旧实例
    cleanup();
    console.log('[ECharts] DOM clientRect:', {
      offsetWidth: dom.offsetWidth,
      offsetHeight: dom.offsetHeight,
      parent: dom.parentElement?.offsetWidth,
      grandparent: dom.parentElement?.parentElement?.offsetWidth
    });
    if (dom.offsetWidth <= 0 || dom.offsetHeight <= 0) {
      if (retryCount < maxRetries) {
        console.log(`[ECharts] DOM has no size, retrying... (${retryCount + 1})`);
        setTimeout(() => attemptInit(dom, retryCount + 1), retryDelay);
      } else {
        console.warn('[ECharts] Failed to initialize after retries');
      }
      return;
    }

    // ✅ 尺寸 OK，初始化
    chartInstance.value = echarts.init(dom, MONITOR_THEME);
    chartInstance.value.setOption(initialOption, true);

    // 绑定 ResizeObserver
    resizeObserver = new ResizeObserver(() => {
      if (dom.offsetWidth > 0 && dom.offsetHeight > 0) {
        chartInstance.value?.resize();
      }
    });
    resizeObserver.observe(dom);

    console.log('[ECharts] Initialized successfully');
  };

  const cleanup = () => {
    if (chartInstance.value) {
      chartInstance.value.dispose();
      chartInstance.value = null;
    }
    if (resizeObserver) {
      resizeObserver.disconnect();
      resizeObserver = null;
    }
  };

  const setOption = (option: EChartsOption, notMerge = true) => {
    if (chartInstance.value) {
      chartInstance.value.setOption(option, notMerge);
    }
  };

  const resize = () => {
    chartInstance.value?.resize();
  };

  onUnmounted(cleanup);
  // 🔄 核心：监听 domRef 变化
  watch(
    domRef,
    (newDom) => {
      if (!newDom) {
        // DOM 被销毁，清理实例
        cleanup();
        return;
      }

      // 有 DOM 了，尝试初始化（带尺寸重试）
      attemptInit(newDom, 0);
    },
    { immediate: true }
  );
  return {
    chart: chartInstance,
    setOption,
    resize,
  };
}