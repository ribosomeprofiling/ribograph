<script setup lang="ts">
import { ref, onMounted } from 'vue'
defineProps<{
    modelValue: boolean,
    tooltip?: string
}>()

const emit = defineEmits(['update:modelValue'])

function update(event: Event) {
    const target: Partial<HTMLInputElement> | null = event.target
    emit('update:modelValue', target?.checked)
}

</script>

<template>
    <div class="form-check form-switch" data-bs-toggle="tooltip" data-bs-placement="right" :title="tooltip"
        ref="checkbox">
        <input class="form-check-input" v-model="modelValue" type="checkbox" id="checkbox" @input="update($event)">
        <label class="form-check-label" for="checkbox">
            <abbr :title="tooltip">
                <slot />
            </abbr>
        </label>
    </div>
</template>
