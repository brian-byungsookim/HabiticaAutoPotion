import json
import requests

import api_routes as routes
import p_config as config

# GLOBAL VARIABLES
WARN_THRESHOLD = 0.4

def tracker(event, context):
    
    habitica_result = requests.get(
                          routes.H_ANON_USER_URL,
                          headers={"x-api-user": config.HABITICA_USER_ID, "x-api-key": config.HABITICA_API_TOKEN}
                      )
    
    user_json = habitica_result.json()["data"]["user"]

    if should_alert(user_json["stats"]):
        auto_potion_result = requests.post(
                                 routes.H_BUY_POTION_URL,
                                 headers={"x-api-user": config.HABITICA_USER_ID, "x-api-key": config.HABITICA_API_TOKEN}
                             )

        if auto_potion_result.status_code==401:
            body="HP running low! Tried to auto-potion, but you're too poor to afford potions!"
        else:
            body="HP running low... but was able to auto-potion!"
    else:
        body = "No need to auto-potion today!"

    email = get_email_from_pushbullet()

    pushbullet_result = requests.post(
                            routes.P_CREATE_PUSH_URL,
                            headers={"Access-Token": config.PUSHBULLET_API_KEY, "Content-Type": "application/json"},
                            json={"type":"note", "title": config.APP_NAME, "body": body, "email": email}
                        )
    print json.dumps(pushbullet_result.json(), indent=4)        

    return json.dumps(user_json["stats"], indent=4)


def get_email_from_pushbullet():
    pushbullet_user_info = requests.get(routes.P_USER_URL, headers={"Access-Token": config.PUSHBULLET_API_KEY})

    return pushbullet_user_info.json()["email"]


def should_alert(user_json):

    return health_below_threshold(user_json["hp"], user_json["maxHealth"])


def health_below_threshold(current_hp, max_hp):
    return (current_hp / max_hp) < WARN_THRESHOLD


if __name__ == "__main__":
    print tracker()
