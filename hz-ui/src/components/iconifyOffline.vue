<template>
  <svg
    :width="size"
    :height="size"
    :viewBox="iconViewbox"
    :style="{ fill: color }"
  >
    <g v-html="iconData"></g>
  </svg>
  <!-- <span>{{ iconData }}</span> -->
</template>

<script setup>
import { ref, onMounted, watch, reactive } from "vue";
// import { ep } from "@iconify/json"; // 这里以 Material Design Icons 为例，你可以根据需要选择不同的图标集
import ep from "@iconify/json/json/ep.json";
import clarity from "@iconify/json/json/clarity.json";
import mdi from "@iconify/json/json/mdi.json";
import carbon from "@iconify/json/json/carbon.json";
import devicon from "@iconify/json/json/devicon.json";
import material_symbols from "@iconify/json/json/material-symbols.json";
import octicon from "@iconify/json/json/octicon.json";
const iconObj = reactive({
  ep: ep,
  clarity: clarity,
  mdi: mdi,
  material_symbols: material_symbols,
  carbon: carbon,
  devicon: devicon,
  octicon: octicon,
});
// 接收父组件传递的 props
const props = defineProps({
  icon: {
    type: String,
    required: true,
  },
  size: {
    type: String,
    default: "24px",
  },
  color: {
    type: String,
    default: "currentColor",
  },
});

// 存储图标数据的响应式引用
const iconData = ref(null);
const iconViewbox = ref("0 0 24 24");
// 根据图标名称查找图标数据
const fetchIconData = (iconStr) => {
  if (iconStr === "" || iconStr == undefined) return;
  // console.log(iconStr);
  // 分割字符串
  let [_iconPrefix, iconName] = iconStr.split(":");
  let iconPrefix = _iconPrefix.replace("-", "_");
  if (iconObj[iconPrefix].icons && iconObj[iconPrefix].icons[iconName]) {
    iconData.value = iconObj[iconPrefix].icons[iconName].body;
    iconViewbox.value = `0 0 ${iconObj[iconPrefix].height || 24} ${
      iconObj[iconPrefix].width || 24
    }`;
  } else {
    console.error(`Icon ${iconStr} not found in the icon set.`);
  }
};

// 组件挂载时查找图标数据
onMounted(() => {
  fetchIconData(props.icon);
});

// 监听图标名称的变化，重新查找图标数据
watch(
  () => props.icon,
  (newVal) => {
    fetchIconData(newVal);
  }
);
</script>