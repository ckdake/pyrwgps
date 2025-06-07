import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ridewithgps import RideWithGPS


def main():
    username = os.environ.get("RIDEWITHGPS_EMAIL")
    password = os.environ.get("RIDEWITHGPS_PASSWORD")
    apikey = os.environ.get("RIDEWITHGPS_KEY")

    # Initialize client and authenticate
    client = RideWithGPS(apikey=apikey)
    user_info = client.authenticate(email=username, password=password)

    print(user_info.id, user_info.display_name)

    # Get a list of 20 rides for this user (returned as objects)
    rides = client.get(
        path=f"/users/{user_info.id}/trips.json", params={"offset": 0, "limit": 20}
    )
    for ride in rides.results:
        print(ride.name, ride.id)


if __name__ == "__main__":
    main()
