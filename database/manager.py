import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

FUSO = ZoneInfo("America/Sao_Paulo")
DATA_DIR = Path(__file__).parent.parent / "data"


class DatabaseManager:
    """Gerenciador de dados baseado em arquivos JSON."""

    def __init__(self):
        self._garantir_diretorios()

    def _garantir_diretorios(self):
        (DATA_DIR / "config").mkdir(parents=True, exist_ok=True)
        (DATA_DIR / "pontos").mkdir(parents=True, exist_ok=True)

    def _caminho_config(self, guild_id: int) -> Path:
        return DATA_DIR / "config" / f"{guild_id}.json"

    def _caminho_pontos(self, guild_id: int) -> Path:
        return DATA_DIR / "pontos" / f"{guild_id}.json"

    def _ler_json(self, caminho: Path) -> dict:
        if not caminho.exists():
            return {}
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)

    def _salvar_json(self, caminho: Path, dados: dict):
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

    # ── Configuração ──────────────────────────────────────────

    def get_config(self, guild_id: int) -> dict:
        config = self._ler_json(self._caminho_config(guild_id))
        return {
            "canal_registro": config.get("canal_registro"),
            "canal_log": config.get("canal_log"),
        }

    def set_canal_registro(self, guild_id: int, canal_id: int):
        config = self.get_config(guild_id)
        config["canal_registro"] = canal_id
        self._salvar_json(self._caminho_config(guild_id), config)

    def set_canal_log(self, guild_id: int, canal_id: int):
        config = self.get_config(guild_id)
        config["canal_log"] = canal_id
        self._salvar_json(self._caminho_config(guild_id), config)

    # ── Ponto ─────────────────────────────────────────────────

    def registrar_entrada(self, guild_id: int, user_id: int) -> datetime:
        pontos = self._ler_json(self._caminho_pontos(guild_id))
        chave = str(user_id)

        if chave not in pontos:
            pontos[chave] = []

        agora = datetime.now(FUSO)
        pontos[chave].append({
            "entrada": agora.isoformat(),
            "saida": None,
        })

        self._salvar_json(self._caminho_pontos(guild_id), pontos)
        return agora

    def registrar_saida(self, guild_id: int, user_id: int) -> tuple[datetime | None, datetime | None]:
        pontos = self._ler_json(self._caminho_pontos(guild_id))
        chave = str(user_id)

        if chave not in pontos or not pontos[chave]:
            return None, None

        for registro in reversed(pontos[chave]):
            if registro["saida"] is None:
                agora = datetime.now(FUSO)
                registro["saida"] = agora.isoformat()
                self._salvar_json(self._caminho_pontos(guild_id), pontos)
                entrada = datetime.fromisoformat(registro["entrada"])
                return entrada, agora

        return None, None

    def get_ponto_aberto(self, guild_id: int, user_id: int) -> dict | None:
        pontos = self._ler_json(self._caminho_pontos(guild_id))
        chave = str(user_id)

        if chave not in pontos:
            return None

        for registro in reversed(pontos[chave]):
            if registro["saida"] is None:
                return registro

        return None

    def get_pontos_periodo(
        self, guild_id: int, user_id: int, inicio: datetime, fim: datetime
    ) -> list[dict]:
        pontos = self._ler_json(self._caminho_pontos(guild_id))
        chave = str(user_id)

        if chave not in pontos:
            return []

        resultado = []
        for registro in pontos[chave]:
            entrada = datetime.fromisoformat(registro["entrada"])
            if inicio <= entrada <= fim:
                resultado.append(registro)

        return resultado

    def get_todos_pontos_abertos(self, guild_id: int) -> dict[str, datetime]:
        pontos = self._ler_json(self._caminho_pontos(guild_id))
        resultado: dict[str, datetime] = {}

        for user_id, registros in pontos.items():
            for registro in reversed(registros):
                if registro["saida"] is None:
                    resultado[user_id] = datetime.fromisoformat(registro["entrada"])
                break  # só verifica o último registro de cada usuário

        return resultado

    def get_todos_pontos_dia(self, guild_id: int, data: datetime) -> dict[str, list[dict]]:
        pontos = self._ler_json(self._caminho_pontos(guild_id))
        resultado: dict[str, list[dict]] = {}

        for user_id, registros in pontos.items():
            for registro in registros:
                entrada = datetime.fromisoformat(registro["entrada"])
                if entrada.date() == data.date():
                    if user_id not in resultado:
                        resultado[user_id] = []
                    resultado[user_id].append(registro)

        return resultado

    def get_todos_pontos_periodo(
        self, guild_id: int, inicio: datetime, fim: datetime
    ) -> dict[str, list[dict]]:
        pontos = self._ler_json(self._caminho_pontos(guild_id))
        resultado: dict[str, list[dict]] = {}

        for user_id, registros in pontos.items():
            for registro in registros:
                entrada = datetime.fromisoformat(registro["entrada"])
                if inicio <= entrada <= fim:
                    if user_id not in resultado:
                        resultado[user_id] = []
                    resultado[user_id].append(registro)

        return resultado
