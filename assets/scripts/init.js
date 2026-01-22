import Alpine from "alpinejs";
import $ from "jquery";

// jQuery global
window.jQuery = $;
window.$ = $;

// Alpine global + start ONCE, posle DOM-a
window.Alpine = Alpine;

function startAlpineOnce() {
  if (window.__alpine_started__) return;
  window.__alpine_started__ = true;
  Alpine.start();
}

document.addEventListener("DOMContentLoaded", function () {
  // Alpine tek kad DOM postoji
  startAlpineOnce();

  // Drawer elementi (ne postoje na svim stranicama / iframe-u)
  const drawer = document.getElementById("service_list_drawer");
  const service_list_toggler = document.getElementById("service_list_toggler");
  const logo_single_service_list_toggler = document.getElementById("logo_single_service_list_toggler");
  const togglers = document.querySelectorAll("#service_list_togglers");

  // Ako nema drawer UI na toj stranici (npr. iframe preview) -> ne radi ništa
  if (!drawer || !service_list_toggler || !logo_single_service_list_toggler) return;

  window.toggleDrawerSurrounds = function toggleDrawerSurrounds(state) {
    service_list_toggler.checked = state;
    logo_single_service_list_toggler.checked = state;

    for (let i = 0; i < togglers.length; i++) {
      togglers[i].checked = state;
    }
  };

  window.toggleDrawer = function toggleDrawer(value, with_drawer = false) {
    window.toggleDrawerSurrounds(value);
    if (with_drawer) drawer.checked = value;
  };

  drawer.addEventListener("change", function () {
    window.toggleDrawerSurrounds(drawer.checked);
  });
});
