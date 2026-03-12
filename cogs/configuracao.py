import discord
from discord import app_commands
from discord.ext import commands

from utils.embeds import embed_config_sucesso, embed_base
from utils.views import PainelPontoView


class Configuracao(commands.Cog):
    """Comandos de configuração do sistema de ponto."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    configurar = app_commands.Group(
        name="configurar",
        description="Configurações do sistema de ponto",
        default_permissions=discord.Permissions(administrator=True),
    )

    @configurar.command(
        name="registro",
        description="Define o canal onde os registros de ponto serão enviados",
    )
    @app_commands.describe(canal="Canal de texto para registros de entrada e saída")
    async def configurar_registro(
        self, interaction: discord.Interaction, canal: discord.TextChannel
    ):
        self.bot.db.set_canal_registro(interaction.guild_id, canal.id)
        await interaction.response.send_message(
            embed=embed_config_sucesso("registro", canal),
            ephemeral=True,
        )

    @configurar.command(
        name="log",
        description="Define o canal de log detalhado do ponto",
    )
    @app_commands.describe(canal="Canal de texto para logs detalhados")
    async def configurar_log(
        self, interaction: discord.Interaction, canal: discord.TextChannel
    ):
        self.bot.db.set_canal_log(interaction.guild_id, canal.id)
        await interaction.response.send_message(
            embed=embed_config_sucesso("log", canal),
            ephemeral=True,
        )

    @app_commands.command(
        name="painel",
        description="Envia o painel de bate-ponto no canal atual",
    )
    @app_commands.default_permissions(administrator=True)
    async def painel(self, interaction: discord.Interaction):
        config = self.bot.db.get_config(interaction.guild_id)

        if not config["canal_registro"] or not config["canal_log"]:
            await interaction.response.send_message(
                embed=embed_base(
                    "⚠️ Configuração Incompleta",
                    "Configure os canais antes de enviar o painel:\n"
                    "• `/configurar registro #canal`\n"
                    "• `/configurar log #canal`",
                ),
                ephemeral=True,
            )
            return

        await interaction.channel.send(view=PainelPontoView())
        await interaction.response.send_message(
            "✅ Painel de ponto enviado com sucesso!",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Configuracao(bot))
