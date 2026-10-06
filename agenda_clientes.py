"""Agenda de clientes simples, com interface gráfica em Tkinter."""

from __future__ import annotations

import json
import tkinter as tk
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable
from tkinter import messagebox, ttk


ARQUIVO_DADOS = Path(__file__).with_name("clientes.json")
AZUL = "#3569f6"
FUNDO = "#f4f2ed"
TEXTO = "#192238"
TEXTO_SUAVE = "#727b8d"
ESCURO = "#0d1524"
VERDE = "#31a17d"
VERMELHO = "#e9544f"
CINZA_BOTAO = "#e9edf3"
CORES_AVATAR = (
    ("#e4ebff", "#3569f6", "#3569f6"),
    ("#def4ed", "#31a17d", "#31a17d"),
    ("#fff0d2", "#e3a629", "#ad7100"),
    ("#ffe3e1", "#e9544f", "#e9544f"),
)


class CampoArredondado(tk.Frame):
    def __init__(self, mestre: tk.Widget) -> None:
        super().__init__(mestre, bg=mestre.cget("bg"), height=42)
        self.pack_propagate(False)
        self.canvas = tk.Canvas(
            self,
            height=42,
            bg=mestre.cget("bg"),
            highlightthickness=0,
            borderwidth=0,
        )
        self.canvas.pack(fill="both", expand=True)
        self.entrada = tk.Entry(
            self,
            font=("Segoe UI", 11),
            fg=TEXTO,
            bg="white",
            insertbackground=TEXTO,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
        )
        self.entrada.place(x=13, y=10, relwidth=1, width=-26, height=22)
        self.canvas.bind("<Configure>", self._desenhar)
        self.entrada.bind("<FocusIn>", self._desenhar)
        self.entrada.bind("<FocusOut>", self._desenhar)

    def _desenhar(self, _evento: tk.Event | None = None) -> None:
        largura = self.canvas.winfo_width()
        altura = self.canvas.winfo_height()
        if largura < 2 or altura < 2:
            return
        borda = AZUL if self.entrada == self.focus_get() else "#d9dee8"
        raio = 10
        pontos = (
            raio, 1,
            largura - raio, 1,
            largura - 1, raio,
            largura - 1, altura - raio,
            largura - raio, altura - 1,
            raio, altura - 1,
            1, altura - raio,
            1, raio,
        )
        self.canvas.delete("campo")
        self.canvas.create_polygon(
            pontos,
            smooth=True,
            splinesteps=24,
            fill="white",
            outline=borda,
            width=1,
            tags="campo",
        )


@dataclass
class Cliente:
    nome: str
    telefone: str
    email: str = ""
    observacoes: str = ""


class AgendaClientes:
    def __init__(self, janela: tk.Tk) -> None:
        self.janela = janela
        self.janela.title("AgendaFácil | Clientes")
        self.janela.geometry("1080x720")
        self.janela.minsize(800, 580)
        self.janela.configure(bg=FUNDO)
        self.clientes: list[Cliente] = []
        self.indice_selecionado: int | None = None
        self.linhas_clientes: list[tuple[tk.Frame, list[tk.Widget]]] = []

        self._montar_estilos()
        self._montar_interface()
        self._carregar_clientes()
        self._atualizar_lista()

    def _montar_estilos(self) -> None:
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Agenda.Vertical.TScrollbar",
            background="#d8deeb",
            troughcolor="#ffffff",
            bordercolor="#ffffff",
            arrowcolor=TEXTO_SUAVE,
        )

    @staticmethod
    def _criar_botao(
        mestre: tk.Widget,
        texto: str,
        comando: Callable[[], None],
        variante: str,
    ) -> tk.Button:
        paleta = {
            "novo": (VERDE, "white", "#278466", "white"),
            "excluir": (VERMELHO, "white", "#d9433e", "white"),
            "editar": (CINZA_BOTAO, TEXTO, "#d8dee8", TEXTO),
            "primario": (AZUL, "white", "#2858d8", "white"),
        }
        cor, texto_cor, cor_ativa, texto_ativo = paleta[variante]
        return tk.Button(
            mestre,
            text=texto,
            command=comando,
            font=("Segoe UI", 9, "bold"),
            fg=texto_cor,
            bg=cor,
            activebackground=cor_ativa,
            activeforeground=texto_ativo,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=9,
        )

    def _montar_interface(self) -> None:
        barra_lateral = tk.Frame(self.janela, bg=ESCURO, width=220)
        barra_lateral.pack(side="left", fill="y")
        barra_lateral.pack_propagate(False)

        marca = tk.Frame(barra_lateral, bg=ESCURO)
        marca.pack(fill="x", padx=20, pady=(30, 38))
        tk.Label(
            marca,
            text="A",
            font=("Segoe UI", 15, "bold"),
            fg="white",
            bg=AZUL,
            width=2,
            pady=4,
        ).pack(side="left", padx=(0, 10))
        tk.Label(
            marca,
            text="AgendaFácil",
            font=("Segoe UI", 15, "bold"),
            fg="white",
            bg=ESCURO,
        ).pack(side="left")

        for icone, nome, ativo in (
            ("◉", "Agenda", False),
            ("☰", "Clientes", True),
            ("◆", "Serviços", False),
            ("⚙", "Configurações", False),
        ):
            tk.Label(
                barra_lateral,
                text=f"  {icone}    {nome}",
                font=("Segoe UI", 11, "bold" if ativo else "normal"),
                fg="white" if ativo else "#9da8ba",
                bg=AZUL if ativo else ESCURO,
                anchor="w",
                padx=14,
                pady=12,
            ).pack(fill="x", padx=12, pady=3)

        tk.Frame(barra_lateral, bg=ESCURO).pack(fill="both", expand=True)
        usuario = tk.Frame(barra_lateral, bg="#111b2b")
        usuario.pack(fill="x", padx=12, pady=16)
        tk.Label(
            usuario,
            text="J",
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg=AZUL,
            width=3,
            pady=7,
        ).pack(side="left", padx=(8, 10), pady=8)
        tk.Label(
            usuario,
            text="Administrador\nAgendaFácil",
            font=("Segoe UI", 9),
            fg="white",
            bg="#111b2b",
            justify="left",
        ).pack(side="left")

        conteudo = tk.Frame(self.janela, bg=FUNDO)
        conteudo.pack(side="left", fill="both", expand=True, padx=32, pady=26)

        cabecalho = tk.Frame(conteudo, bg=FUNDO)
        cabecalho.pack(fill="x", pady=(0, 22))
        titulo = tk.Frame(cabecalho, bg=FUNDO)
        titulo.pack(side="left", fill="x", expand=True)
        tk.Label(
            titulo,
            text="03  •  CLIENTES",
            font=("Segoe UI", 9, "bold"),
            fg=AZUL,
            bg=FUNDO,
        ).pack(anchor="w")
        tk.Label(
            titulo,
            text="Clientes",
            font=("Segoe UI", 27, "bold"),
            fg=TEXTO,
            bg=FUNDO,
        ).pack(anchor="w", pady=(5, 1))
        tk.Label(
            titulo,
            text="Cadastre, consulte e mantenha seus clientes organizados.",
            font=("Segoe UI", 10),
            fg=TEXTO_SUAVE,
            bg=FUNDO,
        ).pack(anchor="w")
        self._criar_botao(
            cabecalho,
            "NOVO CLIENTE",
            self._abrir_cadastro,
            "novo",
        ).pack(side="right", anchor="center", padx=(12, 0))

        resumo = tk.Frame(conteudo, bg=FUNDO)
        resumo.pack(fill="x", pady=(0, 18))
        self.resumo_clientes = self._criar_cartao_resumo(
            resumo, "CLIENTES CADASTRADOS", "0", "Na sua agenda", AZUL
        )
        self.resumo_telefones = self._criar_cartao_resumo(
            resumo, "COM TELEFONE", "0", "Contato disponível", "#31a17d"
        )
        self.resumo_emails = self._criar_cartao_resumo(
            resumo, "COM E-MAIL", "0", "Contato digital", "#e3a629"
        )

        cartao = tk.Frame(conteudo, bg="white", highlightthickness=1, highlightbackground="#e5e8ee")
        cartao.pack(fill="both", expand=True)
        topo = tk.Frame(cartao, bg="white")
        topo.pack(fill="x", padx=20, pady=(17, 12))
        tk.Label(
            topo,
            text="☰  Lista de clientes",
            font=("Segoe UI", 14, "bold"),
            fg=TEXTO,
            bg="white",
        ).pack(side="left")
        self.contagem = tk.Label(
            topo, text="0 clientes", font=("Segoe UI", 9), fg=TEXTO_SUAVE, bg="white"
        )
        self.contagem.pack(side="right")

        area_lista = tk.Frame(cartao, bg="white")
        area_lista.pack(fill="both", expand=True, padx=20)
        self.lista_canvas = tk.Canvas(
            area_lista, bg="white", highlightthickness=0, borderwidth=0
        )
        self.lista_canvas.pack(side="left", fill="both", expand=True)
        barra = ttk.Scrollbar(
            area_lista,
            orient="vertical",
            command=self.lista_canvas.yview,
            style="Agenda.Vertical.TScrollbar",
        )
        barra.pack(side="right", fill="y")
        self.lista_canvas.configure(yscrollcommand=barra.set)
        self.lista_conteudo = tk.Frame(self.lista_canvas, bg="white")
        self.lista_window = self.lista_canvas.create_window(
            (0, 0), window=self.lista_conteudo, anchor="nw"
        )
        self.lista_conteudo.bind(
            "<Configure>",
            lambda _evento: self.lista_canvas.configure(
                scrollregion=self.lista_canvas.bbox("all")
            ),
        )
        self.lista_canvas.bind(
            "<Configure>",
            lambda evento: self.lista_canvas.itemconfigure(
                self.lista_window, width=evento.width
            ),
        )
        self.lista_canvas.bind_all("<MouseWheel>", self._rolar_lista)

        self.detalhes = tk.Label(
            cartao,
            text="Selecione um cliente para ver os detalhes.",
            font=("Segoe UI", 10),
            fg=TEXTO_SUAVE,
            bg="#f8f9fc",
            anchor="w",
            justify="left",
            padx=12,
            pady=10,
        )
        self.detalhes.pack(fill="x", padx=20, pady=(12, 0))

        rodape = tk.Frame(cartao, bg="white")
        rodape.pack(fill="x", padx=20, pady=(10, 14))
        self._criar_botao(
            rodape,
            "EDITAR",
            self._editar_cliente,
            "editar",
        ).pack(side="right", padx=(0, 8))
        self._criar_botao(
            rodape,
            "EXCLUIR",
            self._excluir_cliente,
            "excluir",
        ).pack(side="right")

    @staticmethod
    def _criar_cartao_resumo(
        container: tk.Frame, rotulo: str, valor: str, descricao: str, cor: str
    ) -> tk.Label:
        cartao = tk.Frame(container, bg="white", highlightthickness=1, highlightbackground="#e5e8ee")
        cartao.pack(side="left", fill="both", expand=True, padx=(0, 12))
        tk.Frame(cartao, bg=cor, width=4).pack(side="left", fill="y")
        texto = tk.Frame(cartao, bg="white")
        texto.pack(side="left", fill="both", expand=True, padx=13, pady=10)
        tk.Label(
            texto, text=rotulo, font=("Segoe UI", 8, "bold"), fg=TEXTO_SUAVE, bg="white"
        ).pack(anchor="w")
        valor_label = tk.Label(
            texto, text=valor, font=("Segoe UI", 19, "bold"), fg=TEXTO, bg="white"
        )
        valor_label.pack(anchor="w", pady=(3, 0))
        tk.Label(
            texto, text=descricao, font=("Segoe UI", 8), fg=TEXTO_SUAVE, bg="white"
        ).pack(anchor="w")
        return valor_label

    def _carregar_clientes(self) -> None:
        if not ARQUIVO_DADOS.exists():
            return
        try:
            dados = json.loads(ARQUIVO_DADOS.read_text(encoding="utf-8"))
            if not isinstance(dados, list):
                raise ValueError("O conteúdo precisa ser uma lista de clientes.")
            self.clientes = [Cliente(**item) for item in dados]
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as erro:
            messagebox.showerror(
                "Erro ao carregar clientes",
                f"Não foi possível ler {ARQUIVO_DADOS.name}:\n{erro}",
                parent=self.janela,
            )

    def _salvar_clientes(self) -> None:
        dados = [asdict(cliente) for cliente in self.clientes]
        ARQUIVO_DADOS.write_text(
            json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _atualizar_lista(self) -> None:
        for widget in self.lista_conteudo.winfo_children():
            widget.destroy()
        self.linhas_clientes.clear()
        self.indice_selecionado = None

        if self.clientes:
            for indice, cliente in enumerate(self.clientes):
                self._criar_linha_cliente(indice, cliente)
        else:
            tk.Label(
                self.lista_conteudo,
                text="Nenhum cliente cadastrado. Use “NOVO CLIENTE” para começar.",
                font=("Segoe UI", 10),
                fg=TEXTO_SUAVE,
                bg="white",
                pady=30,
            ).pack(fill="x")

        self.resumo_clientes.configure(text=str(len(self.clientes)))
        self.resumo_telefones.configure(
            text=str(sum(bool(cliente.telefone) for cliente in self.clientes))
        )
        self.resumo_emails.configure(
            text=str(sum(bool(cliente.email) for cliente in self.clientes))
        )
        quantidade = len(self.clientes)
        self.contagem.configure(
            text=f"{quantidade} cliente" if quantidade == 1 else f"{quantidade} clientes"
        )
        self.detalhes.configure(
            text=(
                "Sua lista está vazia. Clique em “+ Novo cliente” para começar."
                if not quantidade
                else "Selecione um cliente para ver os detalhes."
            )
        )

    def _criar_linha_cliente(self, indice: int, cliente: Cliente) -> None:
        fundo_avatar, cor_avatar, cor_detalhe = CORES_AVATAR[indice % len(CORES_AVATAR)]
        linha = tk.Frame(self.lista_conteudo, bg="white", height=82)
        linha.pack(fill="x")
        linha.pack_propagate(False)

        faixa = tk.Frame(linha, bg=cor_detalhe, width=3)
        faixa.pack(side="left", fill="y")

        avatar = tk.Canvas(
            linha, width=48, height=48, bg="white", highlightthickness=0
        )
        avatar.pack(side="left", padx=(16, 12), pady=15)
        avatar.create_oval(2, 2, 46, 46, fill=fundo_avatar, outline="")
        avatar.create_text(
            24,
            24,
            text=self._iniciais(cliente.nome),
            fill=cor_avatar,
            font=("Segoe UI", 10, "bold"),
        )

        informacoes = tk.Frame(linha, bg="white")
        informacoes.pack(side="left", fill="both", expand=True, pady=17)
        nome = tk.Label(
            informacoes,
            text=cliente.nome,
            font=("Segoe UI", 10, "bold"),
            fg=TEXTO,
            bg="white",
            anchor="w",
        )
        nome.pack(anchor="w")
        contato = " • ".join(
            texto for texto in (cliente.telefone, cliente.email) if texto
        )
        subtitulo = tk.Label(
            informacoes,
            text=contato or "Sem informações de contato",
            font=("Segoe UI", 9),
            fg=TEXTO_SUAVE,
            bg="white",
            anchor="w",
        )
        subtitulo.pack(anchor="w", pady=(3, 0))

        mais = tk.Button(
            linha,
            text="⋮",
            command=lambda: self._abrir_menu_linha(indice, mais),
            font=("Segoe UI", 15),
            fg=TEXTO_SUAVE,
            bg="white",
            activebackground="#f1f4fa",
            relief="flat",
            cursor="hand2",
            padx=10,
        )
        mais.pack(side="right", padx=10)

        separador = tk.Frame(self.lista_conteudo, bg="#e5e8ee", height=1)
        separador.pack(fill="x")
        widgets = [linha, avatar, informacoes, nome, subtitulo, mais]
        self.linhas_clientes.append((linha, widgets))
        for widget in (*widgets, faixa):
            widget.bind("<Button-1>", lambda _evento, i=indice: self._selecionar_cliente(i))
        mais.bind("<Button-1>", lambda _evento, i=indice: self._selecionar_cliente(i), add="+")

    @staticmethod
    def _iniciais(nome: str) -> str:
        partes = nome.split()
        if not partes:
            return "?"
        return "".join(parte[0] for parte in (partes[0], partes[-1])).upper()[:2]

    def _selecionar_cliente(self, indice: int) -> None:
        self.indice_selecionado = indice
        for linha_indice, (linha, widgets) in enumerate(self.linhas_clientes):
            cor_fundo = "#f1f5ff" if linha_indice == indice else "white"
            linha.configure(bg=cor_fundo)
            for widget in widgets:
                if isinstance(widget, (tk.Frame, tk.Label, tk.Button)):
                    widget.configure(bg=cor_fundo)
            avatar = widgets[2]
            if isinstance(avatar, tk.Canvas):
                avatar.configure(bg=cor_fundo)
        self._mostrar_detalhes()

    def _abrir_menu_linha(self, indice: int, botao: tk.Widget) -> None:
        self._selecionar_cliente(indice)
        menu = tk.Menu(self.janela, tearoff=False)
        menu.add_command(label="Editar cliente", command=self._editar_cliente)
        menu.add_command(label="Excluir cliente", command=self._excluir_cliente)
        try:
            menu.tk_popup(
                botao.winfo_rootx(), botao.winfo_rooty() + botao.winfo_height()
            )
        finally:
            menu.grab_release()

    def _rolar_lista(self, evento: tk.Event) -> None:
        if str(evento.widget).startswith(str(self.lista_canvas)):
            self.lista_canvas.yview_scroll(int(-evento.delta / 120), "units")

    def _mostrar_detalhes(self, _evento: tk.Event | None = None) -> None:
        if self.indice_selecionado is None:
            return
        cliente = self.clientes[self.indice_selecionado]
        detalhes = f"Telefone: {cliente.telefone}"
        if cliente.email:
            detalhes += f"    •    E-mail: {cliente.email}"
        if cliente.observacoes:
            detalhes += f"\nObservações: {cliente.observacoes}"
        self.detalhes.configure(text=detalhes)

    def _abrir_cadastro(self) -> None:
        self._abrir_formulario_cliente()

    def _editar_cliente(self) -> None:
        if self.indice_selecionado is None:
            messagebox.showinfo(
                "Editar cliente",
                "Selecione um cliente na lista primeiro.",
                parent=self.janela,
            )
            return
        self._abrir_formulario_cliente(self.indice_selecionado)

    def _abrir_formulario_cliente(self, indice: int | None = None) -> None:
        cliente_atual = self.clientes[indice] if indice is not None else None
        dialogo = tk.Toplevel(self.janela)
        dialogo.title("Editar cliente" if cliente_atual else "Novo cliente")
        dialogo.configure(bg="white")
        dialogo.resizable(False, False)
        dialogo.transient(self.janela)
        dialogo.grab_set()

        formulario = tk.Frame(dialogo, bg="white")
        formulario.pack(fill="both", expand=True, padx=26, pady=22)

        topo_formulario = tk.Frame(formulario, bg="white")
        topo_formulario.pack(fill="x", pady=(0, 17))
        tk.Button(
            topo_formulario,
            text="×",
            command=dialogo.destroy,
            font=("Segoe UI", 14),
            fg=TEXTO,
            bg="#f1f3f6",
            activebackground="#e5e8ee",
            relief="flat",
            cursor="hand2",
            width=2,
            height=1,
            borderwidth=0,
        ).pack(side="right")
        tk.Label(
            topo_formulario,
            text="EDITAR CLIENTE" if cliente_atual else "NOVO CLIENTE",
            font=("Segoe UI", 9, "bold"),
            fg=AZUL,
            bg="white",
        ).pack(anchor="w", pady=(2, 4))
        tk.Label(
            topo_formulario,
            text="Editar cliente" if cliente_atual else "Novo cliente",
            font=("Segoe UI", 21, "bold"),
            fg=TEXTO,
            bg="white",
        ).pack(anchor="w")
        tk.Label(
            topo_formulario,
            text=(
                "Atualize as informações do cliente."
                if cliente_atual
                else "Preencha as informações para adicionar um novo cliente."
            ),
            font=("Segoe UI", 9),
            fg=TEXTO_SUAVE,
            bg="white",
            wraplength=350,
            justify="left",
        ).pack(anchor="w", pady=(5, 0))

        campos: dict[str, CampoArredondado] = {}
        for rotulo, chave in (
            ("Nome completo *", "nome"),
            ("Telefone *", "telefone"),
            ("E-mail", "email"),
            ("Observações", "observacoes"),
        ):
            tk.Label(
                formulario,
                text=rotulo,
                font=("Segoe UI", 9, "bold"),
                fg=TEXTO,
                bg="white",
            ).pack(anchor="w", pady=(6, 5))
            campo = CampoArredondado(formulario)
            campo.pack(fill="x", pady=(0, 4))
            if cliente_atual:
                campo.entrada.insert(0, getattr(cliente_atual, chave))
            campos[chave] = campo

        def salvar() -> None:
            nome = campos["nome"].entrada.get().strip()
            telefone = campos["telefone"].entrada.get().strip()
            if not nome or not telefone:
                messagebox.showwarning(
                    "Campos obrigatórios",
                    "Preencha o nome e o telefone do cliente.",
                    parent=dialogo,
                )
                return

            cliente = Cliente(
                nome=nome,
                telefone=telefone,
                email=campos["email"].entrada.get().strip(),
                observacoes=campos["observacoes"].entrada.get().strip(),
            )
            if indice is None:
                self.clientes.append(cliente)
            else:
                self.clientes[indice] = cliente
            try:
                self._salvar_clientes()
            except OSError as erro:
                if indice is None:
                    self.clientes.pop()
                else:
                    self.clientes[indice] = cliente_atual
                messagebox.showerror(
                    "Erro ao salvar",
                    f"Não foi possível salvar as alterações:\n{erro}",
                    parent=dialogo,
                )
                return
            self._atualizar_lista()
            indice_atualizado = indice if indice is not None else len(self.clientes) - 1
            self._selecionar_cliente(indice_atualizado)
            self.lista_canvas.yview_moveto(
                indice_atualizado / max(len(self.clientes), 1)
            )
            dialogo.destroy()

        botao_salvar = self._criar_botao(
            formulario,
            "SALVAR ALTERAÇÕES" if cliente_atual else "CRIAR CLIENTE",
            salvar,
            "primario",
        )
        botao_salvar.configure(pady=11, font=("Segoe UI", 10, "bold"))
        botao_salvar.pack(fill="x", pady=(18, 0))
        dialogo.update_idletasks()
        largura_dialogo = 440
        altura_dialogo = max(510, dialogo.winfo_reqheight())
        self.janela.update_idletasks()
        pos_x = self.janela.winfo_rootx() + (self.janela.winfo_width() - largura_dialogo) // 2
        pos_y = self.janela.winfo_rooty() + (self.janela.winfo_height() - altura_dialogo) // 2
        dialogo.geometry(f"{largura_dialogo}x{altura_dialogo}+{pos_x}+{pos_y}")
        dialogo.minsize(largura_dialogo, altura_dialogo)
        campos["nome"].entrada.focus_set()
        dialogo.bind("<Return>", lambda _evento: salvar())
        dialogo.bind("<Escape>", lambda _evento: dialogo.destroy())

    def _excluir_cliente(self) -> None:
        if self.indice_selecionado is None:
            messagebox.showinfo(
                "Excluir cliente",
                "Selecione um cliente na lista primeiro.",
                parent=self.janela,
            )
            return
        indice = self.indice_selecionado
        cliente = self.clientes[indice]
        if not messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja excluir {cliente.nome}?",
            parent=self.janela,
        ):
            return

        removido = self.clientes.pop(indice)
        try:
            self._salvar_clientes()
        except OSError as erro:
            self.clientes.insert(indice, removido)
            messagebox.showerror(
                "Erro ao salvar",
                f"Não foi possível excluir o cliente:\n{erro}",
                parent=self.janela,
            )
            return
        self._atualizar_lista()


def main() -> None:
    janela = tk.Tk()
    AgendaClientes(janela)
    janela.mainloop()


if __name__ == "__main__":
    main()