# Telegram Messages Gateway

## How to install:

Clone the repo:

```
cd /tmp && git clone https://github.com/xi0n-io/telegram-messages-gateway.git
```

Copy the script to /usr/local/bin (may require additional permissions):

```
cp telegram-messages-gateway/telegram-messages-gateway.py /usr/local/bin/telegram
```

Add the execute permission to the script (may require additional permissions):

```
chmod +x /usr/local/bin/telegram
```

See if installation was successful:
```
telegram -h
```

## Usage:

```
Send a message:
    telegram -a <api> -c <chat> -m 'my message'

Send a message from stdin:
    echo 'my message' | telegram -a <api> -c <chat>

Get a list of all the available chat ids (in the last 24h) of the bot:
    telegram -i -a <api>
    telegram --ids --api <api>

Get a list of all messages received in the last 24 hours:
    telegram -ls -a <api>
    telegram --list --api <api>


Options:
     -a, --api <api>            API key of the bot that should send the message
     -c, --chat <chat>          Chat ID of the recipient
     -m, --message <message>    Do not use stdin as input
     -i, --ids                  Get all available chat ids (from last 24h) of the bot
     -ls, --list                Get a list of all the messages from the last 24 hours
     -h, --help                 Get help for commands
     -v, --verbose              Make the operation more talkative
 ```
