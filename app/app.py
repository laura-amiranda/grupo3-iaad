"""
app.py - Arquivo principal do sistema web do Torneio de Robótica.

Para rodar (a partir da pasta raiz do projeto):
    streamlit run app/app.py

O Streamlit executa este arquivo de cima a baixo a cada clique do usuário.
Aqui montamos o menu lateral e chamamos a função mostrar() da página escolhida.
"""

import streamlit as st

import db
from paginas import (
    consultas,
    crud_equipe,
    crud_integrante,
    crud_resultado,
    crud_robo,
    dashboard,
    inicio,
    integridade,
    trigger,
)

# Configuração da aba do navegador (precisa ser o primeiro comando do Streamlit)
st.set_page_config(page_title="Torneio de Robótica", page_icon="🤖", layout="wide")

# Dicionário "nome no menu" -> módulo da página
PAGINAS = {
    "🏠 Início": inicio,
    "📊 Dashboard": dashboard,
    "👥 Equipes": crud_equipe,
    "🤖 Robôs": crud_robo,
    "🏆 Resultados": crud_resultado,
    "🧑‍🔧 Integrantes": crud_integrante,
    "🔗 Integridade e Cascata": integridade,
    "⚡ Trigger": trigger,
    "🔎 Consultas": consultas,
}

# ----- Menu lateral -----
st.sidebar.title("🤖 Torneio de Robótica")
st.sidebar.caption("Projeto de Banco de Dados - IAAD / UFRPE")
escolha = st.sidebar.radio("Menu", list(PAGINAS.keys()))

# Teste rápido de conexão: se o banco não estiver acessível, avisamos logo
# e não tentamos abrir a página (que daria erro).
try:
    db.consultar("SELECT 1")
except Exception as erro:
    st.title("Não foi possível acessar o banco de dados")
    db.mostrar_erro(erro)
    st.info("Confira o passo a passo do README: o MySQL precisa estar ligado, "
            "o script banco/script_torneio.sql precisa ter sido executado e o "
            "arquivo .env precisa ter usuário e senha corretos.")
    st.stop()

# Mostra a mensagem de sucesso da última operação (se houver) e abre a página
db.mostrar_mensagem_pendente()
PAGINAS[escolha].mostrar()
