import streamlit as st
import pandas as pd
import json

# # Brede layout
st.set_page_config(layout="wide")
# 
# st.title("📊 Regressietesten Viewer")
# 
# # Bestand uploaden
# uploaded_file = st.file_uploader("Kies een Excel-bestand", type=["xlsx", "xls"])
# 
# if uploaded_file is not None:
#     df = pd.read_excel(uploaded_file)
# 
#     df = pd.read_excel(uploaded_file, header=None)
#     df = df.astype(str)   # <- zet alles naar string
# 


st.title("📊 Regressietesten Viewer")

uploaded_file = st.file_uploader("Kies een Excel-bestand", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Haal de sheetnamen op
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names

    # Selectbox om tabblad te kiezen
    sheet = st.selectbox("Kies een tabblad", sheet_names)

    # Lees het gekozen tabblad in, zet alles naar string
    df = pd.read_excel(uploaded_file, sheet_name=sheet, header=None)
    df = df.astype(str)

    st.success(f"Tabblad **{sheet}** is geladen met {len(df)} rijen en {len(df.columns)} kolommen.")
    st.dataframe(df.head(), use_container_width=True)

#else:
 #   st.info("⬆️ Upload hierboven een Excel-bestand om te beginnen.")



    # Zoekbalk
    query = st.text_input("🔍 Zoek in alle kolommen")
    if query:
        mask = df.apply(lambda row: row.astype(str).str.contains(query, case=False, na=False)).any(axis=1)
        df = df[mask]

    # Dropdown voor aantal rijen per pagina
    rows_per_page = st.selectbox("Aantal rijen per pagina", [3, 5, 10, 20, 50, 100], index=3)

    # Huidige pagina
    if "page" not in st.session_state:
        st.session_state.page = 0

    def next_page():
        if (st.session_state.page + 1) * rows_per_page < len(df):
            st.session_state.page += 1

    def prev_page():
        if st.session_state.page > 0:
            st.session_state.page -= 1

    # Subset tonen
    start = st.session_state.page * rows_per_page
    end = start + rows_per_page
    subset = df.iloc[start:end].copy()

    # Status opties (versimpeld)
    status_options = [
        "Goed ✅",
        "Fout ❌"
    ]

    # Initialiseer opslag
    if "status_data" not in st.session_state:
        st.session_state.status_data = {}

    # Formulier per rij
    st.write(f"Toont rijen {start+1} t/m {min(end, len(df))} van {len(df)}")

    for idx, row in subset.iterrows():
        with st.expander(f"Rij {idx+1} bekijken/bewerken"):
            st.write(row)

            status_key = f"status_{idx}"
            note_key = f"note_{idx}"

            status = st.selectbox("Status", status_options, key=status_key)
            note = st.text_input("Opmerking", key=note_key)

            # Opslaan in session_state
            st.session_state.status_data[idx] = {"Status": status, "Opmerking": note}

    # Navigatie
    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Vorige", on_click=prev_page)
    with col2:
        st.button("Volgende ➡️", on_click=next_page)

    # Exportknoppen
    if st.session_state.status_data:
        df_export = pd.DataFrame.from_dict(st.session_state.status_data, orient="index")

        st.download_button(
            "⬇️ Exporteer resultaten (CSV)",
            df_export.to_csv().encode("utf-8"),
            "resultaten.csv",
            "text/csv"
        )

        st.download_button(
            "⬇️ Exporteer resultaten (JSON)",
            json.dumps(st.session_state.status_data, indent=2, ensure_ascii=False).encode("utf-8"),
            "resultaten.json",
            "application/json"
        )

else:
    st.info("⬆️ Upload hierboven een Excel-bestand om te beginnen.")
