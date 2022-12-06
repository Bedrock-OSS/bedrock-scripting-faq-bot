# bedrock-scripting-faq-bot
A bot for the Bedrock Addons Community Discord server

# Contributing

## Setting up Python

Start by forking the repository.

Clone it on your device and run:

```bash
python -m venv .venv

source <path/to/.venv>/bin/activate

pip install -r requirements.txt
```

## Files

### ENV

Then create a file called `.env` in the main directory of this repository and add your bot token:

```
TOKEN=<your bot token>
```

### Config

And in [`config`](./config) create a new file called `ids.json` (or `ids.jsonc`) as well. Input all your test-server roles like they are written in [`ids_EXAMPLE.jsonc`](./config/ids_EXAMPLE.jsonc) (there is a json scheme defined, which helps you create all the necessary attributes).

Last step: If you already have a WORKING `faq.json` file, add in inside [`config`](./config) as `faq.json`. Otherwise the bot will create an empty one for you.

WARNING: This bot does not work with json-files created from the old `bedrock-scripting-faq-bot` out of the box. But to make them compatible, simply
- rename all the `info`-fields to `description` 
- rename all the `tag`-fields to `tags`
- remove the `faq_data` object that surrounds the data

It should look something like this:

```json
[
    {
        "tags": ["...", ...],
        "title": "...",
        "description": "...",
        "image": "..."
    },
    {
        "tags": ["...", ...],
        "title": "...",
        "description": "...",
        "image": "..."
    },
    ...
]
```

## Running the bot

Now you can start the bot by running:

```bash
python main.py
```
