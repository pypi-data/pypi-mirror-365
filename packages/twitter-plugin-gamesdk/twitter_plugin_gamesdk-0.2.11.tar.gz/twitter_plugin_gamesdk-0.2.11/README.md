# Twitter Plugin for GAME SDK

The **Twitter Plugin** provides a lightweight interface for integrating Twitter (X) functionality into your GAME SDK agents. Built on top of [`virtuals_tweepy`](https://pypi.org/project/virtuals-tweepy/) by the Virtuals team — a maintained fork of [`Tweepy`](https://pypi.org/project/tweepy/)) — this plugin lets you easily post tweets, fetch data, and execute workflows through agent logic.

## 📜 GAME X API Usage Terms & Rules
By using our GAME API, you agree to the [Terms of Use](https://virtualsprotocol.notion.site/Terms-of-Use-2152d2a429e980f09a74c85c0a5974c4?source=copy_link) and [GAME X API Terms](https://virtualsprotocol.notion.site/Agents-on-X-Rulebook-1972d2a429e980ddaa85da3c903afade?pvs=74).

## 🚀 API Access Tiers
Virtuals sponsors the community with a **Twitter Enterprise API access plan**, using OAuth 2.0 with PKCE. This provides:

## 🚀 API Access Tiers
### Tier 1 — Default
- Higher rate limits: **50 calls / 5 minutes**
- Smoother onboarding
- Free usage via your `GAME_API_KEY`

### Tier 2 — Elevated
- Even higher rate limits
- Requires approval from the Virtuals team. Request access via Discord → @virtualsio

---
Use it standalone or compose multiple Twitter actions as part of a larger agent job.

## Installation

You can install the plugin using either `poetry` or `pip`:

```bash
# Using Poetry (from the plugin directory)
poetry install
```
or
```bash
# Using pip (recommended for integration projects)
pip install twitter_plugin_gamesdk
```

---

## Authentication Methods
Virtuals sponsors the community with a **Twitter Enterprise API access plan**, using OAuth 2.0 with PKCE. This provides:

- Higher rate limits: **35 calls / 5 minutes**
- Smoother onboarding
- Free usage via your `GAME_API_KEY`

#### 1. Get Your Access Token

Run the following command to authenticate using your `GAME_API_KEY`:

```bash
poetry run twitter-plugin-gamesdk auth -k <GAME_API_KEY>
```

This will prompt:

```bash
Waiting for authentication...

Visit the following URL to authenticate:
https://x.com/i/oauth2/authorize?...

Authenticated! Here's your access token:
apx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 2. Store Your Access Token

We recommend storing environment variables in a `.env` file:

```
# .env

GAME_TWITTER_ACCESS_TOKEN=apx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Then, use `load_dotenv()` to load them:

```python
import os
from dotenv import load_dotenv
from twitter_plugin_gamesdk.twitter_plugin import TwitterPlugin

load_dotenv()

options = {
    "credentials": {
        "game_twitter_access_token": os.environ.get("GAME_TWITTER_ACCESS_TOKEN")
    }
}

twitter_plugin = TwitterPlugin(options)
client = twitter_plugin.twitter_client

client.create_tweet(text="Tweeting with GAME Access Token!")
```
---

## Examples

Explore the [`examples/`](./examples) directory for sample scripts demonstrating how to:

- Post tweets
- Reply to mentions
- Quote tweets
- Fetch user timelines
- And more!

---

## API Reference

This plugin wraps [`virtuals_tweepy`](https://pypi.org/project/virtuals-tweepy/), which is API-compatible with [Tweepy’s client interface](https://docs.tweepy.org/en/stable/client.html). Refer to their docs for supported methods and parameters.

---
