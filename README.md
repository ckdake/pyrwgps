# python-ridewithgps

A simple Python client for the [RideWithGPS API](https://ridewithgps.com/api).

## Features

- Authenticate with the [RideWithGPS API](https://ridewithgps.com/api)
- Make basic API requests (routes, activities, etc.)
- Lightweight and easy to use

## Installation

```sh
pip install ridewithgps
```

Or, for local development:

```sh
git clone https://github.com/ckdake/ridewithgps.git
cd ridewithgps
pip install -r requirements.txt
```

## Usage

```python
from ridewithgps import RideWithGPS

client = RideWithGPS(api_key='YOUR_API_KEY')
routes = client.get_routes()
print(routes)
```

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
   pip install -r requirements.txt
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
   Edit `setup.py` (or `pyproject.toml` if using PEP 517/518) and increment the version.

2. **Install build tools**  
   ```sh
   pip install build twine
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

For more details on the API, see the [RideWithGPS API documentation](https://ridewithgps.com/api).

## License

MIT License

---

*This project is not affiliated with RideWithGPS.*
