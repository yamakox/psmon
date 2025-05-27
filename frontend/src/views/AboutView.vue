<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const version = ref('0.0.0')

onMounted(async () => {
  const res = await axios.get('/api/v1/misc/version')
  version.value = res.data.version
})
</script>

<template>
  <div class="about">
    <h1>psmon v{{ version }}</h1>
    <p>psmon is a tool for monitoring system resources.</p>
    <p>It is written in Vue.js and Plotly.js.</p>
  </div>
</template>

<style scoped>
.about {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}
</style>
