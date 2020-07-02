from ctf_manager import CtfManager
import discord
import re
import traceback

SANITISE_REGEX = re.compile("[^a-zA-Z0-9-]")
SOLVED_CHANNEL = "solved"


def sanitise(name):
    return SANITISE_REGEX.sub("-", name).lower()


class CtfdDiscordClient(discord.Client):
    def __init__(self):
        super().__init__()
        self.ctf_manager = CtfManager()
        self.chall_id_to_channel = {}
        self.channel_id_to_chall_id = {}
        self.discord_categories_map = {}
        self.blocked_categories = ["General", "Voice Channels"]

    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        msg = message.content

        try:
            if msg.startswith("$set username "):
                self.ctf_manager.username = msg.split(" ", 2)[-1]
                await message.channel.send("Username set")
            if msg.startswith("$set password "):
                self.ctf_manager.password = msg.split(" ", 2)[-1]
                await message.channel.send("Password set")
            if msg.startswith("$set url "):
                self.ctf_manager.url = msg.split(" ", 2)[-1]
                await message.channel.send("URL set")
            if msg == "$fetch":
                await message.channel.send("Fetching challenges...")
                challs = self.ctf_manager.fetch()
                await message.channel.send("Challenges fetched. Creating channels...")
                await self.setup_channels(challs, message.guild)
                await message.channel.send("We are done!")
            if msg.startswith("$submit "):
                flag = msg.split(" ", 1)[-1]
                await self.submit_flag(flag, message.channel)
                await message.channel.send("Wow, flag is correct!")
            if msg == "$files":
                chall_id = self.channel_id_to_chall_id[message.channel.id]
                for f in self.ctf_manager.get_file_links(chall_id):
                    await message.channel.send(f"{f}")
            if msg == "$teardown":
                await message.channel.send("Tearing down...")
                await self.teardown()
                await message.channel.send("We are done!")
            if msg == "$help":
                await message.channel.send(
                    """
Usage:
$set username <username>
$set password <password>
$set url <url>
$fetch
$teardown

Inside channels:
$submit flag <flag>
$files
                """
                )
        except Exception as err:
            await message.channel.send(f"Exception: {traceback.format_exc()}"[:2000])

    async def teardown(self):
        for channel in self.chall_id_to_channel.values():
            await channel.delete()
        for category in self.discord_categories_map.values():
            await category.delete()
        self.chall_id_to_channel = {}
        self.channel_id_to_chall_id = {}
        self.discord_categories_map = {}

    async def setup_channels(self, challs, guild):
        self.populate_categories_map(guild)
        self.populate_channels(challs, guild)
        if SOLVED_CHANNEL not in self.discord_categories_map.keys():
            server_category = await guild.create_category(SOLVED_CHANNEL)
            self.discord_categories_map[server_category.name] = server_category

        for chall_id, chall in challs.items():
            chall_category = sanitise(
                SOLVED_CHANNEL if chall.solved else chall.category
            )

            server_category = self.discord_categories_map.get(chall_category)
            if server_category is None:
                server_category = await guild.create_category(chall_category)
                self.discord_categories_map[server_category.name] = server_category

            channel = self.chall_id_to_channel.get(chall_id)
            if channel is None:
                channel = await guild.create_text_channel(
                    sanitise(chall.name), category=server_category
                )
                self.chall_id_to_channel[chall_id] = channel
                self.channel_id_to_chall_id[channel.id] = chall_id

            files_exist_message = ""
            if chall.files_exist:
                files_exist_message = "Files exist for this challenge"
            await channel.send(
                f"""
**{chall.name}**

{chall.description}

Score: {chall.score}
Solves: {chall.solves}
Tags: {chall.tags}
{files_exist_message}
            """
            )

    async def submit_flag(self, flag, channel):
        res = self.ctf_manager.submit_flag(
            self.channel_id_to_chall_id[channel.id], flag
        )
        await channel.edit(category=self.discord_categories_map[SOLVED_CHANNEL])

    def populate_categories_map(self, guild):
        for category in guild.categories:
            if category.name not in self.blocked_categories:
                self.discord_categories_map[category.name] = category

    def populate_channels(self, challs, guild):
        challenge_names_to_id = {}
        for chall_id, chall in challs.items():
            challenge_names_to_id[sanitise(chall.name)] = chall_id

        for server_channel in guild.channels:
            chall_id = challenge_names_to_id.get(server_channel.name)
            if chall_id is not None:
                self.chall_id_to_channel[chall_id] = server_channel
                self.channel_id_to_chall_id[server_channel.id] = chall_id
