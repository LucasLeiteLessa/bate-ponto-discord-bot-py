import discord

from utils.constants import COR_PADRAO


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
        container.add_item(discord.ui.ActionRow(btn))

        self.add_item(container)
