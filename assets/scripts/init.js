import 'htmx.org';
import 'hyperscript.org';

import Alpine from 'alpinejs'
import $ from 'jquery'


window.htmx = require('htmx.org')
window._hyperscript = require('hyperscript.org');
window._hyperscript.browserInit();
window.Alpine = Alpine

window.jQuery = $;
window.$ = $;

document.addEventListener("DOMContentLoaded", function () {
  const drawer = document.getElementById("service_list_drawer");
  var togglers = document.querySelectorAll("#service_list_togglers");

  drawer.addEventListener("change", function () {
    if (drawer.checked) {
      document.getElementById("service_list_toggler").checked = true;
      for (let i = 0; i < togglers.length; i++) {
        togglers[i].checked = true
      }
      document.getElementById("logo_single_service_list_toggler").checked = true;
    } else {
      document.getElementById("service_list_toggler").checked = false;
      for (let i = 0; i < togglers.length; i++) {
        togglers[i].checked = false
      }
      document.getElementById("logo_single_service_list_toggler").checked = false;
    }
    ;
  });
});
