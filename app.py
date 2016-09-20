import json
import logging

import requests

import p_config as config
from hp_tracker import api_routes as routes, message_handler, health_checker


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
        self.mh = message_handler.MessageHandler()
        self.health_checker = health_checker.HealthChecker(config.WARN_THRESHOLD)

    def tracker(self, event, context):
        """

        :param event:
        :param context:
        :return:
        """

        print "event: " + str(event) + "\n"
        print "context: " + str(context)

        should_pot = True
        potted = 0

        while should_pot:

            habitica_result = requests.get(
                                  routes.H_USER_URL,
                                  headers=routes.get_habitica_auth_header(self.h_user_id, self.h_api_token)
                              )

            user_data = habitica_result.json()["data"]
            username = user_data["profile"]["name"]

            if self.health_checker.should_auto_potion(user_data["stats"]):

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

        body = self.mh.get_potion_message(username, potted)
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

    def get_email_from_pushbullet(self):
        """

        :return:
        """

        pushbullet_user_info = requests.get(routes.P_USER_URL, headers={"Access-Token": self.p_api_key})

        return pushbullet_user_info.json()["email"]

    def run(self):
        """
        Main function to run the Habitica Auto-Potion App.
        """

        json_stats = self.tracker(self.event, self.context)
        self.logger.info(json_stats)


if __name__ == "__main__":

    app = HabiticaAutoPotionApp(None, None)
    app.run()
