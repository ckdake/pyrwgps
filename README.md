# pyrwgps

A simple Python client for the [RideWithGPS API](https://ridewithgps.com/api/v1/doc).

*This project is not affiliated with or endorsed by RideWithGPS.*

> **Note:** This client is not yet feature-complete. Read the code before you use it and report any bugs you find.
>
> **API versions:** RideWithGPS has a v1 API (`/api/v1/...`) and a legacy API (no version prefix). This client supports both, but v1 coverage is incomplete. See [API Versions](#api-versions) for a full breakdown of what uses v1 vs legacy.

> **Authentication:** No OAuth required. `authenticate()` uses the v1 Basic auth endpoint (`POST /api/v1/auth_tokens.json`) with your existing API key. The returned token works for both v1 and legacy endpoints.

[![PyPI version](https://img.shields.io/pypi/v/pyrwgps.svg)](https://pypi.org/project/pyrwgps/)
[![PyPI downloads](https://img.shields.io/pypi/dm/pyrwgps.svg)](https://pypi.org/project/pyrwgps/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python versions](https://img.shields.io/pypi/pyversions/pyrwgps.svg)](https://pypi.org/project/pyrwgps/)

[![black](https://github.com/ckdake/pyrwgps/actions/workflows/black.yml/badge.svg)](https://github.com/ckdake/pyrwgps/actions/workflows/black.yml)
[![flake8](https://github.com/ckdake/pyrwgps/actions/workflows/flake8.yml/badge.svg)](https://github.com/ckdake/pyrwgps/actions/workflows/flake8.yml)
[![mypy](https://github.com/ckdake/pyrwgps/actions/workflows/mypy.yml/badge.svg)](https://github.com/ckdake/pyrwgps/actions/workflows/mypy.yml)
[![pylint](https://github.com/ckdake/pyrwgps/actions/workflows/pylint.yml/badge.svg)](https://github.com/ckdake/pyrwgps/actions/workflows/pylint.yml)
[![pytest](https://github.com/ckdake/pyrwgps/actions/workflows/pytest.yml/badge.svg)](https://github.com/ckdake/pyrwgps/actions/workflows/pytest.yml)

## Features

- Authenticates with the [RideWithGPS API](https://ridewithgps.com/api/v1/doc)
- Makes any API request — `get`, `put`, `post`, `patch`, `delete` — to v1 or legacy endpoints.
- Built-in rate limiting, caching, and pagination.
- Use higher-level abstractions like `list` to iterate collections with automatic pagination.

## API Versions

RideWithGPS has a v1 API (`/api/v1/...`) and a legacy API (no version prefix). This client supports
both. The v1 API is preferred where available, but several things are **not yet in v1** and still
require the legacy API.

### Uses v1 API (`/api/v1/...`)

| Resource | Operations |
|---|---|
| Authentication | Create token (email + password + API key, no OAuth needed) |
| Trips | List, get single, delete, get polyline |
| Routes | List, get single, delete, get polyline |
| Collections | List, get single, get pinned |
| Events | List, create, get single, update, delete |
| Club Members | List, get single, update |
| Points of Interest | List, create, get single, update, delete, associate/disassociate with route |
| Sync | Get items for sync |
| Users | Get current user |

For `list` over a v1 endpoint, pass `result_key` matching the response root key (e.g. `result_key="trips"`). See [v1 API usage](#v1-api) for examples.

### Still uses legacy API (no version prefix)

These are **not available on v1** and require the legacy endpoints:

| Resource / Feature | Legacy endpoint | Reason |
|---|---|---|
| Gear | `/users/{user_id}/gear.json` | No v1 gear endpoint exists |
| Create trip | `/trips.json` (POST) | v1 trips is read/delete only |
| Update trip | `/trips/{id}.json` (PUT/PATCH) | v1 trips is read/delete only |
| Create route | `/routes.json` (POST) | v1 routes is read/delete only |
| Update route | `/routes/{id}.json` (PUT/PATCH) | v1 routes is read/delete only |

## v1 API

v1 endpoints live under `/api/v1/` and use `page`/`page_size` pagination, returning results
under a named root key (e.g. `{"trips": [...], "meta": {...}}`).

All of `list`, `get`, `put`, `post`, `patch`, and `delete` work with v1 paths.
For `list`, pass `result_key` matching the response root key:

```python
# List all trips (v1)
for trip in client.list("/api/v1/trips.json", result_key="trips"):
    print(trip.name, trip.id)

# List routes, up to 50 (v1)
for route in client.list("/api/v1/routes.json", result_key="routes", limit=50):
    print(route.name, route.id)

# Get a single resource (v1)
route = client.get(path="/api/v1/routes/123456.json")
print(route.route.name)

# Get the authenticated user's pinned collection (v1)
pinned = client.get(path="/api/v1/collections/pinned.json")

# Create an event (v1)
event = client.post(
    path="/api/v1/events.json",
    params={"name": "My Gran Fondo", "start_date": "2026-06-01"},
)
```

## Installation

The package is published on [PyPI](https://pypi.org/project/pyrwgps/).

---

## Usage

First, install the package:

```sh
pip install pyrwgps
```

Then, in your Python code:

```python
from pyrwgps import RideWithGPS

# Initialize client and authenticate, with optional in-memory GET cache enabled
client = RideWithGPS(apikey="yourapikey", cache=True)
user_info = client.authenticate(email="your@email.com", password="yourpassword")

print(user_info.id, user_info.display_name)

# Update the name of a trip (legacy API — trip update not yet in v1)
activity_id = "123456"
new_name = "Morning Ride"
response = client.put(
    path=f"/trips/{activity_id}.json",
    params={"name": new_name}
)
updated_name = response.trip.name if hasattr(response, "trip") else None
if updated_name == new_name:
    print(f"Activity name updated to: {updated_name}")
else:
    print("Failed to update activity name.")

# We changed something, so probably should clear the cache.
client.clear_cache()

# Simple GET: fetch a single trip via the v1 API
trip = client.get(path="/api/v1/trips/123456.json")
print(trip.trip.name, trip.trip.id)

# Automatically paginate: List up to 25 trips via the v1 API
for trip in client.list(
    path="/api/v1/trips.json",
    result_key="trips",
    limit=25,
):
    print(trip.name, trip.id)

# Automatically paginate: List all routes via the v1 API
for route in client.list(
    path="/api/v1/routes.json",
    result_key="routes",
):
    print(route.name, route.id)

# Get the authenticated user's pinned collection (v1)
pinned = client.get(path="/api/v1/collections/pinned.json")
print(pinned)

# Automatically paginate: List all gear for this user (legacy API — no v1 gear endpoint yet)
gear = {}
for g in client.list(
    path=f"/users/{user_info.id}/gear.json",
    params={},
):
    gear[g.id] = g.nickname
print(gear)
```

**Note:**  
- All API responses are automatically converted from JSON to Python objects with attribute access.
- You must provide your own RideWithGPS credentials and API key.
- Use v1 endpoints (`/api/v1/...`) for trips, routes, collections, events, club members, points of interest, and sync. See the [v1 API section](#v1-api) for what is and isn't available.
- The `list`, `get`, `put`, `post`, `patch` and `delete` methods are the recommended interface for making API requests; see the code and [RideWithGPS API docs](https://ridewithgps.com/api/v1/doc) for available endpoints and parameters.

---

## Development

### Set up environment

If you use this as VS Dev Container, you can skip using a venv.

```sh
python3 -m venv env
source env/bin/activate
pip install .[dev]
```

Or, for local development with editable install:

```sh
git clone https://github.com/ckdake/pyrwgps.git
cd pyrwgps
pip install -e '.[dev]'
```

### Run tests

```sh
python -m pytest --cov=pyrwgps --cov-report=term-missing -v
```

### Run an example
```sh
python3 scripts/example.py
```

### Linting and Formatting

Run these tools locally to check and format your code:

- **pylint** (static code analysis):

    ```sh
    pylint pyrwgps
    ```

- **flake8** (style and lint checks):

    ```sh
    flake8 pyrwgps
    ```

- **black** (auto-formatting):

    ```sh
    black pyrwgps
    ```

- **mypy** (type checking):

    ```sh
    mypy pyrwgps
    ```

### Updating Integration Cassettes

If you need to update the VCR cassettes for integration tests:

1. **Set required environment variables:**
   - `RIDEWITHGPS_EMAIL`
   - `RIDEWITHGPS_PASSWORD`
   - `RIDEWITHGPS_KEY`

   Example:
   ```sh
   export RIDEWITHGPS_EMAIL=your@email.com
   export RIDEWITHGPS_PASSWORD=yourpassword
   export RIDEWITHGPS_KEY=yourapikey
   ```

2. **Delete all existing cassettes (including backups) and re-record:**
   ```sh
   rm tests/cassettes/*.yaml tests/cassettes/*.yaml.original
   python -m pytest --cov=pyrwgps --cov-report=term-missing -v
   ```

3. **Scrub sensitive data from the cassette:**
   ```sh
   python scripts/scrub_cassettes.py
   ```
   - This will back up your cassettes to `*.yaml.original` (if not already present).
   - The sanitized cassettes will overwrite `*.yaml`.

4. **Re-run tests to verify:**
   ```sh
   python -m pytest --cov=pyrwgps --cov-report=term-missing -v
   ```

### Publishing to PyPI

To publish a new version of this package to [PyPI](https://pypi.org/):

1. **Update the version number**  
   Edit `pyproject.toml` and increment the version.

2. **Install build tools**  
   ```sh
   pip install .[dev]
   ```

3. **Build the distribution**  
   ```sh
   python -m build
   ```
   This will create `dist/pyrwgps-<version>.tar.gz` and `.whl` files.

4. **Check the distribution (optional but recommended)**  
   ```sh
   twine check dist/*
   ```

5. **Upload to PyPI**  
   ```sh
   twine upload dist/*
   ```
   You will be prompted for your PyPI API key.

6. **Open your package on PyPI (optional)**  
   ```sh
   $BROWSER https://pypi.org/project/pyrwgps/
   ```

**Note:**  
- Configure your `~/.pypirc` is configured if you want to avoid entering credentials each time.
- For test uploads, use `twine upload --repository testpypi dist/*` and visit [TestPyPI](https://test.pypi.org/).

---

- [PyPI: pyrwgps](https://pypi.org/project/pyrwgps/)
- [RideWithGPS API documentation](https://ridewithgps.com/api/v1/doc)

---

## License

MIT License

---

*This project is not affiliated with or endorsed by RideWithGPS.*
