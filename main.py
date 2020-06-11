from discord_client import CtfdDiscordClient
import os

if __name__ == "__main__":
    token = "NzIwNTMzMDg0OTEwNjQ5Mzk4.XuHW1Q.Yw_hb3Mc-AERzfpE3HJteLSu4NA"
    # token = os.environ["DISCORD_TOKEN"]
    client = CtfdDiscordClient()
    client.run(token)
