import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any

FUSO = ZoneInfo("America/Sao_Paulo")
DB_PATH = "data/bateponto.sqlite3"

class SQLiteManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._criar_tabelas()

    def _criar_tabelas(self):
        cur = self.conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS config (
                guild_id INTEGER PRIMARY KEY,
                canal_registro INTEGER,
                canal_log INTEGER
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS ponto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                entrada TEXT NOT NULL,
                saida TEXT
            )
        ''')
        self.conn.commit()

    # ── Configuração ─────────────────────────────
    def get_config(self, guild_id: int) -> dict:
        cur = self.conn.cursor()
        cur.execute("SELECT canal_registro, canal_log FROM config WHERE guild_id=?", (guild_id,))
        row = cur.fetchone()
        return {
            "canal_registro": row["canal_registro"] if row else None,
            "canal_log": row["canal_log"] if row else None,
        }

    def set_canal_registro(self, guild_id: int, canal_id: int):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO config (guild_id, canal_registro) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET canal_registro=excluded.canal_registro", (guild_id, canal_id))
        self.conn.commit()

    def set_canal_log(self, guild_id: int, canal_id: int):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO config (guild_id, canal_log) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET canal_log=excluded.canal_log", (guild_id, canal_id))
        self.conn.commit()

    # ── Ponto ────────────────────────────────────
    def registrar_entrada(self, guild_id: int, user_id: int) -> datetime:
        agora = datetime.now(FUSO)
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO ponto (guild_id, user_id, entrada, saida) VALUES (?, ?, ?, NULL)",
            (guild_id, user_id, agora.isoformat()),
        )
        self.conn.commit()
        return agora

    def registrar_saida(self, guild_id: int, user_id: int) -> tuple[Any, Any]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, entrada FROM ponto WHERE guild_id=? AND user_id=? AND saida IS NULL ORDER BY entrada DESC LIMIT 1",
            (guild_id, user_id),
        )
        row = cur.fetchone()
        if not row:
            return None, None
        entrada = datetime.fromisoformat(row["entrada"])
        saida = datetime.now(FUSO)
        cur.execute(
            "UPDATE ponto SET saida=? WHERE id=?",
            (saida.isoformat(), row["id"]),
        )
        self.conn.commit()
        return entrada, saida

    def get_ponto_aberto(self, guild_id: int, user_id: int) -> dict | None:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT entrada FROM ponto WHERE guild_id=? AND user_id=? AND saida IS NULL ORDER BY entrada DESC LIMIT 1",
            (guild_id, user_id),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {"entrada": row["entrada"], "saida": None}

    def get_pontos_periodo(self, guild_id: int, user_id: int, inicio: datetime, fim: datetime) -> list[dict]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT entrada, saida FROM ponto WHERE guild_id=? AND user_id=? AND entrada BETWEEN ? AND ?",
            (guild_id, user_id, inicio.isoformat(), fim.isoformat()),
        )
        return [dict(row) for row in cur.fetchall()]

    def get_todos_pontos_dia(self, guild_id: int, data: datetime) -> dict[str, list[dict]]:
        cur = self.conn.cursor()
        data_ini = data.replace(hour=0, minute=0, second=0, microsecond=0)
        data_fim = data.replace(hour=23, minute=59, second=59, microsecond=999999)
        cur.execute(
            "SELECT user_id, entrada, saida FROM ponto WHERE guild_id=? AND entrada BETWEEN ? AND ?",
            (guild_id, data_ini.isoformat(), data_fim.isoformat()),
        )
        resultado = {}
        for row in cur.fetchall():
            uid = str(row["user_id"])
            if uid not in resultado:
                resultado[uid] = []
            resultado[uid].append({"entrada": row["entrada"], "saida": row["saida"]})
        return resultado

    def get_todos_pontos_periodo(self, guild_id: int, inicio: datetime, fim: datetime) -> dict[str, list[dict]]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT user_id, entrada, saida FROM ponto WHERE guild_id=? AND entrada BETWEEN ? AND ?",
            (guild_id, inicio.isoformat(), fim.isoformat()),
        )
        resultado = {}
        for row in cur.fetchall():
            uid = str(row["user_id"])
            if uid not in resultado:
                resultado[uid] = []
            resultado[uid].append({"entrada": row["entrada"], "saida": row["saida"]})
        return resultado

    def get_todos_pontos_abertos(self, guild_id: int) -> dict[str, datetime]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT user_id, entrada FROM ponto WHERE guild_id=? AND saida IS NULL",
            (guild_id,),
        )
        return {str(row["user_id"]): datetime.fromisoformat(row["entrada"]) for row in cur.fetchall()}
