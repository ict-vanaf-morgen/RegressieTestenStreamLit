import streamlit as st
import pandas as pd
import streamlit_hotkeys as hotkeys
import json

st.set_page_config(layout="wide")

# Hotkeys registreren
hotkeys.activate([
    hotkeys.hk("prev_step", "k"),
    hotkeys.hk("next_step", "j"),
    hotkeys.hk("set_good", "g"),
    hotkeys.hk("set_fault", "f"),
    hotkeys.hk("toggle_comment_input", ":"),
    hotkeys.hk("save_comment_and_exit", "escape"),
])

# Initialiseer sessiestate
if "step_index" not in st.session_state:
    st.session_state.step_index = 0
if "statuses" not in st.session_state:
    st.session_state.statuses = {}
if "comments" not in st.session_state:
    st.session_state.comments = {}
if "show_comment_input" not in st.session_state:
    st.session_state.show_comment_input = False

def update_status(step, status):
    st.session_state.statuses[step] = status

def load_test_data():
    # Dummy data voor demo
    steps = [{"step": f"Stap {i}"} for i in range(1, 21)]
    return steps

steps = load_test_data()
df = pd.DataFrame(steps)

# Huidige stap index
step_num = st.session_state.step_index

# Titel en info
st.markdown(
    f'<div style="display:flex; align-items:center;">'
    f'<span>Geselecteerd onderdeel: </span>'
    f'<span style="color:#81a2be; font-weight:bold; margin-left:4px;">Demo Testcase</span>'
    f'<span style="margin-left:auto; font-weight:bold; color:#f0c674;">'
    f'Huidige stap: {step_num + 1} / {len(df)}'
    f'</span>'
    f'</div>',
    unsafe_allow_html=True
)

# Status en commentaar ophalen
df["Status"] = df["step"].map(st.session_state.statuses).fillna("")
df["Opmerking"] = df["step"].map(st.session_state.comments).fillna("")

# Hotkey events afhandelen
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
        value=st.session_state.comments.get(df.iloc[step_num]["step"], ""),
        label_visibility="collapsed",
    )
    if pressed_save_comment:
        st.session_state.comments[df.iloc[step_num]["step"]] = new_comment
        st.session_state.show_comment_input = False
        st.experimental_rerun()
else:
    if pressed_prev:
        st.session_state.step_index = max(0, st.session_state.step_index - 1)
    if pressed_next:
        st.session_state.step_index = min(len(df) - 1, st.session_state.step_index + 1)
    if pressed_good:
        update_status(df.iloc[st.session_state.step_index]["step"], "goed✅")
    if pressed_fault:
        update_status(df.iloc[st.session_state.step_index]["step"], "fout❌")
    if pressed_toggle_comment:
        st.session_state.show_comment_input = True

# Highlight actieve rij in tabel
def highlight_row(rel_idx):
    def hl(x):
        return [
            'background-color: #f0c674; color: #000; font-weight: bold;' if x.name == rel_idx else ''
            for _ in x
        ]
    return hl

start_idx = max(0, step_num - 3)
end_idx = min(len(df), step_num + 4)
if end_idx - start_idx < 7:
    end_idx = min(len(df), start_idx + 7)
df_window = df.iloc[start_idx:end_idx]
relative_active_idx = step_num - start_idx

st.dataframe(df_window.style.apply(highlight_row(relative_active_idx), axis=1))

# Lay-out: knoppen links, slider rechts
col_buttons, col_slider = st.columns([4, 3])

with col_buttons:
    button_cols = st.columns(6)
    with button_cols[0]:
        if st.button("j ⬇️", key="btn_j_down"):
            st.session_state.step_index = min(len(df) - 1, st.session_state.step_index + 1)
            st.experimental_rerun()
    with button_cols[1]:
        if st.button("k ⬆️", key="btn_k_up"):
            st.session_state.step_index = max(0, st.session_state.step_index - 1)
            st.experimental_rerun()
    with button_cols[2]:
        if st.button("g ✅", key="btn_g_good"):
            update_status(df.iloc[st.session_state.step_index]["step"], "goed✅")
            st.experimental_rerun()
    with button_cols[3]:
        if st.button("f ❌", key="btn_f_fault"):
            update_status(df.iloc[st.session_state.step_index]["step"], "fout❌")
            st.experimental_rerun()
    with button_cols[4]:
        if st.button(": 📝", key="btn_colon_comment"):
            st.session_state.show_comment_input = True
            st.experimental_rerun()
    with button_cols[5]:
        if st.button("Esc 🚫", key="btn_esc_cancel"):
            if st.session_state.show_comment_input:
                st.session_state.show_comment_input = False
                st.experimental_rerun()

with col_slider:
    step_num_new = st.slider("Stap navigatie", 1, len(df), step_num + 1)
    st.session_state.step_index = step_num_new - 1
