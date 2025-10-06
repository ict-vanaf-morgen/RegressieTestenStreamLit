import streamlit as st
import json
import pandas as pd
import streamlit_hotkeys as hotkeys

st.set_page_config(layout="wide")

# Activeer hotkeys
hotkeys.activate([
    hotkeys.hk("prev_step", "b"),
    hotkeys.hk("next_step", "n"),
    hotkeys.hk("set_good", "g"),
    hotkeys.hk("set_fault", "f"),
    hotkeys.hk("toggle_comment_input", "t"),
])

title_placeholder = st.empty()
title_placeholder.title("📊 Regressietesten Viewer")

uploaded_file = st.sidebar.file_uploader("Upload je testcase JSON-bestand", type="json")

if "step_index" not in st.session_state:
    st.session_state.step_index = 0
if "statuses" not in st.session_state:
    st.session_state.statuses = {}
if "comments" not in st.session_state:
    st.session_state.comments = {}
if "show_metadata" not in st.session_state:
    st.session_state.show_metadata = False
if "show_comment_input" not in st.session_state:
    st.session_state.show_comment_input = False

def update_status(step, status):
    st.session_state.statuses[step] = status

def toggle_metadata():
    st.session_state.show_metadata = not st.session_state.show_metadata

def toggle_comment_input():
    st.session_state.show_comment_input = not st.session_state.show_comment_input

if uploaded_file:
    try:
        data = json.load(uploaded_file)
        testcase_title = data.get("metadata", {}).get("Testcase", "Onbekende Testcase")
        title_placeholder.title(f"📊 testcase: {testcase_title}")

        # Metadata knop in sidebar
        if st.sidebar.button("Toon/verberg metadata", on_click=toggle_metadata):
            pass

        # Metadata toggle weergave
        if st.session_state.show_metadata:
            st.sidebar.markdown("### Metadata inhoud:")
            metadata = data.get("metadata", {})
            for key, value in metadata.items():
                st.sidebar.markdown(f"- **{key}**: {value}")

        testcases = data.get("testcases", [])
        testcase_ids = [tc["id"] for tc in testcases]
        selected_tc_id = st.selectbox("Selecteer testcase", testcase_ids)
        selected_testcase = next(tc for tc in testcases if tc["id"] == selected_tc_id)
        steps = selected_testcase.get("steps", [])

        df = pd.DataFrame(steps)
        df["Status"] = df["step"].map(st.session_state.statuses).fillna("")
        df["Opmerking"] = df["step"].map(st.session_state.comments).fillna("")

        # Keybindings
        if hotkeys.pressed("prev_step"):
            st.session_state.step_index = max(0, st.session_state.step_index - 1)
        if hotkeys.pressed("next_step"):
            st.session_state.step_index = min(len(df) - 1, st.session_state.step_index + 1)
        if hotkeys.pressed("set_good"):
            update_status(df.iloc[st.session_state.step_index]["step"], "goed✅")
        if hotkeys.pressed("set_fault"):
            update_status(df.iloc[st.session_state.step_index]["step"], "fout❌")
        if hotkeys.pressed("toggle_comment_input"):
            toggle_comment_input()

        step_num = st.slider("Stap navigatie", 1, len(df), st.session_state.step_index + 1) - 1
        st.session_state.step_index = step_num

        st.write(f"Stap {df.iloc[step_num]['step']} | Actie: {df.iloc[step_num]['actie']}")
        st.write(f"Gewenst resultaat: {df.iloc[step_num]['gewenst_resultaat']}")
        st.write(f"Status: {df.iloc[step_num]['Status']}")
        st.write(f"Opmerking: {df.iloc[step_num]['Opmerking']}")

        if st.session_state.show_comment_input:
            new_comment = st.text_input("Typ een opmerking voor deze stap:", key="comment_input")
            if st.button("Opslaan opmerking"):
                st.session_state.comments[df.iloc[step_num]["step"]] = new_comment
                st.session_state.show_comment_input = False
                st.experimental_rerun()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Goed ✅ (g)"):
                update_status(df.iloc[step_num]["step"], "goed✅")
        with col2:
            if st.button("Fout ❌ (f)"):
                update_status(df.iloc[step_num]["step"], "fout❌")

        st.dataframe(df)

        st.info("b/n: Vorige / Volgende stap, g/f: Status goed/fout, t: Opmerking typen, knop in sidebar: Toon/verberg metadata")

    except json.JSONDecodeError:
        st.sidebar.error("Ongeldig JSON bestand, probeer opnieuw.")
else:
    st.sidebar.info("Upload een JSON bestand om te beginnen.")
