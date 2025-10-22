# py -m streamlit run v09lpt.py

import streamlit as st
import json
import pandas as pd
import streamlit_hotkeys as hotkeys

st.set_page_config(layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# --- Hotkeys ---
hotkeys.activate([
    hotkeys.hk("prev_step", "k"),
    hotkeys.hk("next_step", "j"),
    hotkeys.hk("set_good", "g"),
    hotkeys.hk("set_fault", "f"),
    hotkeys.hk("toggle_comment_input", "t"),  # focus commentaar
    hotkeys.hk("cancel_comment", "esc"),
])

# --- Sidebar uitleg ---
with st.sidebar.expander("Sneltoetsen & Werking"):
    st.markdown("""
**Navigatie:**  
- <kbd>j</kbd> : Volgende stap  
- <kbd>k</kbd> : Vorige stap  

**Status:**  
- <kbd>g</kbd> : Markeer als goed  
- <kbd>f</kbd> : Markeer als fout  

**Opmerking:**  
- <kbd>t</kbd> : Focus commentaarveld  
- <kbd>Enter</kbd> : Opslaan  
- <kbd>Esc</kbd> : Wissen
""")

# --- Sessiestate ---
for key, default in [
    ("step_index", 0),
    ("statuses", {}),
    ("comments", {}),
    ("show_metadata", False),
    ("selected_tc_id", None),
    ("comment_input", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

def update_status(step, status):
    st.session_state.statuses[step] = status

def toggle_metadata():
    st.session_state.show_metadata = not st.session_state.show_metadata

# --- Upload JSON ---
uploaded_file = st.sidebar.file_uploader("Upload je testcase JSON-bestand", type="json")

if uploaded_file:
    try:
        data = json.load(uploaded_file)
        testcase_title = data.get("metadata", {}).get("Testcase", "Onbekende Testcase")

        st.markdown(f"<div style='font-size:20px; font-weight:bold; color:#81a2be;'>📊 Testcase: {testcase_title}</div>",
                    unsafe_allow_html=True)

        # Metadata
        if st.sidebar.button("Toon/verberg metadata", on_click=toggle_metadata):
            pass
        if st.session_state.show_metadata:
            metadata = data.get("metadata", {})
            st.sidebar.markdown("### Metadata:")
            for k, v in metadata.items():
                st.sidebar.markdown(f"- **{k}**: {v}")

        # Testcases
        testcases = data.get("testcases", [])
        if not testcases:
            st.warning("⚠️ Geen testcases gevonden in het JSON-bestand.")
            st.stop()

        ids = [tc["id"] for tc in testcases]
        if st.session_state.selected_tc_id not in ids:
            st.session_state.selected_tc_id = ids[0]

        selected_tc = next(tc for tc in testcases if tc["id"] == st.session_state.selected_tc_id)
        steps = selected_tc.get("steps", [])
        df = pd.DataFrame(steps)
        df["Status"] = df["step"].map(st.session_state.statuses).fillna("")
        df["Opmerking"] = df["step"].map(st.session_state.comments).fillna("")

        # --- Hotkeys ---
        in_comment_mode = False  # we zetten dit later True als gebruiker typt
        pressed_toggle_comment = hotkeys.pressed("toggle_comment_input")
        pressed_cancel_comment = hotkeys.pressed("cancel_comment")

        if not in_comment_mode:
            pressed_prev = hotkeys.pressed("prev_step")
            pressed_next = hotkeys.pressed("next_step")
            pressed_good = hotkeys.pressed("set_good")
            pressed_fault = hotkeys.pressed("set_fault")
        else:
            pressed_prev = pressed_next = pressed_good = pressed_fault = False

        # --- Acties ---
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
            # focus commentaarveld via JS
            st.markdown("""
            <script>
            const textarea = window.parent.document.querySelector('textarea[aria-label="comment_input"]');
            if (textarea) { textarea.focus(); }
            </script>
            """, unsafe_allow_html=True)
        if pressed_cancel_comment:
            current_step = df.iloc[st.session_state.step_index]["step"]
            st.session_state.comments[current_step] = ""
            st.info("Opmerking gewist")
            st.rerun()

        # --- Sliding window ---
        window_size = 7
        num_rows = len(df)
        step_num = st.session_state.step_index
        half_window = window_size // 2

        if num_rows <= window_size:
            start_idx = 0
        elif step_num <= half_window:
            start_idx = 0
        elif step_num >= num_rows - half_window - 1:
            start_idx = num_rows - window_size
        else:
            start_idx = step_num - half_window

        end_idx = start_idx + window_size
        df_window = df.iloc[start_idx:end_idx].reset_index(drop=True)

        def highlight_row(x):
            active_rel_idx = st.session_state.step_index - start_idx
            return ['background-color: #f0c674; color: #000; font-weight: bold;' if x.name == active_rel_idx else '' for _ in x]

        st.dataframe(df_window.style.apply(highlight_row, axis=1), use_container_width=True)

        # --- Knoppen en slider ---
        col_buttons, col_slider = st.columns([6,3])
        with col_buttons:
            btn_j, btn_k, btn_g, btn_f, btn_esc = st.columns(5)
            if btn_j.button("j ⬇️", key="btn_j_down"):
                st.session_state.step_index = min(len(df)-1, st.session_state.step_index+1)
                st.rerun()
            if btn_k.button("k ⬆️", key="btn_k_up"):
                st.session_state.step_index = max(0, st.session_state.step_index-1)
                st.rerun()
            if btn_g.button("g ✅", key="btn_g_good"):
                update_status(df.iloc[st.session_state.step_index]["step"], "goed✅")
                st.rerun()
            if btn_f.button("f ❌", key="btn_f_fault"):
                update_status(df.iloc[st.session_state.step_index]["step"], "fout❌")
                st.rerun()
            if btn_esc.button("Esc 🚫", key="btn_esc_cancel"):
                current_step = df.iloc[st.session_state.step_index]["step"]
                st.session_state.comments[current_step] = ""
                st.info("Opmerking gewist")
                st.rerun()

        with col_slider:
            step_num_new = st.slider("Stap navigatie", 1, len(df), st.session_state.step_index+1)
            if step_num_new-1 != st.session_state.step_index:
                st.session_state.step_index = step_num_new-1
                st.rerun()

        # --- Permanent commentaarveld ---
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### ✏️ Opmerking")

        current_step = df.iloc[st.session_state.step_index]["step"]
        st.session_state.comment_input = st.session_state.comments.get(current_step,"")

        with st.form("comment_form"):
            new_comment = st.text_area(
                "Typ hier je opmerking:",
                key="comment_input",
                height=100,
                label_visibility="collapsed",
                placeholder="Druk op Enter om op te slaan"
            )
            submitted = st.form_submit_button("💾 Opslaan")

        if submitted:
            st.session_state.comments[current_step] = st.session_state.comment_input
            st.success("Opmerking opgeslagen!")
            st.rerun()

        # --- Info ---
        st.info("Hotkeys: j/k (navigatie), g/f (goed/fout), Enter (opslaan), Esc (wissen), t (focus commentaar)")

    except json.JSONDecodeError:
        st.sidebar.error("Ongeldig JSON-bestand.")
    except Exception as e:
        st.error(f"Er is een fout opgetreden: {e}")
else:
    st.sidebar.info("Upload een JSON-bestand om te beginnen.")
