import discord
from discord import app_commands
from discord.ext import commands

from utils.embeds import (
    embed_em_servico,
    embed_entrada,
    embed_saida,
    embed_resposta_entrada,
    embed_resposta_saida,
)


class Ponto(commands.Cog):
    """Registra o listener do botão de ponto e o comando /emservico."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component:
            return

        custom_id = interaction.data.get("custom_id", "")
        if custom_id != "flowrp:bater_ponto":
            return

        try:
            db = self.bot.db
            guild_id = interaction.guild_id
            user = interaction.user

            config = db.get_config(guild_id)

            if not config["canal_registro"] or not config["canal_log"]:
                await interaction.response.send_message(
                    "⚠️ O servidor ainda não foi configurado. "
                    "Peça a um administrador para usar `/configurar`.",
                    ephemeral=True,
                )
                return

            ponto_aberto = db.get_ponto_aberto(guild_id, user.id)

            canal_log = interaction.guild.get_channel(config["canal_log"])
            if not canal_log:
                try:
                    canal_log = await self.bot.fetch_channel(config["canal_log"])
                except Exception:
                    canal_log = None

            if ponto_aberto is None:
                agora = db.registrar_entrada(guild_id, user.id)

                await interaction.response.send_message(
                    embed=embed_resposta_entrada(agora),
                    ephemeral=True,
                )

                if canal_log:
                    await canal_log.send(embed=embed_entrada(user, agora))
            else:
                entrada, saida = db.registrar_saida(guild_id, user.id)

                if entrada and saida:
                    await interaction.response.send_message(
                        embed=embed_resposta_saida(entrada, saida),
                        ephemeral=True,
                    )

                    if canal_log:
                        await canal_log.send(embed=embed_saida(user, entrada, saida))
                else:
                    await interaction.response.send_message(
                        "❌ Ocorreu um erro ao registrar sua saída.",
                        ephemeral=True,
                    )
        except Exception as e:
            print(f"[FlowRP][Ponto] ERRO: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Ocorreu um erro interno.",
                    ephemeral=True,
                )

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
