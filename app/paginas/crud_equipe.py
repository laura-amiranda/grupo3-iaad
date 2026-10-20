"""CRUD da tabela EQUIPE: listar, inserir, editar e excluir."""

import streamlit as st

import db


def mostrar():
    st.title("👥 Equipes")
    aba_listar, aba_inserir, aba_editar, aba_excluir = st.tabs(
        ["📋 Listar", "➕ Inserir", "✏️ Editar", "🗑️ Excluir"]
    )

    # ---------------- LISTAR (SELECT) ----------------
    with aba_listar:
        df = db.consultar("SELECT * FROM equipe ORDER BY id_equipe")
        st.dataframe(df, hide_index=True)
        st.caption(f"{len(df)} equipe(s) cadastrada(s).")

    # ---------------- INSERIR (INSERT) ----------------
    with aba_inserir:
        # st.form agrupa os campos: nada é enviado até clicar no botão
        with st.form("form_inserir_equipe", clear_on_submit=True):
            id_equipe = st.number_input("ID da equipe", min_value=1, step=1,
                                        value=db.proximo_id("equipe", "id_equipe"))
            nome = st.text_input("Nome da equipe *")
            escola = st.text_input("Escola")
            cidade = st.text_input("Cidade")
            enviar = st.form_submit_button("Inserir equipe")

        if enviar:
            if not nome.strip():
                st.warning("O nome da equipe é obrigatório.")
            else:
                try:
                    # Os %s são substituídos pelos valores da tupla (com segurança)
                    db.executar(
                        "INSERT INTO equipe (id_equipe, nome_equipe, escola, cidade) "
                        "VALUES (%s, %s, %s, %s)",
                        (int(id_equipe), nome.strip(), escola or None, cidade or None),
                    )
                    db.sucesso_e_recarregar(f"Equipe '{nome}' inserida com sucesso!")
                except Exception as erro:
                    db.mostrar_erro(erro)  # ex.: ID repetido -> chave primária duplicada

    equipes = db.opcoes_equipes()

    # ---------------- EDITAR (UPDATE) ----------------
    with aba_editar:
        if not equipes:
            st.info("Nenhuma equipe cadastrada.")
        else:
            id_sel = st.selectbox("Escolha a equipe", list(equipes),
                                  format_func=equipes.get, key="editar_equipe_sel")
            atual = db.consultar("SELECT * FROM equipe WHERE id_equipe = %s", (id_sel,)).iloc[0]

            # A key com o id faz o formulário recarregar os valores ao trocar de equipe
            with st.form(f"form_editar_equipe_{id_sel}"):
                novo_id = st.number_input("ID da equipe", min_value=1, step=1,
                                          value=int(atual.id_equipe),
                                          help="Alterar o ID atualiza robôs e integrantes em cascata.")
                nome = st.text_input("Nome da equipe *", value=atual.nome_equipe)
                escola = st.text_input("Escola", value=atual.escola or "")
                cidade = st.text_input("Cidade", value=atual.cidade or "")
                salvar = st.form_submit_button("Salvar alterações")

            if salvar:
                if not nome.strip():
                    st.warning("O nome da equipe é obrigatório.")
                else:
                    try:
                        db.executar(
                            "UPDATE equipe SET id_equipe = %s, nome_equipe = %s, "
                            "escola = %s, cidade = %s WHERE id_equipe = %s",
                            (int(novo_id), nome.strip(), escola or None, cidade or None, id_sel),
                        )
                        db.sucesso_e_recarregar("Equipe atualizada com sucesso!")
                    except Exception as erro:
                        db.mostrar_erro(erro)

    # ---------------- EXCLUIR (DELETE) ----------------
    with aba_excluir:
        if not equipes:
            st.info("Nenhuma equipe cadastrada.")
        else:
            id_sel = st.selectbox("Escolha a equipe", list(equipes),
                                  format_func=equipes.get, key="excluir_equipe_sel")
            st.warning("Atenção: por causa do ON DELETE CASCADE, os robôs, os resultados "
                       "desses robôs e os integrantes da equipe também serão excluídos.")
            confirmar = st.checkbox("Confirmo a exclusão", key=f"conf_exc_equipe_{id_sel}")
            if st.button("Excluir equipe", type="primary", disabled=not confirmar):
                try:
                    db.executar("DELETE FROM equipe WHERE id_equipe = %s", (id_sel,))
                    db.sucesso_e_recarregar(f"Equipe {equipes[id_sel]} excluída.")
                except Exception as erro:
                    db.mostrar_erro(erro)
