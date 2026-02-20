import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pyrwgps import RideWithGPS


def main():
    username = os.environ.get("RIDEWITHGPS_EMAIL")
    password = os.environ.get("RIDEWITHGPS_PASSWORD")
    apikey = os.environ.get("RIDEWITHGPS_KEY")

    # Initialize client and authenticate.
    # Uses POST /api/v1/auth_tokens.json with x-rwgps-api-key header (Basic auth,
    # no OAuth required). The same API key you have today works.
    client = RideWithGPS(apikey=apikey, cache=True)
    user_info = client.authenticate(email=username, password=password)

    print(user_info.id, user_info.display_name)

    # --- v1 API: trips ---
    # Trips are available on the v1 API at /api/v1/trips.json.
    # Use result_key="trips" because the v1 response root key matches the resource name.
    print("First 30 trips (v1 API):")
    for trip in client.list(
        path="/api/v1/trips.json",
        result_key="trips",
        limit=30,
    ):
        print(trip.name, trip.id)

    # --- v1 API: routes ---
    print("First 10 routes (v1 API):")
    for route in client.list(
        path="/api/v1/routes.json",
        result_key="routes",
        limit=10,
    ):
        print(route.name, route.id)

    # --- v1 API: collections ---
    print("Collections (v1 API):")
    for collection in client.list(
        path="/api/v1/collections.json",
        result_key="collections",
    ):
        print(collection.name, collection.id)

    # --- v1 API: pinned collection ---
    print("Pinned collection (v1 API):")
    pinned = client.get(path="/api/v1/collections/pinned.json")
    print(pinned)

    # We changed something (not in this example, but good practice), so clear cache.
    client.clear_cache()

    # --- Legacy API: gear ---
    # Gear is not yet available on the v1 API; use the legacy endpoint.
    print("All gear (legacy API):")
    gear = {}
    for g in client.list(
        path=f"/users/{user_info.id}/gear.json",
        params={},
    ):
        gear[g.id] = g.nickname
    print(gear)


if __name__ == "__main__":
    main()
