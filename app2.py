import streamlit as st
import json
import pandas as pd

uploaded_file = st.file_uploader("Upload hier je testcase JSON-bestand", type="json")

if uploaded_file is not None:
    # JSON-bestand inlezen
    try:
        data = json.load(uploaded_file)
        testcase_title = data.get("metadata", {}).get("Testcase", "Onbekende Testcase")
        st.title(f"📊 Regressietesten Viewer - {testcase_title}")

        # Optioneel: toon de ingeladen JSON data mooi geformatteerd
        st.json(data)

        # Hier kan je verder met het verwerken van de testcase data...

    except json.JSONDecodeError:
        st.error("Ongeldig JSON bestand, probeer het opnieuw met een correct JSON bestand.")
else:
    st.info("Wacht op upload van een JSON bestand...")

import streamlit as st
import json

st.title("📊 Regressietesten Viewer")

uploaded_file = st.file_uploader("Upload je testcase JSON-bestand", type="json")

if uploaded_file:
    data = json.load(uploaded_file)
    testcase_title = data.get("metadata", {}).get("Testcase", "Onbekende Testcase")
    st.title(f"📊 Regressietesten Viewer - {testcase_title}")

    # Optioneel, toon de hele JSON
    # st.json(data)

    # Dropdown maken van metadata 'Paginas' als voorbeeld
    paginas_opties = data.get("metadata", {}).get("Paginas", [])
    if paginas_opties:
        geselecteerde_pagina = st.selectbox("Selecteer een pagina", paginas_opties)
        st.write(f"Je hebt gekozen voor: {geselecteerde_pagina}")
    else:
        st.write("Geen paginanaam opties gevonden in metadata.")
else:
    st.info("Wacht op het uploaden van een JSON bestand...")
