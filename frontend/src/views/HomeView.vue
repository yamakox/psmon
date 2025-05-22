<script setup lang="ts">
import PlotlyComponent from '../components/Plotly.vue'
import Plotly from 'plotly.js-dist'
import axios from 'axios'
import { ref, onMounted } from 'vue'

const maxDataCount = 180

const dataSeries = {
  time: [] as Date[],
  cpu_percent_max: [] as number[],
  cpu_percent_mean: [] as number[],
  mem_available_mean: [] as number[],
  disk_used_mean: [] as number[],
}

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
    let mem_total = 0
    let disk_total = 0
    const lastTime = dataSeries.time.at(-1)
    if (lastTime === undefined) {
      const res = await axios.get('http://localhost:8123/api/v1/monitor')
      mem_total = res.data.mem_total
      disk_total = res.data.disk_total
      const records = res.data.records
      dataSeries.time = records.time.map((time: string) => new Date(time))
      dataSeries.cpu_percent_max = records.cpu_percent_max
      dataSeries.cpu_percent_mean = records.cpu_percent_mean
      dataSeries.mem_available_mean = records.mem_available_mean
      dataSeries.disk_used_mean = records.disk_used_mean
    } else {
      const res = await axios.get('http://localhost:8123/api/v1/monitor', {
        params: {
          start_time: lastTime,
        },
      })
      mem_total = res.data.mem_total
      disk_total = res.data.disk_total
      const records = res.data.records
      dataSeries.time.push(...records.time.map((time: string) => new Date(time)))
      dataSeries.cpu_percent_max.push(...records.cpu_percent_max)
      dataSeries.cpu_percent_mean.push(...records.cpu_percent_mean)
      dataSeries.mem_available_mean.push(...records.mem_available_mean)
      dataSeries.disk_used_mean.push(...records.disk_used_mean)
      dataSeries.time = dataSeries.time.slice(-maxDataCount)
      dataSeries.cpu_percent_max = dataSeries.cpu_percent_max.slice(-maxDataCount)
      dataSeries.cpu_percent_mean = dataSeries.cpu_percent_mean.slice(-maxDataCount)
      dataSeries.mem_available_mean = dataSeries.mem_available_mean.slice(-maxDataCount)
      dataSeries.disk_used_mean = dataSeries.disk_used_mean.slice(-maxDataCount)
    }
    cpuData.value = [
      {
        name: 'max',
        x: dataSeries.time,
        y: dataSeries.cpu_percent_max,
        type: 'scatter',
        line: { color: 'rgba(0, 0, 255, 0.5)', width: 1 },
        fill: 'tozeroy',
        fillcolor: 'rgba(0, 0, 255, 0.2)',
        showlegend: false,
      },
      {
        text: 'mean',
        x: dataSeries.time,
        y: dataSeries.cpu_percent_mean,
        type: 'scatter',
        line: { color: 'rgba(0, 0, 255, 0.5)', width: 2 },
        fill: 'tozeroy',
        fillcolor: 'rgba(0, 0, 255, 0.2)',
        showlegend: false,
      },
    ]
    memLayout.value.yaxis = {
      range: [0, toGigaBytes(mem_total)],
      autorange: false,
      ticksuffix: 'GB',
    }
    memData.value = [
      {
        x: dataSeries.time,
        y: dataSeries.mem_available_mean.map((x: number) => toGigaBytes(mem_total - x)),
        type: 'scatter',
        line: { color: 'rgba(0, 255, 0, 0.5)', width: 2 },
        fill: 'tozeroy',
        fillcolor: 'rgba(0, 255, 0, 0.2)',
      },
    ]
    diskLayout.value.yaxis = {
      range: [0, toGigaBytes(disk_total)],
      autorange: false,
      ticksuffix: 'GB',
    }
    diskData.value = [
      {
        x: dataSeries.time,
        y: dataSeries.disk_used_mean.map((x: number) => toGigaBytes(x)),
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
      :dataset="cpuData"
      :layout="cpuLayout"
      :config="commonConfig"
    />
    <plotly-component
      class="plotly-component"
      :dataset="memData"
      :layout="memLayout"
      :config="commonConfig"
    />
    <plotly-component
      class="plotly-component"
      :dataset="diskData"
      :layout="diskLayout"
      :config="commonConfig"
    />
  </main>
</template>

<style scoped></style>
