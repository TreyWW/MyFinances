window.$docsify = {
    name: 'MyFinances',
    repo: 'TreyWW/MyFinances',
    loadNavbar: true,
    loadSidebar: true,
}


waitForElement("select[data-item=\"version_select\"]").then((version_object) => {
    version_object.addEventListener("change", function () {
        window.location = `/#/v/${version_object.value}/`
    })
})


function waitForElement(selector) {
    return new Promise(resolve => {
        if (document.querySelector(selector)) {
            return resolve(document.querySelector(selector));
        }

        const observer = new MutationObserver(mutations => {
            if (document.querySelector(selector)) {
                observer.disconnect();
                resolve(document.querySelector(selector));
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
}