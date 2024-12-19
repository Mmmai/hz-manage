<template>
    <div>zabbix</div>
  </template>
  <script lang="ts" setup>
    import { ref,reactive, watch,getCurrentInstance, nextTick  } from 'vue'
    // import { Delete, Filter,CirclePlus } from '@element-plus/icons-vue'
    const { proxy } = getCurrentInstance();
    const dialogVisible = ref(false)
    const edit = ()=>{
      dialogVisible.value = true
      }
    
  </script>