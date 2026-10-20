"""Página de consultas não triviais: cada uma mostra o SQL e o resultado."""

import streamlit as st

import db

# ---------------------------------------------------------------------------
# SQL de cada consulta (fica separado para aparecer na tela do jeito que é)
# ---------------------------------------------------------------------------

# LEFT JOIN mantém equipes sem robôs/resultados; COALESCE troca NULL por 0
SQL_RANKING = """SELECT e.id_equipe,
       e.nome_equipe,
       COUNT(DISTINCT r.id_robo)          AS qtd_robos,
       COUNT(res.id_robo)                 AS qtd_resultados,
       COALESCE(SUM(res.pontuacao), 0)    AS pontuacao_total
FROM equipe e
LEFT JOIN robo r        ON r.id_equipe = e.id_equipe
LEFT JOIN resultado res ON res.id_robo = r.id_robo
GROUP BY e.id_equipe, e.nome_equipe
ORDER BY pontuacao_total DESC, e.nome_equipe"""

# LEFT JOIN "exclusivo": fica só com quem NÃO encontrou par na outra tabela
SQL_SEM_RESULTADO = """SELECT r.id_robo, r.nome_robo, r.categoria, e.nome_equipe
FROM robo r
JOIN equipe e           ON e.id_equipe = r.id_equipe
LEFT JOIN resultado res ON res.id_robo = r.id_robo
WHERE res.id_robo IS NULL
ORDER BY r.id_robo"""

# HAVING filtra DEPOIS do agrupamento (o WHERE filtra antes)
SQL_MEDIA_CATEGORIA = """SELECT r.categoria,
       COUNT(*)                     AS qtd_resultados,
       ROUND(AVG(res.pontuacao), 2) AS media_pontuacao,
       MAX(res.pontuacao)           AS maior_pontuacao
FROM robo r
JOIN resultado res ON res.id_robo = r.id_robo
GROUP BY r.categoria
HAVING AVG(res.pontuacao) >= %s
ORDER BY media_pontuacao DESC"""

# TIMESTAMPDIFF calcula a diferença entre datas; DATE_FORMAT formata dd/mm/aaaa
SQL_IDADE_ROBOS = """SELECT nome_robo,
       DATE_FORMAT(data_criacao, '%d/%m/%Y')              AS data_criacao,
       TIMESTAMPDIFF(YEAR,  data_criacao, CURDATE())      AS idade_anos,
       TIMESTAMPDIFF(MONTH, data_criacao, CURDATE()) % 12 AS meses_extras
FROM robo
ORDER BY data_criacao"""

SQL_IDADE_INTEGRANTES = """SELECT i.nome,
       e.nome_equipe,
       DATE_FORMAT(i.data_nascimento, '%d/%m/%Y')         AS data_nascimento,
       TIMESTAMPDIFF(YEAR, i.data_nascimento, CURDATE())  AS idade
FROM integrante i
JOIN equipe e ON e.id_equipe = i.id_equipe
ORDER BY idade DESC, i.nome"""

# Subconsulta: compara cada resultado com a média geral de todas as provas
SQL_ACIMA_MEDIA = """SELECT r.nome_robo, res.nome_prova, res.pontuacao
FROM resultado res
JOIN robo r ON r.id_robo = res.id_robo
WHERE res.pontuacao > (SELECT AVG(pontuacao) FROM resultado)
ORDER BY res.pontuacao DESC"""


def bloco(titulo, explicacao, sql, df):
    """Mostra título, explicação, o SQL e a tabela de resultado."""
    st.subheader(titulo)
    st.caption(explicacao)
    st.code(sql, language="sql")
    st.dataframe(df, hide_index=True)


def mostrar():
    st.title("🔎 Consultas")

    abas = st.tabs(["Ranking de equipes", "Robôs sem resultado", "Média por categoria",
                    "Idades", "Acima da média", "Stored procedure"])

    with abas[0]:
        bloco("Ranking de equipes",
              "LEFT JOIN + SUM + COUNT + GROUP BY. Equipes sem robôs ou sem resultados "
              "também aparecem, com 0 pontos.",
              SQL_RANKING, db.consultar(SQL_RANKING))

    with abas[1]:
        bloco("Robôs que ainda não têm resultado",
              "LEFT JOIN exclusivo: robôs cujo id não aparece na tabela resultado.",
              SQL_SEM_RESULTADO, db.consultar(SQL_SEM_RESULTADO))

    with abas[2]:
        minimo = st.slider("Mostrar categorias com média maior ou igual a:",
                           0.0, 100.0, 87.0, 0.5)
        # Na tela mostramos o valor no lugar do %s para ficar fácil de ler
        bloco("Média de pontuação por categoria",
              "GROUP BY agrupa por categoria e HAVING filtra os grupos pela média.",
              SQL_MEDIA_CATEGORIA.replace("%s", str(minimo)),
              db.consultar(SQL_MEDIA_CATEGORIA, (minimo,)))

    with abas[3]:
        bloco("Idade dos robôs",
              "TIMESTAMPDIFF calcula anos e meses desde a criação; "
              "DATE_FORMAT mostra a data no padrão brasileiro.",
              SQL_IDADE_ROBOS, db.consultar(SQL_IDADE_ROBOS))
        bloco("Idade dos integrantes",
              "Mesma ideia, usando a data de nascimento.",
              SQL_IDADE_INTEGRANTES, db.consultar(SQL_IDADE_INTEGRANTES))

    with abas[4]:
        bloco("Resultados acima da média geral",
              "Subconsulta no WHERE: compara cada pontuação com a média de todas.",
              SQL_ACIMA_MEDIA, db.consultar(SQL_ACIMA_MEDIA))

    with abas[5]:
        st.subheader("Stored procedure: sp_desempenho_equipe")
        st.caption("Retorna o nome da equipe, a quantidade de robôs e a soma das pontuações.")
        equipes = db.opcoes_equipes()
        if not equipes:
            st.info("Nenhuma equipe cadastrada.")
            return
        id_equipe = st.selectbox("Equipe", list(equipes), format_func=equipes.get,
                                 key="proc_equipe")
        st.code(f"CALL sp_desempenho_equipe({id_equipe});", language="sql")
        try:
            df = db.chamar_procedure("sp_desempenho_equipe", (id_equipe,))
            st.dataframe(df, hide_index=True)
        except Exception as erro:
            db.mostrar_erro(erro)
