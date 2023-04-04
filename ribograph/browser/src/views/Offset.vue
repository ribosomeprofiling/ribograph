<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import LengthDistributionChart from '../components/LengthDistributionChart.vue'
import RegionCountsChart from '../components/RegionCountsChart.vue'
import CheckboxTooltip from '../components/CheckboxTooltip.vue'
import MetageneCounts from '../components/MetageneCounts.vue'

import { sliderLogic, getMetadata, sliderFormat } from '../utils'
import { setOffset, getOffsetComputed } from '../localStorageStore'

const props = defineProps<{
    experiment: number
}>()

const normalize = ref(false)
const { sliderPositionsRaw, sliderPositions } = sliderLogic()

const min = ref(15)
const max = ref(40)
const offsets = ref<number[] | null>(null)

getMetadata(props.experiment).then(x => {
    min.value = x.min
    max.value = x.max
    // these are the user inputted offsets for each gene length, default all to 0
    offsets.value = Array(max.value - min.value + 1).fill(0) // default to Array of 0s
})

onMounted(async () => {
    const savedOffsets = (await getOffsetComputed(props.experiment)).value
    if (savedOffsets) {
        offsets.value = savedOffsets
    }
})

//////////////////
// AUTOFOCUS
//////////////////

const autofocus = ref(true)
const focusPoint = ref<number | null>(null)
const sliderPositionTemp = ref([15, 40] as [number, number])

watch(focusPoint, (n) => {
    if (autofocus.value) { // if autofocus is on
        if (n != null) {
            const focusedLength = n + min.value
            // while user is focused, store the current positions in a temp variable
            // assume that if the silder positions are the same, it's an artifact of the autofocus
            // and not a user generated move
            if (sliderPositionTemp.value[0] !== sliderPositionTemp.value[1]) {
                sliderPositionTemp.value = sliderPositionsRaw.value
            }
            sliderPositionsRaw.value = [focusedLength, focusedLength]
        } else {
            // replace the current slider value with the previously stored temp value
            sliderPositionsRaw.value = sliderPositionTemp.value
        }
    }
})
</script>

<template>
    <div class=" mb-4 d-flex justify-content-start">
        <div class="align-self-center">
            <a class="btn btn-dark" :href="`/${experiment}/coverage`">
                View Coverage
            </a>
        </div>
        <div class="ms-4 me-auto align-self-center">
            <CheckboxTooltip v-model="autofocus"
                tooltip="Automatically adjust slider bounds based on focused offset element">
                Autofocus
            </CheckboxTooltip>
        </div>

        <div class="">
            <button class="btn btn-warning me-2" @click="offsets.fill(0)" title="Set offsets to 0">Reset</button>
            <button type="button" class="btn btn-success" title="Store offsets locally"
                @click="setOffset(offsets, experiment)">Save</button>
        </div>
    </div>

    <div class="my-5">
        <Slider v-model="sliderPositionsRaw" :min="min" :max="max" :lazy="false" :format="sliderFormat" />
    </div>

    <div class="row">
        <div class="col-md-auto" style="width:200px">
            <!-- The offset inputs -->
            <div class="form-group row mb-0" v-for="(x, i) in offsets" :key="'input' + i">
                <label :for="'offsetcontrol' + i" class="col-sm-1 col-form-label-sm p-0">{{ min + i }}</label>
                <div class="col">
                    <input type="number" v-model.number="offsets[i]" @focusin="focusPoint = i" @focusout="focusPoint = null"
                        class="form-control form-control-sm" :id="'offsetcontrol' + i">
                </div>
            </div>
        </div>
        <div class="col">
            <MetageneCounts :ids="[experiment]" :range="sliderPositions" type="start" :normalize="normalize"
                :offsets="offsets" />
            <MetageneCounts :ids="[experiment]" :range="sliderPositions" type="stop" :normalize="normalize"
                :offsets="offsets" />
        </div>
    </div>
</template>