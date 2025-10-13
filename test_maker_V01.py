import streamlit as st
import json
from datetime import datetime

st.set_page_config(page_title="Regressietest JSON Builder", layout="wide")
st.title("🧱 Regressietest JSON Builder")

# --- Upload sectie ---
st.header("1️⃣ Upload bestaand JSON-bestand (optioneel)")
uploaded_file = st.file_uploader("Upload je regressietest JSON", type="json")

if uploaded_file:
    data = json.load(uploaded_file)
    st.success("✅ JSON geladen!")
else:
    data = {
        "metadata": {
            "Testcase": "",
            "Datum": datetime.now().strftime("%m/%d/%Y"),
            "Paginas": [],
            "Precondities": "",
            "Accounts": [],
            "Omgevingen": []
        },
        "testcases": []
    }

# --- Metadata bewerken ---
st.header("2️⃣ Metadata")
meta = data["metadata"]

col1, col2 = st.columns(2)
with col1:
    meta["Testcase"] = st.text_input("Testcase naam", meta.get("Testcase", ""))
    meta["Datum"] = st.text_input("Datum", meta.get("Datum", datetime.now().strftime("%m/%d/%Y")))
with col2:
    meta["Precondities"] = st.text_area("Precondities", meta.get("Precondities", ""))

meta["Paginas"] = st.text_area(
    "Paginas (komma-gescheiden)",
    ", ".join(meta.get("Paginas", []))
).split(",") if meta.get("Paginas") else []

meta["Accounts"] = st.text_area(
    "Accounts (komma-gescheiden)",
    ", ".join(meta.get("Accounts", []))
).split(",") if meta.get("Accounts") else []

meta["Omgevingen"] = st.text_area(
    "Omgevingen (komma-gescheiden)",
    ", ".join(meta.get("Omgevingen", []))
).split(",") if meta.get("Omgevingen") else []

# --- Bestaande testcases tonen ---
st.header("3️⃣ Bestaande testcases")
if data["testcases"]:
    for tc in data["testcases"]:
        with st.expander(f"🧩 {tc['id']} — {tc['title']}"):
            for step in tc["steps"]:
                st.markdown(f"**Stap {step['step']}** — {step['actie']}")
                st.caption(f"➡️ Verwacht: {step['gewenst_resultaat']}")
else:
    st.info("Nog geen testcases toegevoegd.")

# --- Nieuwe testcase toevoegen ---
st.header("4️⃣ Nieuwe testcase toevoegen")
with st.form("add_testcase"):
    tc_id = st.text_input("Testcase ID (bijv. TC_5.9)")
    tc_title = st.text_input("Titel testcase")
    num_steps = st.number_input("Aantal stappen", min_value=1, max_value=50, value=3)
    steps = []

    st.markdown("### Stappen")
    for i in range(int(num_steps)):
        col_a, col_b = st.columns(2)
        with col_a:
            actie = st.text_input(f"Actie {i+1}", key=f"actie_{i}")
        with col_b:
            gewenst = st.text_input(f"Gewenst resultaat {i+1}", key=f"gewenst_{i}")
        steps.append({"step": i+1, "actie": actie, "gewenst_resultaat": gewenst})

    submitted = st.form_submit_button("➕ Testcase toevoegen")

    if submitted and tc_id and tc_title:
        new_tc = {"id": tc_id, "title": tc_title, "steps": steps}
        data["testcases"].append(new_tc)
        st.success(f"✅ Testcase '{tc_id}' toegevoegd!")

# --- Exporteren ---
st.header("5️⃣ Exporteren als JSON")
json_str = json.dumps(data, indent=2, ensure_ascii=False)
st.download_button(
    label="💾 Download JSON-bestand",
    data=json_str,
    file_name=f"{data['metadata']['Testcase'] or 'regressietest'}.json",
    mime="application/json"
)

with st.expander("📄 Bekijk JSON-voorbeeld"):
    st.json(data)
