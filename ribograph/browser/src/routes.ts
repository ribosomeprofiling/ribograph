import createMatcher from 'feather-route-matcher'
import ExperimentOverview from './views/ExperimentOverview.vue'
import Coverage from './views/Coverage.vue'
import Offset from './views/Offset.vue'

export default createMatcher({
    '/:experiment/experiment_details': ExperimentOverview,
    '/:experiment/coverage': Coverage,
    '/:experiment/offset': Offset
})