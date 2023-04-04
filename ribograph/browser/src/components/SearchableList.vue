
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useToast, POSITION } from 'vue-toastification'

const toast = useToast()
const emit = defineEmits(['update:selected', 'secondarySelect'])

interface SearchListData {
    id: string, // this can be the same as title, but needs to be unique
    title: string,
    subtitle?: string
}

const props = defineProps<{
    searchPlaceholder?: string,
    selected?: Set<string> | string | null, // multi select or single select
    maxSelected?: number,
    data: SearchListData[]
}>()

const search = ref("")

// if the user has searched for something, show the filtered list
// otherwise show all data
const filteredData = computed(() => {
    const val = search.value.toLowerCase()
    return val ? props.data.filter(x => x.title.toLowerCase().includes(val)) : props.data
})

const selected = computed<Set<string> | string>({
    get() {
        return props.selected || ""
    },
    set(value) {
        emit('update:selected', value)
    }
})

// automatically allow for multiselect if selected.value is a Set
function isSelected(id: string) {
    if (typeof selected.value === "string") {
        return selected.value === id
    } else {
        return selected.value.has(id)
    }
}

function selectOrUnselect(id: string) {
    if (isSelected(id)) {
        if (typeof selected.value === "string") {
            selected.value = new Set()
        } else {
            selected.value.delete(id)
        }
    } else {
        select(id)
    }
}

function select(id: string) {
    if (typeof selected.value === "string") {
        selected.value = id
    } else {
        if (selected.value.size == (props.maxSelected || 10 /* default value */)) {
            toast.error("Error: Maximum number of experiments reached", {
                position: POSITION.BOTTOM_RIGHT,
            })
        } else {
            selected.value.add(id)
        }
    }
}

function secondarySelect(event: MouseEvent, item: string) {
    event.preventDefault()
    emit('secondarySelect', item)
}

</script>

<template>
    <input class="form-control mb-2" type="search" :placeholder="searchPlaceholder" v-model="search">
    <RecycleScroller class="mb-2 scroller list-group" :items="filteredData" :item-size="32" key-field="id"
        v-slot="{ item }">
        <div @click="selectOrUnselect(item.id)" @contextmenu="secondarySelect($event, item)"
            class="list-group-item list-group-item-action d-flex justify-content-between align-items-center option"
            :title="item.title" :class="isSelected(item.id) ? 'active' : ''">
            <span class="text-truncate">{{ item.title }}</span>
            <span class="badge bg-primary rounded-pill" v-if="item.subtitle">{{ item.subtitle }}</span>
        </div>
    </RecycleScroller>
</template>

<style scoped>
.option {
    display: flex;
    padding: 0.25rem 1.25rem;
    height: 32px;
}

.scroller {
    max-height: 300px;
    width: 100%;
    overflow-y: scroll;
}
</style>