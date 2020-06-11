from discord_client import CtfdDiscordClient
import os

if __name__ == "__main__":
    token = os.environ["DISCORD_TOKEN"]
    client = CtfdDiscordClient()
    client.run(token)
