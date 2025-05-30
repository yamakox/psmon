<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-container">
    <header class="container-fluid d-flex flex-row justify-content-start align-items-center">
      <div class="row w-100">
        <div class="col-10">
          <h4 class="title">psmon</h4>
        </div>
        <div class="col-2 d-flex flex-row justify-content-end align-items-center gap-4">
          <router-link class="nav-link" to="/">Home</router-link>
          <router-link class="nav-link" to="/about">About</router-link>
        </div>
      </div>
    </header>
    <RouterView class="router-view" />
  </div>
</template>

<style scoped>
header {
  margin: 0;
  padding: 0;
  max-width: 100vw;
  color: white;
  background-color: #2c3e50;
}
.title {
  margin: 0.15em 0.5rem;
  font-size: 1.5rem;
  font-weight: bold;
}
.app-container {
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  justify-content: start;
  align-items: center;
  width: 100%;
  height: 100vh;
}
.router-view {
  width: 100%;
}
.nav-link {
  color: white;
}
</style>
