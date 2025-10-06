import streamlit as st
import json
import pandas as pd

# Placeholder voor dynamische titel
title_placeholder = st.empty()
title_placeholder.title("📊 Regressietesten Viewer")

st.set_page_config(layout="wide")

# Sidebar voor upload en toggle
st.sidebar.header("Bestandsbeheer")
uploaded_file = st.sidebar.file_uploader("Upload je testcase JSON-bestand", type="json")

if 'show_metadata' not in st.session_state:
    st.session_state.show_metadata = False

def toggle_metadata():
    st.session_state.show_metadata = not st.session_state.show_metadata

if uploaded_file:
    try:
        data = json.load(uploaded_file)
        testcase_title = data.get("metadata", {}).get("Testcase", "Onbekende Testcase")
        title_placeholder.title(f"📊 testcase: {testcase_title}")

        btn_label = "Verberg metadata" if st.session_state.show_metadata else "Toon metadata"
        st.sidebar.button(btn_label, on_click=toggle_metadata)

        if st.session_state.show_metadata:
            st.sidebar.markdown("### Metadata inhoud:")
            metadata = data.get("metadata", {})
            for key, value in metadata.items():
                st.sidebar.markdown(f"- **{key}**: {value}")

        # Selecteer testcase uit lijst op basis van id of index
        testcases = data.get("testcases", [])
        testcase_ids = [tc["id"] for tc in testcases]
        selected_tc_id = st.selectbox("geselecteerd sub-onderdeel:", testcase_ids)

        # Uitgekozen testcase ophalen
        selected_testcase = next(tc for tc in testcases if tc["id"] == selected_tc_id)

        # Stappen ophalen en omzetten naar dataframe
        steps = selected_testcase.get("steps", [])
        df_steps = pd.DataFrame(steps)

        # Tabel tonen van stappen
        st.markdown(f"### {selected_tc_id}: {selected_testcase.get('title')}")
        st.dataframe(df_steps)

    except json.JSONDecodeError:
        st.sidebar.error("Ongeldig JSON bestand, probeer het opnieuw met een correct JSON bestand.")
else:
    st.sidebar.info("Upload een JSON bestand om te beginnen.")
