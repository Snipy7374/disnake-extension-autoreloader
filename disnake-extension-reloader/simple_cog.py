import disnake
from disnake.ext import commands

class Test(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
    
    @commands.command()
    async def sus(self, ctx):
        await ctx.reply(f"Sus {ctx.author} (lmao)")
    
def setup(bot):
    bot.add_cog(Test(bot))