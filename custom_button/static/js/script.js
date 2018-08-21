(function() {
    window.onload = function() {
        let timerID = setInterval(function() {
            if (Bokeh.documents.length === 0) {
                console.log("No Bokeh documents found");
                return;
            } else {
                console.log("Found " + Bokeh.documents.length + " Bokeh documents");
                clearInterval(timerID);
                // main()
                return;
            }
        }, 50);

        window.clearClasses = main = function() {
            // Remove all bk-root classes
            let classNames = ["bk-root",
                              "bk-widget",
                              "bk-layout-fixed",
                              "bk-bs-btn",
                              "bk-bs-btn-default"];
            for (let ic=0; ic<classNames.length; ic++) {
                let className = classNames[ic];
                let els = document.getElementsByClassName(className);
                while (els.length > 0) {
                    els[0].classList.remove(className);
                    console.log("els.length ", els.length);
                }
            }
        };
    };
})();
