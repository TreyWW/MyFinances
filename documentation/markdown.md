To use markdown sanitation to HTML we can use the newly installed django-markdownify tool.

```html
{% load markdownify %}
{{ variable|markdownify  }}
```