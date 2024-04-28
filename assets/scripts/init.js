import Alpine from 'alpinejs'
import $ from 'jquery'


window.Alpine = Alpine

Alpine.start()

window.jQuery = $;
window.$ = $;

document.addEventListener("DOMContentLoaded", function () {
  const drawer = document.getElementById("service_list_drawer");
  const service_list_toggler = document.getElementById("service_list_toggler");
  const logo_single_service_list_toggler = document.getElementById("logo_single_service_list_toggler");
  var togglers = document.querySelectorAll("#service_list_togglers");

  window.toggleDrawer = function toggleDrawer(value, with_drawer = false) {
    toggleDrawerSurrounds(value)

    if (with_drawer) {
      drawer.checked = value
    }
  }

  window.toggleDrawerSurrounds = function toggleDrawerSurrounds(state) {
    service_list_toggler.checked = state;
    logo_single_service_list_toggler.checked = state;

    for (let i = 0; i < togglers.length; i++) {
      togglers[i].checked = state
    }
  }


  drawer.addEventListener("change", function () {
    toggleDrawerSurrounds(drawer.checked)
  });
});
