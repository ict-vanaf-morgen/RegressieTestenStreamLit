# py -m streamlit run v04.py
import streamlit as st
import json
import pandas as pd
import streamlit_hotkeys as hotkeys

st.set_page_config(layout="wide")

# --- Verklein lege ruimte bovenin ---
st.markdown(
    """
    <style>
    .block-container { padding-top: 1rem; }
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
    hotkeys.hk("toggle_comment_input", "t"),
    hotkeys.hk("save_comment_and_exit", "enter"),
    hotkeys.hk("cancel_comment", "esc"),
])

# --- Sidebar uitleg ---
with st.sidebar.expander("Sneltoetsen & Werking"):
    st.markdown("""
    **Navigatie:**
    - <kbd>j</kbd> : Volgende stap  
    - <kbd>k</kbd> : Vorige stap  

    **Status:**
    - <kbd>g</kbd> : Stap op 'goed'  
    - <kbd>f</kbd> : Stap op 'fout'  

    **Opmerking:**
    - <kbd>t</kbd> : Opmerking toevoegen  
    - <kbd>Enter</kbd> : Opslaan  
    - <kbd>Esc</kbd> : Sluiten zonder opslaan
    """)

# --- Sessiestate initialiseren ---
for key, default in [
    ("step_index", 0),
    ("statuses", {}),
    ("comments", {}),
    ("show_metadata", False),
    ("selected_tc_id", None),
    ("show_comment_input", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# --- Hulpfuncties ---
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

        st.markdown(
            f"<div style='font-size:20px; font-weight:bold; color:#81a2be;'>📊 Testcase: {testcase_title}</div>",
            unsafe_allow_html=True
        )

        # Metadata tonen/verbergen
        if st.sidebar.button("Toon/verberg metadata", on_click=toggle_metadata):
            pass
        if st.session_state.show_metadata:
            metadata = data.get("metadata", {})
            st.sidebar.markdown("### Metadata:")
            for k, v in metadata.items():
                st.sidebar.markdown(f"- **{k}**: {v}")

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

        # --- Hotkeys detecteren ---
        if not st.session_state.show_comment_input:
            pressed_prev = hotkeys.pressed("prev_step")
            pressed_next = hotkeys.pressed("next_step")
            pressed_good = hotkeys.pressed("set_good")
            pressed_fault = hotkeys.pressed("set_fault")
            pressed_toggle_comment = hotkeys.pressed("toggle_comment_input")
            pressed_save_comment = False
            pressed_cancel_comment = False
        else:
            # Alleen Enter en Esc actief in commentaar-modus
            pressed_prev = pressed_next = pressed_good = pressed_fault = pressed_toggle_comment = False
            pressed_save_comment = hotkeys.pressed("save_comment_and_exit")
            pressed_cancel_comment = hotkeys.pressed("cancel_comment")

        # --- Navigatie ---
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

        # --- Commentaar prompt ---
        if pressed_toggle_comment:
            st.session_state.show_comment_input = not st.session_state.show_comment_input
            st.rerun()

        # --- Tabel tonen met highlight ---
        def highlight_row(x):
            active = st.session_state.step_index
            return ['background-color: #f0c674; color: #000; font-weight: bold;' if x.name == active else '' for _ in x]

        st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True)

        # --- Commentaar gedeelte ---
        st.markdown("---")
        st.markdown("### ✏️ Opmerking")

        current_step = df.iloc[st.session_state.step_index]["step"]

        if st.session_state.show_comment_input:
            new_comment = st.text_area(
                "Typ hier je opmerking:",
                key="comment_input",
                value=st.session_state.comments.get(current_step, ""),
                height=100,
                label_visibility="collapsed",
            )

            cols = st.columns([1, 1, 6])
            with cols[0]:
                if st.button("💾 Opslaan", key="btn_save_comment"):
                    st.session_state.comments[current_step] = new_comment
                    st.session_state.show_comment_input = False
                    st.rerun()
            with cols[1]:
                if st.button("❌ Annuleer", key="btn_cancel_comment"):
                    st.session_state.show_comment_input = False
                    st.rerun()

            if pressed_save_comment:
                st.session_state.comments[current_step] = new_comment
                st.session_state.show_comment_input = False
                st.rerun()

            if pressed_cancel_comment:
                st.session_state.show_comment_input = False
                st.rerun()

        else:
            st.write(st.session_state.comments.get(current_step, "_(geen opmerking)_"))

        # --- Info ---
        st.info("Hotkeys: j/k (navigatie), g/f (goed/fout), t (opmerking), Enter (opslaan), Esc (sluiten)")

    except json.JSONDecodeError:
        st.sidebar.error("Ongeldig JSON-bestand.")
    except Exception as e:
        st.error(f"Er is een fout opgetreden: {e}")
else:
    st.sidebar.info("Upload een JSON-bestand om te beginnen.")
