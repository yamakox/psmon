<script setup lang="ts">
import { ref, watch } from 'vue'
import Plotly from 'plotly.js-dist'

// MARK: properties

const props = defineProps<{
  dataset?: Plotly.Data[]
  layout?: Partial<Plotly.Layout>
  config?: Partial<Plotly.Config>
}>()

// MARK: events

const emit = defineEmits<{
  plotly_click: [event: Plotly.PlotMouseEvent]
  plotly_unhover: [event: Plotly.PlotMouseEvent]
  plotly_hover: [event: Plotly.PlotHoverEvent]
  plotly_selecting: [event: Plotly.PlotSelectionEvent]
  plotly_selected: [event: Plotly.PlotSelectionEvent]
  plotly_restyle: [event: Plotly.PlotRestyleEvent]
  plotly_relayout: [event: Plotly.PlotRelayoutEvent]
  plotly_relayouting: [event: Plotly.PlotRelayoutEvent]
  plotly_clickannotation: [event: Plotly.ClickAnnotationEvent]
  plotly_animatingframe: [event: Plotly.FrameAnimationEvent]
  plotly_legendclick: [event: Plotly.LegendClickEvent, returnValues: { cancelDefault: boolean }]
  plotly_legenddoubleclick: [
    event: Plotly.LegendClickEvent,
    returnValues: { cancelDefault: boolean },
  ]
  plotly_sliderchange: [event: Plotly.SliderChangeEvent]
  plotly_sliderend: [event: Plotly.SliderEndEvent]
  plotly_sliderstart: [event: Plotly.SliderStartEvent]
  plotly_sunburstclick: [event: Plotly.SunburstClickEvent]
  plotly_event: [data: any]
  plotly_beforeplot: [event: Plotly.BeforePlotEvent, returnValues: { cancelDefault: boolean }]
  plotly_afterexport: []
  plotly_afterplot: []
  plotly_animated: []
  plotly_animationinterrupted: []
  plotly_autosize: []
  plotly_beforeexport: []
  plotly_deselect: []
  plotly_doubleclick: []
  plotly_framework: []
  plotly_redraw: []
  plotly_transitioning: []
  plotly_transitioninterrupted: []
}>()

// MARK: state management

const rootRef = ref<HTMLDivElement>()
let plotlyHTMLElement: Plotly.PlotlyHTMLElement | null = null

const debug_logging = true

// MARK: functions

function log(message: string, event: any) {
  if (debug_logging) {
    console.debug(message, event) // NOTE: console.debugはconsoleのVerboseレベルで出力される
  }
}

async function setupPlot() {
  if (rootRef.value && props.dataset) {
    const element = await Plotly.react(rootRef.value, props.dataset, props.layout, props.config)
    if (plotlyHTMLElement !== element) {
      plotlyHTMLElement = element
      plotlyHTMLElement.on('plotly_click', (event: Plotly.PlotMouseEvent) => {
        console.debug('plotly_click', event) // NOTE: console.debugはconsoleのVerboseレベルで出力される
        emit('plotly_click', event)
      })
      plotlyHTMLElement.on('plotly_unhover', (event: Plotly.PlotMouseEvent) => {
        console.debug('plotly_unhover', event)
        emit('plotly_unhover', event)
      })
      plotlyHTMLElement.on('plotly_hover', (event: Plotly.PlotHoverEvent) => {
        console.debug('plotly_hover', event)
        emit('plotly_hover', event)
      })
      plotlyHTMLElement.on('plotly_selecting', (event: Plotly.PlotSelectionEvent) => {
        console.debug('plotly_selecting', event)
        emit('plotly_selecting', event)
      })
      plotlyHTMLElement.on('plotly_selected', (event: Plotly.PlotSelectionEvent) => {
        console.debug('plotly_selected', event)
        emit('plotly_selected', event)
      })
      plotlyHTMLElement.on('plotly_restyle', (event: Plotly.PlotRestyleEvent) => {
        console.debug('plotly_restyle', event)
        emit('plotly_restyle', event)
      })
      plotlyHTMLElement.on('plotly_relayout', (event: Plotly.PlotRelayoutEvent) => {
        console.debug('plotly_relayout', event)
        emit('plotly_relayout', event)
      })
      plotlyHTMLElement.on('plotly_relayouting', (event: Plotly.PlotRelayoutEvent) => {
        console.debug('plotly_relayouting', event)
        emit('plotly_relayouting', event)
      })
      plotlyHTMLElement.on('plotly_clickannotation', (event: Plotly.ClickAnnotationEvent) => {
        console.debug('plotly_clickannotation', event)
        emit('plotly_clickannotation', event)
      })
      plotlyHTMLElement.on('plotly_animatingframe', (event: Plotly.FrameAnimationEvent) => {
        console.debug('plotly_animatingframe', event)
        emit('plotly_animatingframe', event)
      })
      plotlyHTMLElement.on('plotly_legendclick', (event: Plotly.LegendClickEvent) => {
        const returnValues = { cancelDefault: false }
        console.debug('plotly_legendclick', event)
        emit('plotly_legendclick', event, returnValues)
        return !returnValues.cancelDefault
      })
      plotlyHTMLElement.on('plotly_legenddoubleclick', (event: Plotly.LegendClickEvent) => {
        const returnValues = { cancelDefault: false }
        console.debug('plotly_legenddoubleclick', event)
        emit('plotly_legenddoubleclick', event, returnValues)
        return !returnValues.cancelDefault
      })
      plotlyHTMLElement.on('plotly_sliderchange', (event: Plotly.SliderChangeEvent) => {
        console.debug('plotly_sliderchange', event)
        emit('plotly_sliderchange', event)
      })
      plotlyHTMLElement.on('plotly_sliderend', (event: Plotly.SliderEndEvent) => {
        console.debug('plotly_sliderend', event)
        emit('plotly_sliderend', event)
      })
      plotlyHTMLElement.on('plotly_sliderstart', (event: Plotly.SliderStartEvent) => {
        console.debug('plotly_sliderstart', event)
        emit('plotly_sliderstart', event)
      })
      plotlyHTMLElement.on('plotly_sunburstclick', (event: Plotly.SunburstClickEvent) => {
        console.debug('plotly_sunburstclick', event)
        emit('plotly_sunburstclick', event)
      })
      plotlyHTMLElement.on('plotly_event', (event: any) => {
        console.debug('plotly_event', event)
        emit('plotly_event', event)
      })
      plotlyHTMLElement.on('plotly_beforeplot', (event: Plotly.BeforePlotEvent) => {
        const returnValues = { cancelDefault: false }
        console.debug('plotly_beforeplot', event)
        emit('plotly_beforeplot', event, returnValues)
        return !returnValues.cancelDefault
      })
      plotlyHTMLElement.on('plotly_afterexport', () => {
        console.debug('plotly_afterexport')
        emit('plotly_afterexport')
      })
      plotlyHTMLElement.on('plotly_afterplot', () => {
        console.debug('plotly_afterplot')
        emit('plotly_afterplot')
      })
      plotlyHTMLElement.on('plotly_animated', () => {
        console.debug('plotly_animated')
        emit('plotly_animated')
      })
      plotlyHTMLElement.on('plotly_animationinterrupted', () => {
        console.debug('plotly_animationinterrupted')
        emit('plotly_animationinterrupted')
      })
      plotlyHTMLElement.on('plotly_autosize', () => {
        console.debug('plotly_autosize')
        emit('plotly_autosize')
      })
      plotlyHTMLElement.on('plotly_beforeexport', () => {
        console.debug('plotly_beforeexport')
        emit('plotly_beforeexport')
      })
      plotlyHTMLElement.on('plotly_deselect', () => {
        console.debug('plotly_deselect')
        emit('plotly_deselect')
      })
      plotlyHTMLElement.on('plotly_doubleclick', () => {
        console.debug('plotly_doubleclick')
        emit('plotly_doubleclick')
      })
      plotlyHTMLElement.on('plotly_framework', () => {
        console.debug('plotly_framework')
        emit('plotly_framework')
      })
      plotlyHTMLElement.on('plotly_redraw', () => {
        console.debug('plotly_redraw')
        emit('plotly_redraw')
      })
      plotlyHTMLElement.on('plotly_transitioning', () => {
        console.debug('plotly_transitioning')
        emit('plotly_transitioning')
      })
      plotlyHTMLElement.on('plotly_transitioninterrupted', () => {
        console.debug('plotly_transitioninterrupted')
        emit('plotly_transitioninterrupted')
      })
    }
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
