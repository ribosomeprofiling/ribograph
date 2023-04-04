<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import LengthDistributionChart from '../components/LengthDistributionChart.vue'
import RegionCountsChart from '../components/RegionCountsChart.vue'
import CheckboxTooltip from '../components/CheckboxTooltip.vue'
import MetageneCounts from '../components/MetageneCounts.vue'

import { sliderLogic, getMetadata, sliderFormat } from '../utils'

const props = defineProps<{
    experiment: number
}>()

const normalize = ref(false)
const { sliderPositionsRaw, sliderPositions } = sliderLogic()

const min = ref(15)
const max = ref(40)
getMetadata(props.experiment).then(x => {
    min.value = x.min
    max.value = x.max
})

</script>

<template>
    <CheckboxTooltip v-model="normalize" tooltip="Counts per 1,000 total reads (on each experiment)">
        Normalize counts
    </CheckboxTooltip>

    <LengthDistributionChart :ids="[experiment]" :normalize="normalize" />

    <div class="mt-5 mb-4">
        <Slider v-model="sliderPositionsRaw" :min="min" :max="max" :lazy="false" :format="sliderFormat" />
    </div>

    <RegionCountsChart :ids="[experiment]" :range="sliderPositions" />
    <MetageneCounts :ids="[experiment]" :range="sliderPositions" type="start" :normalize="normalize" />
    <MetageneCounts :ids="[experiment]" :range="sliderPositions" type="stop" :normalize="normalize" />
</template>
