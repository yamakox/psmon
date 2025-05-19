<script setup lang="ts">
import PlotlyComponent from '../components/Plotly.vue'
import Plotly from 'plotly.js-dist'
import axios from 'axios'
import { ref, onMounted } from 'vue'

const cpuData = ref<Plotly.Data>()
const memData = ref<Plotly.Data>()
const cpuLayout = ref<Partial<Plotly.Layout>>({
  title: { text: 'CPU Usage', font: { size: 24 } },
  height: 500,
})
const memLayout = ref<Partial<Plotly.Layout>>({
  title: { text: 'Available Memory', font: { size: 24 } },
  height: 500,
})

onMounted(async () => {
  try {
    const res = await axios.get('http://localhost:8123/api/v1/monitor')
    cpuData.value = {
      x: res.data.records.time_delta,
      y: res.data.records.cpu_percent,
      type: 'scatter',
      line: { color: 'rgba(0, 0, 255, 0.5)' },
      fill: 'tozeroy',
      fillcolor: 'rgba(0, 0, 255, 0.2)',
    }
    memData.value = {
      x: res.data.records.time_delta,
      y: res.data.records.mem_available,
      type: 'scatter',
      line: { color: 'rgba(0, 255, 0, 0.5)' },
      fill: 'tozeroy',
      fillcolor: 'rgba(0, 255, 0, 0.2)',
    }
  } catch (error) {
    console.error(error)
  }
})
</script>

<template>
  <main>
    <plotly-component :data="cpuData" :layout="cpuLayout" />
    <plotly-component :data="memData" :layout="memLayout" />
  </main>
</template>
