# 🤖 Torneio de Robótica — Projeto de Banco de Dados (IAAD / UFRPE)

Sistema para gerenciar um **torneio de robótica**: equipes, robôs, integrantes e resultados das provas.

O projeto tem três partes:

1. **Banco relacional MySQL** (`banco/script_torneio.sql`): tabelas, dados iniciais, trigger e stored procedure.
2. **Sistema web em Python + Streamlit** (`app/`): CRUD completo das 4 tabelas, demonstração de integridade referencial e cascata, trigger, consultas e dashboard.
3. **NoSQL com Neo4j** (`nosql/comandos_neo4j.cypher`): roteiro de minicurso com os mesmos dados em grafo.

---

## 👥 Integrantes do grupo

| Nome | Matrícula / E-mail |
|------|--------------------|
|Laura Miranda|laura.miranda2@ufrpe.br|
|      |                    |
|      |                    |
|      |                    |

**Disciplina:** Introdução ao Armazenamento e Análise de Dados (IAAD) — UFRPE
**Professora:** Roberta Macêdo Marques Gouveia

---

## 🛠️ Tecnologias

- **MySQL 8.0** e **MySQL Workbench 8.0**
- **Python 3.10 ou mais novo**
- **Streamlit** (interface web), **mysql-connector-python** (conexão com o MySQL), **pandas** (tabelas), **plotly** (gráficos), **python-dotenv** (leitura do arquivo `.env`)
- **Neo4j** (parte NoSQL)

---

## 🗂️ Estrutura das pastas

```
grupo3-iaad/
├── banco/
│   └── script_torneio.sql     # cria o banco inteiro (tabelas, dados, trigger, procedure)
├── app/
│   ├── app.py                 # arquivo principal (menu lateral)
│   ├── db.py                  # conexão com o MySQL e tratamento de erros
│   └── paginas/               # uma página do sistema por arquivo
│       ├── inicio.py
│       ├── dashboard.py
│       ├── crud_equipe.py
│       ├── crud_robo.py
│       ├── crud_resultado.py
│       ├── crud_integrante.py
│       ├── integridade.py     # FK inválida, exclusão e atualização em cascata
│       ├── trigger.py
│       └── consultas.py
├── nosql/
│   ├── comandos_neo4j.cypher  # minicurso de Neo4j
│   └── carga_neo4j.cypher     # apaga e recarrega os dados (reset)
├── .env.example               # modelo do arquivo de configuração
├── requirements.txt           # bibliotecas Python necessárias
└── README.md
```

---

## 🧱 Modelo do banco de dados

| Tabela | Colunas | Chave primária | Chaves estrangeiras |
|---|---|---|---|
| **equipe** | id_equipe, nome_equipe, escola, cidade | id_equipe | — |
| **robo** | id_robo, nome_robo, categoria, data_criacao, id_equipe | id_robo | id_equipe → equipe |
| **resultado** | nome_prova, classificacao, pontuacao, id_robo | **(nome_prova, classificacao)** — composta | id_robo → robo |
| **integrante** *(tabela escolhida pelo grupo)* | id_integrante, nome, funcao, email (UNIQUE), data_nascimento, id_equipe | id_integrante | id_equipe → equipe |

Todas as chaves estrangeiras usam **`ON DELETE CASCADE`** e **`ON UPDATE CASCADE`**.

- **Trigger** (`trg_resultado_valida_pontuacao_ins` e `..._upd`): antes de inserir ou alterar um resultado, impede pontuação fora de 0 a 100 com a mensagem *"Pontuação inválida: deve estar entre 0 e 100"*.
- **Stored procedure** `sp_desempenho_equipe(id_equipe)`: retorna o nome da equipe, a quantidade de robôs e a soma das pontuações (0 se não tiver).

Dados iniciais: 8 equipes, 12 robôs, 10 resultados e 15 integrantes. A equipe **Equipe Gama** não tem robôs e os robôs **Spark** e **Zeus** não têm resultado, para que as consultas com LEFT JOIN mostrem esses casos.

---

## ▶️ Passo a passo para rodar (do zero)

> Os comandos abaixo são para **Windows**. No Linux/Mac a diferença está indicada.

### Passo 1 — Instalar o Python

1. Baixe em <https://www.python.org/downloads/> (versão 3.10 ou mais nova).
2. Na primeira tela do instalador, **marque a opção "Add python.exe to PATH"** e clique em *Install Now*.
3. Para conferir, abra o **Prompt de Comando** (tecla Windows, digite `cmd`) e rode:
   ```
   python --version
   ```
   Deve aparecer algo como `Python 3.13.5`.

### Passo 2 — Instalar o MySQL Server e o MySQL Workbench

1. Baixe o **MySQL Installer** em <https://dev.mysql.com/downloads/installer/>.
2. Instale o **MySQL Server 8.0** e o **MySQL Workbench**.
3. Durante a instalação, **anote a senha que você definir para o usuário `root`**. Ela será usada no Passo 5.
4. Deixe marcada a opção para iniciar o MySQL como serviço do Windows (padrão).

### Passo 3 — Baixar o projeto

- Pelo GitHub: botão verde **Code → Download ZIP**, e depois extraia o ZIP; **ou**
- Com git: `git clone <endereço do repositório>`

### Passo 4 — Criar o banco de dados no Workbench

1. Abra o **MySQL Workbench** e clique na conexão **Local instance MySQL80** (digite a senha do root).
2. Menu **File → Open SQL Script...** e escolha o arquivo `banco/script_torneio.sql` do projeto.
3. Clique no ícone do **raio** ⚡ (*Execute*) **sem selecionar nenhuma linha**, para rodar o script inteiro.
4. No painel da esquerda (*Schemas*), clique no ícone de atualizar 🔄. Deve aparecer o banco **torneio_robotica** com as 4 tabelas.

> O script começa com `DROP SCHEMA IF EXISTS`, então pode ser executado quantas vezes quiser: ele sempre recria tudo do zero com os dados iniciais.

### Passo 5 — Criar o arquivo `.env` (configuração da conexão)

O sistema lê usuário e senha do MySQL de um arquivo chamado `.env`, que **não vai para o GitHub** (por segurança).

1. Na pasta do projeto, faça uma **cópia** do arquivo `.env.example` e renomeie a cópia para **`.env`**.
   - Pelo Prompt de Comando, dentro da pasta do projeto: `copy .env.example .env`
   - Linux/Mac: `cp .env.example .env`
2. Abra o `.env` no Bloco de Notas (ou VS Code) e troque `sua_senha_aqui` pela senha do root do **seu** MySQL:
   ```
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=minha_senha_do_mysql
   DB_NAME=torneio_robotica
   ```
3. Salve o arquivo.

### Passo 6 — Instalar as bibliotecas Python

Abra o Prompt de Comando **na pasta do projeto** (no Explorador de Arquivos, clique na barra de endereço, digite `cmd` e aperte Enter) e rode:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

- A primeira linha cria um **ambiente virtual** (uma pasta `.venv` só com as bibliotecas deste projeto).
- A segunda **ativa** o ambiente; o início da linha passa a mostrar `(.venv)`.
- Linux/Mac: use `source .venv/bin/activate` na segunda linha.

> Se preferir não usar ambiente virtual, rode apenas `pip install -r requirements.txt`.

### Passo 7 — Rodar o sistema

Ainda na pasta do projeto (e com o `(.venv)` ativo):

```
streamlit run app/app.py
```

O navegador abre sozinho em **<http://localhost:8501>**. Se não abrir, copie esse endereço no navegador.
Para parar o sistema, volte ao Prompt de Comando e aperte **Ctrl + C**.

> Da próxima vez, basta abrir o Prompt na pasta do projeto, rodar `.venv\Scripts\activate` e `streamlit run app/app.py`.

---

## 🧭 O que tem em cada página

| Página | O que faz |
|---|---|
| **Início** | Apresentação do modelo e botão **Recriar banco**, que restaura os dados iniciais |
| **Dashboard** | Cards com totais e gráficos: pontuação por equipe, robôs por categoria e média por prova |
| **Equipes / Robôs / Resultados / Integrantes** | CRUD completo: abas Listar, Inserir, Editar e Excluir. Chaves estrangeiras são escolhidas em listas |
| **Integridade e Cascata** | (a) tenta inserir robô com equipe inexistente e mostra o erro de FK; (b) exclui uma equipe e mostra antes/depois dos robôs, resultados e integrantes removidos em cascata; (c) altera o id de um robô e mostra a atualização em cascata em `resultado` |
| **Trigger** | Formulário para inserir resultado; com pontuação acima de 100 aparece o erro do trigger |
| **Consultas** | Ranking de equipes, robôs sem resultado, média por categoria com HAVING, idades (TIMESTAMPDIFF e DATE_FORMAT), resultados acima da média (subconsulta) e chamada da stored procedure. Cada consulta mostra o SQL usado |

Os erros do MySQL aparecem em português: chave primária duplicada (código 1062), violação de chave estrangeira (1452) e a mensagem do trigger (1644).

> 💡 Depois de demonstrar exclusões em cascata, use **Início → Recriar banco** para voltar aos dados originais.

---

## 🕸️ Parte NoSQL (Neo4j)

O arquivo `nosql/comandos_neo4j.cypher` tem os comandos do minicurso:

- Criação dos nós `Equipe`, `Robo`, `Integrante` e `Prova` e dos relacionamentos
  `(Robo)-[:PERTENCE_A]->(Equipe)`, `(Integrante)-[:MEMBRO_DE]->(Equipe)` e
  `(Robo)-[:PARTICIPOU_DE {classificacao, pontuacao}]->(Prova)`;
- Exemplos de **CREATE**, **MATCH** (leitura), **SET** (atualização), **DELETE** e **DETACH DELETE**;
- Consultas com relacionamentos (ranking por equipe, robôs sem participação, caminhos de 2 saltos);
- Comentários comparando cada comando com o SQL equivalente.

**Como executar:** use o **Neo4j Desktop**, o **Neo4j Aura Free** (<https://neo4j.com/cloud/aura-free/>) ou o **Neo4j Sandbox**. Abra o *Neo4j Browser* e execute os blocos um de cada vez, na ordem (cada bloco termina com `;`).

O bloco **8b** (`CALL db.schema.visualization();`) mostra o modelo do grafo, que equivale ao DER no Workbench. O bloco **21** dá erro de propósito (um `DELETE` simples num nó que ainda tem relacionamentos): nada é apagado, então execute-o sozinho e siga para o bloco 22. Para voltar ao estado inicial (por exemplo, antes de regravar o vídeo), execute o arquivo `nosql/carga_neo4j.cypher` com a opção *Enable multi statement query editor* ativada no Browser; ele apaga tudo e recarrega os dados originais (equivale aos blocos 0 a 6).

---

## 🆘 Problemas comuns

| Problema | Causa provável | Como resolver |
|---|---|---|
| `'python' não é reconhecido como um comando` | Python não foi adicionado ao PATH | Reinstale o Python marcando **"Add python.exe to PATH"**, ou use `py` no lugar de `python` |
| `'streamlit' não é reconhecido` | Ambiente virtual não ativado ou bibliotecas não instaladas | Rode `.venv\Scripts\activate` e depois `pip install -r requirements.txt`. Alternativa: `python -m streamlit run app/app.py` |
| `.venv\Scripts\activate` dá erro de "execução de scripts desabilitada" (PowerShell) | Política de segurança do PowerShell | Use o **Prompt de Comando (cmd)** em vez do PowerShell, ou rode `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Tela "Acesso negado: confira DB_USER e DB_PASSWORD" | Senha errada no `.env` | Abra o `.env` e coloque a mesma senha que você usa no Workbench |
| Tela "O banco 'torneio_robotica' não existe" | O script SQL não foi executado | Faça o **Passo 4** |
| Tela "Não foi possível conectar ao MySQL" | O serviço do MySQL está desligado | Tecla Windows → digite **Serviços** → procure **MySQL80** → botão direito → **Iniciar** |
| Mudei o `.env` e nada aconteceu | O Streamlit leu o `.env` antigo | Pare com **Ctrl + C** e rode `streamlit run app/app.py` de novo |
| O arquivo virou `.env.txt` | O Windows esconde extensões | No Explorador: **Exibir → Mostrar → Extensões de nomes de arquivos** e renomeie para `.env` |
| No Workbench o script parou no meio | Só um trecho estava selecionado | Clique em qualquer lugar do editor sem selecionar nada e use o raio ⚡ (não o raio com cursor) |
| `Port 8501 is already in use` | Já existe um Streamlit aberto | Feche o outro Prompt de Comando ou rode `streamlit run app/app.py --server.port 8502` |
| Acentos aparecem estranhos no Workbench | Arquivo aberto com outra codificação | O script está em UTF-8; abra pelo menu **File → Open SQL Script** do Workbench |
