
<script setup lang="ts">
import { Bar } from 'vue-chartjs'
import { computed } from 'vue'
import {
    Chart,
    LinearScale,
    CategoryScale,
    BarElement,
    Legend,
    Title,
    Tooltip
} from 'chart.js';
import { getRegionPercentages, apiDataComposable, DataArray2D, getAsPercentages } from '../utils';
import Skeleton from '../components/Skeleton.vue'

Chart.register(
    LinearScale,
    CategoryScale,
    BarElement,
    Legend,
    Title,
    Tooltip,
)

const props = defineProps<{
    ids: number[],
    range: [number, number],
}>()

interface RegionCountsData {
    index: number[],
    columns: [string, string, string],
    data: [number, number, number][],
    experiment: string,
    min: number
}
const { min, max, apiData } = apiDataComposable<RegionCountsData>(props.ids, getRegionPercentages)

const dataArr = computed(() => Object.values(apiData).map(x => new DataArray2D(x.data, x.min)))
const summed = computed(() => dataArr.value.map(x => getAsPercentages(x.sliceSum(...props.range))))

const data = computed(() => ({
    labels: Object.values(apiData).map(x => x.experiment),
    datasets: [{
        axis: 'y',
        label: '5\' UTR %',
        data: summed.value.map(x => x[0]),
        fill: false,
        backgroundColor: 'rgba(42, 64, 189, 0.5)',
        borderColor: 'rgb(42, 64, 189)',
        borderWidth: 1
    },
    {
        axis: 'y',
        label: 'CDS %',
        data: summed.value.map(x => x[1]),
        fill: false,
        backgroundColor: 'rgba(191, 87, 0, 0.5)',
        borderColor: 'rgb(191, 87, 0)',
        borderWidth: 1
    },
    {
        axis: 'y',
        label: '3\' UTR %',
        data: summed.value.map(x => x[2]),
        fill: false,
        backgroundColor: 'rgba(19, 120, 64, 0.5)',
        borderColor: 'rgb(19, 120, 64)',
        borderWidth: 1
    }]
}));

const options = {
    maintainAspectRatio: false,
    indexAxis: 'y' as ('x' | 'y' | undefined),
    scales: {
        x: {
            stacked: true,
            max: 100,
            // type: 'linear'
        },
        y: {
            stacked: true,
            max: 100,
            // type: 'category'
        }
    },
    plugins: {
        title: {
            display: true,
            text: 'RPF Distribution on Regions'
        },
        legend: { display: true },
        tooltips: { enabled: true },
    },
}

</script>

<template>
    <Bar :chart-options="options" :chart-data="data" :height="200" v-if="Object.keys(apiData).length > 0" />
    <Skeleton v-else style="height:200px;" />
</template>