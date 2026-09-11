import sys
import os

# Auto-inject the subfolder venv site-packages so Python can find langchain_community
project_root = os.path.dirname(os.path.abspath(__file__))
venv_site = os.path.join(project_root, "knowledge_engineering", "venv", "Lib", "site-packages")
if os.path.exists(venv_site) and venv_site not in sys.path:
    sys.path.insert(0, venv_site)

# Make knowledge_engineering available for import
ke_path = os.path.join(project_root, "knowledge_engineering")
if ke_path not in sys.path:
    sys.path.append(ke_path)

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Import the new hybrid system
from hybrid_system import HybridIPCSystem

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

load_dotenv()

# Initialize the Rule-Based + RAG Hybrid System
print("Initializing Hybrid IPC Legal Analysis System for API...")
# Change directory to knowledge_engineering temporarily so it can find its JSON files
original_cwd = os.getcwd()
os.chdir(ke_path)
try:
    system = HybridIPCSystem()
finally:
    os.chdir(original_cwd)

# Load RAG DB explicitly for direct chat (so we don't reload it heavily on every request)
def load_rag_retriever():
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

rag_db, rag_err = load_rag_retriever()
if rag_err:
    print(f"Warning: Failed to load FAISS db explicitly: {rag_err}")

def is_ipc_related(question):
    keywords = ["ipc", "penal code", "indian penal code", "section", "crime", "offense", "punishment", "law", "repercussion", "legal"]
    return any(k in question.lower() for k in keywords)

@app.route('/analyze_rule_based', methods=['POST', 'OPTIONS'])
def analyze_rule_based():
    """Handles deterministic Rule-Based Analysis."""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    data = request.json
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'success': False, 'message': 'No input provided.'})

    try:
        results = system.analyze_case(user_message)
        # Results contains: matched_sections, partial_matches, explanations, etc.
        return jsonify({
            'success': True,
            'matched_sections': results.get('matched_sections', []),
            'partial_matches': results.get('partial_matches', []),
            'explanations': results.get('explanations', []),
            'warnings': results.get('warnings', [])
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


from rate_limiter import (
    check_and_increment_rate_limit,
    get_user_quota,
    DAILY_LIMIT,
    CONTACT_EMAIL
)


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


@app.route('/user_quota', methods=['POST', 'GET', 'OPTIONS'])
def user_quota_endpoint():
    """Returns the remaining daily quota for a logged in user."""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    user_id = request.args.get('user_id')
    if not user_id and request.is_json:
        user_id = request.json.get('user_id')

    if not user_id:
        return jsonify({
            'success': False,
            'message': 'No user identifier provided.',
            'remaining': 0,
            'daily_limit': DAILY_LIMIT,
            'contact_email': CONTACT_EMAIL
        }), 400

    remaining, limit = get_user_quota(user_id)
    return jsonify({
        'success': True,
        'user_id': user_id,
        'remaining': remaining,
        'daily_limit': limit,
        'contact_email': CONTACT_EMAIL
    })


@app.route('/analyze_rag', methods=['POST', 'OPTIONS'])
def analyze_rag():
    """Handles conversational AI RAG queries directly via Groq LLM with rate limiting."""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    data = request.json or {}
    question = data.get('message', '').strip()
    chat_history = data.get('history', [])
    user_id = data.get('user_id') or request.headers.get('X-User-Id')

    if not question:
        return jsonify({'success': False, 'message': 'No input provided.'})

    # 1. Require user to be logged in
    if not user_id:
        return jsonify({
            'success': False,
            'message': "🔒 Login Required: Only logged-in users are permitted to query the AI LLM assistant. Please sign in to continue.",
            'requires_login': True,
            'contact_email': CONTACT_EMAIL
        }), 401

    # 2. Check and enforce 5 queries/day rate limit
    is_allowed, remaining, limit = check_and_increment_rate_limit(user_id)
    if not is_allowed:
        return jsonify({
            'success': False,
            'message': f"⚠️ Daily Limit Reached: You have used your {limit} free AI legal queries for today. Please try again tomorrow, or contact {CONTACT_EMAIL} for extended quota.",
            'rate_limited': True,
            'remaining': 0,
            'daily_limit': limit,
            'contact_email': CONTACT_EMAIL
        }), 429

    # Reload environment to pick up any key updates in .env dynamically
    load_dotenv(override=True)
    groq_api_key = os.environ.get("GROQ_API_KEY")

    if not groq_api_key:
        return jsonify({
            'success': False,
            'message': "⚠️ No Groq API Key found. Please add `GROQ_API_KEY=your_key` to your `.env` file.",
            'contact_email': CONTACT_EMAIL
        })
    
    if not rag_db:
        return jsonify({'success': False, 'message': "⚠️ Vector database unavailable, cannot perform RAG."})

    try:
        docs = rag_db.similarity_search(question, k=4)
        context = "\n\n".join([doc.page_content for doc in docs])

        history_text = ""
        for msg in chat_history[-4:]:
            role = "User" if msg.get("role") == "user" else "Assistant"
            history_text += f"{role}: {msg.get('content', '')}\n"

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

        import groq
        client = groq.Groq(api_key=groq_api_key)
        model = get_groq_model(client)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        answer = response.choices[0].message.content

        return jsonify({
            'success': True,
            'message': answer,
            'model': model,
            'remaining': remaining,
            'daily_limit': limit,
            'contact_email': CONTACT_EMAIL
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'contact_email': CONTACT_EMAIL})


# Keep old /chat endpoint to not break existing frontend temporarily while refactoring is happening
@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    return analyze_rag()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Legal Research Assistant API',
        'model_provider': 'Groq',
        'rate_limit_daily': DAILY_LIMIT,
        'contact_email': CONTACT_EMAIL,
        'rag_db_loaded': rag_db is not None
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
