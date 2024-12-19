<template>
  <div class="card"> 11</div>
</template>

<script lang="ts" setup>
import { ref, computed, watch, getCurrentInstance, onMounted, reactive, nextTick } from "vue";
const { proxy } = getCurrentInstance();
import { useStore } from "vuex";
const store = useStore();

</script>
<style scoped lang="scss"></style>