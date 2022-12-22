<script setup lang="ts">
import { onMounted, onBeforeUnmount, watch } from 'vue'
import routeMatcher from './routes'
import { storage } from './localStorageStore'

const { pathname } = window.location
const route: any = routeMatcher(pathname) // typedefs seem to be wrong for this one

/////////
/// LOCAL STORAGE
/////////

onMounted(() => {
  // initialize reactive vue storage variable with localStorage data
  Object.keys(localStorage).forEach(key => storage[key] = localStorage[key])
  window.addEventListener("storage", onStorageUpdate)
})

onBeforeUnmount(() => {
  window.removeEventListener("storage", onStorageUpdate);
})

const onStorageUpdate = (event: StorageEvent) => {
  const { key, newValue } = event
  if (key) {
    if (newValue) {
      // value has been added/updated
      storage[key] = newValue
    } else {
      // key has been removed
      delete storage[key]
    }
  } else {
    // localStorage has been cleared, empty the storage object
    Object.keys(storage).forEach(key => delete storage[key]);
  }
}

// TODO make sure this doesn't recursively do something weird
// TODO remove from localStorage when removed from storage
// when storage changes, update localStorage
watch(storage, () => Object.keys(storage).forEach(key => localStorage[key] = storage[key]))

</script>

<template>
  <main>
    <component v-if="route" :is="route.value" v-bind="route.params" />
  </main>
</template>

<style>
#app,
.noUi-target {
  width: 100%
}

:root {
  --slider-connect-bg: #3B82F6;
  --slider-tooltip-bg: #3B82F6;
  --slider-handle-ring-color: #3B82F630;
}
</style>
