<script setup lang="ts">
import { ref } from 'vue'
const open = ref(false)
const props = defineProps<{ title?: string }>()
</script>

<template>
    <div class="accordion">
        <div class="accordion-item">
            <h2 class="accordion-header">
                <button class="accordion-button" :class="{ 'collapsed': !open }" type="button" @click="open = !open">
                    {{props.title || "Information"}}
                </button>
            </h2>
            <div class="accordion-collapse  " :class="{ 'collapse': !open, 'collapsed': open }">
                <div class="accordion-body">
                    <slot></slot>
                </div>
            </div>
        </div>
    </div>
</template>