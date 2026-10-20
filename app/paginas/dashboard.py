"""Dashboard: indicadores (cards) e gráficos feitos com plotly."""

import plotly.express as px
import streamlit as st

import db

# Paleta de cores fixa: cada categoria sempre recebe a mesma cor, na mesma ordem
COR_PRINCIPAL = "#2a78d6"
CORES_CATEGORIAS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
                    "#e87ba4", "#008300", "#6250d6", "#e34948"]


def estilo(fig):
    """Ajustes visuais comuns a todos os gráficos."""
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360,
                      hoverlabel=dict(bgcolor="white"))
    return fig


def mostrar():
    st.title("📊 Dashboard")

    # ---------------- Cards com totais ----------------
    totais = db.consultar(
        """
        SELECT (SELECT COUNT(*) FROM equipe)                      AS equipes,
               (SELECT COUNT(*) FROM robo)                        AS robos,
               (SELECT COUNT(DISTINCT nome_prova) FROM resultado) AS provas,
               (SELECT COUNT(*) FROM integrante)                  AS integrantes
        """
    ).iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Equipes", int(totais.equipes), border=True)
    c2.metric("Robôs", int(totais.robos), border=True)
    c3.metric("Provas", int(totais.provas), border=True)
    c4.metric("Integrantes", int(totais.integrantes), border=True)

    col_esq, col_dir = st.columns(2)

    # ---------------- Barras: pontuação total por equipe ----------------
    with col_esq:
        st.subheader("Pontuação total por equipe")
        df = db.consultar(
            """
            SELECT e.nome_equipe, COALESCE(SUM(res.pontuacao), 0) AS pontuacao_total
            FROM equipe e
            LEFT JOIN robo r        ON r.id_equipe = e.id_equipe
            LEFT JOIN resultado res ON res.id_robo = r.id_robo
            GROUP BY e.id_equipe, e.nome_equipe
            ORDER BY pontuacao_total
            """
        )
        fig = px.bar(df, x="pontuacao_total", y="nome_equipe", orientation="h",
                     text="pontuacao_total",
                     labels={"pontuacao_total": "Pontuação total", "nome_equipe": ""},
                     color_discrete_sequence=[COR_PRINCIPAL])
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside", cliponaxis=False)
        st.plotly_chart(estilo(fig))

    # ---------------- Pizza: robôs por categoria ----------------
    with col_dir:
        st.subheader("Robôs por categoria")
        df = db.consultar(
            "SELECT categoria, COUNT(*) AS quantidade FROM robo "
            "GROUP BY categoria ORDER BY quantidade DESC, categoria"
        )
        fig = px.pie(df, names="categoria", values="quantidade", hole=0.45,
                     color_discrete_sequence=CORES_CATEGORIAS)
        fig.update_traces(textinfo="label+value", marker_line_color="white",
                          marker_line_width=2)
        st.plotly_chart(estilo(fig))

    # ---------------- Barras: média de pontuação por prova ----------------
    st.subheader("Média de pontuação por prova")
    df = db.consultar(
        """
        SELECT nome_prova, ROUND(AVG(pontuacao), 2) AS media, COUNT(*) AS participantes
        FROM resultado
        GROUP BY nome_prova
        ORDER BY nome_prova
        """
    )
    fig = px.bar(df, x="nome_prova", y="media", text="media",
                 hover_data={"participantes": True},
                 labels={"nome_prova": "Prova", "media": "Média de pontuação",
                         "participantes": "Participantes"},
                 color_discrete_sequence=[COR_PRINCIPAL])
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside", cliponaxis=False)
    fig.update_yaxes(range=[0, 105])
    st.plotly_chart(estilo(fig))
