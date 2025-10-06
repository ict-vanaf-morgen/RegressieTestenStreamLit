import streamlit as st
import json
import pandas as pd
import streamlit_hotkeys as hotkeys

st.set_page_config(layout="wide")

# --- Verklein lege ruimte bovenin ---
st.markdown(
    """
    <style>
    /* Verklein de top-padding van de main content container */
    .block-container {
        padding-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --- Hotkeys activeren ---
hotkeys.activate([
    hotkeys.hk("prev_step", "k"),
    hotkeys.hk("next_step", "j"),
    hotkeys.hk("set_good", "g"),
    hotkeys.hk("set_fault", "f"),
    hotkeys.hk("toggle_comment_input", ":"),
    hotkeys.hk("save_comment_and_exit", "escape"),
])

title_placeholder = st.empty()

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

# --- Sessiestate initialiseren ---
for key, default in [
    ("step_index", 0),
    ("statuses", {}),
    ("comments", {}),
    ("show_metadata", False),
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

        # --- Compacte titel ---
        title_placeholder.markdown(
            f"<div style='font-size:20px; font-weight:bold; color:#81a2be; margin:0 0 0px 0;'>📊 testcase: {testcase_title}</div>",
            unsafe_allow_html=True
        )

        # Metadata sidebar
        if st.sidebar.button("Toon/verberg metadata", on_click=toggle_metadata):
            pass
        if st.session_state.show_metadata:
            st.sidebar.markdown("### Metadata inhoud:")
            metadata = data.get("metadata", {})
            for key, value in metadata.items():
                st.sidebar.markdown(f"- **{key}**: {value}")

        # Testcases selecteren
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

        # --- Hotkeys detecteren ---
        pressed_prev = hotkeys.pressed("prev_step")
        pressed_next = hotkeys.pressed("next_step")
        pressed_good = hotkeys.pressed("set_good")
        pressed_fault = hotkeys.pressed("set_fault")
        pressed_save_comment = hotkeys.pressed("save_comment_and_exit")

        # Hotkeys acties
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

        # --- Sliding window max 7 rijen ---
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

        df_window = df.iloc[start_idx:end_idx].reset_index(drop=True)

        def highlight_row(x):
            active_rel_idx = st.session_state.step_index - start_idx
            return [
                'background-color: #f0c674; color: #000; font-weight: bold;' if x.name == active_rel_idx else ''
                for _ in x
            ]

        st.dataframe(df_window.style.apply(highlight_row, axis=1), use_container_width=True)

        # --- Knoppen en slider ---
        col_buttons, col_slider = st.columns([6, 3])  # Verhoudingen naar wens

        with col_buttons:
            # Maak 6 kolommen voor de buttons
            btn_j, btn_k, btn_g, btn_f, btn_colon, btn_esc = st.columns(6)
    
            if btn_j.button("j ⬇️", key="btn_j_down"):
                st.session_state.step_index = min(len(df) - 1, st.session_state.step_index + 1)
                st.rerun()
            if btn_k.button("k ⬆️", key="btn_k_up"):
                st.session_state.step_index = max(0, st.session_state.step_index - 1)
                st.rerun()
            if btn_g.button("g ✅", key="btn_g_good"):
                update_status(df.iloc[st.session_state.step_index]["step"], "goed✅")
                st.rerun()
            if btn_f.button("f ❌", key="btn_f_fault"):
                update_status(df.iloc[st.session_state.step_index]["step"], "fout❌")
                st.rerun()
            if btn_colon.button(": 📝", key="btn_colon_comment"):
                pass  # veld is permanent
            if btn_esc.button("Esc 🚫", key="btn_esc_cancel"):
                pressed_save_comment = True  # simuleer Escape voor opslaan

        with col_slider:
            step_num_new = st.slider(
                "Stap navigatie",
                1,
                len(df),
                st.session_state.step_index + 1
            )
            if step_num_new - 1 != st.session_state.step_index:
                st.session_state.step_index = step_num_new - 1
                st.rerun()


        # --- Permanent opmerkingenveld onderaan ---
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### ✏️ Opmerking")

        current_step = df.iloc[st.session_state.step_index]["step"]
        new_comment = st.text_input(
            "Typ hier je opmerking:",
            key="comment_input",
            value=st.session_state.comments.get(current_step, ""),
            label_visibility="collapsed",
        )

        # Opslaan bij Enter of Escape
        if new_comment != st.session_state.comments.get(current_step, "") or pressed_save_comment:
            st.session_state.comments[current_step] = new_comment

        # --- Info onderaan pagina ---
        st.info(
            "j/k: Vorige / Volgende stap, "
            "g/f: Status goed/fout, "
            ": voor opmerking, "
            "Esc: opslaan opmerking en stoppen met typen, "
            "knop in sidebar: Toon/verberg metadata"
        )

    except json.JSONDecodeError:
        st.sidebar.error("Ongeldig JSON bestand, probeer opnieuw.")
else:
    st.sidebar.info("Upload een JSON bestand om te beginnen.")
