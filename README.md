# ReactBot V2
- Automated slack tool which adds user reactions to messages .

# Get Started
- You'll need to create a Slack app with the following configuration:
    - Create App-Level Token with `connections:write` scope.
    - Enable Socket Mode
    - Event Subscriptions (on behalf of users):
        - `message.channels`
        - `reaction_added`
    - User Token Scopes:
        - `channels:history`
        - `channels:read`
        - `chat:write`
        - `emoji:read`
        - `groups:read`
        - `im:read`
        - `mpim:read`
        - `reactions:read`
        - `reactions:write`
        - `users:read`
- Create a `tokens.json` file with the following format:
    ```
    {
        "app_token": "YOUR APP TOKEN",
        "bot_token": "xoxp-526362008167-524703344609-4150523723972-178282c3a6547ceab2113f5bf3adf311"
    }
    ```


# Adding Custom Emoji Keywords
- Follow the format in emoji_dict.txt (outer key is the emoji name, inner list are the keywords to match)

# Commands to Install/Run
```
pip3 install slack_sdk
python bot.py
```

