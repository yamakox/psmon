<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import Plotly from 'plotly.js-dist'
import axios from 'axios'

const props = defineProps<{
  data?: Plotly.Data
  layout?: Partial<Plotly.Layout>
}>()

const rootRef = ref<HTMLDivElement>()
const plotlyElement = ref<Plotly.PlotlyHTMLElement>()

async function setupPlotly() {
  if (!plotlyElement.value) {
    if (!rootRef.value) {
      return
    }
    if (props.data && props.layout) {
      plotlyElement.value = await Plotly.newPlot(rootRef.value, [props.data], props.layout)
    }
    return
  }
  if (props.data && props.layout) {
    await Plotly.update(plotlyElement.value, props.data, props.layout)
  } else {
    console.error('No data or layout')
  }
}

watch(props, async () => {
  await setupPlotly()
})

watch(rootRef, async () => {
  await setupPlotly()
})

onMounted(async () => {
  await setupPlotly()
})
</script>

<template>
  <div ref="rootRef" />
</template>

<style scoped></style>
