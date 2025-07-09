# pyrwgps

A simple Python client for the [RideWithGPS API](https://ridewithgps.com/api).

*This project is not affiliated with or endorsed by RideWithGPS.*

Note: This client isn't used for a lot yet, so it may not work quite right. Read
the code before you use it, and report any bugs you find.

Also Note: The Ride With GPS API is JSON based and under active development. It
doesn't have full documentation published, and the best way to figure out how
things work is to use the dev tools in your browser to watch actual requests.

[![PyPI version](https://img.shields.io/pypi/v/ridewithgps.svg)](https://pypi.org/project/ridewithgps/)
[![PyPI downloads](https://img.shields.io/pypi/dm/ridewithgps.svg)](https://pypi.org/project/ridewithgps/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python versions](https://img.shields.io/pypi/pyversions/ridewithgps.svg)](https://pypi.org/project/ridewithgps/)

[![black](https://github.com/ckdake/python-ridewithgps/actions/workflows/black.yml/badge.svg)](https://github.com/ckdake/python-ridewithgps/actions/workflows/black.yml)
[![flake8](https://github.com/ckdake/python-ridewithgps/actions/workflows/flake8.yml/badge.svg)](https://github.com/ckdake/python-ridewithgps/actions/workflows/flake8.yml)
[![mypy](https://github.com/ckdake/python-ridewithgps/actions/workflows/mypy.yml/badge.svg)](https://github.com/ckdake/python-ridewithgps/actions/workflows/mypy.yml)
[![pylint](https://github.com/ckdake/python-ridewithgps/actions/workflows/pylint.yml/badge.svg)](https://github.com/ckdake/python-ridewithgps/actions/workflows/pylint.yml)
[![pytest](https://github.com/ckdake/python-ridewithgps/actions/workflows/pytest.yml/badge.svg)](https://github.com/ckdake/python-ridewithgps/actions/workflows/pytest.yml)

## Features

- Authenticates with the [RideWithGPS API](https://ridewithgps.com/api)
- Makes any API request, `get` or `put`, to the API.
- Built-in rate limiting, caching, and pagination.
- Use higher level abstrations like `list` to get collections of things.

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

# Update the name of an activity (trip)
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

# Simple GET: Get a list of 20 rides for this user (returned as objects)
rides = client.get(
    path=f"/users/{user_info.id}/trips.json", 
    params = {"offset": 0, "limit": 20}
)
for ride in rides.results:
    print(ride.name, ride.id)

# Automatically paginate: List up to 25 activities (trips) for this user
for ride in client.list(
    path=f"/users/{user_info.id}/trips.json",
    params={},
    limit=25,
):
    print(ride.name, ride.id)

# Automatically paginate: List all gear for this user
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
- The `list`, `get`, `put`, `post`, and `delete` methods are the recommended interface for making API requests; see the code and [RideWithGPS API docs](https://ridewithgps.com/api) for available endpoints and parameters.

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
pip install -e . .[dev]
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

2. **Run the integration test to generate a new cassette:**
   ```sh
   rm tests/cassettes/ridewithgps_integration.yaml
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
- [RideWithGPS API documentation](https://ridewithgps.com/api)

---

## License

MIT License

---

*This project is not affiliated with or endorsed by RideWithGPS.*
