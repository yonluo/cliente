# AgendaFácil — Clientes

Aplicação web em Python com Flask e SQLite para cadastrar, consultar, editar e
excluir clientes. A interface abre no navegador e mantém os registros no
arquivo local `agenda_clientes.db`.

## Executar localmente

No terminal, dentro da pasta do projeto:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Depois abra <http://127.0.0.1:5000>. A agenda importa automaticamente os
clientes já existentes em `clientes.json` na primeira execução. O arquivo
original não é alterado.

Também é possível executar sem ativar o ambiente virtual:

```powershell
.\.venv\Scripts\python.exe app.py
```

O banco SQLite e os dados de clientes são locais e não são enviados ao Git.
Para alterar o endereço do banco SQLite, configure `AGENDA_DATABASE` com o
caminho desejado.

O arquivo `agenda_clientes.py` contém a interface desktop Tkinter anterior.
