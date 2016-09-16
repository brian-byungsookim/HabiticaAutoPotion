# HABITICA API URLS
H_USER_URL = "https://habitica.com/api/v3/user"
H_BUY_POTION_URL = "https://habitica.com/api/v3/user/buy-health-potion"

# PUSHBULLET API URLS
P_USER_URL = "https://api.pushbullet.com/v2/users/me"
P_CREATE_PUSH_URL = "https://api.pushbullet.com/v2/pushes"


# AUTH HEADERS
def get_habitica_auth_header(api_user, api_token):

    return {"x-api-user": api_user, "x-api-key": api_token}


def get_pushbullet_auth_header(access_token, content_type):

    return {"Access-Token": access_token, "Content-Type": content_type}
