<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { getGeneCorrelations, openGeneView } from '../utils'
import { useToast, POSITION } from "vue-toastification";
import type Plotly from '../plotly'

import PlotlyPlot from '../components/PlotlyPlot.vue';

const props = defineProps<{
    project: number
}>()

const correlations = ref<number[][]>([])
const geneCounts = ref<Record<string, Record<string, number>>>({}) // {experiment : {gene : frequency}}
const genome = ref<string>("")
const experiments = ref<string[]>([])

// selected experiments
const e1 = ref<string>("")
const e2 = ref<string>("")

const e1GeneData = computed(() => geneCounts.value[e1.value])
const e2GeneData = computed(() => geneCounts.value[e2.value])
const rho = computed(() => (
    experiments.value.length >= 2 ?
        correlations.value
        [experiments.value.findIndex(x => x === e1.value)] // index of the first selected experiment
        [experiments.value.findIndex(x => x === e2.value)] // index of the second selected experiment
        : 0 // default to 0
))

const toast = useToast()
onMounted(async () => {
    await nextTick() // this is needed to wait for the notification system to load in
    getGeneCorrelations(props.project).then(data => {
        if (data) {
            geneCounts.value = data.geneCounts
            experiments.value = Object.keys(data.geneCounts)

            if (experiments.value.length < 2) {
                toast.error("Not enough experiments", {
                    position: POSITION.BOTTOM_RIGHT,
                })
                return
            }

            correlations.value = data.correlations
            genome.value = data.genome

            // set default selected experiment 
            e1.value = experiments.value[0]
            e2.value = experiments.value[1]
        }
    })
})

const boldExperiment = (experiment_aliases: string[], tgt: string) => (
    experiment_aliases.map(x => x == tgt ? `<b>${x}</b>` : x))


const heatmapData = computed(() => ({
    type: 'heatmap' as Plotly.PlotType,
    hoverongaps: false,
    colorscale: 'Viridis',
    zmin: Math.min(...correlations.value.flat(2)),
    zmax: 1,
    z: correlations.value,
    x: boldExperiment(experiments.value, e1.value),
    y: boldExperiment(experiments.value, e2.value)
}))


const heatmapOptions = {
    title: "Pairwise Spearman correlation coefficients of read counts",
    yaxis: {
        tickangle: -45
    },
    xaxis: {
        tickangle: -45
    },
    dragmode: 'pan' as 'pan',
}


const scatterOptions = computed(() => ({
    xaxis: {
        type: 'log' as Plotly.AxisType,
        autorange: true,
        title: e1.value
    },
    yaxis: {
        type: 'log' as Plotly.AxisType,
        autorange: true,
        title: e2.value
    },
    dragmode: 'pan' as 'pan',
    title: 'Pairwise correlation of gene-level ribosome occupancy' + (rho ? ` (ρ=${rho.value.toFixed(2)})` : ""),
    // margin: { t: 0, b: 100, l: 100, r: 100 },
}))

const scatterData = computed(() => ({
    x: Object.values(e1GeneData.value || {}),
    y: Object.values(e2GeneData.value || {}),
    mode: 'markers' as 'markers',
    type: 'scattergl' as Plotly.PlotType, // scattergl has increased performance!
    text: Object.keys(e1GeneData.value || {}),
    marker: {
        size: 4,
        opacity: 0.15,
    }
}))


function heatmapClick(data: Plotly.PlotMouseEvent) {
    let { x, y } = data.points[0]

    // x and y might be bolded, so we need to strip it out
    const boldMatcher = new RegExp("<b>(.*)<\/b>")
    const xmatch = boldMatcher.exec(x as string);
    const ymatch = boldMatcher.exec(y as string);
    if (xmatch) x = xmatch[1];
    if (ymatch) y = ymatch[1];

    // set selected experiments
    e1.value = x as string
    e2.value = y as string
}

function scatterClick(data: Plotly.PlotMouseEvent) {
    const point = data.points[0] as Partial<Plotly.PlotDatum & { text: string }>
    const gene = point.text?.split("-")[0] // get the gene name from the point text

    if (gene && data.event.button == 2) { // on right click only
        openGeneView(gene, genome.value)
    }
}

</script>

<template>

    <div class="row">
        <div class="col-xl-6 m-0 p-0">
            <PlotlyPlot :datasets="[scatterData]" :options="scatterOptions" @plotly_click="scatterClick($event)"
                style="width:100%;height:600px;" />
        </div>
        <div class="col-xl-6 m-0 p-0">
            <PlotlyPlot :datasets="[heatmapData]" :options="heatmapOptions" @plotly_click="heatmapClick($event)"
                style="width:100%;height:600px;" />
        </div>
    </div>

</template>