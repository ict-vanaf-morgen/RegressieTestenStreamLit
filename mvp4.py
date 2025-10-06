import streamlit as st
import pandas as pd
import json

st.set_page_config(layout="wide")

st.title("📊 Meebewegende highlighter demo")

uploaded_file = st.sidebar.file_uploader("Upload testcase JSON", type="json")

with st.sidebar.expander("Sneltoetsen & navigatie"):
    st.markdown("""
    - <kbd>j</kbd>: volgende stap
    - <kbd>k</kbd>: vorige stap
    """)

# Initieer sessiestatus
if "step_index" not in st.session_state:
    st.session_state.step_index = 0

if uploaded_file:
    data = json.load(uploaded_file)
    steps = data.get("testcases", [])[0].get("steps", [])  # Eerste testcase
    df = pd.DataFrame(steps)

    step_num = st.session_state.step_index
    total_steps = len(df)

    st.markdown(f"Huidige stap: {step_num + 1} / {total_steps}")

    # --- Sliding window highlight logic ---
    window_size = 7
    num_rows = len(df)
    if num_rows <= window_size:
        start_idx = 0
        end_idx = num_rows
    else:
        start_idx = max(0, min(step_num - window_size // 2, num_rows - window_size))
        end_idx = start_idx + window_size

    relative_active_idx = step_num - start_idx
    df_window = df.iloc[start_idx:end_idx]

    def highlight_row(rel_idx):
        def hl(x):
            return [
                'background-color: #f0c674; color: #000; font-weight: bold;' if x.name == rel_idx else ''
                for _ in x
            ]
        return hl

    st.dataframe(df_window.style.apply(highlight_row(relative_active_idx), axis=1))

    # Navigatie knoppen
    cols = st.columns([1,1,4])
    with cols[0]:
        if st.button("⬆️ (k)"):
            st.session_state.step_index = max(0, st.session_state.step_index - 1)
    with cols[1]:
        if st.button("⬇️ (j)"):
            st.session_state.step_index = min(total_steps - 1, st.session_state.step_index + 1)
    with cols[2]:
        step_num_new = st.slider("Stap navigatie", 1, total_steps, step_num + 1)
        st.session_state.step_index = step_num_new - 1

else:
    st.info("Upload een JSON testcase (structuur met 'testcases'/ 'steps').")