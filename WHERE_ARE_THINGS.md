# Where are things?
- [views](#views)
- [tests](#tests)
- [Page routes (URLS.py)](#page-routes-urlspy)
- [context_processors](#context-processors-c_ppy-variables-passed-into-every-page)
- [static files](#static-files)
- [templates](#templates-html-pages)
<!--
- [docker files](#)
- [nginx files](#)
- -->


### Views
```
backend/<section/app>/views/<file>.py
```

### Tests
```
backend/tests/test_<section>.py
```

### Page Routes ([URLS.py](https://github.com/TreyWW/MyFinances/blob/main/backend/urls.py))
```
backend/urls.py
```

### Context Processors ([c_p.py](https://github.com/TreyWW/MyFinances/blob/main/backend/context_processors.py)) (variables passed into every page)
```
backend/context_processors.py
```

### Static Files
```
frontend/static/img/
frontend/static/js/
```


### Templates (HTML Pages)
```
  frontend/templates/pages/<section>/<page_name>.html
```

### Partial Templates
```
  frontend/templates/pages/<section>/_<page_name>-<partial_topic>.html
  e.g. --> frontend/templates/pages/receipts/_dashboard_search_results.html
```
