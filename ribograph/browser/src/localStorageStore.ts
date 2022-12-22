// A reactive global Vue store that syncs with the js LocalStorage API
// Logic is in App.vue
import { ref, reactive, computed, nextTick, onMounted } from 'vue'
import { useToast, POSITION } from "vue-toastification";

const toast = useToast()

export const storage = reactive<Record<string, string>>({})

export async function getOffsetComputed(experiment: number) {
    await nextTick()
    return computed((): number[] | null => {
        const offsetString = storage[`offsets-${experiment}`]
        if (offsetString) {
            return offsetString.split(',').map(x => +x)
        }
        return null
    })
}

export function setOffset(offsets: number[], experiment: number) {
    storage[`offsets-${experiment}`] = offsets.toString()
    toast("Offset Saved", { position: POSITION.BOTTOM_RIGHT, });
}
