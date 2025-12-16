// src/composables/echarts/useLineChart.ts
import { ref, watch, Ref } from 'vue';
import type { EChartsOption } from 'echarts';
import { useEChartsBase } from './useEChartsBase';
import { DEFAULT_TOOLTIP, DEFAULT_GRID } from './theme';
import type { LineChartData } from './types';

export function useLineChart(
  domRef: Ref<HTMLElement | null>,
  data?: Ref<LineChartData | null>
) {
  const defaultOption: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      },
    },
    legend: { top: '5%' },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: [],
    },
    yAxis: { type: 'value', name: '负载' },
    series: [],
    grid: DEFAULT_GRID,
  };

  const optionRef = ref<EChartsOption>(defaultOption);
  const { setOption, resize } = useEChartsBase(domRef, optionRef.value);

  if (data) {
    watch(
      data,
      (newData) => {
        if (!newData) {
          setOption(defaultOption);
          return;
        }

        const newOption: EChartsOption = {
          ...defaultOption,
          xAxis: { ...defaultOption.xAxis, data: newData.timeLabels || [] },
          legend: { ...defaultOption.legend, data: newData.legend || [] },
          series: (newData.series || []).map((s) => ({
            ...s,
            type: 'line',
            // smooth: true,
            emphasis: {
              focus: 'series'
            },
          })),
        };
        setOption(newOption);
      },
      { immediate: true, deep: true }
    );
  }

  return { setOption, resize };
}