import 'htmx.org';
import 'hyperscript.org';

import '@fortawesome/fontawesome-free/js/fontawesome'
import '@fortawesome/fontawesome-free/js/solid'
import '@fortawesome/fontawesome-free/js/regular'
import '@fortawesome/fontawesome-free/js/brands'
import Alpine from 'alpinejs'
import $ from 'jquery'


window.htmx = require('htmx.org')
window._hyperscript = require('hyperscript.org');
window._hyperscript.browserInit();
window.Alpine = Alpine

window.jQuery = $;
window.$ = $;