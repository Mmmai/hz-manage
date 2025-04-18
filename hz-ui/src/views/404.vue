<template>
  <h1>404 Not Found</h1>
</template>
<script setup>
import {useStore} from 'vuex'
import {useRouter} from 'vue-router'
const router = useRouter()
console.log(router.getRoutes())
// const router = useRouter()
const store = useStore()
console.log(store.state.routerInfo)
</script>