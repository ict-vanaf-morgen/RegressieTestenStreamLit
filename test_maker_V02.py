import streamlit as st
import json
from datetime import datetime
# bash command: py -m streamlit run app.py
st.set_page_config(page_title="JSON Builder", layout="wide")

# --- Kleine topmarge zodat titel niet tegen Streamlit-menu botst ---
st.markdown("""
    <style>
    header {visibility: visible;}
    .block-container {
        padding-top: 1.5rem !important; /* iets meer ruimte bovenaan */
    }
    h3 {
        margin-top: 0.3rem;
        margin-bottom: 0.4rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- Compacte stijl ---
st.markdown("""
    <style>
    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    h1, h2, h3, h4 {
        margin-bottom: 0.2rem;
        margin-top: 0.6rem;
    }
    .section {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.8rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h4 style='margin-top:0rem; color:#444;'>🧱 Regressietest JSON Builder</h4>", unsafe_allow_html=True)


# --- Upload sectie ---
st.markdown("<div class='section'><b>1️⃣ Upload bestaand JSON-bestand (optioneel)</b>", unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Upload JSON-bestand",
    type="json",
    label_visibility="collapsed"
)

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
st.markdown("</div>", unsafe_allow_html=True)

# --- Metadata ---
st.markdown("<div class='section'><b>2️⃣ Metadata</b>", unsafe_allow_html=True)
meta = data["metadata"]

cols = st.columns(2)
with cols[0]:
    meta["Testcase"] = st.text_input("Testcase naam", meta.get("Testcase", ""))
    meta["Datum"] = st.text_input("Datum", meta.get("Datum", datetime.now().strftime("%m/%d/%Y")))
with cols[1]:
    meta["Precondities"] = st.text_area("Precondities", meta.get("Precondities", ""), height=80)

meta["Paginas"] = [p.strip() for p in st.text_input("Paginas (komma-gescheiden)", ", ".join(meta.get("Paginas", []))).split(",") if p.strip()]
meta["Accounts"] = [a.strip() for a in st.text_input("Accounts (komma-gescheiden)", ", ".join(meta.get("Accounts", []))).split(",") if a.strip()]
meta["Omgevingen"] = [o.strip() for o in st.text_input("Omgevingen (komma-gescheiden)", ", ".join(meta.get("Omgevingen", []))).split(",") if o.strip()]
st.markdown("</div>", unsafe_allow_html=True)

# --- Testcases overzicht ---
st.markdown("<div class='section'><b>3️⃣ Bestaande testcases</b>", unsafe_allow_html=True)
if data["testcases"]:
    for tc in data["testcases"]:
        with st.expander(f"{tc['id']} — {tc['title']}"):
            for step in tc["steps"]:
                st.markdown(f"**Stap {step['step']}** — {step['actie']}")
                st.caption(f"➡️ {step['gewenst_resultaat']}")
else:
    st.info("Nog geen testcases toegevoegd.")
st.markdown("</div>", unsafe_allow_html=True)

# --- Nieuwe testcase toevoegen ---
st.markdown("<div class='section'><b>4️⃣ Nieuwe testcase toevoegen</b>", unsafe_allow_html=True)

# Auto-ID generator
if data["testcases"]:
    last_id = data["testcases"][-1]["id"]
    try:
        prefix, num = last_id.split("_")
        base, sub = num.split(".")
        new_id = f"{prefix}_{base}.{int(sub)+1}"
    except Exception:
        new_id = f"TC_{len(data['testcases'])+1}.1"
else:
    new_id = "TC_1.1"

# Sessiestate voor reset
if "form_reset" not in st.session_state:
    st.session_state.form_reset = 0

with st.form("add_testcase", clear_on_submit=True):
    tc_id = st.text_input("Testcase ID", new_id, key=f"id_{st.session_state.form_reset}")
    tc_title = st.text_input("Titel testcase", key=f"title_{st.session_state.form_reset}")
    num_steps = st.number_input("Aantal stappen", min_value=1, max_value=50, value=3, key=f"steps_{st.session_state.form_reset}")
    steps = []

    for i in range(int(num_steps)):
        c1, c2 = st.columns(2)
        with c1:
            actie = st.text_input(f"Actie {i+1}", key=f"actie_{st.session_state.form_reset}_{i}")
        with c2:
            gewenst = st.text_input(f"Gewenst resultaat {i+1}", key=f"gewenst_{st.session_state.form_reset}_{i}")
        steps.append({"step": i+1, "actie": actie, "gewenst_resultaat": gewenst})

    submitted = st.form_submit_button("➕ Toevoegen")

    if submitted and tc_id and tc_title:
        new_tc = {"id": tc_id, "title": tc_title, "steps": steps}
        data["testcases"].append(new_tc)
        st.session_state.form_reset += 1  # reset velden
        st.success(f"✅ Testcase '{tc_id}' toegevoegd!")

st.markdown("</div>", unsafe_allow_html=True)

# --- Export ---
st.markdown("<div class='section'><b>5️⃣ Exporteren als JSON</b>", unsafe_allow_html=True)
json_str = json.dumps(data, indent=2, ensure_ascii=False)
st.download_button(
    label="💾 Download JSON-bestand",
    data=json_str,
    file_name=f"{data['metadata']['Testcase'] or 'regressietest'}.json",
    mime="application/json"
)
with st.expander("📄 Bekijk JSON-voorbeeld"):
    st.json(data)
st.markdown("</div>", unsafe_allow_html=True)
