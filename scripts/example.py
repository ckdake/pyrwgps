import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ridewithgps import RideWithGPS


def main():
    username = os.environ.get("RIDEWITHGPS_EMAIL")
    password = os.environ.get("RIDEWITHGPS_PASSWORD")
    apikey = os.environ.get("RIDEWITHGPS_KEY")

    # Initialize client and authenticate with caching enabled
    client = RideWithGPS(apikey=apikey, cache=True)
    user_info = client.authenticate(email=username, password=password)

    print(user_info.id, user_info.display_name)

    # List up to 30 activities (trips) for this user
    print("First 30 activities:")
    for ride in client.list(
        path=f"/users/{user_info.id}/trips.json",
        params={},
        limit=30,
    ):
        print(ride.name, ride.id)

    # List all gear for this user
    print("All gear:")
    gear = {}
    for g in client.list(
        path=f"/users/{user_info.id}/gear.json",
        params={},
    ):
        gear[g.id] = g.nickname
    print(gear)

if __name__ == "__main__":
    main()
