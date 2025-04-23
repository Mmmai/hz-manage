<template>
  <!-- src="http://192.168.163.100:31521/" -->

  <div class="card">
    <iframe :src="urlPath" width="100%" height="800px" frameborder="0" allowfullscreen></iframe>
  </div>
</template>
<script setup lang="ts">

import { computed } from '@vue/reactivity';
import { ref, watch } from 'vue';
// const urlPath = ref('http://192.168.163.160:3000/?orgId=1')
import { useRoute,useRouter } from 'vue-router'
const route = useRoute()
// const router = useRouter()
const urlPath = computed(()=>{
  return route.query.url 
})
</script>

<style scoped>
/* .iframe-container {
    overflow: hidden;
  } */
</style>