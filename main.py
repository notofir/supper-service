# https://developers.google.com/maps/documentation/places/web-service/search
import os

import requests
from slack_bolt import App
# from slack_bolt.oauth.oauth_settings import OAuthSettings
# from slack_sdk.oauth.installation_store import FileInstallationStore
# from slack_sdk.oauth.state_store import FileOAuthStateStore


# oauth_settings = OAuthSettings(
#    client_id=os.environ["SLACK_CLIENT_ID"],
#    client_secret=os.environ["SLACK_CLIENT_SECRET"],
#    scopes=["channels:read", "groups:read", "chat:write"],
#    installation_store=FileInstallationStore(base_dir="./data"),
#    state_store=FileOAuthStateStore(expiration_seconds=600, base_dir="./data")
# )


app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)


URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
KEY = os.environ.get("GOOGLE_API_KEY")
LOCATION = os.environ.get("DEFAULT_LOCATION")
RADIUS = os.environ.get("DEFAULT_RADIUS")


page_token = None


def parse_response(response):
    global page_token
    if response["status"] != "OK":
        return str(response)

    page_token = response["next_page_token"]
    restaurants = response["results"]
    result = []
    for restaurant in restaurants:
        if restaurant.get("rating", 0) >= 4:
            result.append(restaurant["name"])

    return ", ".join(result)


@app.message("next")
def next_(message, say):
    global page_token
    params = {
        "key": KEY,
        "pagetoken": page_token
    }

    response = requests.get(url=URL, params=params).json()
    say(parse_response(response))


@app.message("get")
def start(message, say):
    global page_token
    params = {
        "key": KEY,
        "location": LOCATION,
        "radius": RADIUS,
        "type": "restaurant"
    }

    response = requests.get(url=URL, params=params).json()
    say(parse_response(response))


if __name__ == "__main__":
    app.start(port=3000)
