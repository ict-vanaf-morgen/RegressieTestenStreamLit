import streamlit as st
import json
import pandas as pd
import streamlit_hotkeys as hotkeys

st.set_page_config(layout="wide")

hotkeys.activate([
    hotkeys.hk("prev_step", "b"),
    hotkeys.hk("next_step", "n"),
    hotkeys.hk("set_good", "g"),
    hotkeys.hk("set_fault", "f"),
    hotkeys.hk("toggle_sidebar", "s", alt=True),    # Alt+S
    hotkeys.hk("attach_movie", "m", alt=True),     # Alt+M
    hotkeys.hk("attach_screenshot", "p", alt=True),# Alt+P
    hotkeys.hk("view_keybinds", "k", alt=True),    # Alt+K
])

title_placeholder = st.empty()
title_placeholder.title("📊 Regressietesten Viewer")

uploaded_file = st.sidebar.file_uploader("Upload je testcase JSON-bestand", type="json")

if 'step_index' not in st.session_state:
    st.session_state.step_index = 0
if 'statuses' not in st.session_state:
    st.session_state.statuses = {}
if 'sidebar_visible' not in st.session_state:
    st.session_state.sidebar_visible = True

def update_status(step, status):
    st.session_state.statuses[step] = status

def toggle_sidebar():
    st.session_state.sidebar_visible = not st.session_state.sidebar_visible

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
        df["Status"] = df["step"].map(st.session_state.statuses).fillna("")

        # Hotkey acties
        if hotkeys.pressed("prev_step"):
            st.session_state.step_index = max(0, st.session_state.step_index - 1)
        if hotkeys.pressed("next_step"):
            st.session_state.step_index = min(len(df)-1, st.session_state.step_index +1)
        if hotkeys.pressed("set_good"):
            update_status(df.iloc[st.session_state.step_index]["step"], "goed✅")
        if hotkeys.pressed("set_fault"):
            update_status(df.iloc[st.session_state.step_index]["step"], "fout❌")
        if hotkeys.pressed("toggle_sidebar"):
            toggle_sidebar()
        if hotkeys.pressed("attach_movie"):
            st.toast("Voeg video toe aan huidige subsection - nog te implementeren")
        if hotkeys.pressed("attach_screenshot"):
            st.toast("Voeg screenshot toe aan huidige subsection - nog te implementeren")
        if hotkeys.pressed("view_keybinds"):
            st.toast("""
            Keybindings:\n
            b/n: vorige / volgende step\n
            g/f: status goed / fout\n
            Alt+S: Sidebar togglen\n
            Alt+M: Video toevoegen\n
            Alt+P: Screenshot toevoegen\n
            Alt+K: Keybindings tonen
            """)

        # Sidebar toggle
        if st.session_state.sidebar_visible:
            with st.sidebar:
                st.header("Bestandsbeheer")
                st.file_uploader("Upload je testcase JSON-bestand", type="json")
                st.write("Sidebar zichtbaar (met inhoud).")

        # Navigatie slider en status details
        step_num = st.slider("Stap navigatie", 1, len(df), st.session_state.step_index + 1) - 1
        st.session_state.step_index = step_num

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

        st.dataframe(df)

        st.info("Gebruik b/n om door stappen te navigeren.\nGebruik g/f om status te zetten.\nGebruik Alt+S/M/P/K voor extra functies.")

    except json.JSONDecodeError:
        st.sidebar.error("Ongeldig JSON bestand, probeer opnieuw.")
else:
    if st.session_state.sidebar_visible:
        with st.sidebar:
            st.header("Bestandsbeheer")
            uploaded_file = st.file_uploader("Upload een JSON bestand om te beginnen.")
