import { useToast, POSITION } from "vue-toastification";
import Axios from 'axios'
import { ref, watch, onMounted, nextTick, reactive, computed } from "vue";
import { setupCache } from 'axios-cache-interceptor';
import { throttle, isEqual } from 'lodash'

const axios = setupCache(Axios);
const toast = useToast()
const BASE_URL = process.env.NODE_ENV === "development" ? "http://localhost:8000" : ""

// https://stackoverflow.com/questions/43725419/converting-nucleotides-to-amino-acids-using-javascript
const aminoDict: Record<string, string[]> = { 'A': ['GCA', 'GCC', 'GCG', 'GCT'], 'C': ['TGC', 'TGT'], 'D': ['GAC', 'GAT'], 'E': ['GAA', 'GAG'], 'F': ['TTC', 'TTT'], 'G': ['GGA', 'GGC', 'GGG', 'GGT'], 'H': ['CAC', 'CAT'], 'I': ['ATA', 'ATC', 'ATT'], 'K': ['AAA', 'AAG'], 'L': ['CTA', 'CTC', 'CTG', 'CTT', 'TTA', 'TTG'], 'M': ['ATG'], 'N': ['AAC', 'AAT'], 'P': ['CCA', 'CCC', 'CCG', 'CCT'], 'Q': ['CAA', 'CAG'], 'R': ['AGA', 'AGG', 'CGA', 'CGC', 'CGG', 'CGT'], 'S': ['AGC', 'AGT', 'TCA', 'TCC', 'TCG', 'TCT'], 'T': ['ACA', 'ACC', 'ACG', 'ACT'], 'V': ['GTA', 'GTC', 'GTG', 'GTT'], 'W': ['TGG'], 'Y': ['TAC', 'TAT'] };

// codon dictionary derived from aminoDict
export const CODON_DICT: Record<string, string> =
    Object.keys(aminoDict).reduce((dict, a) =>
        Object.assign(dict, ...aminoDict[a].map(c => ({ [c]: a }))), {})

////////////////////////
//// API INTERFACES
////////////////////////

/**
 * A general function that can be used to get data from an arbitrary api endpoint
 * 
 * @param message text to show on the the loading message toast
 * @param endpoint the relative endpoint to fetch
 */
async function handleAPICall(message: string, endpoint: string) {
    await nextTick() // this is needed to wait for the notification system to load in

    let data = null

    // create the loading notification toast
    const loadingNotification = toast(message, {
        timeout: false, position: POSITION.BOTTOM_RIGHT,
    });

    try {
        data = (await axios.get(BASE_URL + endpoint, { withCredentials: true })).data // the actual data fetch
    } catch (error) {
        // create an error message, defaulting to 'Unknown Error' if the error 
        // doesn't have an inbuilt message
        const errorMessage = error instanceof Error ? error.message : 'Unknown Error'
        toast.error(errorMessage, {
            position: POSITION.BOTTOM_RIGHT,
        })
    }

    // hide the loading notification toast
    toast.dismiss(loadingNotification)
    return data
}

export const getMetadata = (experiment_id: number) => (
    handleAPICall(`Loading Metadata`,
        `/api/experiment/${experiment_id}/getMetadata`))

export const getRegionPercentages = (experiment_id: number) => (
    handleAPICall(`Loading Region Percentages`,
        `/api/experiment/${experiment_id}/getRegionPercentages`))

export const getLengthDistribution = (experiment_id: number) => (
    handleAPICall(`Loading Length Distribution`,
        `/api/experiment/${experiment_id}/getLengthDistribution`))

export const getMetageneCounts = (experiment_id: number, site: 'start' | 'stop') => (
    handleAPICall(`Loading ${site[0].toUpperCase() + site.slice(1)} Site Metagene Counts`,
        `/api/experiment/${experiment_id}/getMetageneCounts?site=${site}`))

export const getGeneList = (experiment_id: number) => (
    handleAPICall(`Loading Gene List`,
        `/api/experiment/${experiment_id}/listGenes`))

export const getCoverageData = (experiment_id: number, gene: string) => (
    handleAPICall(`Loading ${gene} for experiment ${experiment_id}`,
        `/api/experiment/${experiment_id}/getCoverage?gene=${gene}`)
)

export const getExperimentList = (experiment_id: number) => (
    handleAPICall(`Loading experiment list`,
        `/api/experiment/${experiment_id}/listExperiments`)
)

export const getGeneCorrelations = (project_id: number, referenceHash: string, range_lower: number, range_upper: number) => (
    handleAPICall(`Loading gene correlations`,
        `/api/project/${project_id}/getGeneCorrelations?referenceHash=${referenceHash}&range_lower=${range_lower}&range_upper=${range_upper}`)
)
/////////////////////////
/// CHART UTILITIES
/////////////////////////

// generate an array of ints from [start, stop)
export const generateRange = (start: number, stop: number): Array<number> => Array(stop - start).fill(start).map((x, y) => x + y)

const COLORS = [
    "#003f5c",
    "#ffa600",
    "#2f4b7c",
    "#ff7c43",
    "#665191",
    "#f95d6a",
    "#a05195",
    "#d45087",
]

export const selectColor = (i: number): string => COLORS[i % COLORS.length]

// multiply each data point by a constant
export const scaleData = (data: Array<number>, scaleFactor: number): Array<number> => data.map(x => x * scaleFactor)

// get an array of counts as an array of percentages
export function getAsPercentages(data: Array<number>): Array<number> {
    const total = data.reduce((a, b) => a + b, 0)
    return scaleData(data, 100 / total)
}

export function openGeneView(gene: string, genome?: string): void {
    gene = gene.split("-")[0]
    const genomeName = genome || (new URL(window.location.href).searchParams.get("genome"))
    if (genomeName) {
        window.open(
            `https://genome.ucsc.edu/cgi-bin/hgGene?hgg_gene=${gene}&db=${genomeName}`
            , '_blank');
    }
}

export function openCoverageView(experiment_id: number) {
    window.open(`/${experiment_id}/coverage`, "_self")
}

export const sliderFormat = { 'suffix': 'nt' }


/////////////////////////////
//// DATA ARRAY CLASSES
////////////////////////////

/**
 * The following classes are designed to simplify data processing by abstracting away
 * the fact that data in an array is often a representation of gene data at some offset.
 * For example, coverage data might be from gene lengths of [15, 40], but the array is indexed
 * by [0, 25]. These classes store the array internally, and xalling .slice() on this classes will 
 * automatically compute the offset .
 */


// a class to wrap around an array to query it at a given offset
abstract class DataArray<T> {
    array: Array<T>
    offset: number

    constructor(data: Array<T>, min: number) {
        this.array = data
        this.offset = min
    }

    /**
     * map start and stop to indices in the actual array
     * for example, [15:40] is mapped onto [0:25]
     */
    slice(start: number, stop: number): Array<T> {
        return DataArray.slice(this.array, this.offset, start, stop)
    }

    protected static slice(array: Array<any>, offset: number, start: number, stop: number): Array<any> {
        const startPos = start - offset;
        const stopPos = stop - offset + 1 // inclusive stop position

        const slice = array.slice(
            Math.max(startPos, 0), // cap min value at the start of the array, 0
            Math.max(Math.min(stopPos, array.length), 0) // cap max index at the length of the array
        )

        return slice
    }

    // a helper function to collapse a list of arrays into one summed array
    static sumArrays(arrays: Array<Array<number>>): Array<number> {
        const n = arrays.reduce((max, xs) => Math.max(max, xs.length), 0);
        const result = Array.from({ length: n });
        return result.map((_, i) => arrays.map(xs => xs[i] || 0).reduce((sum, x) => sum + x, 0));
    }

    /**
     * Shifts an array arr over by num spaces
     * Pads to the left or right with 0s
     */
    static shiftArray(arr: Array<any>, offset: number) {
        if (offset > 0) {
            const offsetSlice = arr.slice(0, Math.max(0, arr.length - offset)) // slice from begining to end - offset
            return [
                ...Array(arr.length - offsetSlice.length).fill(0), // add padding before
                ...offsetSlice
            ]
        } else {
            const offsetSlice = arr.slice(-offset) // slice from -num to end
            return [
                ...offsetSlice,
                ...Array(arr.length - offsetSlice.length).fill(0), // add padding after
            ]
        }
    }
}

export class DataArray1D extends DataArray<number> {

    constructor(data: Array<number>, min: number) {
        super(data, min)
    }

    /**
     * Slices the offset array from [start, stop] inclusive, and adds padding 0s
     * for where the array isn't defined
     */
    slicePad(start: number, stop: number): Array<number> {
        const slice = this.slice(start, stop)

        const startPad = Math.max(this.offset - start, 0);
        const endPad = Math.max(stop - this.offset - this.array.length + 1, 0)

        return [
            ...Array(startPad).fill(0),
            ...slice,
            ...Array(endPad).fill(0)
        ]
    }

    /**
     * Returns a new DataArray1D which is scaled by the given scale factor
     */
    scaleData(scaleFactor: number): DataArray1D {
        return new DataArray1D(scaleData(this.array, scaleFactor), this.offset)
    }
}


export class DataArray2D extends DataArray<Array<number>>{

    constructor(data: Array<Array<number>>, min: number) {
        super(data, min)
    }

    /**
     * Sum across an offset slice of the array.
     * Because we're summing the array at the same time, 0 padding 
     * isn't neccessary until after summation.
     */
    sliceSum(start: number, stop: number, offsets?: number[] | null): number[] {

        let slice: number[][] | null = null
        if (offsets) {
            if (this.array.length !== offsets.length) {
                throw new Error("Invalid offsets provided")
            } else {
                // offset x by a certain amount left or right and pad with 0s
                const offsetData = this.array.map((x, i) => DataArray.shiftArray(x, offsets[i]))
                slice = DataArray.slice(offsetData, this.offset, start, stop)
            }
        } else {
            slice = this.slice(start, stop)
        }

        return DataArray.sumArrays(slice)
    }
}


////////////////////////////
///// COMPOSABLES
///////////////////////////

// these are some pieces of shared logic between different components

/**
 * Returns sliderPositionsRaw, which can be directly connected to a vue-slider component,
 * and sliderPositions, a debounced version that can be hooked up to data intensive computed properties
 */
export function sliderLogic(throttleDuration = 2000) {
    // TODO don't hardcode slider min and max
    const sliderPositionsRaw = ref([15, 40] as [number, number]) // slider positions as a tuple
    const sliderPositions = ref(sliderPositionsRaw.value)

    watch(sliderPositionsRaw, throttle((val) => {
        sliderPositions.value = val
    }, throttleDuration, { leading: false }))

    return { sliderPositionsRaw, sliderPositions }
}

interface ApiDataType {
    min: number,
    data: any[]
}

export function apiDataComposable<Type extends ApiDataType>(ids: number[], apiFetchFn: (id: number) => Promise<any>) {
    const apiData = reactive<Record<number, Type>>({})

    // make api request for each of the ids passed in to the component
    const fetchData = () => ids.map(id => apiFetchFn(id).then(data => apiData[id] = data))

    // fetch once on init, and refetch every time ids change
    fetchData()
    watch(() => ids, (newVal, oldVal) => {
        if (!isEqual(newVal, oldVal)) {
            fetchData()
        }
    })

    // min and max are computed to the minimum and maximum across all experiments
    const min = computed(() => (Object.values(apiData).length > 0 ?
        Math.min(...Object.values(apiData).map((x: Type) => x.min)) : 25))

    const max = computed(() => (Object.values(apiData).length > 0 ?
        Math.max(...Object.values(apiData).map((x: Type) => x.data.length + x.min)) : 35))

    return { apiData, min, max }
}