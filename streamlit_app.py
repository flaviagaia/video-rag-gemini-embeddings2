from __future__ import annotations

import streamlit as st

from src.pipeline import DEFAULT_QUERY, run_pipeline


st.set_page_config(
    page_title="Busca em Vídeos",
    page_icon="🎬",
    layout="wide",
)

SUGGESTED_QUESTIONS = [
    "Em que momento o vídeo mostra como preparar o molho com alho e manteiga?",
    "Onde aparece a etapa de cortar tomates e pepino?",
    "Quando o vídeo mostra como fazer o molho da salada?",
]


st.title("Encontre o momento certo do vídeo")
st.caption(
    "Faça uma pergunta e a demo encontra o trecho mais relevante do vídeo, com o tempo exato da etapa."
)

with st.sidebar:
    st.subheader("Como usar")
    st.markdown(
        "- Escreva uma pergunta sobre uma etapa da receita.\n"
        "- Clique em **Buscar no vídeo**.\n"
        "- Veja a resposta e o tempo exato do trecho.\n"
        "- Abaixo você pode comparar outros trechos parecidos."
    )
    selected_example = st.selectbox(
        "Ou escolha um exemplo",
        options=SUGGESTED_QUESTIONS,
        index=0,
    )

question = st.text_input(
    "O que você quer encontrar no vídeo?",
    value=selected_example,
    help="Exemplo: Em que momento o vídeo mostra como preparar o molho com alho e manteiga?",
)

run_clicked = st.button("Buscar no vídeo", type="primary", use_container_width=True)

if run_clicked or question:
    result = run_pipeline(question)
    answer = result["answer"]
    citations = answer["citations"]
    top_citation = citations[0]

    metric_col_1, metric_col_2, metric_col_3 = st.columns(3)
    metric_col_1.metric("Vídeo encontrado", top_citation["recipe_title"])
    metric_col_2.metric("Momento do vídeo", result["top_time_range"])
    metric_col_3.metric("Trechos sugeridos", str(len(citations)))

    left_col, right_col = st.columns([1.3, 1])

    with left_col:
        st.subheader("Resposta")
        st.markdown(answer["answer"])
        st.info("Resultado gerado a partir do conteúdo disponível nesta demo.")

        st.subheader("Outros trechos relacionados")
        for position, citation in enumerate(citations, start=1):
            with st.container(border=True):
                st.markdown(
                    f"**#{position} {citation['recipe_title']}**  \n"
                    f"Momento: **{citation['time_range']}**  \n"
                    f"Trecho do vídeo: `{citation['video_id']}`"
                )

    with right_col:
        st.subheader("Melhor momento encontrado")
        st.success(
            f"O melhor resultado está em {top_citation['time_range']} do vídeo {top_citation['video_id']}."
        )

        st.markdown("**Por que isso é útil**")
        st.write(
            "Em vez de mostrar um vídeo inteiro, a busca aponta exatamente o momento em que a etapa aparece."
        )

        with st.expander("Detalhes técnicos"):
            st.json(
                {
                    "runtime_mode": result["runtime_mode"],
                    "dataset_source": result["dataset_source"],
                    "segment_count": result["segment_count"],
                    "top_segment_id": result["top_segment_id"],
                    "top_similarity": result["top_similarity"],
                    "report_artifact": result["report_artifact"],
                }
            )
