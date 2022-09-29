import json
import string
import difflib
import random
from datetime import datetime
random.seed(datetime.now())

from slack_sdk.socket_mode.aiohttp import SocketModeClient

class EmojiParser:
    @classmethod
    async def create(cls, client: SocketModeClient):
        self = EmojiParser()

        self.emojis = (await client.web_client.emoji_list())['emoji']
        self.users = (await client.web_client.users_list())['members']

        conversations = (await client.web_client.conversations_list())['channels']
        self.channels = [conversation for conversation in conversations if not all([conversation['is_im'], conversation['is_mpim']])]    

        self.emoji_keys = set(self.emojis.keys())

        with open("emoji_dict.json") as json_file:
            self.custom_emoji_dict = json.load(json_file)

        return self

    # Get the channel name by ID.
    def get_channel_name(self, channel_id):
        for channel in self.channels:
            if channel_id == channel['id']:
                return channel['name']

    # Get the user's name by ID.
    def get_user(self, user_id):
        for users in self.users:
            if(user_id == users['id']):
                return users['name']
        return None

    # Extract metadata from message.
    def get_metadata(self, message): 
        try:
            return message['text'], message['channel'], self.get_channel_name(message['channel']), message['user'], self.get_user(message['user']), message['ts']
        except Exception as ex:
            print("Failed to get metadata.", ex)
            return None, None, None, None, None, None

    # Convert message to lowercase and remove punctuation.
    def format_message(self, message): 
        for char in string.punctuation:
            if char not in ['_', ':', '(', ')', '&', ';', '-']:
                formatted_message = message.replace(char, ' ')
        print(message)
        return formatted_message.lower()

    # Populates reaction list by searching for matching keywords.
    def populate_reactions(self, query): 
        try:
            reactions = set()
            if query.startswith(':') and query.endswith(':'):
                reactions.add(query[1:-1])

            # Adjust this value between 0-1 to change random chance of react.
            if random.random() <= 0.15: 
                if query.startswith('j'):
                    reactions.add('j')
                
                # Adjust decimal value to determine partial match strength.
                matching_emojis = set(difflib.get_close_matches(query, self.emoji_keys, 100, 0.8)) 

                if len(matching_emojis) > 0:
                    matching_emoji_list = list(matching_emojis)
                    random_number = random.randint(1, 3 if len(matching_emoji_list) > 3 else len(matching_emoji_list))
                    num = 0 
                    while num < random_number:
                        emote = matching_emoji_list[random.randint(0, len(matching_emoji_list) - 1)]
                        if emote not in reactions:
                            reactions.add(emote)
                            num += 1

                for emoji in self.custom_emoji_dict:
                    if query in self.custom_emoji_dict[emoji]['list']:
                        reactions.add(emoji)
            return reactions
        except Exception as ex:
            print("Failed to populate reactions.", ex)

    # Add reactions found by populate_reactions() to the result set.
    def search_message_for_reactions(self, query_list): 
        result_set = set()
        for query in query_list:
            for emote in self.populate_reactions(query):
                result_set.add(emote)
        return result_set

    # Parse message.
    def parse_message(self, message): 
        text, channel, channel_name, user, username, timestamp = self.get_metadata(message)
        if text and channel and timestamp and user:
            text = self.format_message(text)
            reactions = self.search_message_for_reactions(text.split())
            return reactions, channel, channel_name, user, username, timestamp
        else:
            return None, None, None, None, None, None