This is a lightweight RideWithGPS API client in python. For now it's a wrapper on 
urllib3 using https://github.com/shazow/apiclient as a prototype.  Once it's done,
it will speak python objects instead of JSON.

API Docs here: https://ridewithgps.com/api

note:  issue a PUT or a PATCH to https://ridewithgps.com/trips/{id}.json, with a JSON post body or a form encoded body that contains 'trip[name]' in the case of a form body, or "{trip: {name: 'new name'}}" in the case of JSON. JSON is the easiest.

If your client doesn't support PUT or PATCH, use the method hack. Meaning, in your form post, include a field method set to 'PUT'.

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
