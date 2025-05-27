<script setup lang="ts">
import PlotlyComponent from '../components/Plotly.vue'
import Plotly from 'plotly.js-dist'
import axios from 'axios'
import { ref, onMounted, onUnmounted } from 'vue'

// MARK: durations

const durations = ref<
  {
    name: string
    period_start: string
    period_seconds: number
    every: string
    every_seconds: number
  }[]
>([])
const selectedDurationIndex = ref<number>(0)
const storedDurationIndex = sessionStorage.getItem('durationIndex')
if (storedDurationIndex !== null) {
  selectedDurationIndex.value = JSON.parse(storedDurationIndex)
}

async function durationSelected(index: number) {
  if (selectedDurationIndex.value === index) {
    return
  }
  selectedDurationIndex.value = index
  sessionStorage.setItem('durationIndex', JSON.stringify(index))
  dataSeries.time.length = 0
  await fetchData()
}

// MARK: data series

const dataSeries = {
  time: [] as Date[],
  cpu_percent_max: [] as number[],
  cpu_percent_mean: [] as number[],
  mem_available_max: [] as number[],
  mem_available_mean: [] as number[],
  disk_used_max: [] as number[],
  disk_used_mean: [] as number[],
}

// MARK: plot data

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
      // tickformat: '%H:%M\n%Y-%m-%d',   ← Plotlyの不具合? データが空のとき`WARN: encountered bad format`となる
    },
    ...optionalArgs,
  })
const setLayoutYaxis = (layout: Partial<Plotly.Layout>, yaxis: Partial<Plotly.LayoutAxis>) => {
  layout.xaxis = {
    tickformat: '%H:%M\n%Y-%m-%d',
  }
  layout.yaxis = yaxis
}
const cpuLayout = makeLayout('CPU (Max,Mean)')
const memLayout = makeLayout('Memory (Max)')
const diskLayout = makeLayout('Disk (Max)')

const commonConfig = ref<Partial<Plotly.Config>>({
  responsive: true,
  displayModeBar: false,
})

// MARK: process CPU records
const processCpuRecords = ref<
  {
    pid: number
    name: string
    cpu_max: number
    cpu_min: number
    cpu_mean: number
  }[]
>([])
const processCpuTime = ref<Date | null>(null)

// MARK: utility functions

function toGigaBytes(bytes: number) {
  return bytes / 1024 / 1024 / 1024
}

function toTeraBytes(bytes: number) {
  return bytes / 1024 / 1024 / 1024 / 1024
}

// MARK: state management

const isLoading = ref<boolean>(false)

// MARK: fetch data

async function fetchData() {
  if (durations.value.length === 0) {
    console.error('durations is empty')
    return
  }
  if (isLoading.value) {
    return
  }
  isLoading.value = true
  try {
    let mem_total = 0
    let disk_total = 0
    const lastTime = dataSeries.time.at(-1)
    if (lastTime === undefined) {
      const res = await axios.get('/api/v1/monitor', {
        params: {
          duration_index: selectedDurationIndex.value,
        },
      })
      mem_total = res.data.mem_total
      disk_total = res.data.disk_total
      const records = res.data.records
      dataSeries.time = records.time.map((time: string) => new Date(time))
      dataSeries.cpu_percent_max = records.cpu_percent_max
      dataSeries.cpu_percent_mean = records.cpu_percent_mean
      dataSeries.mem_available_max = records.mem_available_max
      dataSeries.mem_available_mean = records.mem_available_mean
      dataSeries.disk_used_max = records.disk_used_max
      dataSeries.disk_used_mean = records.disk_used_mean
    } else {
      const res = await axios.get('/api/v1/monitor', {
        params: {
          duration_index: selectedDurationIndex.value,
          start_time: lastTime,
        },
      })
      mem_total = res.data.mem_total
      disk_total = res.data.disk_total
      const records = res.data.records
      if (records.time?.length > 0) {
        dataSeries.time.push(...records.time.map((time: string) => new Date(time)))
        dataSeries.cpu_percent_max.push(...records.cpu_percent_max)
        dataSeries.cpu_percent_mean.push(...records.cpu_percent_mean)
        dataSeries.mem_available_max.push(...records.mem_available_max)
        dataSeries.mem_available_mean.push(...records.mem_available_mean)
        dataSeries.disk_used_max.push(...records.disk_used_max)
        dataSeries.disk_used_mean.push(...records.disk_used_mean)
        const duration = durations.value[selectedDurationIndex.value]
        const maxDataCount = Math.floor(duration.period_seconds / duration.every_seconds)
        dataSeries.time = dataSeries.time.slice(-maxDataCount)
        dataSeries.cpu_percent_max = dataSeries.cpu_percent_max.slice(-maxDataCount)
        dataSeries.cpu_percent_mean = dataSeries.cpu_percent_mean.slice(-maxDataCount)
        dataSeries.mem_available_max = dataSeries.mem_available_max.slice(-maxDataCount)
        dataSeries.mem_available_mean = dataSeries.mem_available_mean.slice(-maxDataCount)
        dataSeries.disk_used_max = dataSeries.disk_used_max.slice(-maxDataCount)
        dataSeries.disk_used_mean = dataSeries.disk_used_mean.slice(-maxDataCount)
      }
    }
    setLayoutYaxis(cpuLayout.value, {
      range: [0, 100],
      autorange: false,
      ticksuffix: '%',
    })
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
    setLayoutYaxis(memLayout.value, {
      range: [0, toGigaBytes(mem_total)],
      autorange: false,
      ticksuffix: 'GB',
    })
    memData.value = [
      {
        x: dataSeries.time,
        y: dataSeries.mem_available_max.map((x: number) => toGigaBytes(mem_total - x)),
        type: 'scatter',
        line: { color: 'rgba(0, 255, 0, 0.5)', width: 2 },
        fill: 'tozeroy',
        fillcolor: 'rgba(0, 255, 0, 0.2)',
      },
    ]
    setLayoutYaxis(diskLayout.value, {
      range: [0, toGigaBytes(disk_total)],
      autorange: false,
      ticksuffix: 'GB',
    })
    diskData.value = [
      {
        x: dataSeries.time,
        y: dataSeries.disk_used_max.map((x: number) => toGigaBytes(x)),
        type: 'scatter',
        line: { color: 'rgba(255, 0, 255, 0.5)', width: 2 },
        fill: 'tozeroy',
        fillcolor: 'rgba(255, 0, 255, 0.2)',
      },
    ]
  } catch (error) {
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

// MARK: event handlers

async function plotly_click(event: Plotly.PlotMouseEvent) {
  console.log('HomeView: plotly_click', event)
  const point = event.points?.shift()
  if (point === undefined) {
    return
  }
  console.log(
    `HomeView: plotly_click: x=${point.x}, y=${point.y}, pointNumber=${point.pointNumber} dataSeries.time=${dataSeries.time[point.pointNumber]}`,
  )
  try {
    const res = await axios.get('/api/v1/monitor/process-cpu', {
      params: {
        time: dataSeries.time[point.pointNumber],
        duration_index: selectedDurationIndex.value,
      },
    })
    processCpuRecords.value = res.data.records
    processCpuTime.value = new Date(res.data.timestamp)
  } catch (error) {
    console.error(error)
  }
}

// MARK: onMounted / onUnmounted

let intervalId: number | null = null

onMounted(async () => {
  console.log('HomeView: onMounted')
  try {
    durations.value = (await axios.get('/api/v1/monitor/durations')).data
    await fetchData()
    if (intervalId !== null) {
      clearInterval(intervalId)
    }
    intervalId = setInterval(async () => {
      try {
        await fetchData()
      } catch (error) {
        console.error(error)
      }
    }, 60 * 1000)
  } catch (error) {
    console.error(error)
  }
})

onUnmounted(() => {
  console.log('HomeView: onUnmounted')
  if (intervalId !== null) {
    clearInterval(intervalId)
    intervalId = null
  }
})
</script>

<template>
  <main>
    <div class="dropdown-center duration-selector" v-if="durations.length > 0">
      <button
        class="btn btn-primary dropdown-toggle duration-selector-btn"
        type="button"
        data-bs-toggle="dropdown"
        aria-expanded="false"
      >
        {{ durations[selectedDurationIndex].name }}
      </button>
      <ul class="dropdown-menu">
        <li v-for="(duration, index) in durations" :key="index">
          <a class="dropdown-item" href="#" @click="durationSelected(index)">
            {{ duration.name }}
          </a>
        </li>
      </ul>
    </div>
    <plotly-component
      class="plotly-component"
      :dataset="cpuData"
      :layout="cpuLayout"
      :config="commonConfig"
      @plotly_click="plotly_click"
    />
    <plotly-component
      class="plotly-component"
      :dataset="memData"
      :layout="memLayout"
      :config="commonConfig"
      @plotly_click="plotly_click"
    />
    <plotly-component
      class="plotly-component"
      :dataset="diskData"
      :layout="diskLayout"
      :config="commonConfig"
      @plotly_click="plotly_click"
    />
    <div class="process-cpu" v-if="processCpuTime !== null">
      <div class="process-cpu-time">
        Processes with high CPU utilization at {{ processCpuTime.toLocaleString() }}:
      </div>
      <div class="process-cpu-table-container">
        <table class="table process-cpu-table table-striped table-light table-sm">
          <thead>
            <tr>
              <th class="column-pid">PID</th>
              <th class="column-name">Name</th>
              <th class="column-cpu">CPU</th>
            </tr>
          </thead>
          <tbody class="table-group-divider">
            <tr v-for="record in processCpuRecords" :key="record.pid">
              <td class="column-pid">{{ record.pid }}</td>
              <td class="column-name">{{ record.name }}</td>
              <td class="column-cpu">
                <span class="process-cpu-mean">{{ record.cpu_mean }}%</span>
                <span class="process-cpu-min">
                  ({{ record.cpu_min }}% 〜 {{ record.cpu_max }}%)
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </main>
</template>

<style scoped>
.plotly-component {
  height: 250px;
}
.duration-selector {
  margin: 4px 8px;
}
.duration-selector-btn {
  min-width: 10rem;
}
.process-cpu {
  margin: 4px 8px;
  padding: 4px 8px;
  border: 1px solid #ccc;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.process-cpu-time {
  margin: 0;
  padding: 0;
}
.process-cpu-table-container {
  margin: 0;
  padding: 0;
  overflow-x: auto;
}
.process-cpu-table {
  margin: 0;
  padding: 0;
  width: 100%;
}
.column-pid {
  width: 10%;
  min-width: 5rem;
  padding-right: 1rem;
  text-align: right;
}
.column-name {
  width: 40%;
  white-space: nowrap;
}
.column-cpu {
  width: 50%;
  white-space: nowrap;
}
.process-cpu-mean {
  display: inline-block;
  min-width: 3.3rem;
  text-align: right;
  margin: 0 0.25rem 0 0;
}
</style>
