from importlib.resources import path
import disnake
from disnake.ext import commands
import asyncio
from extension import ExtensionLoader

class MyBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix=commands.when_mentioned, intents=disnake.Intents.default(), test_guilds=[826100750111211623], sync_commands_debug=True)
    
    async def on_ready(self) -> None:
        print(f"Logged in as {self.user} (Test bot)")
    
bot = MyBot()

async def main() -> None:
    asyncio.create_task(bot.start("LMAO")) # btw i've resetted the token

    changes = ExtensionLoader(paths="./simple_cog.py", project_path="./", ignore_paths=None, bot=bot, extension_loader_debug=True)
    print(changes.files)

    await changes.watch_for_changes()

asyncio.run(main())
