<script setup lang="ts">
import PlotlyComponent from '../components/Plotly.vue'
import Plotly from 'plotly.js-dist'
import axios from 'axios'
import { ref, onMounted } from 'vue'

const cpuPlotRef = ref<InstanceType<typeof PlotlyComponent>>()
const memPlotRef = ref<InstanceType<typeof PlotlyComponent>>()

const cpuData = ref<Plotly.Data[]>([])
const memData = ref<Plotly.Data[]>([])
const diskData = ref<Plotly.Data[]>([])
const makeLayout = (title: string, optionalArgs: Partial<Plotly.Layout> = {}) =>
  ref<Partial<Plotly.Layout>>({
    title: { text: title, font: { size: 20 }, y: 0.94 },
    height: 250,
    autosize: true,
    margin: {
      l: 60,
      r: 20,
      t: 50,
      b: 50,
    },
    xaxis: {
      tickformat: '%H:%M\n%Y-%m-%d',
    },
    ...optionalArgs,
  })
const cpuLayout = makeLayout('CPU Usage', {
  yaxis: {
    range: [0, 100],
    autorange: false,
    ticksuffix: '%',
  },
})
const memLayout = makeLayout('Memory Usage')
const diskLayout = makeLayout('Disk Usage')
const commonConfig = ref<Partial<Plotly.Config>>({
  responsive: true,
  displayModeBar: false,
})

function toGigaBytes(bytes: number) {
  return bytes / 1024 / 1024 / 1024
}

function toTeraBytes(bytes: number) {
  return bytes / 1024 / 1024 / 1024 / 1024
}

async function fetchData() {
  try {
    const res = await axios.get('http://localhost:8123/api/v1/monitor')
    const baseTime = new Date(res.data.timestamp).getTime()
    const timeSeries = res.data.records.time_delta.map(
      (time: number) => new Date(baseTime + time * 1000),
    )
    cpuData.value = [
      {
        name: 'max',
        x: timeSeries,
        y: res.data.records.cpu_percent_max,
        type: 'scatter',
        line: { color: 'rgba(0, 0, 255, 0.5)', width: 1 },
        fill: 'tozeroy',
        fillcolor: 'rgba(0, 0, 255, 0.2)',
        showlegend: false,
      },
      {
        text: 'mean',
        x: timeSeries,
        y: res.data.records.cpu_percent_mean,
        type: 'scatter',
        line: { color: 'rgba(0, 0, 255, 0.5)', width: 2 },
        fill: 'tozeroy',
        fillcolor: 'rgba(0, 0, 255, 0.2)',
        showlegend: false,
      },
    ]
    memLayout.value.yaxis = {
      range: [0, toGigaBytes(res.data.mem_total)],
      autorange: false,
      ticksuffix: 'GB',
    }
    memData.value = [
      {
        x: timeSeries,
        y: res.data.records.mem_available_mean.map((x: number) =>
          toGigaBytes(res.data.mem_total - x),
        ),
        type: 'scatter',
        line: { color: 'rgba(0, 255, 0, 0.5)', width: 2 },
        fill: 'tozeroy',
        fillcolor: 'rgba(0, 255, 0, 0.2)',
      },
    ]
    diskLayout.value.yaxis = {
      range: [0, toGigaBytes(res.data.disk_total)],
      autorange: false,
      ticksuffix: 'GB',
    }
    diskData.value = [
      {
        x: timeSeries,
        y: res.data.records.disk_used_mean.map((x: number) => toGigaBytes(x)),
        type: 'scatter',
        line: { color: 'rgba(255, 0, 255, 0.5)', width: 2 },
        fill: 'tozeroy',
        fillcolor: 'rgba(255, 0, 255, 0.2)',
      },
    ]
  } catch (error) {
    console.error(error)
  }
}

onMounted(async () => {
  await fetchData()
  setInterval(async () => {
    await fetchData()
  }, 60 * 1000)
})
</script>

<template>
  <main>
    <plotly-component
      class="plotly-component"
      ref="cpuPlotRef"
      :dataset="cpuData"
      :layout="cpuLayout"
      :config="commonConfig"
    />
    <plotly-component
      class="plotly-component"
      ref="memPlotRef"
      :dataset="memData"
      :layout="memLayout"
      :config="commonConfig"
    />
    <plotly-component
      class="plotly-component"
      ref="diskPlotRef"
      :dataset="diskData"
      :layout="diskLayout"
      :config="commonConfig"
    />
  </main>
</template>

<style scoped></style>
