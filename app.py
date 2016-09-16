import json
import logging

import requests

import config as config
from hp_tracker import api_routes as routes


class HabiticaAutoPotionApp:

    def __init__(self, event, context):
        self.event = event
        self.context = context
        self.logger = logging.getLogger(__name__)
        self.name = config.APP_NAME
        self.warn_threshold = config.WARN_THRESHOLD
        self.h_user_id = config.HABITICA_USER_ID
        self.h_api_token = config.HABITICA_API_TOKEN
        self.p_api_key = config.PUSHBULLET_API_KEY

    def tracker(self, event, context):
        """

        :param event:
        :param context:
        :return:
        """

        should_pot = True
        potted = 0

        while should_pot:

            habitica_result = requests.get(
                                  routes.H_USER_URL,
                                  headers=routes.get_habitica_auth_header(self.h_user_id, self.h_api_token)
                              )

            user_data = habitica_result.json()["data"]
            username = user_data["profile"]["name"]

            if self.should_auto_potion(user_data["stats"]):

                auto_potion_result = requests.post(
                                         routes.H_BUY_POTION_URL,
                                         headers=routes.get_habitica_auth_header(self.h_user_id, self.h_api_token)
                                     )

                # TODO: shouldn't only filter against 401s
                if auto_potion_result.status_code != 401:
                    potted += 1
                # Not enough money
                else:
                    potted = -1
                    should_pot = False

                user_data["stats"]["hp"] += 15

            else:
                should_pot = False

        body = self.build_message(username, potted)
        email = self.get_email_from_pushbullet()

        pushbullet_result = requests.post(
                                routes.P_CREATE_PUSH_URL,
                                headers=routes.get_pushbullet_auth_header(self.p_api_key, "application/json"),
                                json={
                                    "type": "note",
                                    "title": self.name,
                                    "body": body,
                                    "email": email
                                }
                            )

        self.logger.info(json.dumps(pushbullet_result.json(), indent=4))

        return json.dumps(user_data["stats"], indent=4)

    @staticmethod
    def build_message(username, potted):

        if potted < 0:
            message = "Didn't have enough gold to auto potion!"
        elif potted == 0:
            message = "Didn't need to auto potion today!"
        else:
            message = "{0} used potion (x{1})!".format(username, potted)

        return message

    def get_email_from_pushbullet(self):
        """

        :return:
        """

        pushbullet_user_info = requests.get(routes.P_USER_URL, headers={"Access-Token": self.p_api_key})

        return pushbullet_user_info.json()["email"]

    def should_auto_potion(self, user_json):
        """
        Determines whether to auto_potion or not.

        :param user_json: Raw JSON from Habitica's API
        :return: boolean
        """

        print user_json["hp"]

        return \
            self.health_below_percentage(user_json["hp"], user_json["maxHealth"]) or \
            self.health_below_threshold(user_json["hp"])

    def health_below_threshold(self, current_hp):
        """
        Determines whether to auto-potion or not depending on health value set by user.

        :param current_hp: float from Habitica's API
        :return: boolean
        """

        return current_hp < self.warn_threshold if isinstance(self.warn_threshold, int) else False

    def health_below_percentage(self, current_hp, max_hp):
        """
        Determines whether to auto-potion or not depending on health percentage set by user.

        :param current_hp: float from Habitica's API
        :param max_hp: float from Habitica's API
        :return: boolean
        """

        return (current_hp / max_hp) < self.warn_threshold if isinstance(self.warn_threshold, float) else False

    def run(self):
        """
        Main function to run the Habitica Auto-Potion App.
        """

        json_stats = self.tracker(self.event, self.context)
        self.logger.info(json_stats)


if __name__ == "__main__":

    app = HabiticaAutoPotionApp(None, None)
    app.run()
