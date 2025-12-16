// src/composables/echarts/useGaugeChart.ts
import { ref, watch, Ref } from 'vue';
import type { EChartsOption } from 'echarts';
import { useEChartsBase } from './useEChartsBase';
import { GAUGE_COLOR_STAGES } from './theme';
import type { GaugeChartData } from './types';

export function useGaugeChart(
  domRef: Ref<HTMLElement | null>,
  config: Ref<GaugeChartData>
) {
  const createOption = (value: number, title: string): EChartsOption => ({
    title: {
      text: title,
      left: 'center',
      top: '8%',
      textStyle: { fontSize: 14 },
    },
    series: [
      {
        type: 'gauge',
        center: ['50%', '65%'],
        startAngle: 180,
        endAngle: 0,
        min: 0,
        max: 100,
        progress: { show: true, width: 18 },
        axisLine: {
          lineStyle: {
            width: 30,
            color: GAUGE_COLOR_STAGES,
          },
        },
        pointer: {
          // icon: 'path://M12.8,0C12.8,0,12.8,0,12.8,0L12.8,14.7L0,14.7L6.4,27.4L12.8,40.1L19.2,27.4L25.6,14.7L12.8,14.7L12.8,0Z',
          // icon: 'path://M12.8,40.1C12.8,40.1,12.8,40.1,12.8,40.1L12.8,25.4L0,25.4L6.4,12.7L12.8,0L19.2,12.7L25.6,25.4L12.8,25.4L12.8,40.1Z',
          // width: 10,
          itemStyle: {
            color: 'auto'
          }
        },
        axisTick: { distance: -30, length: 8, lineStyle: { color: '#fff', width: 2 } },
        splitLine: { distance: -30, length: 30, lineStyle: { color: '#fff', width: 4 } },
        axisLabel: { color: 'inherit', distance: -20, fontSize: 10 },
        detail: {
          valueAnimation: true,
          formatter: '{value} %',
          offsetCenter: [0, '60%'],
          fontSize: 20,
        },
        data: [{ value }],
      },
    ],
  });

  const optionRef = ref<EChartsOption>(
    createOption(config.value.value, config.value.title || '')
  );

  const { setOption, resize } = useEChartsBase(domRef, optionRef.value);

  watch(
    config,
    (newConfig) => {
      // ✅ 防御：确保 newConfig 是有效对象
      console.log(newConfig)
      if (!newConfig || typeof newConfig !== 'object') return;

      const value = typeof newConfig.value === 'number' ? newConfig.value : 0;
      const title = typeof newConfig.title === 'string' ? newConfig.title : '';

      const opt = createOption(value, title);
      setOption(opt);
    },
    { deep: true, immediate: true }
  );

  return { setOption, resize };
}