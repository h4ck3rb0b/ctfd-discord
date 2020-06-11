from ctf_manager import CtfManager
import discord


class CtfdDiscordClient(discord.Client):
    def __init__(self):
        super().__init__()
        self.ctf_manager = CtfManager()

    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        msg = message.content

        if msg.startswith("$set username"):
            self.ctf_manager.username = msg.split(" ", 2)[-1]
        if msg.startswith("$set password"):
            self.ctf_manager.password = msg.split(" ", 2)[-1]
        if msg.startswith("$set url"):
            self.ctf_manager.url = msg.split(" ", 2)[-1]
        if msg.startswith("$start"):
            self.ctf_manager.start()
