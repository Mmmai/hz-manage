
import router from '../router';
<template>
  <div>
    <h1>This is an about page</h1>
    <router-link to="/about/1">1的内容</router-link>|
    <router-link to="/about/2">2的内容</router-link>

    <router-view></router-view>
  </div>
</template>

<style>
</style>
