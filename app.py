import streamlit as st
import requests
import httpx
import json
import os
import subprocess
import shutil

API_URL = "http://localhost:8000"

st.set_page_config(page_title="UroAssist", page_icon="🩺", layout="wide")

# Custom CSS for clinical aesthetic
st.markdown("""
<style>
    body {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background-color: #ffffff;
    }
    .css-1d391kg {
        background-color: #f0f4f8;
    }
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def fetch_documents(collection):
    try:
        response = requests.get(f"{API_URL}/documents", params={"collection": collection})
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []

# Sidebar
st.sidebar.title("🩺 UroAssist")
st.sidebar.subheader("AI for Urology Practice")
st.sidebar.markdown("---")

st.sidebar.markdown("### 📋 Clinical Guidelines")
clinical_file = st.sidebar.file_uploader("Upload Guideline PDF", type=["pdf"], key="clin_up")
if clinical_file:
    with st.spinner("Uploading..."):
        try:
            files = {"file": (clinical_file.name, clinical_file.getvalue(), "application/pdf")}
            data = {"collection": "clinical"}
            res = requests.post(f"{API_URL}/upload", files=files, data=data)
            if res.status_code == 200:
                st.sidebar.success(f"Uploaded {clinical_file.name}")
            else:
                st.sidebar.error("Upload failed")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

clin_docs = fetch_documents("clinical")
for doc in clin_docs:
    st.sidebar.caption(f"📄 {doc['doc_name']} ({doc['num_chunks']} chunks)")

st.sidebar.markdown("---")

st.sidebar.markdown("### 💵 Coding References")
coding_file = st.sidebar.file_uploader("Upload Coding PDF", type=["pdf"], key="code_up")
if coding_file:
    with st.spinner("Uploading..."):
        try:
            files = {"file": (coding_file.name, coding_file.getvalue(), "application/pdf")}
            data = {"collection": "coding"}
            res = requests.post(f"{API_URL}/upload", files=files, data=data)
            if res.status_code == 200:
                st.sidebar.success(f"Uploaded {coding_file.name}")
            else:
                st.sidebar.error("Upload failed")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

code_docs = fetch_documents("coding")
for doc in code_docs:
    st.sidebar.caption(f"📄 {doc['doc_name']} ({doc['num_chunks']} chunks)")

st.sidebar.markdown("---")

if not clin_docs and not code_docs:
    if st.sidebar.button("🌱 Seed Demo Data"):
        with st.spinner("Seeding data..."):
            try:
                env = os.environ.copy()
                env["PYTHONPATH"] = "."
                subprocess.run(["python3", "scripts/seed_demo.py"], env=env, check=True)
                st.sidebar.success("Demo data seeded!")
                st.rerun()
            except subprocess.CalledProcessError as e:
                st.sidebar.error(f"Failed to seed data: {e}")

if st.sidebar.button("🗑️ Reset Database"):
    with st.spinner("Resetting..."):
        if os.path.exists("chroma_db"):
            shutil.rmtree("chroma_db")
        if os.path.exists("data"):
            shutil.rmtree("data")
        st.rerun()

# Main Content
tab1, tab2, tab3 = st.tabs(["🩺 Nurse Triage", "👤 Patient Intake", "💵 Billing & Coding"])

async def stream_chat(mode, question, placeholder, sources_placeholder):
    full_response = ""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", f"{API_URL}/chat", json={"mode": mode, "question": question}) as response:
                if response.status_code != 200:
                    placeholder.error(f"Error: {response.status_code}")
                    return None, None
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[len("data: "):]
                        try:
                            data = json.loads(data_str)
                            if "text" in data:
                                full_response += data["text"]
                                placeholder.markdown(full_response + "▌")
                            elif "error" in data:
                                placeholder.error(data["error"])
                                return full_response, None
                        except Exception:
                            # It could be the sources event
                            pass
                    elif line.startswith("event: sources"):
                        # next line should be data
                        pass
                
                # Check for sources in the lines?
                # Actually, our API sends event: sources then data: [...]
                # We can do a simpler way: just append to full_response then find sources.
                # Let's fix this slightly.
    except Exception as e:
        placeholder.error(f"Stream error: {e}")
        return full_response, None
    return full_response, None

def do_chat_sync(mode, question, placeholder, sources_placeholder):
    full_response = ""
    sources = []
    try:
        with requests.post(f"{API_URL}/chat", json={"mode": mode, "question": question}, stream=True, timeout=60) as r:
            if r.status_code != 200:
                placeholder.error(f"Error: {r.status_code}")
                return "", []
            
            is_sources_event = False
            for line in r.iter_lines():
                if line:
                    decoded = line.decode("utf-8")
                    if decoded.startswith("event: sources"):
                        is_sources_event = True
                        continue
                    if decoded.startswith("event: error"):
                        continue
                    if decoded.startswith("data: "):
                        data_str = decoded[len("data: "):]
                        try:
                            data = json.loads(data_str)
                            if is_sources_event:
                                sources = data
                            elif "text" in data:
                                full_response += data["text"]
                                placeholder.markdown(full_response + "▌")
                            elif "error" in data:
                                placeholder.error(data["error"])
                        except Exception:
                            pass
                        
            placeholder.markdown(full_response)
    except Exception as e:
        placeholder.error(f"Request failed: {e}")
    return full_response, sources

with tab1:
    st.header("Nurse Triage")
    st.caption("Ask questions based on clinical guidelines. Red flags are automatically surfaced.")
    
    if "triage_messages" not in st.session_state:
        st.session_state.triage_messages = []
        
    for msg in st.session_state.triage_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("Sources"):
                    for i, src in enumerate(msg["sources"], 1):
                        st.write(f"[{i}] {src['doc_name']} — page {src['page']}")
                        
    prompt = st.chat_input("Ask about a clinical scenario...?", key="triage")
    if prompt:
        st.session_state.triage_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            placeholder = st.empty()
            sources_placeholder = st.empty()
            response_text, sources = do_chat_sync("triage", prompt, placeholder, sources_placeholder)
            if sources:
                with sources_placeholder.expander("Sources"):
                    for i, src in enumerate(sources, 1):
                        st.write(f"[{i}] {src['doc_name']} — page {src['page']}")
                        
        st.session_state.triage_messages.append({"role": "assistant", "content": response_text, "sources": sources})

with tab2:
    st.markdown("<h2 style='font-size: 2.5rem;'>Patient Intake</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.2rem;'>Ask plain-English questions before your visit. 💬</p>", unsafe_allow_html=True)
    
    if "intake_messages" not in st.session_state:
        st.session_state.intake_messages = []
        
    for msg in st.session_state.intake_messages:
        with st.chat_message(msg["role"]):
            st.markdown(f"<p style='font-size: 1.1rem;'>{msg['content']}</p>", unsafe_allow_html=True)
            
    prompt = st.chat_input("Describe your symptoms or ask a question...?", key="intake")
    if prompt:
        st.session_state.intake_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f"<p style='font-size: 1.1rem;'>{prompt}</p>", unsafe_allow_html=True)
            
        with st.chat_message("assistant"):
            placeholder = st.empty()
            response_text, sources = do_chat_sync("intake", prompt, placeholder, st.empty())
            # For intake, we update the placeholder with larger text after generation
            placeholder.markdown(f"<p style='font-size: 1.1rem;'>{response_text}</p>", unsafe_allow_html=True)
            
        st.session_state.intake_messages.append({"role": "assistant", "content": response_text})

with tab3:
    st.header("Billing & Coding Helper")
    st.caption("Paste a clinical note to get ICD-10 and CPT suggestions.")
    
    note = st.text_area("Clinical Note", height=200, placeholder="Paste a clinical note...")
    
    if st.button("Suggest Codes"):
        if not note.strip():
            st.warning("Please enter a clinical note.")
        else:
            with st.spinner("Analyzing..."):
                try:
                    res = requests.post(f"{API_URL}/code", json={"clinical_note": note})
                    if res.status_code == 200:
                        data = res.json()
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("ICD-10")
                            if data.get("icd10"):
                                st.dataframe(data["icd10"], use_container_width=True)
                            else:
                                st.info("No ICD-10 codes found.")
                                
                        with col2:
                            st.subheader("CPT")
                            if data.get("cpt"):
                                st.dataframe(data["cpt"], use_container_width=True)
                            else:
                                st.info("No CPT codes found.")
                                
                        st.markdown("### Rationale")
                        st.write(data.get("rationale", ""))
                        
                        if data.get("sources"):
                            with st.expander("Sources"):
                                for i, src in enumerate(data["sources"], 1):
                                    st.write(f"[{i}] {src['doc_name']} — page {src['page']}")
                    else:
                        st.error(f"Error suggesting codes: {res.text}")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {e}")
