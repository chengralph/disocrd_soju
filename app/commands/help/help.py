from discord.ext import commands
import discord


class Help(commands.Cog):
    @commands.command()
    async def help(self, message):
        info_board = discord.Embed(
            title="Soju🍾",
            colour=discord.Colour.blue()
        )
        info_board.add_field(name="$init", value="Initializes Player with LiChess Token.", inline=False)
        info_board.add_field(name="$game", value="$game @User to start LiChesss Game", inline=False)
        await message.send(embed=info_board)


def setup(bot):
    bot.add_cog(Help(bot))
