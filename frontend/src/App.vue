<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header class="container-fluid d-flex flex-row justify-content-start align-items-center">
    <div class="row w-100">
      <div class="col-10">
        <h1>psui</h1>
      </div>
      <div class="col-2 d-flex flex-row justify-content-end align-items-center gap-3">
        <a href="/">Home</a>
        <a href="/about">About</a>
      </div>
    </div>
  </header>
  <RouterView />
</template>

<style scoped>
header {
  margin: 0;
  padding: 0;
  max-width: 100vw;
  color: white;
  background-color: #2c3e50;
}
</style>
