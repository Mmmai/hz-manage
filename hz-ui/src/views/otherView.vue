<template>
  <div class="main-box card" style="flex: 0.1">111</div>

  <div class="table-box">
    <div
      class="card"
      style="
        flex: 0.2;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
      "
    >
      <el-icon style="position: absolute; top: 10px; right: 20px" size="large">
        <CircleClose />
      </el-icon>
      <div style="width: 100%; flex-grow: 1; overflow: auto">
        <p
          :key="index"
          v-for="(, index) in [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
          ]"
        >
          111
        </p>
      </div>
      <div style="width: 100%; background-color: blue; align-self: flex-end">
        555
      </div>
    </div>

    <div class="card">333</div>
  </div>
</template>

<script lang="ts" setup>
import { CircleClose } from "@element-plus/icons-vue";
import { watch, ref } from "vue";
const props = { multiple: true, checkStrictly: true };
const test = ref([]);
watch(
  () => test.value,
  (n) => {
    console.log(test.value);
  }
);
const options = [
  {
    value: 1,
    label: "Asia",
    children: [
      {
        value: 2,
        label: "China",
        children: [
          { value: 3, label: "Beijing" },
          { value: 4, label: "Shanghai" },
          { value: 5, label: "Hangzhou" },
        ],
      },
      {
        value: 6,
        label: "Japan",
        children: [
          { value: 7, label: "Tokyo" },
          { value: 8, label: "Osaka" },
          { value: 9, label: "Kyoto" },
        ],
      },
      {
        value: 10,
        label: "Korea",
        children: [
          { value: 11, label: "Seoul" },
          { value: 12, label: "Busan" },
          { value: 13, label: "Taegu" },
        ],
      },
    ],
  },
  {
    value: 14,
    label: "Europe",
    children: [
      {
        value: 15,
        label: "France",
        children: [
          { value: 16, label: "Paris" },
          { value: 17, label: "Marseille" },
          { value: 18, label: "Lyon" },
        ],
      },
      {
        value: 19,
        label: "UK",
        children: [
          { value: 20, label: "London" },
          { value: 21, label: "Birmingham" },
          { value: 22, label: "Manchester" },
        ],
      },
    ],
  },
  {
    value: 23,
    label: "North America",
    children: [
      {
        value: 24,
        label: "US",
        children: [
          { value: 25, label: "New York" },
          { value: 26, label: "Los Angeles" },
          { value: 27, label: "Washington" },
        ],
      },
      {
        value: 28,
        label: "Canada",
        children: [
          { value: 29, label: "Toronto" },
          { value: 30, label: "Montreal" },
          { value: 31, label: "Ottawa" },
        ],
      },
    ],
  },
];
</script>
