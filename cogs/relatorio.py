import discord
from datetime import datetime, time
from discord import app_commands
from discord.ext import commands, tasks

from utils.constants import FUSO
from utils.embeds import embed_base, embed_relatorio_diario, embed_relatorio_periodo


class Relatorio(commands.Cog):
    """Relatórios automáticos e sob demanda."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.relatorio_diario.start()

    def cog_unload(self):
        self.relatorio_diario.cancel()

    # ── Relatório diário automático (23:59 BRT) ──────────────

    @tasks.loop(time=time(hour=23, minute=59, tzinfo=FUSO))
    async def relatorio_diario(self):
        hoje = datetime.now(FUSO)

        for guild in self.bot.guilds:
            try:
                config = self.bot.db.get_config(guild.id)
                canal_id = config.get("canal_registro")
                if not canal_id:
                    continue

                canal = guild.get_channel(canal_id)
                if not canal:
                    continue

                registros = self.bot.db.get_todos_pontos_dia(guild.id, hoje)
                embed = embed_relatorio_diario(hoje, registros, guild)
                await canal.send(embed=embed)
            except Exception as e:
                print(f"[FlowRP] Erro no relatório diário ({guild.name}): {e}")

    @relatorio_diario.before_loop
    async def before_relatorio(self):
        await self.bot.wait_until_ready()

    # ── Relatório por período (comando) ──────────────────────

    @app_commands.command(
        name="relatorio",
        description="Gera um relatório de ponto por período",
    )
    @app_commands.describe(
        inicio="Data inicial (DD/MM/AAAA)",
        fim="Data final (DD/MM/AAAA)",
        membro="Filtrar por membro específico (opcional)",
    )
    @app_commands.default_permissions(administrator=True)
    async def relatorio(
        self,
        interaction: discord.Interaction,
        inicio: str,
        fim: str,
        membro: discord.Member | None = None,
    ):
        try:
            data_inicio = datetime.strptime(inicio, "%d/%m/%Y").replace(tzinfo=FUSO)
            data_fim = datetime.strptime(fim, "%d/%m/%Y").replace(
                hour=23, minute=59, second=59, tzinfo=FUSO
            )
        except ValueError:
            await interaction.response.send_message(
                embed=embed_base(
                    "❌ Formato Inválido",
                    "Use o formato **DD/MM/AAAA** para as datas.\n"
                    "Exemplo: `01/03/2026`",
                ),
                ephemeral=True,
            )
            return

        if data_inicio > data_fim:
            await interaction.response.send_message(
                embed=embed_base(
                    "❌ Período Inválido",
                    "A data inicial deve ser anterior à data final.",
                ),
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        if membro:
            registros_raw = self.bot.db.get_pontos_periodo(
                interaction.guild_id, membro.id, data_inicio, data_fim
            )
            registros = {str(membro.id): registros_raw} if registros_raw else {}
        else:
            registros = self.bot.db.get_todos_pontos_periodo(
                interaction.guild_id, data_inicio, data_fim
            )

        embeds = embed_relatorio_periodo(
            data_inicio, data_fim, registros, interaction.guild
        )

        for embed in embeds:
            await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Relatorio(bot))
