import json
import os
import random
import re
import shelve
import subprocess
import time
import traceback

from slackclient import SlackClient


class SupperService:
    SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
    MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
    RTM_READ_DELAY = 1

    def __init__(self):
        # starterbot's user ID in Slack: value is assigned after the bot starts up
        self.starterbot_id = None
        self.slack_client = SlackClient(self.SLACK_BOT_TOKEN)
        self._db = shelve.open("db.shelve")
        if "restaurants" not in self._db:
            self._db["restaurants"] = {}
            self._db["yesterday"] = None

        self.suggested = self._db["yesterday"]
        self.restaurants = self._db["restaurants"]
        self.commands = {
            "rm": self.rm,
            "set": self.set,
            "refresh": self.refresh,
            "list": self.list,
            "ok": self.ok,
            "suggest": self.suggest,
            "help": self.help
        }

    def parse_bot_commands(self, slack_events):
        """
            Parses a list of events coming from the Slack RTM API to find bot commands.
            If a bot command is found, this function returns a tuple of command and channel.
            If its not found, then this function returns None, None.
        """
        for event in slack_events:
            if event["type"] == "message" and "subtype" not in event:
                user_id, message = self.parse_direct_mention(event["text"])
                if user_id == self.starterbot_id:
                    return message, event

        return None, None

    def parse_direct_mention(self, message_text):
        """
            Finds a direct mention (a mention that is at the beginning) in message text
            and returns the user ID which was mentioned. If there is no direct mention, returns None
        """
        matches = re.search(self.MENTION_REGEX, message_text)
        # the first group contains the username, the second group contains the remaining message
        return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

    def rm(self, line):
        self.restaurants.pop(line)
        return "Removed '{}' successfully.".format(line)

    def set(self, line):
        restaurant, rank = line.rsplit(" ", 1)
        self.restaurants[restaurant] = int(rank)
        return "Set '{}:{}' successfully.".format(restaurant, rank)

    def refresh(self, line):
        self._db["yesterday"] = None
        return "Refreshed successfully."

    def list(self, line):
        return "Last Supper: {}\nRestaurants: {}".format(self._db["yesterday"], json.dumps(self.restaurants))

    def ok(self, line):
        self._db["yesterday"] = self.suggested
        return "Bon Appetite! Will not suggest '{}' tomorrow.".format(self.suggested)

    def suggest(self, line):
        rankings = []
        for restaurant, rank in self.restaurants.items():
            if restaurant != self._db["yesterday"]:
                rankings.extend([restaurant] * rank)

        self.suggested = random.choice(rankings)
        return self.suggested

    def help(self, line):
        return json.dumps(list(self.commands.keys()))

    def handle_command(self, message, event):
        if " " not in message:
            command = message
            line = ""

        else:
            command, line = message.split(" ", 1)

        if command in self.commands:
            response = self.commands[command](line)

        else:
            response = "Unknown command '{}'.".format(command)

        if not isinstance(response, str):
            raise TypeError("Bad response: `{}`.".format(response))

        self._db["restaurants"] = self.restaurants
        self._db.sync()
        return response

    def run(self):
        if self.slack_client.rtm_connect(with_team_state=False):
            print("Bot connected and running!")
            # Read bot's user ID by calling Web API method `auth.test`
            self.starterbot_id = self.slack_client.api_call("auth.test")["user_id"]
            while True:
                command, event = service.parse_bot_commands(self.slack_client.rtm_read())
                if command:
                    try:
                        response = "<@{}> ; {}".format(event["user"], service.handle_command(command, event))

                    except:
                        response = traceback.format_exc()

                    self.slack_client.api_call(
                        "chat.postMessage",
                        channel=event["channel"],
                        text=response
                    )

                time.sleep(self.RTM_READ_DELAY)
        else:
            print("Connection failed. Exception traceback printed above.")

    def _commit_db(self):
        subprocess.Popen("git commit db.shelve -m \"Update {}\"".format(time.time()), shell=True).communicate()
        subprocess.Popen("git push", shell=True).communicate()

    def close(self):
        self._db.close()
        self._commit_db()


if __name__ == "__main__":
    service = SupperService()
    try:
        service.run()

    except KeyboardInterrupt:
        service.close()
        print("Closed supperservice gracefully.")
