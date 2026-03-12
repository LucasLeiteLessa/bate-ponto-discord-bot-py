import discord
from discord import app_commands
from discord.ext import commands

from utils.embeds import embed_em_servico
from utils.views import PainelPontoView


class Ponto(commands.Cog):
    """Registra a view persistente do bate-ponto."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.add_view(PainelPontoView())

    @app_commands.command(
        name="emservico",
        description="Mostra quem está com o ponto batido no momento",
    )
    async def em_servico(self, interaction: discord.Interaction):
        membros = self.bot.db.get_todos_pontos_abertos(interaction.guild_id)
        embed = embed_em_servico(membros, interaction.guild)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Ponto(bot))
