// src/composables/echarts/theme.ts
import * as echarts from 'echarts';

// ✅ 直接注册，无需 getTheme 检查
export const MONITOR_THEME = 'monitor-theme';

// 安全注册（即使多次 import 也不会出错）
echarts.registerTheme(MONITOR_THEME, {
  color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452'],
  backgroundColor: 'rgba(0,0,0,0)',
  textStyle: {
    fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif',
    fontSize: 12,
    color: '#333',
  },
  animationDuration: 800,
  animationEasing: 'quinticInOut',
});

// 也可以导出默认样式片段，供 option 合并使用
export const DEFAULT_GRID = {
  left: '10%',
  right: '5%',
  top: '20%',
  bottom: '15%',
};

export const DEFAULT_TOOLTIP = {
  trigger: 'axis' as const,
  backgroundColor: 'rgba(50, 50, 50, 0.85)',
  textStyle: { color: '#fff' },
  borderColor: '#333',
};

export const GAUGE_COLOR_STAGES = [
  [0.3, '#67e0e3'],
  [0.7, '#37a2da'],
  [1, '#fd666d'],
] as [number, string][];