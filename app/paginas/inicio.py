"""Página inicial: apresentação do projeto e opção de restaurar os dados."""

import streamlit as st

import db


def mostrar():
    st.title("🤖 Torneio de Robótica")
    st.write(
        "Sistema web para gerenciar um torneio de robótica: equipes, robôs, "
        "integrantes e resultados das provas. Os dados ficam em um banco "
        "**MySQL** e a interface foi feita em **Python + Streamlit**."
    )

    st.subheader("Modelo do banco de dados")
    st.markdown(
        """
| Tabela | Chave primária | Chaves estrangeiras |
|---|---|---|
| **equipe** | id_equipe | — |
| **robo** | id_robo | id_equipe → equipe (CASCADE) |
| **resultado** | (nome_prova, classificacao) — composta | id_robo → robo (CASCADE) |
| **integrante** | id_integrante | id_equipe → equipe (CASCADE) |
"""
    )
    st.markdown(
        "- **Trigger:** impede pontuação fora do intervalo 0 a 100 em `resultado`.\n"
        "- **Stored procedure:** `sp_desempenho_equipe(id)` mostra robôs e pontos de uma equipe.\n"
        "- Use o **menu lateral** para navegar entre as páginas."
    )

    st.divider()
    secao_restaurar()


def secao_restaurar():
    """Botão que recria o banco com os dados iniciais (usado também em outras páginas)."""
    st.subheader("♻️ Restaurar dados iniciais")
    st.caption("Executa de novo o banco/script_torneio.sql. Útil depois de testar "
               "exclusões em cascata. Apaga tudo o que foi alterado.")
    confirmar = st.checkbox("Entendo que todas as alterações serão perdidas",
                            key="confirmar_restaurar")
    if st.button("Recriar banco", disabled=not confirmar, key="botao_restaurar"):
        try:
            db.recriar_banco()
            db.sucesso_e_recarregar("Banco recriado com os dados iniciais.")
        except Exception as erro:
            db.mostrar_erro(erro)
