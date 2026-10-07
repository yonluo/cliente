"""Agenda web de clientes com Flask e SQLite."""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

from flask import Flask, abort, flash, redirect, render_template, request, url_for


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PADRAO = (
    Path(tempfile.gettempdir()) / "agenda_clientes.db"
    if os.environ.get("VERCEL")
    else BASE_DIR / "agenda_clientes.db"
)
DATABASE = Path(os.environ.get("AGENDA_DATABASE", DATABASE_PADRAO))
LEGACY_DATA_FILE = BASE_DIR / "clientes.json"

app = Flask(
    __name__,
    static_folder=None if os.environ.get("VERCEL") else str(BASE_DIR / "public"),
    static_url_path="",
)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "agenda-facil-local-dev")


@contextmanager
def conectar_banco() -> Generator[sqlite3.Connection, None, None]:
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row
    try:
        with conexao:
            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    telefone TEXT NOT NULL,
                    email TEXT NOT NULL DEFAULT '',
                    observacoes TEXT NOT NULL DEFAULT ''
                )
                """
            )
            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS configuracao (
                    chave TEXT PRIMARY KEY,
                    valor TEXT NOT NULL
                )
                """
            )
            migrado = conexao.execute(
                "SELECT 1 FROM configuracao WHERE chave = 'clientes_json_migrado'"
            ).fetchone()
            if migrado is None:
                quantidade = conexao.execute(
                    "SELECT COUNT(*) FROM clientes"
                ).fetchone()[0]
                if quantidade == 0 and LEGACY_DATA_FILE.exists():
                    dados = json.loads(LEGACY_DATA_FILE.read_text(encoding="utf-8"))
                    if not isinstance(dados, list):
                        raise ValueError("clientes.json precisa conter uma lista.")
                    registros = []
                    for indice, item in enumerate(dados, start=1):
                        if not isinstance(item, dict):
                            raise ValueError(
                                f"O cliente na posição {indice} não é um objeto."
                            )
                        nome = item.get("nome")
                        telefone = item.get("telefone")
                        email = item.get("email", "")
                        observacoes = item.get("observacoes", "")
                        if not isinstance(nome, str) or not nome.strip():
                            raise ValueError(
                                f"O cliente na posição {indice} não tem um nome válido."
                            )
                        if not isinstance(telefone, str) or not telefone.strip():
                            raise ValueError(
                                f"O cliente na posição {indice} não tem um telefone válido."
                            )
                        if not isinstance(email, str) or not isinstance(
                            observacoes, str
                        ):
                            raise ValueError(
                                f"Os dados opcionais do cliente na posição {indice} são inválidos."
                            )
                        registros.append((nome, telefone, email, observacoes))
                    conexao.executemany(
                        """
                        INSERT INTO clientes (nome, telefone, email, observacoes)
                        VALUES (?, ?, ?, ?)
                        """,
                        registros,
                    )
                conexao.execute(
                    """
                    INSERT INTO configuracao (chave, valor)
                    VALUES ('clientes_json_migrado', '1')
                    """
                )
            yield conexao
    finally:
        conexao.close()


def buscar_cliente(cliente_id: int) -> sqlite3.Row:
    with conectar_banco() as conexao:
        cliente = conexao.execute(
            "SELECT * FROM clientes WHERE id = ?", (cliente_id,)
        ).fetchone()
    if cliente is None:
        abort(404)
    return cliente


def renderizar_pagina(
    *,
    cliente_edicao: sqlite3.Row | dict[str, Any] | None = None,
    formulario_aberto: bool = False,
    valores: dict[str, str] | None = None,
    erro: str | None = None,
) -> str:
    with conectar_banco() as conexao:
        clientes = conexao.execute(
            "SELECT * FROM clientes ORDER BY nome COLLATE NOCASE, id"
        ).fetchall()
    return render_template(
        "index.html",
        clientes=clientes,
        cliente_edicao=cliente_edicao,
        formulario_aberto=formulario_aberto,
        valores=valores or {},
        erro=erro,
        total=len(clientes),
        total_telefone=sum(bool(cliente["telefone"]) for cliente in clientes),
        total_email=sum(bool(cliente["email"]) for cliente in clientes),
    )


@app.get("/")
def inicio() -> str:
    return renderizar_pagina()


@app.get("/clientes/novo")
def novo_cliente() -> str:
    return renderizar_pagina(formulario_aberto=True)


@app.post("/clientes/novo")
def criar_cliente() -> Any:
    valores = {
        campo: request.form.get(campo, "").strip()
        for campo in ("nome", "telefone", "email", "observacoes")
    }
    if not valores["nome"] or not valores["telefone"]:
        return renderizar_pagina(
            formulario_aberto=True,
            valores=valores,
            erro="Preencha o nome e o telefone do cliente.",
        ), 400
    with conectar_banco() as conexao:
        conexao.execute(
            """
            INSERT INTO clientes (nome, telefone, email, observacoes)
            VALUES (:nome, :telefone, :email, :observacoes)
            """,
            valores,
        )
    flash("Cliente cadastrado com sucesso.", "sucesso")
    return redirect(url_for("inicio"))


@app.get("/clientes/<int:cliente_id>/editar")
def editar_cliente(cliente_id: int) -> str:
    return renderizar_pagina(
        cliente_edicao=buscar_cliente(cliente_id),
        formulario_aberto=True,
    )


@app.post("/clientes/<int:cliente_id>/editar")
def salvar_edicao(cliente_id: int) -> Any:
    cliente_atual = buscar_cliente(cliente_id)
    valores = {
        campo: request.form.get(campo, "").strip()
        for campo in ("nome", "telefone", "email", "observacoes")
    }
    if not valores["nome"] or not valores["telefone"]:
        return renderizar_pagina(
            cliente_edicao=cliente_atual,
            formulario_aberto=True,
            valores=valores,
            erro="Preencha o nome e o telefone do cliente.",
        ), 400
    valores["id"] = str(cliente_id)
    with conectar_banco() as conexao:
        conexao.execute(
            """
            UPDATE clientes
            SET nome = :nome, telefone = :telefone,
                email = :email, observacoes = :observacoes
            WHERE id = :id
            """,
            valores,
        )
    flash("Alterações salvas com sucesso.", "sucesso")
    return redirect(url_for("inicio"))


@app.post("/clientes/<int:cliente_id>/excluir")
def excluir_cliente(cliente_id: int) -> Any:
    with conectar_banco() as conexao:
        resultado = conexao.execute(
            "DELETE FROM clientes WHERE id = ?", (cliente_id,)
        )
    if resultado.rowcount == 0:
        abort(404)
    flash("Cliente excluído.", "sucesso")
    return redirect(url_for("inicio"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
