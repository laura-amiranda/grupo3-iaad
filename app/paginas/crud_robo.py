"""CRUD da tabela ROBO: listar, inserir, editar e excluir."""

from datetime import date

import streamlit as st

import db

CATEGORIAS = ["Combate", "Resgate", "Seguidor de Linha", "Sumô", "Outra"]
DATA_MINIMA = date(1990, 1, 1)  # sem isso o calendário só aceita os últimos 10 anos


def campo_categoria(valor_atual=None, key=None):
    """Selectbox de categoria; mantém categorias que não estão na lista padrão."""
    opcoes = CATEGORIAS.copy()
    if valor_atual and valor_atual not in opcoes:
        opcoes.insert(0, valor_atual)
    indice = opcoes.index(valor_atual) if valor_atual in opcoes else 0
    return st.selectbox("Categoria", opcoes, index=indice, key=key)


def mostrar():
    st.title("🤖 Robôs")
    aba_listar, aba_inserir, aba_editar, aba_excluir = st.tabs(
        ["📋 Listar", "➕ Inserir", "✏️ Editar", "🗑️ Excluir"]
    )

    # ---------------- LISTAR ----------------
    with aba_listar:
        # JOIN para mostrar o nome da equipe em vez de só o número
        df = db.consultar(
            """
            SELECT r.id_robo, r.nome_robo, r.categoria,
                   DATE_FORMAT(r.data_criacao, '%d/%m/%Y') AS data_criacao,
                   r.id_equipe, e.nome_equipe
            FROM robo r
            JOIN equipe e ON e.id_equipe = r.id_equipe
            ORDER BY r.id_robo
            """
        )
        st.dataframe(df, hide_index=True)
        st.caption(f"{len(df)} robô(s) cadastrado(s).")

    equipes = db.opcoes_equipes()

    # ---------------- INSERIR ----------------
    with aba_inserir:
        if not equipes:
            st.info("Cadastre uma equipe antes de cadastrar robôs.")
        else:
            with st.form("form_inserir_robo", clear_on_submit=True):
                id_robo = st.number_input("ID do robô", min_value=1, step=1,
                                          value=db.proximo_id("robo", "id_robo"))
                nome = st.text_input("Nome do robô *")
                categoria = campo_categoria(key="cat_inserir")
                data_criacao = st.date_input("Data de criação", value=date.today(),
                                             min_value=DATA_MINIMA, format="DD/MM/YYYY")
                # A chave estrangeira é escolhida numa lista: só equipes que existem
                id_equipe = st.selectbox("Equipe", list(equipes), format_func=equipes.get)
                enviar = st.form_submit_button("Inserir robô")

            if enviar:
                if not nome.strip():
                    st.warning("O nome do robô é obrigatório.")
                else:
                    try:
                        db.executar(
                            "INSERT INTO robo (id_robo, nome_robo, categoria, data_criacao, id_equipe) "
                            "VALUES (%s, %s, %s, %s, %s)",
                            (int(id_robo), nome.strip(), categoria, data_criacao, id_equipe),
                        )
                        db.sucesso_e_recarregar(f"Robô '{nome}' inserido com sucesso!")
                    except Exception as erro:
                        db.mostrar_erro(erro)

    robos = db.opcoes_robos()

    # ---------------- EDITAR ----------------
    with aba_editar:
        if not robos:
            st.info("Nenhum robô cadastrado.")
        else:
            id_sel = st.selectbox("Escolha o robô", list(robos),
                                  format_func=robos.get, key="editar_robo_sel")
            atual = db.consultar("SELECT * FROM robo WHERE id_robo = %s", (id_sel,)).iloc[0]

            with st.form(f"form_editar_robo_{id_sel}"):
                novo_id = st.number_input("ID do robô", min_value=1, step=1,
                                          value=int(atual.id_robo),
                                          help="Alterar o ID atualiza os resultados em cascata.")
                nome = st.text_input("Nome do robô *", value=atual.nome_robo)
                categoria = campo_categoria(atual.categoria, key=f"cat_editar_{id_sel}")
                data_criacao = st.date_input("Data de criação",
                                             value=atual.data_criacao or date.today(),
                                             min_value=DATA_MINIMA, format="DD/MM/YYYY")
                lista_equipes = list(equipes)
                indice = (lista_equipes.index(atual.id_equipe)
                          if atual.id_equipe in lista_equipes else 0)
                id_equipe = st.selectbox("Equipe", lista_equipes, index=indice,
                                         format_func=equipes.get)
                salvar = st.form_submit_button("Salvar alterações")

            if salvar:
                if not nome.strip():
                    st.warning("O nome do robô é obrigatório.")
                else:
                    try:
                        db.executar(
                            "UPDATE robo SET id_robo = %s, nome_robo = %s, categoria = %s, "
                            "data_criacao = %s, id_equipe = %s WHERE id_robo = %s",
                            (int(novo_id), nome.strip(), categoria, data_criacao,
                             id_equipe, id_sel),
                        )
                        db.sucesso_e_recarregar("Robô atualizado com sucesso!")
                    except Exception as erro:
                        db.mostrar_erro(erro)

    # ---------------- EXCLUIR ----------------
    with aba_excluir:
        if not robos:
            st.info("Nenhum robô cadastrado.")
        else:
            id_sel = st.selectbox("Escolha o robô", list(robos),
                                  format_func=robos.get, key="excluir_robo_sel")
            st.warning("Os resultados deste robô também serão excluídos (ON DELETE CASCADE).")
            confirmar = st.checkbox("Confirmo a exclusão", key=f"conf_exc_robo_{id_sel}")
            if st.button("Excluir robô", type="primary", disabled=not confirmar):
                try:
                    db.executar("DELETE FROM robo WHERE id_robo = %s", (id_sel,))
                    db.sucesso_e_recarregar(f"Robô {robos[id_sel]} excluído.")
                except Exception as erro:
                    db.mostrar_erro(erro)
