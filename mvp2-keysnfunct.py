import streamlit as st
import json
import pandas as pd
import streamlit_hotkeys as hotkeys

st.set_page_config(layout="wide")

hotkeys.activate([
    hotkeys.hk("prev_step", "k"),
    hotkeys.hk("next_step", "j"),
    hotkeys.hk("set_good", "g"),
    hotkeys.hk("set_fault", "f"),
    hotkeys.hk("toggle_comment_input", ":"),
    hotkeys.hk("save_comment_and_exit", "escape"),
])

title_placeholder = st.empty()
title_placeholder.title("📊 Regressietesten Viewer")

uploaded_file = st.sidebar.file_uploader("Upload je testcase JSON-bestand", type="json")

with st.sidebar.expander("Sneltoetsen & Werking"):
    st.markdown("""
    Gebruik de onderstaande toetsen om door de stappen te navigeren en hun status bij te werken
    
    **Navigatie:**
    - `j` : Volgende stap, rij naar beneden
    - `k` : Vorige stap, rij naar boven

    **Status:**
    - `g` : Stap op 'goed'
    - `f` : Stap op 'fout'

    **Opmerking:**
    - `:`   : Opmerking toevoegen
    - `Esc` : Opmerking sluiten
    """)

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

if uploaded_file:
    try:
        data = json.load(uploaded_file)
        testcase_title = data.get("metadata", {}).get("Testcase", "Onbekende Testcase")
        title_placeholder.title(f"📊 testcase: {testcase_title}")

        if st.sidebar.button("Toon/verberg metadata", on_click=toggle_metadata):
            pass

        if st.session_state.show_metadata:
            st.sidebar.markdown("### Metadata inhoud:")
            metadata = data.get("metadata", {})
            for key, value in metadata.items():
                st.sidebar.markdown(f"- **{key}**: {value}")

        testcases = data.get("testcases", [])
        testcase_ids = [tc["id"] for tc in testcases]

        if "selected_tc_id" not in st.session_state:
            st.session_state.selected_tc_id = testcase_ids[0]

        selected_tc_id = st.session_state.selected_tc_id
        selected_testcase = next(tc for tc in testcases if tc["id"] == selected_tc_id)
        selected_title = selected_testcase.get("title", "")

        step_num = st.session_state.step_index

        # Combineer titel en huidige stap op één lijn
        st.markdown(
            f'<div style="display:flex; align-items:center;">'
            f'<span>Geselecteerd onderdeel: </span>'
            f'<span style="color:#81a2be; font-weight:bold; margin-left:4px;">{selected_title}</span>'
            f'<span style="margin-left:auto; font-weight:bold; color:#f0c674;">Huidige stap: {step_num + 1} / {len(selected_testcase.get("steps", []))}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        selected_tc_id_new = st.selectbox(
            "",
            testcase_ids,
            index=testcase_ids.index(selected_tc_id),
            key="selected_tc_id"
        )
        if selected_tc_id_new != selected_tc_id:
            st.session_state.selected_tc_id = selected_tc_id_new
            st.session_state.step_index = 0  # reset stap index bij andere testcase
            st.rerun()

        selected_testcase = next(tc for tc in testcases if tc["id"] == st.session_state.selected_tc_id)
        steps = selected_testcase.get("steps", [])
        df = pd.DataFrame(steps)
        df["Status"] = df["step"].map(st.session_state.statuses).fillna("")
        df["Opmerking"] = df["step"].map(st.session_state.comments).fillna("")

        # Hotkeys lezen
        pressed_prev = hotkeys.pressed("prev_step")
        pressed_next = hotkeys.pressed("next_step")
        pressed_good = hotkeys.pressed("set_good")
        pressed_fault = hotkeys.pressed("set_fault")
        pressed_toggle_comment = hotkeys.pressed("toggle_comment_input")
        pressed_save_comment = hotkeys.pressed("save_comment_and_exit")

        # Commentaar invoer afhandeling
        if st.session_state.show_comment_input:
            new_comment = st.text_input(
                ":",
                key="comment_input",
                value=st.session_state.comments.get(df.iloc[step_num]["step"], ""),
                label_visibility="collapsed",
            )
            if pressed_save_comment:
                st.session_state.comments[df.iloc[step_num]["step"]] = new_comment
                st.session_state.show_comment_input = False
                st.rerun()
        else:
            if pressed_prev:
                st.session_state.step_index = max(0, st.session_state.step_index - 1)
                st.rerun()
            if pressed_next:
                st.session_state.step_index = min(len(df) - 1, st.session_state.step_index + 1)
                st.rerun()
            if pressed_good:
                update_status(df.iloc[st.session_state.step_index]["step"], "goed✅")
                st.rerun()
            if pressed_fault:
                update_status(df.iloc[st.session_state.step_index]["step"], "fout❌")
                st.rerun()
            if pressed_toggle_comment:
                st.session_state.show_comment_input = True
                st.rerun()

        start_idx = max(0, step_num - 3)
        end_idx = min(len(df), step_num + 4)
        if end_idx - start_idx < 7:
            end_idx = min(len(df), start_idx + 7)
        df_window = df.iloc[start_idx:end_idx]
        relative_active_idx = step_num - start_idx

        def highlight_row(rel_idx):
            def hl(x):
                return [
                    'background-color: #f0c674; color: #000; font-weight: bold;' if x.name == rel_idx else ''
                    for _ in x
                ]
            return hl

        st.dataframe(df_window.style.apply(highlight_row(relative_active_idx), axis=1))

        # Knoppen en slider layout
        col_buttons, col_slider = st.columns([4, 3])

        with col_buttons:
            button_cols = st.columns(6)
            with button_cols[0]:
                if st.button("j ⬇️", key="btn_j_down"):
                    st.session_state.step_index = min(len(df) - 1, st.session_state.step_index + 1)
                    st.rerun()
            with button_cols[1]:
                if st.button("k ⬆️", key="btn_k_up"):
                    st.session_state.step_index = max(0, st.session_state.step_index - 1)
                    st.rerun()
            with button_cols[2]:
                if st.button("g ✅", key="btn_g_good"):
                    update_status(df.iloc[st.session_state.step_index]["step"], "goed✅")
                    st.rerun()
            with button_cols[3]:
                if st.button("f ❌", key="btn_f_fault"):
                    update_status(df.iloc[st.session_state.step_index]["step"], "fout❌")
                    st.rerun()
            with button_cols[4]:
                if st.button(": 📝", key="btn_colon_comment"):
                    st.session_state.show_comment_input = True
                    st.rerun()
            with button_cols[5]:
                if st.button("Esc 🚫", key="btn_esc_cancel"):
                    if st.session_state.show_comment_input:
                        st.session_state.show_comment_input = False
                        st.rerun()


        with col_slider:
            step_num_new = st.slider("Stap navigatie", 1, len(df), step_num + 1)
            st.session_state.step_index = step_num_new - 1

        st.info("j/k: Vorige / Volgende stap, g/f: Status goed/fout, : voor opmerking, Esc: opslaan opmerking en stoppen met typen, knop in sidebar: Toon/verberg metadata")

    except json.JSONDecodeError:
        st.sidebar.error("Ongeldig JSON bestand, probeer opnieuw.")
else:
    st.sidebar.info("Upload een JSON bestand om te beginnen.")
