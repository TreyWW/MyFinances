window.$docsify = {
    name: 'MyFinances',
    repo: 'TreyWW/MyFinances',
    loadNavbar: true,
    loadSidebar: true,
}

window.addEventListener('load', function () {
    let version_object = document.querySelector('select[data-item="version_select"]')

    version_object.addEventListener("change", function () {
        window.location = `/#/v${version_object.value}/`
    })
})