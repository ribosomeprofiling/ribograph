<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import CoveragePlot from '../components/CoveragePlot.vue'
import { getGeneList, openGeneView, getExperimentList, openCoverageView } from '../utils'
import SearchableList from '../components/SearchableList.vue';
import CheckboxTooltip from '../components/CheckboxTooltip.vue';
import InfoBox from '../components/InfoBox.vue';

const props = defineProps<{
    experiment: number
}>()

const useOffsets = ref(false)
const normalize = ref(false)
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
    subtitle: geneList.value[gene].toLocaleString('en-US') + " reads"
})))

const experimentSearchListData = computed(() => experimentList.value.map(x => ({
    id: x.id.toString(),
    title: x.name,
    subtitle: x.project
})))

const genome = ref("")

</script>

<template>
    <div class="d-flex flex-wrap">
        <a class="btn btn-secondary" :href="`/${experiment}/offset`">
            Edit Offsets
        </a>

        <CheckboxTooltip class="ms-4 align-self-center" v-model="useOffsets" tooltip="Use offsets for P site correction">
            Use Offsets
        </CheckboxTooltip>

        <CheckboxTooltip class="me-auto ms-4 align-self-center" v-model="normalize"
            tooltip="Normalize values for each experiment to per 1,000 total reads">
            Normalize counts
        </CheckboxTooltip>

        <div class="d-flex">
            <div class="form-check ms-4 align-self-center">
                <input class="form-check-input" type="radio" name="genome" id="hg38" value="hg38" v-model="genome">
                <label class="form-check-label" for="hg38">
                    <abbr title="use UCSC Genome Browser hg38 database">hg38 (Homo sapiens)</abbr>
                </label>
            </div>
            <div class="form-check ms-4 align-self-center">
                <input class="form-check-input" type="radio" name="genome" id="mm10" value="mm10" v-model="genome">
                <label class="form-check-label" for="mm10">
                    <abbr title="use UCSC Genome Browser mm10 database">mm10 (Mus musculus)</abbr>
                </label>
            </div>
        </div>

    </div>

    <div class="row">
        <div class="col-12">
            <CoveragePlot :gene="gene || ''" :ids="experiment ? [...experiments].map(x => parseInt(x)) : []"
                :useOffsets="useOffsets" :normalize="normalize" />
        </div>
    </div>

    <div class="row">
        <div class="col-6">
            <SearchableList :data="geneSearchListData" v-model:selected="gene" search-placeholder="Search for a gene"
                @secondarySelect="openGeneView($event.title, genome)" />
        </div>

        <div class="col-6">
            <SearchableList :data="experimentSearchListData" v-model:selected="experiments"
                search-placeholder="Search for an experiment" :max-selected="5"
                @secondary-select="openCoverageView($event.id)" />
        </div>
    </div>

    <InfoBox class="mt-3">
        The coverage view shows the distribution of the reads of a gene for one or more experiments.

        <ul>
            <li>Scroll to zoom into and drag to pan the coverage plot.</li>
            <li>Select a gene in the left menu to display its coverage for this experiment. Right click a gene to open its
                entry in the UCSC genome browser. Select
                either the hg38 or the mm10 database at the top to enable this functionality.</li>
            <li>Select more experiments to compare with the current one in the menu to the right. Right click an experiment to switch to
                its coverage page.
            </li>
            <li>To display nucleotide level information alongside the coverage data, including amino acid labels on hover, 
                an appropriate reference must be provided. For performance reasons, a full track labeling each
                nucleotide is only available when zoomed in sufficiently.
            </li>
            <li>To apply P-site correction, edit the offsets by clicking 'Edit Offsets' and save them. Then, 
                toggling 'Use offsets' will apply them to the coverage plot.
            </li>

        </ul>
    </InfoBox>
</template>