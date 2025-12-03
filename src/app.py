import streamlit as st

from rag_pipeline import answer_question

st.set_page_config(
    page_title="NJDOT C&M Spec Assistant",
    layout="wide",
)

st.title("NJDOT C&M Spec Assistant")
st.caption("Ask questions about the 2019 Standard Specifications for Road and Bridge Construction.")

st.markdown(
    """
This assistant uses a Retrieval-Augmented Generation (RAG) pipeline over the
**2019 Standard Specifications for Road and Bridge Construction**.

Type your question below, and it will:
- Search the spec for relevant sections
- Ask an LLM (via Groq) to answer based only on those sections
- Show which sections/pages were used
"""
)

with st.form("question_form"):
    question = st.text_area(
        "Ask a question about the 2019 Standard Specs:",
        placeholder="e.g., What are the requirements for hot mix asphalt?",
        height=100,
    )
    k = st.slider("Number of sections to retrieve", min_value=3, max_value=10, value=5)
    submitted = st.form_submit_button("Ask")

if submitted and question.strip():
    with st.spinner("Thinking..."):
        try:
            result = answer_question(question.strip(), k=k)
        except Exception as e:
            st.error(f"Error while answering question: {e}")
        else:
            st.subheader("Answer")
            st.write(result["answer"])

            st.subheader("Sources")
            sources = result.get("sources", [])
            if not sources:
                st.write("No sources returned.")
            else:
                for s in sources:
                    st.markdown(
                        f"- **Section {s['section_id']}**, pages {s['page_start']}–{s['page_end']} "
                        f"(score: {s['score']:.4f})"
                    )

            with st.expander("Debug info (for internal testing)", expanded=False):
                st.json(result.get("debug", {}))
elif submitted:
    st.warning("Please enter a question before submitting.")

st.markdown("---")
st.caption("Phase 1 prototype · C&M Training Assistant")