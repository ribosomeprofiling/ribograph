<script setup lang="ts">
import { ref, onMounted, nextTick, watch, computed } from 'vue'
import LengthDistributionChart from '../components/LengthDistributionChart.vue'
import RegionCountsChart from '../components/RegionCountsChart.vue'
import CheckboxTooltip from '../components/CheckboxTooltip.vue'
import MetageneCounts from '../components/MetageneCounts.vue'
import InfoBox from '../components/InfoBox.vue'

import { sliderLogic, getMetadata, sliderFormat, getMetageneCounts, apiDataComposable } from '../utils'
import { setOffset, getOffsetComputed } from '../localStorageStore'

const props = defineProps<{
    experiment: number
}>()

const normalize = ref(false)
const { sliderPositionsRaw, sliderPositions } = sliderLogic(500)

const min = ref(15)
const max = ref(40)
const offsets = ref<number[]>([])

onMounted(async () => {
    const savedOffsets = (await getOffsetComputed(props.experiment)).value
    getMetadata(props.experiment).then(x => {
        min.value = x.min
        max.value = x.max
    }).then(() => {
        if (savedOffsets) {
            offsets.value = savedOffsets
        } else {
            // these are the user inputted offsets for each gene length, default all to 0
            offsets.value = Array(max.value - min.value + 1).fill(0) // default to Array of 0s
        }
    })
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

//////////////////
//// AUTO-INITTIALIZE
//////////////////

interface MetageneCountsData {
    index: number[],
    columns: number[],
    data: number[][],
    experiment: string,
    min: number,
    totalReads: number
}

const { apiData } = apiDataComposable<MetageneCountsData>([props.experiment], (id) => getMetageneCounts(id, "start"))

const minPosition = computed(() => (Object.values(apiData).length > 0 ?
    Math.min(...Object.values(apiData).map(x => x.columns[0])) : -50))

const searchBounds = [-18, -6]

const autoInitializedValues = computed(() => {
    const x = apiData[props.experiment]
    if (!x) return []
    return x.data.map(x => {
        const possibleOffsets = x.slice(searchBounds[0] - minPosition.value, searchBounds[1] - minPosition.value)
        const i = possibleOffsets.indexOf(Math.max(...possibleOffsets));
        return -searchBounds[0] - i
    })
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
            <button class="btn btn-danger me-2" @click="offsets = [...autoInitializedValues]"
                v-if="apiData[props.experiment]" title="Auto Initialize offset values">Auto-Init</button>
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
            <p class="mb-0"><b>Adjust Offsets</b></p>
            <p class="mb-1 col-form-label-sm"><i>(per read length)</i></p>

            <div class="form-group row mb-0" v-for="(x, i) in offsets" :key="'input' + i">
                <label :for="'offsetcontrol' + i" class="col-sm-2 col-form-label-sm">{{ min + i }}nt</label>
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
            <InfoBox class="mt-3">
                The offset page allows you to apply P-site correction to an experiment's coverage plot.

                <ul>
                    <li>With autofocus on, when editing an offset value for a certain read length, only the data for that
                        read length will display on the start and stop site plots.</li>
                    <li>'Auto-Init' can automatically determine reasonable offset values by taking the peak of the
                        start site plot from [-18, -6] and aligning it to 0. Note that this will overwrite current
                        selections.
                    </li>
                    <li>'Reset' will initialize all offsets to 0, overwriting current selections.</li>
                    <li>After editing the offsets, including when auto-initializing, <b>you must save for your changes to
                            take effect</b>.
                    </li>

                </ul>
            </InfoBox>
        </div>
    </div>
</template>