import ridewithgps
import urllib.parse
import os

ridewithgpsclient = ridewithgps.RideWithGPS()

username = os.environ['RIDEWITHGPS_EMAIL']
password = os.environ['RIDEWITHGPS_PASSWORD']
apikey   = os.environ['RIDEWITHGPS_KEY']

auth = ridewithgpsclient.call(
    "/users/current.json", 
    {"email": username, "password": password, "apikey": apikey, "version": 2}
)

userid =  auth['user']['id']
auth_token = auth['user']['auth_token']

rides = ridewithgpsclient.call(
    "/users/{0}/trips.json".format(userid),
    {"offset": 0, "limit": 20, "apikey": apikey, "version": 2, "auth_token": auth_token}
)

print(rides)
