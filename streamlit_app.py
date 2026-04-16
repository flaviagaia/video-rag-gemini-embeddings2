from __future__ import annotations

import streamlit as st

from src.pipeline import DEFAULT_QUERY, run_pipeline


st.set_page_config(
    page_title="Video RAG Demo",
    page_icon="🎬",
    layout="wide",
)

st.title("Video RAG with Gemini Embedding 2")
st.caption(
    "Demo de retrieval grounded para videos instrucionais com chunks temporais, "
    "timestamps e fallback local reproduzivel."
)

with st.sidebar:
    st.subheader("Como ler esta demo")
    st.markdown(
        "- Faça uma pergunta sobre um passo do vídeo.\n"
        "- O sistema recupera os trechos mais relevantes.\n"
        "- A resposta final aponta o momento exato do vídeo.\n"
        "- O runtime pode ser `gemini_embedding_2` ou `local_tfidf_fallback`."
    )

question = st.text_input(
    "Pergunta sobre o vídeo",
    value=DEFAULT_QUERY,
    help="Exemplo: Where does the video show slicing garlic and melting butter for the sauce?",
)

run_clicked = st.button("Buscar trecho", type="primary", use_container_width=True)

if run_clicked or question:
    result = run_pipeline(question)
    answer = result["answer"]
    citations = answer["citations"]

    metric_col_1, metric_col_2, metric_col_3, metric_col_4 = st.columns(4)
    metric_col_1.metric("Runtime", result["runtime_mode"])
    metric_col_2.metric("Top Segment", result["top_segment_id"])
    metric_col_3.metric("Top Time Range", result["top_time_range"])
    metric_col_4.metric("Top Similarity", f'{result["top_similarity"]:.4f}')

    left_col, right_col = st.columns([1.3, 1])

    with left_col:
        st.subheader("Resposta grounded")
        st.markdown(answer["answer"])
        st.info(answer["limitation_note"])

        st.subheader("Top trechos recuperados")
        for position, citation in enumerate(citations, start=1):
            with st.container(border=True):
                st.markdown(
                    f"**#{position} {citation['recipe_title']}**  \n"
                    f"`segment_id = {citation['segment_id']}`  \n"
                    f"`video_id = {citation['video_id']}`  \n"
                    f"`time_range = {citation['time_range']}`  \n"
                    f"`similarity = {citation['similarity']}`"
                )

    with right_col:
        st.subheader("Resumo do run")
        st.json(
            {
                "dataset_source": result["dataset_source"],
                "query": result["query"],
                "segment_count": result["segment_count"],
                "report_artifact": result["report_artifact"],
            }
        )

        st.subheader("Melhor evidência")
        top_citation = citations[0]
        st.success(
            f"O melhor match está em `{top_citation['time_range']}` "
            f"do vídeo `{top_citation['video_id']}`."
        )

        st.markdown("**Por que isso importa**")
        st.write(
            "A demo mostra que o sistema não responde apenas com um texto. "
            "Ele aponta um trecho temporal específico do vídeo, o que melhora "
            "grounding, explicabilidade e experiência de uso."
        )
