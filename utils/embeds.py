import discord
from datetime import datetime, timedelta

from utils.constants import COR_PADRAO, NOME_BOT, FUSO


def formatar_duracao(delta: timedelta) -> str:
    total_segundos = max(int(delta.total_seconds()), 0)
    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    return f"{horas}h{minutos:02d}min"


def embed_base(titulo: str, descricao: str | None = None) -> discord.Embed:
    embed = discord.Embed(
        title=titulo,
        description=descricao,
        color=COR_PADRAO,
        timestamp=datetime.now(FUSO),
    )
    embed.set_footer(text=f"{NOME_BOT} • Sistema de Ponto")
    return embed


# ── Painel ────────────────────────────────────────────────────

def embed_painel() -> discord.Embed:
    return embed_base(
        "⏰ Bate-Ponto | FlowRP",
        "Clique no botão abaixo para **registrar sua entrada** ou **saída**.\n\n"
        "📥 Se você **não está em serviço**, será registrada uma **entrada**.\n"
        "📤 Se você **está em serviço**, será registrada uma **saída**.",
    )


# ── Entrada / Saída (log) ────────────────────────────────────

def embed_entrada(usuario: discord.Member, horario: datetime) -> discord.Embed:
    embed = embed_base("📥 Entrada Registrada")
    embed.add_field(name="Membro", value=usuario.mention, inline=True)
    embed.add_field(name="Horário", value=horario.strftime("%H:%M:%S"), inline=True)
    embed.add_field(name="Data", value=horario.strftime("%d/%m/%Y"), inline=True)
    embed.set_thumbnail(url=usuario.display_avatar.url)
    return embed


def embed_saida(
    usuario: discord.Member, entrada: datetime, saida: datetime
) -> discord.Embed:
    duracao = saida - entrada
    embed = embed_base("📤 Saída Registrada")
    embed.add_field(name="Membro", value=usuario.mention, inline=True)
    embed.add_field(name="Entrada", value=entrada.strftime("%H:%M:%S"), inline=True)
    embed.add_field(name="Saída", value=saida.strftime("%H:%M:%S"), inline=True)
    embed.add_field(name="Duração", value=formatar_duracao(duracao), inline=True)
    embed.add_field(name="Data", value=saida.strftime("%d/%m/%Y"), inline=True)
    embed.set_thumbnail(url=usuario.display_avatar.url)
    return embed


# ── Respostas efêmeras ───────────────────────────────────────

def embed_resposta_entrada(horario: datetime) -> discord.Embed:
    return embed_base(
        "📥 Ponto Registrado",
        f"Sua **entrada** foi registrada às **{horario.strftime('%H:%M:%S')}**.\n"
        "Bom trabalho! 💼",
    )


def embed_resposta_saida(entrada: datetime, saida: datetime) -> discord.Embed:
    duracao = saida - entrada
    return embed_base(
        "📤 Ponto Registrado",
        f"Sua **saída** foi registrada às **{saida.strftime('%H:%M:%S')}**.\n"
        f"Você trabalhou por **{formatar_duracao(duracao)}**.\n"
        "Até a próxima! 👋",
    )


# ── Configuração ─────────────────────────────────────────────

def embed_em_servico(
    membros: dict[str, datetime], guild: discord.Guild
) -> discord.Embed:
    embed = embed_base("🟢 Membros em Serviço")

    if not membros:
        embed.description = "Nenhum membro está em serviço no momento."
        return embed

    agora = datetime.now(FUSO)
    linhas: list[str] = []

    for user_id, entrada in membros.items():
        membro = guild.get_member(int(user_id))
        nome = membro.mention if membro else f"Usuário ({user_id})"
        duracao = agora - entrada
        linhas.append(
            f"👤 {nome}\n"
            f"　⏰ Entrada: **{entrada.strftime('%H:%M:%S')}** — "
            f"Há **{formatar_duracao(duracao)}**"
        )

    embed.description = "\n\n".join(linhas)
    return embed


def embed_config_sucesso(tipo: str, canal: discord.TextChannel) -> discord.Embed:
    return embed_base(
        "✅ Configuração Atualizada",
        f"O canal de **{tipo}** foi definido para {canal.mention}.",
    )


# ── Relatório Diário ─────────────────────────────────────────

def embed_relatorio_diario(
    data: datetime, registros: dict[str, list[dict]], guild: discord.Guild
) -> discord.Embed:
    embed = embed_base(f"📋 Relatório Diário — {data.strftime('%d/%m/%Y')}")

    if not registros:
        embed.description = "Nenhum registro de ponto encontrado para hoje."
        return embed

    linhas: list[str] = []

    for user_id, pontos in registros.items():
        membro = guild.get_member(int(user_id))
        nome = membro.display_name if membro else f"Usuário ({user_id})"

        total_segundos = 0
        detalhes: list[str] = []

        for ponto in pontos:
            entrada = datetime.fromisoformat(ponto["entrada"])
            if ponto["saida"]:
                saida = datetime.fromisoformat(ponto["saida"])
                duracao = saida - entrada
                total_segundos += duracao.total_seconds()
                detalhes.append(
                    f"　⏰ {entrada.strftime('%H:%M')} → {saida.strftime('%H:%M')} "
                    f"({formatar_duracao(duracao)})"
                )
            else:
                detalhes.append(
                    f"　⚠️ {entrada.strftime('%H:%M')} → **Pendente**"
                )

        total_fmt = formatar_duracao(timedelta(seconds=total_segundos))
        linhas.append(f"👤 **{nome}** — Total: **{total_fmt}**")
        linhas.extend(detalhes)
        linhas.append("")

    embed.description = "\n".join(linhas)
    return embed


# ── Relatório por Período ────────────────────────────────────

def embed_relatorio_periodo(
    inicio: datetime,
    fim: datetime,
    registros: dict[str, list[dict]],
    guild: discord.Guild,
) -> list[discord.Embed]:
    titulo = f"📋 Relatório — {inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}"

    if not registros:
        embed = embed_base(titulo, "Nenhum registro de ponto encontrado neste período.")
        return [embed]

    linhas: list[str] = []

    for user_id, pontos in registros.items():
        membro = guild.get_member(int(user_id))
        nome = membro.display_name if membro else f"Usuário ({user_id})"

        total_segundos = 0
        detalhes: list[str] = []

        for ponto in pontos:
            entrada = datetime.fromisoformat(ponto["entrada"])
            if ponto["saida"]:
                saida = datetime.fromisoformat(ponto["saida"])
                duracao = saida - entrada
                total_segundos += duracao.total_seconds()
                detalhes.append(
                    f"　📅 {entrada.strftime('%d/%m')} — "
                    f"{entrada.strftime('%H:%M')} → {saida.strftime('%H:%M')} "
                    f"({formatar_duracao(duracao)})"
                )
            else:
                detalhes.append(
                    f"　⚠️ {entrada.strftime('%d/%m')} — "
                    f"{entrada.strftime('%H:%M')} → **Pendente**"
                )

        total_fmt = formatar_duracao(timedelta(seconds=total_segundos))
        linhas.append(f"👤 **{nome}** — Total: **{total_fmt}**")
        linhas.extend(detalhes)
        linhas.append("")

    texto = "\n".join(linhas)

    # Embed description limit: 4096 chars — dividir se necessário
    if len(texto) <= 4000:
        embed = embed_base(titulo)
        embed.description = texto
        return [embed]

    embeds: list[discord.Embed] = []
    pedaco: list[str] = []
    tamanho_atual = 0

    for linha in linhas:
        if tamanho_atual + len(linha) + 1 > 3900 and pedaco:
            e = embed_base(titulo if not embeds else f"{titulo} (cont.)")
            e.description = "\n".join(pedaco)
            embeds.append(e)
            pedaco = []
            tamanho_atual = 0
        pedaco.append(linha)
        tamanho_atual += len(linha) + 1

    if pedaco:
        e = embed_base(titulo if not embeds else f"{titulo} (cont.)")
        e.description = "\n".join(pedaco)
        embeds.append(e)

    return embeds
