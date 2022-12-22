<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import CoveragePlot from '../components/CoveragePlot.vue'
import { getGeneList, openGeneView, getCoverageData, sliderLogic, getExperimentList, openCoverageView } from '../utils'
import SearchableList from '../components/SearchableList.vue';
import CheckboxTooltip from '../components/CheckboxTooltip.vue';

const props = defineProps<{
    experiment: number
}>()

const useOffsets = ref(false)
const geneList = ref<Record<string, number>>({})
getGeneList(props.experiment).then(data => geneList.value = data.genes)

const experimentList = ref<{ id: number, name: string, project: string }[]>([])
getExperimentList(props.experiment).then(data => experimentList.value = data.experiments)

const url = new URL(window.location.href)
const gene = ref<string | null>(url.searchParams.get("gene"))
const experiments = ref<Set<string>>(new Set([props.experiment.toString()]))

watch(gene, (newGene) => {
    if (newGene) {
        url.searchParams.set("gene", newGene)
    } else {
        url.searchParams.delete("gene")
    }
    experiments.value.clear()
    experiments.value.add(props.experiment.toString())
    window.history.replaceState({}, '', url);
})

const geneSearchListData = computed(() => Object.keys(geneList.value).map(gene => ({
    id: gene,
    title: gene,
    subtitle: geneList.value[gene].toString()
})))

const experimentSearchListData = computed(() => experimentList.value.map(x => ({
    id: x.id.toString(),
    title: x.name,
    subtitle: x.project
})))

</script>

<template>

    <div class="d-flex">
        <a class="btn btn-secondary" :href="`/${experiment}/offset`">
            Edit Offsets
        </a>

        <CheckboxTooltip class="ms-4 align-self-center" v-model="useOffsets"
            tooltip="Use offsets for P site correction">
            Use Offsets
        </CheckboxTooltip>
    </div>

    <div class="row">
        <div class="col-12">
            <CoveragePlot :gene="gene || ''" :ids="experiment ? [...experiments].map(x => parseInt(x)) : []"
             :useOffsets="useOffsets"/>
        </div>
    </div>

    <div class="row">
        <div class="col-6">
            <SearchableList :data="geneSearchListData" v-model:selected="gene" search-placeholder="Search for a gene"
                @secondarySelect="openGeneView($event.title)" />
        </div>

        <div class="col-6">
            <SearchableList :data="experimentSearchListData" v-model:selected="experiments"
                search-placeholder="Search for an experiment" :max-selected="5"
                @secondary-select="openCoverageView($event.id)" />
        </div>
    </div>
</template>