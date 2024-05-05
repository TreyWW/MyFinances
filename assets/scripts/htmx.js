import 'htmx.org';
import 'hyperscript.org';

window.htmx = require('htmx.org');
window._hyperscript = require('hyperscript.org');
window._hyperscript.browserInit();

function htmx_resend(event) {
  let eventType;

  if (event.detail.statusCode === 403) {
    return // forbidden
  }

  if (event.detail.requestConfig.triggeringEvent) {
    eventType = event.detail.requestConfig.triggeringEvent.type
  } else {
    eventType = "retry"
  }

  let timeout;

  if (event.detail.error.includes("429")) {
    timeout = 4000;
  } else {
    timeout = 2000;
  }

  setTimeout(function () {
    console.log("Sending HTMX retry event")
    htmx.trigger(event.detail.elt, eventType);
  }, timeout);
}

// https://htmx.org/docs/#config
htmx.config.globalViewTransitions = true
htmx.config.useTemplateFragments = true // for swapping of table items


window.addEventListener("DOMContentLoaded", (event) => {
  document.body.addEventListener("htmx:sendError", htmx_resend);
  document.body.addEventListener("htmx:responseError", htmx_resend);
  document.body.addEventListener("htmx:loadError", htmx_resend);
  document.body.addEventListener("htmx:afterRequest", (event) => {
    const drawer = document.getElementById("service_list_drawer");
    if (drawer) {
      toggleDrawer(false, true);
    }
  });
});
