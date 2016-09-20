import logging


class HealthChecker:

    def __init__(self, warn_threshold):
        self.logger = logging.getLogger()
        self.warn_threshold = warn_threshold

    def should_auto_potion(self, user_json):
        """
        Determines whether to auto_potion or not.

        :param user_json: Raw JSON from Habitica's API
        :return: boolean
        """

        print "HealthChecker.should_auto_potion() ==> " + str(user_json["hp"])
        self.logger.info(user_json["hp"])

        return \
            self._health_below_percentage(user_json["hp"], user_json["maxHealth"]) or \
            self._health_below_threshold(user_json["hp"])

    def _health_below_threshold(self, current_hp):
        """
        Determines whether to auto-potion or not depending on health value set by user.

        :param current_hp: float from Habitica's API
        :return: boolean
        """

        return current_hp < self.warn_threshold if isinstance(self.warn_threshold, int) else False

    def _health_below_percentage(self, current_hp, max_hp):
        """
        Determines whether to auto-potion or not depending on health percentage set by user.

        :param current_hp: float from Habitica's API
        :param max_hp: float from Habitica's API
        :return: boolean
        """

        return (current_hp / max_hp) < self.warn_threshold if isinstance(self.warn_threshold, float) else False
