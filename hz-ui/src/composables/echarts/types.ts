import type { EChartsOption } from 'echarts';

export interface LineChartData {
  timeLabels: string[];
  legend: string[];
  series: Array<{
    name: string;
    type: 'line';
    data: number[];
    smooth?: boolean;
  }>;
}

export interface BarChartData {
  yAxisData: string[];
  seriesData: number[];
}

export interface GaugeChartData {
  value: number;
  title?: string;
}

