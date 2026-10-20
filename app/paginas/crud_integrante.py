"""CRUD da tabela INTEGRANTE (tabela nova escolhida pelo grupo)."""

from datetime import date

import streamlit as st

import db

DATA_MINIMA = date(1940, 1, 1)  # sem isso o calendário só aceita os últimos 10 anos
DATA_PADRAO = date(2007, 1, 1)


def mostrar():
    st.title("🧑‍🔧 Integrantes")
    st.caption("O e-mail é UNIQUE: dois integrantes não podem ter o mesmo e-mail.")
    aba_listar, aba_inserir, aba_editar, aba_excluir = st.tabs(
        ["📋 Listar", "➕ Inserir", "✏️ Editar", "🗑️ Excluir"]
    )

    # ---------------- LISTAR ----------------
    with aba_listar:
        df = db.consultar(
            """
            SELECT i.id_integrante, i.nome, i.funcao, i.email,
                   DATE_FORMAT(i.data_nascimento, '%d/%m/%Y') AS data_nascimento,
                   i.id_equipe, e.nome_equipe
            FROM integrante i
            JOIN equipe e ON e.id_equipe = i.id_equipe
            ORDER BY i.id_integrante
            """
        )
        st.dataframe(df, hide_index=True)
        st.caption(f"{len(df)} integrante(s) cadastrado(s).")

    equipes = db.opcoes_equipes()

    # ---------------- INSERIR ----------------
    with aba_inserir:
        if not equipes:
            st.info("Cadastre uma equipe antes de cadastrar integrantes.")
        else:
            with st.form("form_inserir_integrante", clear_on_submit=True):
                id_integrante = st.number_input(
                    "ID do integrante", min_value=1, step=1,
                    value=db.proximo_id("integrante", "id_integrante"))
                nome = st.text_input("Nome *")
                funcao = st.text_input("Função", placeholder="Ex.: Programadora, Capitão")
                email = st.text_input("E-mail")
                nascimento = st.date_input("Data de nascimento", value=DATA_PADRAO,
                                           min_value=DATA_MINIMA, format="DD/MM/YYYY")
                id_equipe = st.selectbox("Equipe", list(equipes), format_func=equipes.get)
                enviar = st.form_submit_button("Inserir integrante")

            if enviar:
                if not nome.strip():
                    st.warning("O nome é obrigatório.")
                else:
                    try:
                        db.executar(
                            "INSERT INTO integrante (id_integrante, nome, funcao, email, "
                            "data_nascimento, id_equipe) VALUES (%s, %s, %s, %s, %s, %s)",
                            (int(id_integrante), nome.strip(), funcao or None,
                             email.strip() or None, nascimento, id_equipe),
                        )
                        db.sucesso_e_recarregar(f"Integrante '{nome}' inserido com sucesso!")
                    except Exception as erro:
                        db.mostrar_erro(erro)  # ID ou e-mail repetido -> erro 1062

    integrantes_df = db.consultar(
        "SELECT id_integrante, nome FROM integrante ORDER BY id_integrante")
    integrantes = {int(l.id_integrante): f"{l.id_integrante} - {l.nome}"
                   for l in integrantes_df.itertuples()}

    # ---------------- EDITAR ----------------
    with aba_editar:
        if not integrantes:
            st.info("Nenhum integrante cadastrado.")
        else:
            id_sel = st.selectbox("Escolha o integrante", list(integrantes),
                                  format_func=integrantes.get, key="editar_int_sel")
            atual = db.consultar(
                "SELECT * FROM integrante WHERE id_integrante = %s", (id_sel,)).iloc[0]

            with st.form(f"form_editar_int_{id_sel}"):
                novo_id = st.number_input("ID do integrante", min_value=1, step=1,
                                          value=int(atual.id_integrante))
                nome = st.text_input("Nome *", value=atual.nome)
                funcao = st.text_input("Função", value=atual.funcao or "")
                email = st.text_input("E-mail", value=atual.email or "")
                nascimento = st.date_input("Data de nascimento",
                                           value=atual.data_nascimento or DATA_PADRAO,
                                           min_value=DATA_MINIMA, format="DD/MM/YYYY")
                lista_equipes = list(equipes)
                indice = (lista_equipes.index(atual.id_equipe)
                          if atual.id_equipe in lista_equipes else 0)
                id_equipe = st.selectbox("Equipe", lista_equipes, index=indice,
                                         format_func=equipes.get)
                salvar = st.form_submit_button("Salvar alterações")

            if salvar:
                if not nome.strip():
                    st.warning("O nome é obrigatório.")
                else:
                    try:
                        db.executar(
                            "UPDATE integrante SET id_integrante = %s, nome = %s, funcao = %s, "
                            "email = %s, data_nascimento = %s, id_equipe = %s "
                            "WHERE id_integrante = %s",
                            (int(novo_id), nome.strip(), funcao or None, email.strip() or None,
                             nascimento, id_equipe, id_sel),
                        )
                        db.sucesso_e_recarregar("Integrante atualizado com sucesso!")
                    except Exception as erro:
                        db.mostrar_erro(erro)

    # ---------------- EXCLUIR ----------------
    with aba_excluir:
        if not integrantes:
            st.info("Nenhum integrante cadastrado.")
        else:
            id_sel = st.selectbox("Escolha o integrante", list(integrantes),
                                  format_func=integrantes.get, key="excluir_int_sel")
            confirmar = st.checkbox("Confirmo a exclusão", key=f"conf_exc_int_{id_sel}")
            if st.button("Excluir integrante", type="primary", disabled=not confirmar):
                try:
                    db.executar("DELETE FROM integrante WHERE id_integrante = %s", (id_sel,))
                    db.sucesso_e_recarregar(f"Integrante {integrantes[id_sel]} excluído.")
                except Exception as erro:
                    db.mostrar_erro(erro)
