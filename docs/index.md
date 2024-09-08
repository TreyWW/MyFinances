# MyFinances

MyFinances is an open-source web application designed to empower individuals and teams to efficiently manage their finances.
Whether you're managing client invoices, onboarding new clients or storing business files, MyFinances provides a
user-friendly platform to streamline these tasks.

## User Guide
---



## Developer Guide
---

<div class="grid cards" markdown>

- :material-clock-fast:{ .lg .middle } __Set up in 5 minutes__

    ---

    Git clone the project, install dependencies and get up
    and running in minutes

    [:octicons-arrow-right-24: Getting started](getting-started/)

  - :fontawesome-solid-clock-rotate-left:{ .md .middle } __Release Notes__

      ---

    View our most recent changes. Make sure to view the changelog before upgrading!

    [:octicons-arrow-right-24: Changelog](changelog)

	<li>
        <p>Join our Discord</p>
        <hr>
        <a target="_blank" href="https://discord.gg/9kKG3SMbAr?utm_source=Discord%20Widget&utm_medium=Connect">
            <img src="https://discord.com/api/guilds/1139553863175778367/widget.png?style=banner2"/>
        </a>
        <li>
			<p>Book a call with the project lead</p>
			<hr>
			<button class="md-button" data-cal-link="treyww/myfinances-development-help"
					data-cal-namespace="myfinances-development-help" data-cal-config='{"layout":"month_view"}'>
					See availability</button>
		</li>
    </li>
</div>

<script type="text/javascript">
  (function (C, A, L) { let p = function (a, ar) { a.q.push(ar); }; let d = C.document; C.Cal = C.Cal || function () { let cal = C.Cal; let ar = arguments; if (!cal.loaded) { cal.ns = {}; cal.q = cal.q || []; d.head.appendChild(d.createElement("script")).src = A; cal.loaded = true; } if (ar[0] === L) { const api = function () { p(api, arguments); }; const namespace = ar[1]; api.q = api.q || []; if(typeof namespace === "string"){cal.ns[namespace] = cal.ns[namespace] || api;p(cal.ns[namespace], ar);p(cal, ["initNamespace", namespace]);} else p(cal, ar); return;} p(cal, ar); }; })(window, "https://app.cal.com/embed/embed.js", "init");
  Cal("init", "myfinances-development-help", {origin:"https://cal.com"});


  // Important: Please add the following attributes to the element that should trigger the calendar to open upon clicking.
  // `data-cal-link="treyww/myfinances-development-help"`
  // data-cal-namespace="myfinances-development-help"
  // `data-cal-config='{"layout":"month_view"}'`

  Cal.ns["myfinances-development-help"]("ui", {"styles":{"branding":{"brandColor":"#000000"}},"hideEventTypeDetails":false,"layout":"month_view"});
</script>
