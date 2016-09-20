import logging


class MessageHandler:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_potion_message(self, username, potted):
        """
        Builds message for the user to receive.

        :param username: username to be used only if user needed to pot
        :param potted: number of times the user potted
        :return: message as a string
        """

        if potted < 0:
            message = "Didn't have enough gold to auto potion!"
        elif potted == 0:
            message = "Didn't need to auto potion today!"
        else:
            message = "{0} used potion (x{1})!".format(username, potted)

        self.logger.info("message: {0}", message)

        return message
