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

# Sidebar: uitleg sneltoetsen
with st.sidebar.expander("Sneltoetsen & Werking"):
    st.markdown("""
    **Navigatie:**
    - <kbd>j</kbd> : Volgende stap
    - <kbd>k</kbd> : Vorige stap

    **Status:**
    - <kbd>g</kbd> : Stap op 'goed'
    - <kbd>f</kbd> : Stap op 'fout'

    **Opmerking:**
    - <kbd>:</kbd> : Opmerking toevoegen
    - <kbd>Esc</kbd> : Opmerking sluiten
    """)

# Initialiseer sessiestate
for key, default in [
    ("step_index", 0),
    ("statuses", {}),
    ("comments", {}),
    ("show_metadata", False),
    ("show_comment_input", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default


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

        st.markdown(
            f'<div style="display:flex; align-items:center;">'
            f'<span>Geselecteerd onderdeel: </span>'
            f'<span style="color:#81a2be; font-weight:bold; margin-left:4px;">{selected_title}</span>'
            f'<span style="margin-left:auto; font-weight:bold; color:#f0c674;">Huidige stap: {st.session_state.step_index + 1} / {len(selected_testcase.get("steps", []))}</span>'
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
            st.session_state.step_index = 0
            st.rerun()

        selected_testcase = next(tc for tc in testcases if tc["id"] == st.session_state.selected_tc_id)
        steps = selected_testcase.get("steps", [])
        df = pd.DataFrame(steps)
        df["Status"] = df["step"].map(st.session_state.statuses).fillna("")
        df["Opmerking"] = df["step"].map(st.session_state.comments).fillna("")

        # Hotkeys
        pressed_prev = hotkeys.pressed("prev_step")
        pressed_next = hotkeys.pressed("next_step")
        pressed_good = hotkeys.pressed("set_good")
        pressed_fault = hotkeys.pressed("set_fault")
        pressed_toggle_comment = hotkeys.pressed("toggle_comment_input")
        pressed_save_comment = hotkeys.pressed("save_comment_and_exit")

        if st.session_state.show_comment_input:
            new_comment = st.text_input(
                ":",
                key="comment_input",
                value=st.session_state.comments.get(df.iloc[st.session_state.step_index]["step"], ""),
                label_visibility="collapsed",
            )
            if pressed_save_comment:
                st.session_state.comments[df.iloc[st.session_state.step_index]["step"]] = new_comment
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

        # Sliding window max 7 rijen met correcte start_idx berekening
        window_size = 7
        num_rows = len(df)
        step_num = st.session_state.step_index

        if num_rows <= window_size:
            start_idx = 0
        else:
            half_window = window_size // 2
            if step_num <= half_window:
                start_idx = 0
            elif step_num >= num_rows - half_window - 1:
                start_idx = num_rows - window_size
            else:
                start_idx = step_num - half_window
        end_idx = start_idx + window_size

        # ✅ FIX: reset index zodat highlight synchroon loopt
        df_window = df.iloc[start_idx:end_idx].reset_index(drop=True)

        def highlight_row(x):
            active_rel_idx = st.session_state.step_index - start_idx
            return [
                'background-color: #f0c674; color: #000; font-weight: bold;'
                if x.name == active_rel_idx else ''
                for _ in x
            ]

        st.dataframe(df_window.style.apply(highlight_row, axis=1), use_container_width=True)

        # Knoppen en slider
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
            step_num_new = st.slider("Stap navigatie", 1, len(df), st.session_state.step_index + 1)
            if step_num_new - 1 != st.session_state.step_index:
                st.session_state.step_index = step_num_new - 1
                st.rerun()

        st.info("j/k: Vorige / Volgende stap, g/f: Status goed/fout, : voor opmerking, Esc: opslaan opmerking en stoppen met typen, knop in sidebar: Toon/verberg metadata")

    except json.JSONDecodeError:
        st.sidebar.error("Ongeldig JSON bestand, probeer opnieuw.")
else:
    st.sidebar.info("Upload een JSON bestand om te beginnen.")
