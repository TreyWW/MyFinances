import Alpine from "alpinejs";
import $ from "jquery";

// Expose jQuery globally (some pages rely on it)
window.jQuery = $;
window.$ = $;

// Expose Alpine globally and start it once
window.Alpine = Alpine;

function getThemeFromLocalStorage() {
  // if user already changed the theme, use it
  if (window.localStorage.getItem('dark')) {
    return JSON.parse(window.localStorage.getItem('dark'))
  }
  // else return their preferences
  return (
    !!window.matchMedia &&
    window.matchMedia('(prefers-color-scheme: dark)').matches
  )
}

function setThemeToLocalStorage(value) {
  window.localStorage.setItem('dark', value)
}

function data() {
  return {
    dark: getThemeFromLocalStorage(),
    toggleTheme() {
      this.dark = !this.dark;
      setThemeToLocalStorage(this.dark);
    },
    isSideMenuOpen: false,
    toggleSideMenu() {
      this.isSideMenuOpen = !this.isSideMenuOpen
    },
    closeSideMenu() {
      this.isSideMenuOpen = false
    },
    isNotificationsMenuOpen: false,
    toggleNotificationsMenu() {
      this.isNotificationsMenuOpen = !this.isNotificationsMenuOpen
    },
    closeNotificationsMenu() {
      this.isNotificationsMenuOpen = false
    },
    isProfileMenuOpen: false,
    toggleProfileMenu() {
      this.isProfileMenuOpen = !this.isProfileMenuOpen
    },
    closeProfileMenu() {
      this.isProfileMenuOpen = false
    },
    isPagesMenuOpen: false,
    togglePagesMenu() {
      this.isPagesMenuOpen = !this.isPagesMenuOpen
    },
    isModalOpen: false,
    trapCleanup: null,
    openModal() {
      this.isModalOpen = true
      this.trapCleanup = focusTrap(document.querySelector('#modal'))
    },
    closeModal() {
      this.isModalOpen = false
      this.trapCleanup()
    },
  }
}

// Expose data() globally so x-data="data()" works in templates
window.data = data;

function startAlpineOnce() {
  if (window.__alpine_started__) return;
  window.__alpine_started__ = true;
  Alpine.start();
}

document.addEventListener("DOMContentLoaded", function () {
  startAlpineOnce();

  const drawer = document.getElementById("service_list_drawer");
  const serviceListToggler = document.getElementById("service_list_toggler");
  const logoSingleServiceListToggler = document.getElementById(
    "logo_single_service_list_toggler"
  );

  const togglers = document.querySelectorAll("#service_list_togglers");

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