# python-ridewithgps

A simple Python client for the [RideWithGPS API](https://ridewithgps.com/api).

Note: this is super under development and in no way should be used without reading
all of the code first. I'll remove this notice once I'm actually using this package!

## Features

- Authenticate with the [RideWithGPS API](https://ridewithgps.com/api)
- Make basic API requests (routes, activities, etc.)
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

# Create a client instance (optionally pass API key or authentication info if needed)
client = RideWithGPS()

# Example: Fetch current user info (you may need to authenticate first)
user_info = client.call("/users/current.json", {
    "email": "your@email.com",
    "password": "yourpassword",
    "apikey": "yourapikey",
    "version": 2
})
print(user_info)

# Example: Fetch 20 rides for a user (replace user_id and auth_token as needed)
rides = client.call(f"/users/{user_info['user']['id']}/trips.json", {
    "offset": 0,
    "limit": 20,
    "apikey": "yourapikey",
    "version": 2,
    "auth_token": user_info['user']['auth_token']
})
print(rides)
```

**Note:**  
- You must provide your own RideWithGPS credentials and API key.
- The `call` method is a thin wrapper for making API requests; see the code and [RideWithGPS API docs](https://ridewithgps.com/api) for available endpoints and parameters.

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
   pytest
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
