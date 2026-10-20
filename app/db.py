"""
db.py - Camada de acesso ao banco de dados.

Todas as páginas do sistema usam as funções deste arquivo para falar com o
MySQL. Assim, a conexão e o tratamento de erros ficam em um lugar só.
"""

import os
from decimal import Decimal
from pathlib import Path

import mysql.connector
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Pasta raiz do projeto (um nível acima da pasta app/)
PASTA_PROJETO = Path(__file__).resolve().parent.parent

# Lê o arquivo .env da raiz do projeto e coloca os valores nas variáveis de
# ambiente. Desse jeito a senha nunca fica escrita no código.
load_dotenv(PASTA_PROJETO / ".env")

# Script SQL usado para recriar o banco com os dados iniciais
CAMINHO_SCRIPT = PASTA_PROJETO / "banco" / "script_torneio.sql"


def configuracao(com_banco=True):
    """Monta o dicionário de configuração da conexão a partir do .env."""
    config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "charset": "utf8mb4",
    }
    if com_banco:
        config["database"] = os.getenv("DB_NAME", "torneio_robotica")
    return config


def conectar(com_banco=True):
    """Abre uma nova conexão com o MySQL."""
    return mysql.connector.connect(**configuracao(com_banco))


def _decimal_para_float(df):
    """O MySQL devolve DECIMAL como objetos Decimal; convertemos para float
    para que pandas e plotly consigam fazer contas e gráficos."""
    for coluna in df.columns:
        if df[coluna].map(lambda v: isinstance(v, Decimal)).any():
            df[coluna] = df[coluna].astype(float)
    return df


def consultar(sql, parametros=None):
    """Executa um SELECT e devolve o resultado como DataFrame do pandas.

    Os valores vêm em 'parametros' (e não concatenados no texto do SQL)
    para evitar SQL Injection: o conector cuida de escapar os valores.
    """
    with conectar() as conexao:
        with conexao.cursor() as cursor:
            if parametros:
                cursor.execute(sql, parametros)
            else:
                cursor.execute(sql)
            linhas = cursor.fetchall()
            colunas = cursor.column_names
    return _decimal_para_float(pd.DataFrame(linhas, columns=colunas))


def executar(sql, parametros=None):
    """Executa INSERT, UPDATE ou DELETE e confirma (commit) a alteração.

    Devolve quantas linhas foram afetadas. Se o MySQL recusar o comando
    (chave duplicada, chave estrangeira inválida, trigger...), a exceção
    sobe para quem chamou, que mostra a mensagem com mostrar_erro().
    """
    with conectar() as conexao:
        with conexao.cursor() as cursor:
            if parametros:
                cursor.execute(sql, parametros)
            else:
                cursor.execute(sql)
            conexao.commit()
            return cursor.rowcount


def chamar_procedure(nome, argumentos):
    """Chama uma stored procedure e devolve o primeiro resultado como DataFrame."""
    with conectar() as conexao:
        with conexao.cursor() as cursor:
            cursor.callproc(nome, argumentos)
            for resultado in cursor.stored_results():
                linhas = resultado.fetchall()
                colunas = resultado.column_names
                return _decimal_para_float(pd.DataFrame(linhas, columns=colunas))
    return pd.DataFrame()


def traduzir_erro(erro):
    """Transforma o erro técnico do MySQL em uma mensagem amigável.

    Cada erro do MySQL tem um código (errno). Os principais deste projeto:
      1062 - chave primária (ou campo UNIQUE) duplicada
      1452 - chave estrangeira aponta para um registro que não existe
      1644 - erro disparado por nós mesmos com SIGNAL (o trigger)
    """
    codigo = getattr(erro, "errno", None)
    detalhe = getattr(erro, "msg", str(erro))

    if codigo == 1062:
        return ("Registro duplicado: já existe um registro com essa chave "
                f"(chave primária ou campo único). Detalhe: {detalhe}")
    if codigo == 1452:
        return ("Violação de chave estrangeira: o registro relacionado não existe "
                f"(ex.: a equipe ou o robô informado não está cadastrado). Detalhe: {detalhe}")
    if codigo == 1451:
        return ("Não é possível excluir/alterar: existem registros que dependem deste. "
                f"Detalhe: {detalhe}")
    if codigo == 1644:
        # Mensagem definida no SIGNAL do trigger
        return f"Regra de negócio (trigger): {detalhe}"
    if codigo == 1048:
        return f"Campo obrigatório não preenchido. Detalhe: {detalhe}"
    if codigo == 1406:
        return f"Texto maior do que o permitido para o campo. Detalhe: {detalhe}"
    if codigo == 1045:
        return "Acesso negado: confira DB_USER e DB_PASSWORD no arquivo .env."
    if codigo == 1049:
        return ("O banco 'torneio_robotica' não existe. Execute o arquivo "
                "banco/script_torneio.sql no MySQL Workbench.")
    if codigo in (2003, 2005):
        return ("Não foi possível conectar ao MySQL. Verifique se o serviço do MySQL "
                "está ligado e se DB_HOST/DB_PORT no .env estão corretos.")
    return f"Erro do MySQL ({codigo}): {detalhe}"


def mostrar_erro(erro):
    """Mostra o erro na tela de forma amigável (e o código técnico abaixo)."""
    st.error(traduzir_erro(erro), icon="🚫")
    with st.expander("Ver mensagem técnica do MySQL"):
        st.code(str(erro))


# ---------------------------------------------------------------------------
# Mensagens de sucesso que sobrevivem ao st.rerun()
# ---------------------------------------------------------------------------
# Depois de inserir/editar/excluir chamamos st.rerun() para a tela recarregar
# e a listagem mostrar os dados novos. Como o rerun apaga a tela, guardamos a
# mensagem na "session_state" (memória da sessão) e mostramos na próxima vez.

def sucesso_e_recarregar(mensagem):
    st.session_state["mensagem_sucesso"] = mensagem
    st.rerun()


def mostrar_mensagem_pendente():
    mensagem = st.session_state.pop("mensagem_sucesso", None)
    if mensagem:
        st.success(mensagem, icon="✅")


# ---------------------------------------------------------------------------
# Recriar o banco a partir do script SQL
# ---------------------------------------------------------------------------

def recriar_banco():
    """Executa o banco/script_torneio.sql inteiro, restaurando os dados iniciais.

    Útil depois das demonstrações de exclusão em cascata. O script usa
    DELIMITER (comando do Workbench, não do servidor), então lemos o arquivo
    linha a linha e separamos os comandos respeitando o delimitador atual.
    """
    delimitador = ";"
    comandos = []
    buffer = []

    for linha in CAMINHO_SCRIPT.read_text(encoding="utf-8").splitlines():
        if linha.strip().upper().startswith("DELIMITER"):
            delimitador = linha.split()[1]
            continue
        if linha.strip().startswith("--"):
            continue  # linha só de comentário: ignorada
        buffer.append(linha)
        if linha.rstrip().endswith(delimitador):
            comando = "\n".join(buffer).rstrip()[: -len(delimitador)].strip()
            if comando:
                comandos.append(comando)
            buffer = []

    with conectar(com_banco=False) as conexao:
        with conexao.cursor() as cursor:
            for comando in comandos:
                cursor.execute(comando)
        conexao.commit()


def opcoes_equipes():
    """Lista de equipes para usar em selectbox: {id: 'id - nome'}."""
    df = consultar("SELECT id_equipe, nome_equipe FROM equipe ORDER BY id_equipe")
    return {int(l.id_equipe): f"{l.id_equipe} - {l.nome_equipe}" for l in df.itertuples()}


def opcoes_robos():
    """Lista de robôs para usar em selectbox: {id: 'id - nome'}."""
    df = consultar("SELECT id_robo, nome_robo FROM robo ORDER BY id_robo")
    return {int(l.id_robo): f"{l.id_robo} - {l.nome_robo}" for l in df.itertuples()}


def proximo_id(tabela, coluna):
    """Sugere o próximo id livre (maior id + 1) para facilitar o cadastro."""
    df = consultar(f"SELECT COALESCE(MAX({coluna}), 0) + 1 AS proximo FROM {tabela}")
    return int(df.iloc[0, 0])
