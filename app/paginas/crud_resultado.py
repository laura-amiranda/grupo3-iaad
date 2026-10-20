"""CRUD da tabela RESULTADO (chave primária composta: nome_prova + classificacao)."""

import streamlit as st

import db


def mostrar():
    st.title("🏆 Resultados")
    st.caption("A chave primária é composta por (nome_prova, classificacao): "
               "numa mesma prova não pode haver duas classificações iguais.")
    aba_listar, aba_inserir, aba_editar, aba_excluir = st.tabs(
        ["📋 Listar", "➕ Inserir", "✏️ Editar", "🗑️ Excluir"]
    )

    # ---------------- LISTAR ----------------
    with aba_listar:
        df = db.consultar(
            """
            SELECT res.nome_prova, res.classificacao, res.pontuacao,
                   res.id_robo, r.nome_robo
            FROM resultado res
            JOIN robo r ON r.id_robo = res.id_robo
            ORDER BY res.nome_prova, res.classificacao
            """
        )
        st.dataframe(df, hide_index=True)
        st.caption(f"{len(df)} resultado(s) cadastrado(s).")

    robos = db.opcoes_robos()

    # ---------------- INSERIR ----------------
    with aba_inserir:
        if not robos:
            st.info("Cadastre um robô antes de lançar resultados.")
        else:
            with st.form("form_inserir_resultado", clear_on_submit=True):
                nome_prova = st.text_input("Nome da prova *", placeholder="Ex.: Arena_A")
                classificacao = st.number_input("Classificação", min_value=1, step=1)
                # Sem limite máximo aqui de propósito: quem barra valores > 100 é o trigger
                pontuacao = st.number_input("Pontuação (0 a 100)", value=0.0, step=0.5,
                                            format="%.2f")
                id_robo = st.selectbox("Robô", list(robos), format_func=robos.get)
                enviar = st.form_submit_button("Inserir resultado")

            if enviar:
                if not nome_prova.strip():
                    st.warning("O nome da prova é obrigatório.")
                else:
                    try:
                        db.executar(
                            "INSERT INTO resultado (nome_prova, classificacao, pontuacao, id_robo) "
                            "VALUES (%s, %s, %s, %s)",
                            (nome_prova.strip(), int(classificacao), pontuacao, id_robo),
                        )
                        db.sucesso_e_recarregar("Resultado inserido com sucesso!")
                    except Exception as erro:
                        db.mostrar_erro(erro)  # PK duplicada ou trigger

    # Para escolher um resultado precisamos das DUAS colunas da chave primária
    chaves_df = db.consultar(
        "SELECT nome_prova, classificacao FROM resultado ORDER BY nome_prova, classificacao"
    )
    chaves = [(l.nome_prova, int(l.classificacao)) for l in chaves_df.itertuples()]

    def rotulo(chave):
        return f"{chave[0]} — {chave[1]}º lugar"

    # ---------------- EDITAR ----------------
    with aba_editar:
        if not chaves:
            st.info("Nenhum resultado cadastrado.")
        else:
            chave = st.selectbox("Escolha o resultado", chaves, format_func=rotulo,
                                 key="editar_res_sel")
            atual = db.consultar(
                "SELECT * FROM resultado WHERE nome_prova = %s AND classificacao = %s", chave
            ).iloc[0]

            with st.form(f"form_editar_res_{chave[0]}_{chave[1]}"):
                nome_prova = st.text_input("Nome da prova *", value=atual.nome_prova)
                classificacao = st.number_input("Classificação", min_value=1, step=1,
                                                value=int(atual.classificacao))
                pontuacao = st.number_input("Pontuação (0 a 100)", step=0.5, format="%.2f",
                                            value=float(atual.pontuacao or 0))
                lista_robos = list(robos)
                indice = lista_robos.index(atual.id_robo) if atual.id_robo in lista_robos else 0
                id_robo = st.selectbox("Robô", lista_robos, index=indice, format_func=robos.get)
                salvar = st.form_submit_button("Salvar alterações")

            if salvar:
                try:
                    # O WHERE usa a chave composta ANTIGA para achar a linha certa
                    db.executar(
                        "UPDATE resultado SET nome_prova = %s, classificacao = %s, "
                        "pontuacao = %s, id_robo = %s "
                        "WHERE nome_prova = %s AND classificacao = %s",
                        (nome_prova.strip(), int(classificacao), pontuacao, id_robo, *chave),
                    )
                    db.sucesso_e_recarregar("Resultado atualizado com sucesso!")
                except Exception as erro:
                    db.mostrar_erro(erro)  # o trigger também vale para UPDATE

    # ---------------- EXCLUIR ----------------
    with aba_excluir:
        if not chaves:
            st.info("Nenhum resultado cadastrado.")
        else:
            chave = st.selectbox("Escolha o resultado", chaves, format_func=rotulo,
                                 key="excluir_res_sel")
            confirmar = st.checkbox("Confirmo a exclusão",
                                    key=f"conf_exc_res_{chave[0]}_{chave[1]}")
            if st.button("Excluir resultado", type="primary", disabled=not confirmar):
                try:
                    db.executar(
                        "DELETE FROM resultado WHERE nome_prova = %s AND classificacao = %s",
                        chave,
                    )
                    db.sucesso_e_recarregar(f"Resultado {rotulo(chave)} excluído.")
                except Exception as erro:
                    db.mostrar_erro(erro)
