// src/composables/echarts/useBarChart.ts
import { ref, watch, Ref } from 'vue';
import type { EChartsOption } from 'echarts';
import { useEChartsBase } from './useEChartsBase';
import { DEFAULT_GRID } from './theme';
import type { BarChartData } from './types';
import * as echarts from 'echarts';

export function useBarChart(
  domRef: Ref<HTMLElement | null>,
  data?: Ref<BarChartData | null>
) {
  const defaultOption: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(50, 50, 50, 0.85)',
      textStyle: { color: '#fff' },
    },
    xAxis: {
      type: 'value',
      name: '使用率 (%)',
      min: 0,
      max: 100,
      axisLabel: { formatter: '{value} %' },
    },
    yAxis: {
      type: 'category',
      data: [],
    },
    series: [
      {
        type: 'bar',
        data: [],
        label: {
          show: true,
          position: 'insideRight',
          color: '#fff',
          fontWeight: 'bold',
        },
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#5470c6' },
            { offset: 1, color: '#91cc75' },
          ]),
        },
      },
    ],
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
          yAxis: { ...defaultOption.yAxis, data: newData.yAxisData || [] },
          series: [
            {
              ...defaultOption.series![0],
              data: newData.seriesData || [],
            },
          ],
        };
        console.log("barOptions: ", newOption);
        setOption(newOption);
      },
      { immediate: true, deep: true }
    );
  }

  return { setOption, resize };
}