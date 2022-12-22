<script setup lang="ts">
import { Line } from 'vue-chartjs'
import { computed, reactive, ref, watch } from 'vue'
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
import { generateRange, selectColor, getLengthDistribution, DataArray1D, apiDataComposable } from '../utils'
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

interface LengthDistributionData {
    min: number,
    max?: number,
    data: number[],
    experiment: string,
    totalReads: number
}

const props = defineProps<{ ids: number[], normalize: boolean }>()
const { apiData, min, max } = apiDataComposable<LengthDistributionData>(props.ids, getLengthDistribution)


const data = computed(() => ({
    labels: generateRange(min.value, max.value),
    datasets: Object.values(apiData).map((data, i) => ({
        label: data.experiment,
        data: (new DataArray1D(data.data, data.min))
            // normalize data if needed
            .scaleData(props.normalize ? 1_000 / data.totalReads : 1)
            .slicePad(min.value, max.value),
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
            ticks: {},
            title: { display: true, text: 'count' }
        },
        x: {
            ticks: {},
            title: { display: true, text: 'length' }

        }
    },
    plugins: {
        title: {
            display: true,
            text: 'Length Distribution'
        },
        // legend: { display: false },
        tooltips: { enabled: true },
    },
}

</script>


<template>
    <Line :chart-options="options" :chart-data="data" :height="240" v-if="Object.keys(apiData).length > 0"/>
    <Skeleton v-else style="height:240px;"/>
</template>