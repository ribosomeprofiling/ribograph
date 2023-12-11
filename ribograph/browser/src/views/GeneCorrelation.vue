<script setup lang="ts">
import { ref, onMounted, nextTick, computed, watch } from 'vue'
import { getGeneCorrelations, openGeneView } from '../utils'
import { useToast, POSITION } from "vue-toastification";
import type Plotly from '../plotly'

import PlotlyPlot from '../components/PlotlyPlot.vue';
import InfoBox from '../components/InfoBox.vue';
import { sliderLogic, sliderFormat } from '../utils'

const props = defineProps<{
    project: number,
    referenceHash: string
}>()

const correlations = ref<number[][]>([])
const geneCounts = ref<Record<string, Record<string, number>>>({}) // {experiment : {gene : frequency}}
const genome = ref<string>("")
const mode = ref(0)
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

const { sliderPositionsRaw, sliderPositions } = sliderLogic(1500)
// TODO make min and max real numbers from the backend
const min = ref(15)
const max = ref(40)
const correlationsLoading = ref(true)

const toast = useToast()
onMounted(async () => {
    await nextTick() // this is needed to wait for the notification system to load in
    initCorrelations()
})

function initCorrelations() {
    correlationsLoading.value = true
    const [range_lower, range_upper] = sliderPositions.value

    getGeneCorrelations(props.project, props.referenceHash, range_lower, range_upper, mode.value).then(data => {
        if (data) {
            min.value = data.min
            max.value = data.max

            geneCounts.value = data.geneCounts
            experiments.value = Object.keys(data.geneCounts)

            if (experiments.value.length < 2) {
                toast.error("Not enough experiments", {
                    position: POSITION.BOTTOM_RIGHT,
                })
                return
            }

            correlations.value = data.correlations
            // genome.value = data.genome

            // set default selected experiment 
            e1.value = experiments.value[0]
            e2.value = experiments.value[1]
        }
        correlationsLoading.value = false
    })
}

watch(sliderPositions, initCorrelations)
watch(mode, initCorrelations)

const boldExperiment = (experiment_aliases: string[], tgt: string) => {
    const boldIdx = experiment_aliases.findIndex(x => x === tgt)
    const LENGTH_THRESHOLD = 10
    const lineBrokenText = experiment_aliases.map(x => {
        if (x.length > LENGTH_THRESHOLD) {
            return x.slice(0, LENGTH_THRESHOLD) + "<br>" + x.slice(LENGTH_THRESHOLD)
        } else {
            return x
        }
    })

    lineBrokenText[boldIdx] = `<b>${lineBrokenText[boldIdx]}</b>`
    return lineBrokenText
}


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
    x = x as string
    y = y as string

    // x and y might be bolded, so we need to strip it out
    const boldMatcher = new RegExp("<b>(.*)<\/b>")
    const xmatch = boldMatcher.exec(x);
    const ymatch = boldMatcher.exec(y);
    if (xmatch) x = xmatch[1];
    if (ymatch) y = ymatch[1];

    // remove potential line breaks
    x = x.replace("<br>", "")
    y = y.replace("<br>", "")

    // set selected experiments
    e1.value = x
    e2.value = y
}

function scatterClick(data: Plotly.PlotMouseEvent) {
    const point = data.points[0] as Partial<Plotly.PlotDatum & { text: string }>
    const gene = point.text?.split("-")[0] // get the gene name from the point text

    if (gene && genome.value && data.event.button == 2) { // on right click only
        data.event.preventDefault()
        openGeneView(gene, genome.value)
    }
}

</script>

<template>
    <div class="form-group mt-3 mb-3">
        <label class="fs-5">Show Ribo/RNA-Seq</label>
        <div>
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="show_ribo_rna" id="ribo_only" value="0" v-model="mode">
                <label class="form-check-label" for="ribo_only">Ribo Only</label>
            </div>
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="show_ribo_rna" id="rna_seq_only" value="1" v-model="mode">
                <label class="form-check-label" for="rna_seq_only">RNA-Seq Only</label>
            </div>
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="show_ribo_rna" id="both" value="2" v-model="mode">
                <label class="form-check-label" for="both">Ribo and RNA-Seq</label>
            </div>
        </div>
    </div>


    <div class="form-group mt-3 mb-3">
        <label class="fs-5">UCSC Genome DB Lookup</label>
        <div>
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="genome" id="hg38" value="hg38" v-model="genome">
                <label class="form-check-label" for="hg38">hg38 (Homo sapiens)</label>
            </div>
            <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" name="genome" id="mm10" value="mm10" v-model="genome">
                <label class="form-check-label" for="mm10">mm10 (Mus musculus)</label>
            </div>
        </div>
    </div>

    <div class="row" :class="{ opacity30: correlationsLoading }">
        <div class="col-xl-6 m-0 p-0">
            <PlotlyPlot :datasets="[scatterData]" :options="scatterOptions" @plotly_click="scatterClick($event)"
                style="width:100%;height:600px;" />
        </div>
        <div class="col-xl-6 m-0 p-0">
            <PlotlyPlot :datasets="[heatmapData]" :options="heatmapOptions" @plotly_click="heatmapClick($event)"
                style="width:100%;height:600px;" />
        </div>
    </div>

    <div class="my-5" v-show="max > min">
        <Slider v-model="sliderPositionsRaw" :min="min" :max="max" :lazy="false" :format="sliderFormat"
            :disabled="correlationsLoading" />
    </div>

    <InfoBox class="mt-3">
        <ul>
            <li>On the right is a heatmap of the Spearman correlation between every pair of compatible experiments in this
                project.
                On the left is a scatterplot between two experiments comparing the number of reads for each gene.</li>
            <li>If there are multiple sets of compatible experiments, a 'Reference Group' toggle will appear to switch
                between them.</li>
            <li>Scroll to zoom or drag to pan in either the heatmap or the scatterplot.</li>
            <li>By clicking a cell in the heatmap, the corresponding two experiments will be shown in the scatterplot.</li>
            <li>Right clicking a gene point in the scatterplot will open up the gene in the UCSC genome browser. Select
                either
                the hg38 or the mm10 database at the top to enable this functionality.</li>
            <li>Underneath the heatmap is a slider to filter read lengths. While new data is loading, the read length slider
                is disabled.</li>
        </ul>
    </InfoBox>
</template>

<style scoped>
.opacity30 {
    opacity: 0.3
}
</style>