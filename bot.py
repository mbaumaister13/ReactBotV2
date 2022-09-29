import asyncio
import json
from emoji_parser import EmojiParser

from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.socket_mode.aiohttp import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest


async def main():
    # Read in the authentication token.
    f = open('tokens.json')
    tokens = json.load(f)
    f.close()

    # Initialize client.
    client = SocketModeClient(
        app_token=tokens['app_token'],
        web_client=AsyncWebClient(token=tokens['bot_token'])
    )

    emoji_parser = await EmojiParser.create(client)

    # Message Listener
    async def messageListener(client: SocketModeClient, req: SocketModeRequest):
        if req.type == "events_api":
            response = SocketModeResponse(envelope_id = req.envelope_id)
            await client.send_socket_mode_response(response)
            event = req.payload['event']

            if event['type'] == "message" and event['channel_type'] == "channel":
                reactions, channel, channel_name, username, timestamp = emoji_parser.parse_message(event)

                print(username, "in #" + channel_name + ",", "found reactions:", [reaction for reaction in reactions if reaction not in [None, 'a', 'b', 'o', 'i', 'u', 'thx', 'm', 'v', 'x', 't']])
                print("")

                for reaction in reactions:
                    if reaction not in [None, 'a', 'b', 'o', 'i', 'u', 'thx', 'm', 'v', 'x', 't']:
                        await client.web_client.reactions_add(
                            name=reaction,
                            channel=channel, 
                            timestamp=timestamp, 
                            as_user=True
                        )
        

    # React Listener
    async def reactListener(client: SocketModeClient, req: SocketModeRequest):
        if req.type == "events_api":
            response = SocketModeResponse(envelope_id = req.envelope_id)
            await client.send_socket_mode_response(response)
            event = req.payload['event']

            if event['type'] == "reaction_added":
                print("+" + event['reaction'] + " in #" + emoji_parser.get_channel_name(event['item']['channel']) + "\n")
                await client.web_client.reactions_add(
                    name=event['reaction'],
                    channel=event['item']['channel'],
                    timestamp=event['item']['ts'],
                    as_user=True
                )

    client.socket_mode_request_listeners.append(messageListener)
    client.socket_mode_request_listeners.append(reactListener)

    await client.connect()
    print("ReactBot is up and running!")

    # Keep process alive.
    await asyncio.sleep(float("inf"))

try:
    asyncio.run(main())
except:
    print("ReactBot shut down.")