// this one definetly works
import Plotly from 'plotly.js-dist-min'

// this way would be more efficient since we only import the modules we are using,
// but doesn't work in the current build setup
// import * as Plotly from 'plotly.js/lib/core'
// // import * as Bar from 'plotly.js/lib/core'
// // import * as Heatmap from 'plotly.js/lib/heatmap'
// // import * as Scattergl from 'plotly.js/lib/scattergl'
// Plotly.register([
//     require('plotly.js/lib/bar'), 
//     require('plotly.js/lib/heatmap'), 
//     require('plotly.js/lib/scattergl'), 
// ]);

export default Plotly