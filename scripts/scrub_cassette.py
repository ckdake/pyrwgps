import yaml
import re
import random
import os
import json
import shutil

CASSETTE_PATH = os.path.join(
    os.path.dirname(__file__), "../tests/cassettes/ridewithgps_integration.yaml"
)
ORIGINAL_PATH = CASSETTE_PATH + ".original"


def get_json_body(interaction):
    """Safely extract the JSON string from the YAML cassette interaction."""
    body = interaction["response"]["body"]["string"]
    if isinstance(body, dict):
        body = json.dumps(body)
    if isinstance(body, list):
        body = "".join(body)
    return body.strip()


def fake_id(real_id, id_map, prefix):
    if not real_id:
        return real_id
    if real_id not in id_map:
        id_map[real_id] = int(f"{prefix}{random.randint(100000,999999)}")
    return id_map[real_id]


def scrub_user(user, id_maps):
    # For now, don't scrube the user_id; just leave it as is
    # user['id'] = fake_id(user['id'], id_maps['user'], 1)
    user["first_name"] = "Fake"
    user["last_name"] = "User"
    user["email"] = "fakeuser@example.com"
    user["display_name"] = "FAKEUSER"
    user["locality"] = "Faketown"
    user["administrative_area"] = "TestState"
    user["postal_code"] = "00000"
    user["country_code"] = "XX"
    user["name"] = "FakeUser"
    user["dob"] = "1990-01-01T00:00:00-00:00"
    user["auth_token"] = "FAKE_TOKEN"
    # Set any dict or list child of user to empty version
    for k, v in list(user.items()):
        if isinstance(v, dict):
            user[k] = {}
        elif isinstance(v, list):
            user[k] = []
    if "gear" in user and isinstance(user["gear"], list):
        for gear in user["gear"]:
            gear["id"] = fake_id(gear.get("id"), id_maps["gear"], 2)
            gear["group_membership_id"] = fake_id(
                gear.get("group_membership_id"), id_maps["group"], 3
            )
            gear["name"] = "FakeGear"
            gear["nickname"] = "FakeGear"
    return user


def scrub_results(results, id_maps):
    for ride in results:
        ride["id"] = fake_id(ride.get("id"), id_maps["ride"], 4)
        # For now, do not replace user_id in rides; just leave it as is
        # if 'user_id' in ride:
        #     ride['user_id'] = fake_id(ride['user_id'], id_maps['user'], 1)
        if "gear_id" in ride and ride["gear_id"]:
            ride["gear_id"] = fake_id(ride["gear_id"], id_maps["gear"], 2)
        if "group_membership_id" in ride and ride["group_membership_id"]:
            ride["group_membership_id"] = fake_id(
                ride["group_membership_id"], id_maps["group"], 3
            )
        ride["name"] = "FakeActivity"
        ride["locality"] = "Faketown"
        ride["administrative_area"] = "TestState"
        ride["country_code"] = "XX"
    return results


def scrub_string(s):
    s = re.sub(r"[\w\.-]+@[\w\.-]+", "fakeuser@example.com", s)
    # Replace auth_token with preserved quotes (or none)
    s = re.sub(r'(auth_token)(["\']?)\s*:\s*\2[^"\']*\2', r"\1\2:\2FAKE_TOKEN\2", s)
    return s


def scrub_uri(uri, id_maps):
    # For now, Do not replace user IDs in the path; just return the original URI
    return uri
    # Later, figure out how to replace user IDs in the path but not break VCR. e.g.
    # match = re.search(r'/users/(\d+)/trips\.json', uri)
    # if match:
    #     real_id = int(match.group(1))
    #     fake_userid = fake_id(real_id, id_maps['user'], 1)
    #     uri = uri.replace(f"/users/{real_id}/", f"/users/{fake_userid}/")
    # return uri


def main():
    # Copy original cassette to .original if not already present
    if not os.path.exists(ORIGINAL_PATH):
        shutil.copyfile(CASSETTE_PATH, ORIGINAL_PATH)
        print(f"Original cassette backed up to {ORIGINAL_PATH}")

    with open(ORIGINAL_PATH) as f:
        cassette = yaml.safe_load(f)

    id_maps = {"user": {}, "gear": {}, "ride": {}, "group": {}}

    for interaction in cassette["interactions"]:
        if "/users/current.json" in interaction["request"]["uri"]:
            body = get_json_body(interaction)
            resp = json.loads(body)
            # Scrub user and remove labs
            resp["user"] = scrub_user(resp["user"], id_maps)
            interaction["response"]["body"]["string"] = json.dumps(
                resp, ensure_ascii=False, separators=(",", ":")
            )
        if "/trips.json" in interaction["request"]["uri"]:
            body = get_json_body(interaction)
            resp = json.loads(body)
            if "results" in resp:
                resp["results"] = scrub_results(resp["results"], id_maps)
            interaction["response"]["body"]["string"] = json.dumps(
                resp, ensure_ascii=False, separators=(",", ":")
            )
        interaction["response"]["body"]["string"] = scrub_string(
            interaction["response"]["body"]["string"]
        )
        interaction["request"]["uri"] = scrub_uri(
            interaction["request"]["uri"], id_maps
        )

    with open(CASSETTE_PATH, "w") as f:
        yaml.dump(cassette, f, sort_keys=False, allow_unicode=True)

    print(f"Sanitized cassette written to {CASSETTE_PATH}")


if __name__ == "__main__":
    main()
