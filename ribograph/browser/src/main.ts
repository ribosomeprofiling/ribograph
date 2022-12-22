import { createApp } from 'vue'
import App from './App.vue'
import Toast from "vue-toastification";
import type { PluginOptions } from "vue-toastification";
import VueVirtualScroller from 'vue-virtual-scroller'
import Slider from '@vueform/slider'

import '@vueform/slider/themes/default.css'
import "vue-toastification/dist/index.css";
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css'

const app = createApp(App)

const options: PluginOptions = {
    transition: "Vue-Toastification__bounce",
    maxToasts: 20,
    newestOnTop: true
};

app.use(Toast, options);
app.use(VueVirtualScroller)
app.component('Slider', Slider)
app.mount('#app');
