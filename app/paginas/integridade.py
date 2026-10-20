"""Página de demonstração: integridade referencial e ações em cascata."""

import streamlit as st

import db
from paginas.inicio import secao_restaurar


def mostrar():
    st.title("🔗 Integridade e Cascata")
    st.write("Demonstrações das regras de chave estrangeira definidas no banco "
             "(`ON DELETE CASCADE` e `ON UPDATE CASCADE`).")

    demo_fk_invalida()
    st.divider()
    demo_exclusao_cascata()
    st.divider()
    demo_atualizacao_cascata()
    st.divider()
    secao_restaurar()


# ---------------------------------------------------------------------------
# (a) Inserir robô com equipe que não existe -> erro de chave estrangeira
# ---------------------------------------------------------------------------
def demo_fk_invalida():
    st.header("a) Violação de chave estrangeira")
    st.write("Tentamos inserir um robô ligado à equipe **9999**, que não existe. "
             "O MySQL recusa o comando para manter a integridade referencial.")

    sql = ("INSERT INTO robo (id_robo, nome_robo, categoria, data_criacao, id_equipe)\n"
           "VALUES (9001, 'Robô Fantasma', 'Combate', '2024-01-01', 9999);")
    st.code(sql, language="sql")

    if st.button("Tentar inserir robô com equipe inexistente"):
        try:
            db.executar(sql)
            st.warning("O comando foi aceito (isso não deveria acontecer!).")
        except Exception as erro:
            db.mostrar_erro(erro)  # esperado: erro 1452


# ---------------------------------------------------------------------------
# (b) Excluir equipe -> robôs, resultados e integrantes somem em cascata
# ---------------------------------------------------------------------------
def dados_da_equipe(id_equipe):
    """Busca tudo o que depende de uma equipe (direta ou indiretamente)."""
    robos = db.consultar(
        "SELECT id_robo, nome_robo, categoria FROM robo WHERE id_equipe = %s", (id_equipe,))
    resultados = db.consultar(
        """
        SELECT res.nome_prova, res.classificacao, res.pontuacao, res.id_robo
        FROM resultado res
        JOIN robo r ON r.id_robo = res.id_robo
        WHERE r.id_equipe = %s
        """, (id_equipe,))
    integrantes = db.consultar(
        "SELECT id_integrante, nome, funcao FROM integrante WHERE id_equipe = %s",
        (id_equipe,))
    return robos, resultados, integrantes


def exibir_dados(titulo, dados):
    st.markdown(f"**{titulo}**")
    for nome, df in zip(["Robôs", "Resultados", "Integrantes"], dados):
        st.caption(f"{nome}: {len(df)} registro(s)")
        st.dataframe(df, hide_index=True)


def demo_exclusao_cascata():
    st.header("b) Exclusão em cascata")
    st.write("Ao excluir uma equipe, o `ON DELETE CASCADE` remove automaticamente "
             "os robôs dela, os resultados desses robôs e os integrantes.")

    equipes = db.opcoes_equipes()
    if not equipes:
        st.info("Nenhuma equipe cadastrada. Use 'Recriar banco' abaixo.")
        return

    id_equipe = st.selectbox("Equipe a excluir", list(equipes),
                             format_func=equipes.get, key="cascata_equipe")
    st.code(f"DELETE FROM equipe WHERE id_equipe = {id_equipe};", language="sql")

    if st.button("Excluir equipe e ver a cascata", type="primary"):
        antes = dados_da_equipe(id_equipe)
        try:
            db.executar("DELETE FROM equipe WHERE id_equipe = %s", (id_equipe,))
        except Exception as erro:
            db.mostrar_erro(erro)
            return
        depois = dados_da_equipe(id_equipe)

        st.success(f"Equipe {equipes[id_equipe]} excluída.")
        col_antes, col_depois = st.columns(2)
        with col_antes:
            exibir_dados("ANTES da exclusão", antes)
        with col_depois:
            exibir_dados("DEPOIS da exclusão", depois)


# ---------------------------------------------------------------------------
# (c) Alterar o id de um robô -> resultado.id_robo é atualizado em cascata
# ---------------------------------------------------------------------------
def demo_atualizacao_cascata():
    st.header("c) Atualização em cascata")
    st.write("Ao mudar o `id_robo` de um robô, o `ON UPDATE CASCADE` atualiza "
             "sozinho a coluna `id_robo` na tabela `resultado`.")

    # Só faz sentido para robôs que têm resultado
    robos_df = db.consultar(
        """
        SELECT DISTINCT r.id_robo, r.nome_robo
        FROM robo r
        JOIN resultado res ON res.id_robo = r.id_robo
        ORDER BY r.id_robo
        """)
    if robos_df.empty:
        st.info("Nenhum robô com resultado. Use 'Recriar banco' abaixo.")
        return
    robos = {int(l.id_robo): f"{l.id_robo} - {l.nome_robo}" for l in robos_df.itertuples()}

    col1, col2 = st.columns(2)
    with col1:
        id_antigo = st.selectbox("Robô (com resultados)", list(robos),
                                 format_func=robos.get, key="cascata_robo")
    with col2:
        sugestao = db.proximo_id("robo", "id_robo") + 100
        id_novo = st.number_input("Novo ID", min_value=1, step=1, value=sugestao)

    st.code(f"UPDATE robo SET id_robo = {id_novo} WHERE id_robo = {id_antigo};",
            language="sql")

    sql_resultados = ("SELECT nome_prova, classificacao, pontuacao, id_robo "
                      "FROM resultado WHERE id_robo = %s")

    if st.button("Atualizar ID e ver a cascata", type="primary"):
        antes = db.consultar(sql_resultados, (id_antigo,))
        try:
            db.executar("UPDATE robo SET id_robo = %s WHERE id_robo = %s",
                        (int(id_novo), id_antigo))
        except Exception as erro:
            db.mostrar_erro(erro)  # ex.: novo ID já existe -> chave duplicada
            return
        depois = db.consultar(sql_resultados, (int(id_novo),))

        st.success(f"ID do robô alterado de {id_antigo} para {id_novo}.")
        col_antes, col_depois = st.columns(2)
        with col_antes:
            st.markdown(f"**ANTES** — resultados com id_robo = {id_antigo}")
            st.dataframe(antes, hide_index=True)
        with col_depois:
            st.markdown(f"**DEPOIS** — resultados com id_robo = {id_novo}")
            st.dataframe(depois, hide_index=True)
