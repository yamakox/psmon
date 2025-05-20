<script setup lang="ts">
import { ref, watch } from 'vue'
import Plotly from 'plotly.js-dist'

const props = defineProps<{
  dataset?: Plotly.Data[]
  layout?: Partial<Plotly.Layout>
  config?: Partial<Plotly.Config>
}>()

const rootRef = ref<HTMLDivElement>()

async function setupPlot() {
  if (rootRef.value && props.dataset) {
    await Plotly.react(rootRef.value, props.dataset, props.layout, props.config)
  }
}

watch(rootRef, async () => {
  await setupPlot()
})

watch(props, async () => {
  await setupPlot()
})
</script>

<template>
  <div ref="rootRef" />
</template>

<style scoped></style>
