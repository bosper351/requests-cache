[![](docs/_static/requests-cache-logo-header.png)](https://requests-cache.readthedocs.io)

[![Build](https://github.com/requests-cache/requests-cache/actions/workflows/build.yml/badge.svg)](https://github.com/requests-cache/requests-cache/actions)
[![Codecov](https://codecov.io/gh/requests-cache/requests-cache/branch/main/graph/badge.svg?token=FnybzVWbt2)](https://codecov.io/gh/requests-cache/requests-cache)
[![Documentation](https://img.shields.io/readthedocs/requests-cache/latest)](https://requests-cache.readthedocs.io/en/stable/)
[![Code Shelter](https://www.codeshelter.co/static/badges/badge-flat.svg)](https://www.codeshelter.co/)

[![PyPI](https://img.shields.io/pypi/v/requests-cache?color=blue)](https://pypi.org/project/requests-cache)
[![Conda](https://img.shields.io/conda/vn/conda-forge/requests-cache?color=blue)](https://anaconda.org/conda-forge/requests-cache)
[![PyPI - Python Versions](https://img.shields.io/pypi/pyversions/requests-cache)](https://pypi.org/project/requests-cache)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/requests-cache?color=blue)](https://pypi.org/project/requests-cache)

## Summary
**requests-cache** is a persistent HTTP cache that provides an easy way to get better
performance with the python [requests](https://requests.readthedocs.io/) library.

<!-- RTD-IGNORE -->
Complete project documentation can be found at [requests-cache.readthedocs.io](https://requests-cache.readthedocs.io).
<!-- END-RTD-IGNORE -->

## Features
* 🍰 **Ease of use:** Keep using the `requests` library you're already familiar with. Add caching
  with a [drop-in replacement](https://requests-cache.readthedocs.io/en/stable/user_guide/general.html#sessions)
  for `requests.Session`, or
  [install globally](https://requests-cache.readthedocs.io/en/stable/user_guide/general.html#patching)
  to add transparent caching to all `requests` functions.
* 🚀 **Performance:** Get sub-millisecond response times for cached responses. When they expire, you
  still save time with
  [conditional requests](https://requests-cache.readthedocs.io/en/stable/user_guide/headers.html#conditional-requests).
* 💾 **Persistence:** Works with several
  [storage backends](https://requests-cache.readthedocs.io/en/stable/user_guide/backends.html)
  including SQLite, Redis, MongoDB, and DynamoDB; or save responses as plain JSON files, YAML,
  and more
* 🕗 **Expiration:** Use
  [Cache-Control](https://requests-cache.readthedocs.io/en/stable/user_guide/headers.html#cache-control)
  and other standard HTTP headers, define your own expiration schedule, keep your cache clutter-free
  with backends that natively support TTL, or any combination of strategies
* ⚙️ **Customization:** Works out of the box with zero config, but with a robust set of features for
  configuring and extending the library to suit your needs
* 🧩 **Compatibility:** Can be combined with other
  [popular libraries based on requests](https://requests-cache.readthedocs.io/en/stable/user_guide/compatibility.html)

## Quickstart
First, install with pip:
```bash
pip install requests-cache
```

Then, use [requests_cache.CachedSession](https://requests-cache.readthedocs.io/en/stable/modules/requests_cache.session.html)
to make your requests. It behaves like a normal
[requests.Session](https://requests.readthedocs.io/en/latest/user/advanced/#session-objects),
but with caching behavior.

To illustrate, we'll call an endpoint that adds a delay of 1 second, simulating a slow or
rate-limited website.

**This takes 1 minute:**
```python
import requests

session = requests.Session()
for i in range(60):
    session.get('https://httpbin.org/delay/1')
```

**This takes 1 second:**
```python
import requests_cache

session = requests_cache.CachedSession('demo_cache')
for i in range(60):
    session.get('https://httpbin.org/delay/1')
```

With caching, the response will be fetched once, saved to `demo_cache.sqlite`, and subsequent
requests will return the cached response near-instantly.

### Patching
If you don't want to manage a session object, or just want to quickly test it out in your
application without modifying any code, requests-cache can also be installed globally, and all
requests will be transparently cached:
```python
import requests
import requests_cache

requests_cache.install_cache('demo_cache')
requests.get('https://httpbin.org/delay/1')
```

### Headers and Expiration
By default, requests-cache will keep cached responses indefinitely. In most cases, you will want to
use one of the two following strategies to balance cache freshness and performance:

**Define exactly how long to keep responses:**

Use the `expire_after` parameter to set a fixed expiration time for all new responses:
```python
from requests_cache import CachedSession
from datetime import timedelta

# Keep responses for 360 seconds
session = CachedSession('demo_cache', expire_after=360)

# Or use timedelta objects to specify other units of time
session = CachedSession('demo_cache', expire_after=timedelta(hours=1))
```
See [Expiration](https://requests-cache.readthedocs.io/en/stable/user_guide/expiration.html) for
more features and settings.

**Use Cache-Control headers:**

Use the `cache_control` parameter to enable automatic expiration based on `Cache-Control` and other
standard HTTP headers sent by the server:
```python
from requests_cache import CachedSession

session = CachedSession('demo_cache', cache_control=True)
```
See [Cache Headers](https://requests-cache.readthedocs.io/en/stable/user_guide/headers.html)
for more details.


### Settings
The default settings work well for most use cases, but there are plenty of ways to customize
caching behavior when needed. Here is a quick example of some of the options available:
```python
from datetime import timedelta
from requests_cache import CachedSession

session = CachedSession(
    'demo_cache',
    use_cache_dir=True,                # Save files in the default user cache dir
    cache_control=True,                # Use Cache-Control response headers for expiration, if available
    expire_after=timedelta(days=1),    # Otherwise expire responses after one day
    allowable_codes=[200, 400],        # Cache 400 responses as a solemn reminder of your failures
    allowable_methods=['GET', 'POST'], # Cache whatever HTTP methods you want
    ignored_parameters=['api_key'],    # Don't match this request param, and redact if from the cache
    match_headers=['Accept-Language'], # Cache a different response per language
    stale_if_error=True,               # In case of request errors, use stale cache data if possible
)
```

<!-- RTD-IGNORE -->
## Next Steps
To find out more about what you can do with requests-cache, see:

* [User Guide](https://requests-cache.readthedocs.io/en/stable/user_guide.html)
* [Examples](https://requests-cache.readthedocs.io/en/stable/examples.html)
* [API Reference](https://requests-cache.readthedocs.io/en/stable/reference.html)
* [Project Info](https://requests-cache.readthedocs.io/en/stable/project_info.html)
<!-- END-RTD-IGNORE -->
