import Alpine from "alpinejs";
import $ from "jquery";

// Expose jQuery globally (some pages rely on it)
window.jQuery = $;
window.$ = $;

// Expose Alpine globally and start it once
window.Alpine = Alpine;

function startAlpineOnce() {
  if (window.__alpine_started__) return;
  window.__alpine_started__ = true;
  Alpine.start();
}

document.addEventListener("DOMContentLoaded", function () {
  startAlpineOnce();

  // Drawer elements are not present on every page (e.g. invoice preview iframe)
  const drawer = document.getElementById("service_list_drawer");
  const serviceListToggler = document.getElementById("service_list_toggler");
  const logoSingleServiceListToggler = document.getElementById(
    "logo_single_service_list_toggler"
  );

  // Note: querySelectorAll returns an empty NodeList if none exist
  const togglers = document.querySelectorAll("#service_list_togglers");

  // If the drawer UI isn't on this page, exit silently
  if (!drawer || !serviceListToggler || !logoSingleServiceListToggler) return;

  window.toggleDrawerSurrounds = function toggleDrawerSurrounds(state) {
    serviceListToggler.checked = state;
    logoSingleServiceListToggler.checked = state;

    togglers.forEach((t) => {
      t.checked = state;
    });
  };

  window.toggleDrawer = function toggleDrawer(value, withDrawer = false) {
    window.toggleDrawerSurrounds(value);
    if (withDrawer) drawer.checked = value;
  };

  drawer.addEventListener("change", function () {
    window.toggleDrawerSurrounds(drawer.checked);
  });
});

