import discord

from utils.constants import COR_PADRAO
from utils.embeds import (
    embed_entrada,
    embed_saida,
    embed_resposta_entrada,
    embed_resposta_saida,
)


class PainelPontoView(discord.ui.LayoutView):
    """View persistente V2 — painel de bate-ponto com botão integrado ao container."""

    def __init__(self):
        super().__init__(timeout=None)

        container = discord.ui.Container(accent_colour=COR_PADRAO)

        container.add_item(discord.ui.TextDisplay(
            "# ⏰ Bate-Ponto | FlowRP\n\n"
            "Clique no botão abaixo para **registrar sua entrada** ou **saída**.\n\n"
            "📥 Se você **não está em serviço**, será registrada uma **entrada**.\n"
            "📤 Se você **está em serviço**, será registrada uma **saída**."
        ))

        container.add_item(discord.ui.Separator())

        btn = discord.ui.Button(
            label="Bater Ponto",
            style=discord.ButtonStyle.secondary,
            custom_id="flowrp:bater_ponto",
            emoji="⏰",
        )
        btn.callback = self._bater_ponto
        container.add_item(discord.ui.ActionRow(btn))

        self.add_item(container)

    async def _bater_ponto(self, interaction: discord.Interaction):
        db = interaction.client.db
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
                canal_log = await interaction.client.fetch_channel(config["canal_log"])
            except Exception:
                canal_log = None

        if ponto_aberto is None:
            # ── Registrar entrada ─────────────────────────────
            agora = db.registrar_entrada(guild_id, user.id)

            if canal_log:
                await canal_log.send(embed=embed_entrada(user, agora))

            await interaction.response.send_message(
                embed=embed_resposta_entrada(agora),
                ephemeral=True,
            )
        else:
            # ── Registrar saída ───────────────────────────────
            entrada, saida = db.registrar_saida(guild_id, user.id)

            if entrada and saida:
                if canal_log:
                    await canal_log.send(embed=embed_saida(user, entrada, saida))

                await interaction.response.send_message(
                    embed=embed_resposta_saida(entrada, saida),
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    "❌ Ocorreu um erro ao registrar sua saída.",
                    ephemeral=True,
                )
