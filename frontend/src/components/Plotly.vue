<script setup lang="ts">
import { ref, onMounted, type Ref } from 'vue'

const plot: Ref<HTMLDivElement | undefined> = ref<HTMLDivElement>()

onMounted(() => {
  if (!plot.value) {
    return
  }
  Plotly.newPlot(plot.value, [
    {
      x: [1, 2, 3, 4, 5],
      y: [1, 2, 3, 4, 5],
    },
  ])
})
</script>

<template>
  <div class="plot" ref="plot" />
</template>

<style scoped>
.plot {
  width: 100%;
  height: 100%;
}
</style>
