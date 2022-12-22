<script setup lang="ts">
import { Line } from 'vue-chartjs'
import { computed } from 'vue'
import {
    Chart,
    LinearScale,
    CategoryScale,
    BarElement,
    Legend,
    Title,
    Tooltip,
    PointElement,
    LineElement,
} from 'chart.js';
import { DataArray1D, generateRange, selectColor } from '../utils'
import { getMetageneCounts, apiDataComposable, DataArray2D } from '../utils';
import Skeleton from '../components/Skeleton.vue'

Chart.register(
    LinearScale,
    CategoryScale,
    BarElement,
    Legend,
    Title,
    Tooltip,
    PointElement,
    LineElement
)

const props = defineProps<{
    ids: number[],
    range: [number, number],
    type: 'start' | 'stop',
    normalize: boolean,
    offsets?: number[]
}>()


interface MetageneCountsData {
    index: number[],
    columns: number[],
    data: number[][],
    experiment: string,
    min: number,
    totalReads: number
}

const { apiData } = apiDataComposable<MetageneCountsData>(props.ids, (id) => getMetageneCounts(id, props.type))

const minPosition = computed(() => (Object.values(apiData).length > 0 ?
    Math.min(...Object.values(apiData).map(x => x.columns[0])) : -50))

const maxPosition = computed(() => (Object.values(apiData).length > 0 ?
    Math.max(...Object.values(apiData).map(x => x.columns[x.columns.length - 1])) : 50))

const data = computed(() => ({
    labels: generateRange(minPosition.value, maxPosition.value + 1),
    datasets: Object.values(apiData).map((x, i) => ({
        label: x.experiment,
        data: (new DataArray1D(
            (new DataArray2D(x.data, x.min))
                // sliceSum the data by the slider values
                .sliceSum(...props.range, props.offsets), x.columns[0])
            // normalize data if needed
            .scaleData(props.normalize ? 1_000 / x.totalReads : 1)
            // crop the data array to the computed min and max positions
            .slicePad(minPosition.value, maxPosition.value)),
        fill: false,
        borderColor: selectColor(i),
        tension: 0
    })) as Array<any>
}))


const options = {
    maintainAspectRatio: false,
    scales: {
        y: {
            beginAtZero: true,
            title: { display: true, text: 'count' }
        },
        x: {
            ticks: {},
            title: { display: true, text: 'position' }

        }
    },
    plugins: {
        title: {
            display: true,
            text: `${props.type == 'start' ? "Start" : "Stop"} Site Metagene`
        },
        // legend: { display: false },
        tooltips: { enabled: true },
    },
    elements: {
        point: {
            radius: 2
        }
    },
}

</script>

<template>
    <Line :chart-options="options" :chart-data="data" :height="240" v-if="Object.keys(apiData).length > 0" />
    <Skeleton v-else style="height:240px;"/>
</template>