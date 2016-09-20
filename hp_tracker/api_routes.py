import requests


# HABITICA API URLS
H_USER_URL = "https://habitica.com/api/v3/user"
H_BUY_POTION_URL = "https://habitica.com/api/v3/user/buy-health-potion"

# PUSHBULLET API URLS
P_USER_URL = "https://api.pushbullet.com/v2/users/me"
P_CREATE_PUSH_URL = "https://api.pushbullet.com/v2/pushes"


# Habitica
def get_habitica_auth_header(api_user, api_token):

    return {"x-api-user": api_user, "x-api-key": api_token}


# Pushbullet
def get_pushbullet_auth_header(access_token, content_type):

    return {"Access-Token": access_token, "Content-Type": content_type}


def get_email_from_pushbullet(self):
    """

    :return:
    """

    pushbullet_user_info = requests.get(P_USER_URL, headers={"Access-Token": self.p_api_key})

    return pushbullet_user_info.json()["email"]
