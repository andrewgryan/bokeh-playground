"use strict";
let resize = function() {
    console.log("window.onresize event detected");
    let figure = Bokeh.documents[0].roots()[0];
    figure.width = window.innerWidth;
    figure.height = window.innerHeight;
};
window.addEventListener('resize', resize);
