"""
Streamlit UI for the IPC Legal Research Assistant.
Describe a case in plain English and get relevant IPC sections.
"""

import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))

# Auto-inject the subfolder venv site-packages so Streamlit can find langchain_community
venv_site = os.path.join(project_root, "knowledge_engineering", "venv", "Lib", "site-packages")
if os.path.exists(venv_site) and venv_site not in sys.path:
    sys.path.insert(0, venv_site)

# Ensure project root is on the path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
from knowledge_engineering.hybrid_system import HybridIPCSystem

# ── Page config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="IPC Legal Research Assistant",
    page_icon="⚖️",
    layout="wide",
)

# ── Custom CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Apply font selectively to avoid breaking Streamlit's Material icons */
    html, body, .stApp { 
        font-family: 'Outfit', sans-serif; 
    }
    p, span, div, h1, h2, h3, h4, h5, h6, li, a { 
        font-family: inherit; 
    }
    /* Force Material Icons back to their original font */
    .st-emotion-cache-1gfk02a, .material-symbols-rounded, svg {
        font-family: 'Material Symbols Rounded', sans-serif !important;
    }

    .main {
        background-color: #09090b;
        background-image: radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), radial-gradient(at 50% 0%, hsla(225,39%,30%,0.1) 0, transparent 50%), radial-gradient(at 100% 0%, hsla(339,49%,30%,0.1) 0, transparent 50%);
    }

    .hero-title {
        font-size: 3rem; 
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8, #818cf8, #e879f9);
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: -0.02em;
    }
    .hero-sub { color: #a1a1aa; font-size: 1.15rem; margin-bottom: 2rem; font-weight: 300; }

    .section-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .section-card:hover {
        transform: translateY(-4px);
        background: rgba(30, 41, 59, 0.6);
        box-shadow: 0 12px 32px rgba(56, 189, 248, 0.15);
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    .section-id {
        font-size: 1.4rem; font-weight: 700; 
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .section-desc {
        font-size: 1rem; color: #f8fafc; margin-top: 0.25rem; font-weight: 400;
    }
    .score-badge {
        display: inline-block; 
        background: rgba(129, 140, 248, 0.15); 
        color: #a5b4fc;
        border: 1px solid rgba(129, 140, 248, 0.3); 
        border-radius: 20px;
        padding: 4px 14px; 
        font-size: 0.8rem; 
        font-weight: 600;
        margin-top: 0.6rem;
    }
    .cond-chip {
        display: inline-block; 
        background: rgba(56, 189, 248, 0.1); 
        color: #7dd3fc;
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 8px; 
        padding: 3px 10px; 
        margin: 4px 6px 4px 0;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .missing-chip {
        display: inline-block; 
        background: rgba(248, 113, 113, 0.1); 
        color: #fca5a5;
        border: 1px solid rgba(248, 113, 113, 0.2);
        border-radius: 8px; 
        padding: 3px 10px; 
        margin: 4px 6px 4px 0;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .fact-tag {
        display: inline-block; 
        background: rgba(52, 211, 153, 0.15); 
        color: #6ee7b7;
        border: 1px solid rgba(52, 211, 153, 0.3);
        border-radius: 8px; 
        padding: 4px 12px; 
        margin: 4px 6px;
        font-size: 0.85rem; 
        font-weight: 600;
    }
    .warning-box {
        background: rgba(251, 191, 36, 0.1); 
        border: 1px solid rgba(251, 191, 36, 0.3);
        border-radius: 12px; 
        padding: 1rem 1.2rem;
        color: #fcd34d; 
        font-size: 0.95rem; 
        margin-top: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .supporting-text {
        background: rgba(15, 23, 42, 0.4); 
        border-left: 3px solid #818cf8;
        padding: 1rem 1.2rem; 
        border-radius: 0 12px 12px 0;
        color: #cbd5e1; 
        font-size: 0.9rem; 
        margin-top: 0.8rem;
        line-height: 1.5;
    }
    div[data-testid="stTextArea"] textarea {
        background: rgba(30, 41, 59, 0.5) !important; 
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        border-radius: 12px !important;
        font-size: 1.05rem !important;
        transition: all 0.2s;
    }
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2) !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #38bdf8, #818cf8, #e879f9) !important;
        color: white !important; 
        border: none !important;
        border-radius: 12px !important; 
        padding: 0.7rem 2.5rem !important;
        font-weight: 700 !important; 
        font-size: 1.05rem !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .stButton > button:hover {
        transform: scale(1.02) translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(129, 140, 248, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Load system (cached) ─────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading IPC Knowledge Base (158 rules)…")
def load_system():
    return HybridIPCSystem()

system = load_system()

@st.cache_resource(show_spinner="Loading RAG Vector Database…")
def load_rag_retriever():
    """Load FAISS retriever only (lightweight, no LLM dependency)."""
    try:
        from langchain_community.vectorstores import FAISS
        from langchain_huggingface import HuggingFaceEmbeddings

        embeddings = HuggingFaceEmbeddings(
            model_name="nomic-ai/nomic-embed-text-v1",
            model_kwargs={"trust_remote_code": True, "revision": "289f532e14dbbbd5a04753fa58739e9ba766f3c7"}
        )
        db_path = os.path.join(project_root, "ipc_vector_db")
        db = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
        return db, None
    except Exception as e:
        return None, str(e)

def get_groq_model(client):
    preferred = os.environ.get("GROQ_MODEL")
    if preferred:
        return preferred
    candidates = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-120b",
        "groq/compound"
    ]
    try:
        available = {m.id for m in client.models.list().data}
        for c in candidates:
            if c in available:
                return c
        chat_models = [m for m in available if "whisper" not in m and "guard" not in m]
        if chat_models:
            return chat_models[0]
    except Exception:
        pass
    return "llama-3.3-70b-versatile"


def get_rag_response(db, question: str, chat_history: list, user_id: str = "streamlit_user") -> str:
    """Use Groq SDK for fast conversational legal analysis with daily rate limiting."""
    from dotenv import load_dotenv
    load_dotenv(override=True)

    from rate_limiter import check_and_increment_rate_limit, DAILY_LIMIT, CONTACT_EMAIL

    # Enforce 5 queries/day rate limit
    is_allowed, remaining, limit = check_and_increment_rate_limit(user_id)
    if not is_allowed:
        return (
            f"⚠️ **Daily Quota Reached**: You have reached the limit of {limit} free AI legal queries for today.\n\n"
            f"If you need extended access or custom legal analysis, please contact us at "
            f"[{CONTACT_EMAIL}](mailto:{CONTACT_EMAIL}?subject=Legal%20Advisor%20Quota%20Inquiry)."
        )

    groq_api_key = os.environ.get("GROQ_API_KEY")

    if not groq_api_key:
        return "⚠️ No Groq API Key found. Please add `GROQ_API_KEY=your_key` to your `.env` file."

    # Retrieve relevant IPC context from FAISS
    docs = db.similarity_search(question, k=4)
    context = "\n\n".join([doc.page_content for doc in docs])

    # Build conversation history (last 4 messages)
    history_text = ""
    for msg in chat_history[-4:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"

    prompt = f"""You are a knowledgeable Legal Research Assistant trained in the Indian Penal Code (IPC).
Given the case description and IPC context, identify the most relevant IPC section(s).
Your response should:
- Start directly with the applicable IPC section(s) and their titles.
- Provide a brief, human-readable explanation of the offense and punishment.
- Avoid robotic phrasing. DO NOT use "You:" or "Based on your case".

Relevant IPC Context:
{context}

{f"Previous conversation:{chr(10)}{history_text}" if history_text else ""}

User Question: {question}"""

    try:
        import groq
        client = groq.Groq(api_key=groq_api_key)
        model = get_groq_model(client)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Groq API Error: {str(e)}"


# ── Header ───────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">⚖️ IPC Legal Research Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Analyze any incident using rule-based reasoning or directly ask our conversational AI assistant.</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🏛️ Expert System", "💬 Conversational AI"])

with tab1:
    # ── Example cases ────────────────────────────────────────────────────
    EXAMPLES = [
        "A drunk driver was speeding and hit a pedestrian who later died in the hospital.",
        "Someone forged my signature on a property document and sold my land.",
        "My husband and his family have been demanding dowry and torturing me since our marriage.",
        "A group of people broke into my house at night and stole my jewelry at knifepoint.",
        "A man threw acid on a woman after she rejected his proposal.",
    ]

    with st.expander("💡 Try an example case", expanded=False):
        cols = st.columns(len(EXAMPLES))
        for i, ex in enumerate(EXAMPLES):
            if cols[i].button(f"Example {i+1}", key=f"ex_{i}", use_container_width=True):
                st.session_state["case_input"] = ex

    # ── Input ────────────────────────────────────────────────────────────
    case_text = st.text_area(
        "Describe the incident / case",
        value=st.session_state.get("case_input", ""),
        height=120,
        placeholder="e.g. Someone stole my laptop from my office without my permission…",
    )

    analyze_btn = st.button("🔍 Analyze Case", use_container_width=False)

    # ── Analysis ─────────────────────────────────────────────────────────
    if analyze_btn and case_text.strip():
        with st.spinner("Analyzing case against 158 IPC rules…"):
            results = system.analyze_case(case_text.strip())

        # ── Extracted Facts ──────────────────────────────────────────────
        facts = results["extracted_facts"]
        true_facts = [k for k, v in facts.items() if v is True]

        st.markdown("---")
        st.subheader("🧠 Extracted Facts")
        if true_facts:
            tags = "".join(f'<span class="fact-tag">{f}</span>' for f in true_facts)
            st.markdown(tags, unsafe_allow_html=True)
        else:
            st.info("No legal facts could be extracted from the description. Try rephrasing with more detail.")

        # ── Matched Sections ─────────────────────────────────────────────
        matched = results["matched_sections"]
        partial = results["partial_matches"]
        explanations = results["explanations"]
        supporting = results.get("supporting_text", {})
        warnings = results.get("warnings", [])

        st.markdown("---")
        st.subheader(f"✅ Matched IPC Sections ({len(matched)})")

        if matched:
            for s in matched:
                conds = "".join(f'<span class="cond-chip">{c}</span>' for c in s["matched_conditions"])
                sup_html = ""
                if s["section_id"] in supporting:
                    texts = supporting[s["section_id"]]
                    if texts:
                        sup_html = f'<div class="supporting-text">📖 {texts[0][:300]}{"…" if len(texts[0]) > 300 else ""}</div>'

                st.markdown(f"""
                <div class="section-card">
                    <div class="section-id">Section {s["section_id"]}</div>
                    <div class="section-desc">{s["description"]}</div>
                    <span class="score-badge">Specificity: {s["specificity_score"]}</span>
                    <div style="margin-top:0.5rem">{conds}</div>
                    {sup_html}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No IPC sections fully matched the described case. Check partial matches below.")

        # ── Partial Matches ──────────────────────────────────────────────
        if partial:
            with st.expander(f"🔶 Partial Matches ({len(partial)})", expanded=False):
                for s in partial[:15]:
                    matched_chips = "".join(f'<span class="cond-chip">{c}</span>' for c in s["matched_conditions"])
                    missing_chips = "".join(f'<span class="missing-chip">✗ {c}</span>' for c in s["unmatched_conditions"])
                    st.markdown(f"""
                    <div class="section-card">
                        <div class="section-id">Section {s["section_id"]}</div>
                        <div class="section-desc">{s["description"]}</div>
                        <div style="margin-top:0.4rem"><b style="color:#93c5fd;font-size:0.8rem">Matched:</b> {matched_chips}</div>
                        <div style="margin-top:0.3rem"><b style="color:#fca5a5;font-size:0.8rem">Missing:</b> {missing_chips}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # ── Explanations ─────────────────────────────────────────────────
        if explanations:
            matched_explanations = [e for e in explanations if not e["missing_facts"]]
            if matched_explanations:
                with st.expander("📝 Detailed Reasoning Trace", expanded=False):
                    for e in matched_explanations:
                        st.markdown(f"**Section {e['section_id']}** — {e['description']}  \nSpecificity: `{e['specificity_score']}`")
                        for f in e["matched_facts"]:
                            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;✓ `{f['unit']}` {f['operator']} `{f['expected']}` → actual: `{f['actual']}`")
                        st.markdown("---")

        # ── Warnings ─────────────────────────────────────────────────────
        for w in warnings:
            st.markdown(f'<div class="warning-box">⚠️ {w}</div>', unsafe_allow_html=True)

    elif analyze_btn:
        st.error("Please enter a case description before analyzing.")

with tab2:
    db, err = load_rag_retriever()
    
    if err:
        st.error(f"Failed to load RAG Vector Database. Ensure packages are installed.\nError: `{err}`")
    else:
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        chat_container = st.container(height=500)
        
        # Display chat messages from history
        with chat_container:
            if len(st.session_state.messages) == 0:
                st.info("Ask me a direct question about IPC laws or describe an incident to chat about it.")
                
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Accept user input
        if prompt := st.chat_input("Ask: What is the punishment for robbery?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing IPC knowledge…"):
                        try:
                            response = get_rag_response(db, prompt, st.session_state.messages)
                        except Exception as e:
                            response = f"⚠️ An error occurred: {str(e)}"
                            
                        st.markdown(response)
                
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

# ── Contact Clause Footer ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; padding: 1.5rem 0; color: #a1a1aa; font-size: 0.95rem;">
        <p style="margin-bottom: 0.8rem;">
            ⚖️ <strong>IPC Legal Research Assistant</strong> • Daily LLM Limit: 5 queries per user.<br/>
            Need higher query limits, dedicated API integration, or have legal questions?
        </p>
        <a href="mailto:ashishsingh67788@gmail.com?subject=Legal%20Advisor%20Inquiry%20-%20Extended%20Quota" 
           style="background: linear-gradient(135deg, #4f46e5, #7c3aed); color: white; padding: 0.6rem 1.4rem; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-flex; align-items: center; gap: 0.5rem; box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3);">
            ✉️ Contact: ashishsingh67788@gmail.com
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
