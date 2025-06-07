# python-ridewithgps

A simple Python client for the [RideWithGPS API](https://ridewithgps.com/api).

Note: this is super under development and in no way should be used without reading
all of the code first. I'll remove this notice once I'm actually using this package!

## Features

- Authenticate with the [RideWithGPS API](https://ridewithgps.com/api)
- Make basic API requests (routes, activities, etc.)
- Built-in rate limiting
- Lightweight and easy to use

## Installation

The package is published on [PyPI](https://pypi.org/project/ridewithgps/).

Install the latest release with:

```sh
pip install ridewithgps
```

For development, install the dev dependencies:

```sh
pip install -r requirements-dev.txt
```

Or, for local development with editable install:

```sh
git clone https://github.com/ckdake/ridewithgps.git
cd ridewithgps
pip install -e . -r requirements-dev.txt
```

---

## Usage

First, install the package:

```sh
pip install ridewithgps
```

Then, in your Python code:

```python
from ridewithgps import RideWithGPS

client = RideWithGPS(api_key="yourapikey")

# Authenticate client and return user_info.
user_info = client.authenticate(email="your@email.com", password="yourpassword")
print(user_info)

# Update the name of an activity (trip)
activity_id = "123456"
new_name = "Morning Ride"
response = client.put(
    f"/trips/{activity_id}.json",
    {"name": new_name}
)
updated_name = response.get("trip", {}).get("name")
if updated_name == new_name:
    print(f"Activity name updated to: {updated_name}")
else:
    print("Failed to update activity name.")

# You can also get a list of 20 rides for this user:
rides = client.get(f"/users/{user_info['id']}/trips.json", {
    "offset": 0,
    "limit": 20
})
print(rides)
```

**Note:**  
- You must provide your own RideWithGPS credentials and API key.
- The `get` and `put` methods are the recommended interface for making API requests; see the code and [RideWithGPS API docs](https://ridewithgps.com/api) for available endpoints and parameters.

## Development

### Set up environment

```sh
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### Run example script

```sh
python scripts/doit.py
```

### Run tests

```sh
python -m pytest --cov=ridewithgps --cov-report=term-missing -v
```

### Linting and Formatting

Run these tools locally to check and format your code:

- **pylint** (static code analysis):

    ```sh
    pylint ridewithgps
    ```

- **flake8** (style and lint checks):

    ```sh
    flake8 ridewithgps
    ```

- **black** (auto-formatting):

    ```sh
    black ridewithgps
    ```

- **mypy** (type checking):

    ```sh
    mypy ridewithgps
    ```

## Developer Setup

1. **Install dependencies:**
   ```sh
   pip install -r requirements-dev.txt
   ```

2. **Run tests:**
   ```sh
   python -m pytest --cov=ridewithgps --cov-report=term-missing -v
   ```

---

## Updating Integration Cassettes

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

2. **Delete or move the old cassette (optional, for a clean start):**
   ```sh
   mv tests/cassettes/ridewithgps_integration.yaml tests/cassettes/ridewithgps_integration.yaml.bak
   ```

3. **Run the integration test to generate a new cassette:**
   ```sh
   pytest -m integration
   ```

4. **Scrub sensitive data from the cassette:**
   ```sh
   python scripts/scrub_cassette.py
   ```
   - This will back up your cassette to `ridewithgps_integration.yaml.original` (if not already present).
   - The sanitized cassette will overwrite `ridewithgps_integration.yaml`.

5. **Re-run tests to verify:**
   ```sh
   pytest
   ```

---

## Publishing to PyPI

To publish a new version of this package to [PyPI](https://pypi.org/):

1. **Update the version number**  
   Edit `pyproject.toml` and increment the version.

2. **Install build tools**  
   ```sh
   pip install -r requirements-dev.txt
   ```

3. **Build the distribution**  
   ```sh
   python -m build
   ```
   This will create `dist/ridewithgps-<version>.tar.gz` and `.whl` files.

4. **Check the distribution (optional but recommended)**  
   ```sh
   twine check dist/*
   ```

5. **Upload to PyPI**  
   ```sh
   twine upload dist/*
   ```
   You will be prompted for your PyPI username and password.

6. **Open your package on PyPI (optional)**  
   ```sh
   $BROWSER https://pypi.org/project/ridewithgps/
   ```

**Note:**  
- Make sure your `~/.pypirc` is configured if you want to avoid entering credentials each time.
- For test uploads, use `twine upload --repository testpypi dist/*` and visit [TestPyPI](https://test.pypi.org/).

---

- [PyPI: ridewithgps](https://pypi.org/project/ridewithgps/)
- [RideWithGPS API documentation](https://ridewithgps.com/api)

## License

MIT License

---

*This project is not affiliated with RideWithGPS.*
