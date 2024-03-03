<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import Plotly from '../plotly'

const props = defineProps<{
    datasets: Partial<Plotly.PlotData>[],
    options: Partial<Plotly.Layout>
}>()
const emit = defineEmits(['plotly_click', 'plotly_relayout'])

const plot = ref<Plotly.PlotlyHTMLElement | null>(null);

onMounted(() => {
    if (plot.value) {
        Plotly.newPlot(plot.value, props.datasets, props.options, {
            responsive: true, scrollZoom: true, displaylogo: false, modeBarButtonsToRemove: ['select2d', 'lasso2d']
        });

        plot.value.on('plotly_click', e => emit('plotly_click', e))
        plot.value.on('plotly_relayout', e => emit('plotly_relayout', e))
    }
})

watch(props, ({ datasets, options }) => {
    if (plot.value) {
        Plotly.react(plot.value, datasets, options);
    }
})

</script>


<template>
    <div ref="plot"></div>
</template>