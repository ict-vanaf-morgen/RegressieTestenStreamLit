import streamlit as st
import json
import pandas as pd
import streamlit_hotkeys as hotkeys

st.set_page_config(layout="wide")

# Activeer keybindings
hotkeys.activate([
    hotkeys.hk("prev_step", "b"),
    hotkeys.hk("next_step", "n"),
    hotkeys.hk("set_good", "g"),
    hotkeys.hk("set_fault", "f"),
])

title_placeholder = st.empty()
title_placeholder.title("📊 Regressietesten Viewer")

uploaded_file = st.sidebar.file_uploader("Upload je testcase JSON-bestand", type="json")

# Initialiseer session state variabelen
if 'step_index' not in st.session_state:
    st.session_state.step_index = 0
if 'statuses' not in st.session_state:
    st.session_state.statuses = {}

def update_status(step, status):
    st.session_state.statuses[step] = status

if uploaded_file:
    try:
        data = json.load(uploaded_file)
        testcase_title = data.get("metadata", {}).get("Testcase", "Onbekende Testcase")
        title_placeholder.title(f"📊 testcase: {testcase_title}")

        testcases = data.get("testcases", [])
        testcase_ids = [tc["id"] for tc in testcases]
        selected_tc_id = st.selectbox("Selecteer testcase", testcase_ids)

        selected_testcase = next(tc for tc in testcases if tc["id"] == selected_tc_id)
        steps = selected_testcase.get("steps", [])

        df = pd.DataFrame(steps)
        # Voeg Status kolom toe gebaseerd op st.session_state
        df["Status"] = df["step"].map(st.session_state.statuses).fillna("")

        # Verwerk keypress events
        if hotkeys.pressed("prev_step"):
            st.session_state.step_index = max(0, st.session_state.step_index - 1)
        if hotkeys.pressed("next_step"):
            st.session_state.step_index = min(len(df) - 1, st.session_state.step_index + 1)
        if hotkeys.pressed("set_good"):
            update_status(df.iloc[st.session_state.step_index]["step"], "goed✅")
        if hotkeys.pressed("set_fault"):
            update_status(df.iloc[st.session_state.step_index]["step"], "fout❌")

        # Navigatie slider
        step_num = st.slider("Stap navigatie", 1, len(df), st.session_state.step_index + 1) - 1
        st.session_state.step_index = step_num

        # Toon details van de huidige stap
        st.write(f"Stap {df.iloc[step_num]['step']} | Actie: {df.iloc[step_num]['actie']}")
        st.write(f"Gewenst resultaat: {df.iloc[step_num]['gewenst_resultaat']}")
        st.write(f"Status: {df.iloc[step_num]['Status']}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Goed ✅ (g)"):
                update_status(df.iloc[step_num]["step"], "goed✅")
        with col2:
            if st.button("Fout ❌ (f)"):
                update_status(df.iloc[step_num]["step"], "fout❌")

        # Toon de volledige tabel met actuele statussen
        st.dataframe(df)

        st.info("Gebruik b (back) en n (next) om te navigeren door de stappen. Gebruik g (goed) en f (fout) om status in te stellen.")

    except json.JSONDecodeError:
        st.sidebar.error("Ongeldig JSON bestand, probeer opnieuw.")
else:
    st.sidebar.info("Upload een JSON bestand om te beginnen.")
