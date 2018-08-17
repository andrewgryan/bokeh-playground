const jsdom = require('jsdom');
const bokeh = require('bokehjs');
global.document = jsdom.jsdom();
global.window = document.defaultView();
console.log("Hello, node!");
console.log("Hello, JSDOM!", jsdom);
console.log("Hello, Bokeh!", bokeh);
