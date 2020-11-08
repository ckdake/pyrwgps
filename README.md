This is a lightweight RideWithGPS API client in python. For now it's a wrapper on 
urllib3 using https://github.com/shazow/apiclient as a prototype.  Once it's done,
it will speak python objects instead of JSON.

API Docs here: https://ridewithgps.com/api

Python Docs TBD!

## First Run

    cd python-ridewithgps
    pip3 install virtualenv --user
    virtualenv env
    source env/bin/activate
    pip3 install -r requirements.txt
    pip3 install .
    python3 doit.py
    deactivate