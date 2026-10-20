"""Página de demonstração do trigger que valida a pontuação (0 a 100)."""

import streamlit as st

import db

CODIGO_TRIGGER = """CREATE TRIGGER trg_resultado_valida_pontuacao_ins
BEFORE INSERT ON resultado
FOR EACH ROW
BEGIN
    IF NEW.pontuacao < 0 OR NEW.pontuacao > 100 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Pontuação inválida: deve estar entre 0 e 100';
    END IF;
END"""


def mostrar():
    st.title("⚡ Trigger: validação da pontuação")
    st.write(
        "O trigger roda **antes** de cada INSERT (e de cada UPDATE) na tabela "
        "`resultado`. Se a pontuação estiver fora de 0 a 100, ele dispara um erro "
        "com `SIGNAL` e o MySQL cancela o comando."
    )
    st.code(CODIGO_TRIGGER, language="sql")

    robos = db.opcoes_robos()
    if not robos:
        st.info("Nenhum robô cadastrado.")
        return

    st.subheader("Teste o trigger")
    with st.form("form_trigger"):
        col1, col2 = st.columns(2)
        with col1:
            nome_prova = st.text_input("Nome da prova", value="Arena_Teste")
            classificacao = st.number_input("Classificação", min_value=1, step=1, value=1)
        with col2:
            # Valor padrão 150 para demonstrar o erro; sem max_value de propósito
            pontuacao = st.number_input("Pontuação", value=150.0, step=0.5, format="%.2f")
            id_robo = st.selectbox("Robô", list(robos), format_func=robos.get)
        enviar = st.form_submit_button("Inserir resultado")

    if enviar:
        st.code(
            "INSERT INTO resultado (nome_prova, classificacao, pontuacao, id_robo)\n"
            f"VALUES ('{nome_prova}', {classificacao}, {pontuacao:.2f}, {id_robo});",
            language="sql",
        )
        try:
            db.executar(
                "INSERT INTO resultado (nome_prova, classificacao, pontuacao, id_robo) "
                "VALUES (%s, %s, %s, %s)",
                (nome_prova.strip(), int(classificacao), pontuacao, id_robo),
            )
            st.success("Pontuação válida: o trigger deixou o resultado ser inserido.", icon="✅")
        except Exception as erro:
            db.mostrar_erro(erro)

    st.subheader("Resultados cadastrados")
    st.dataframe(
        db.consultar("SELECT * FROM resultado ORDER BY nome_prova, classificacao"),
        hide_index=True,
    )
