from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain_together import Together
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain

app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": "*"}}, supports_credentials=True)

# Setup API key
TOGETHER_AI_API_KEY = ''
os.environ['TOGETHER_API_KEY'] = TOGETHER_AI_API_KEY

# Load HuggingFace Embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="nomic-ai/nomic-embed-text-v1",
    model_kwargs={"trust_remote_code": True, "revision": "289f532e14dbbbd5a04753fa58739e9ba766f3c7"}
)

# Load FAISS DB
db = FAISS.load_local("ipc_vector_db", embeddings, allow_dangerous_deserialization=True)
retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})

# Prompt
prompt_template = """
You are a knowledgeable and professional Legal Research Assistant trained in the Indian Penal Code (IPC).

Given the case description and IPC context, identify the most relevant IPC section(s). Your tone should be confident yet approachable.

Your response should:
- Start directly with the applicable IPC section(s) and their titles — no preface like "You might be charged..."
- Provide a brief, human-readable explanation of the offense.
- Mention the punishment clearly.
- Optionally add a note about related sections (e.g., Section 338 if hurt becomes grievous).
- Avoid robotic or speculative phrasing.
- DO NOT use "You:", "It seems", or "Based on your case".

Context:
{context}

Case:
{question}

Chat history (if any):
{chat_history}

Respond only with applicable IPC section(s), an explanation, and punishment. Keep the tone informative and slightly conversational, but professional.
"""




prompt = PromptTemplate.from_template(prompt_template)

# TogetherAI LLM
llm = Together(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    temperature=0.5,
    max_tokens=512
)

# Memory
memory = ConversationBufferWindowMemory(k=2, memory_key="chat_history", return_messages=True)

# Chain
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    combine_docs_chain_kwargs={"prompt": prompt}
)

def is_ipc_related(question):
    keywords = ["ipc", "penal code", "indian penal code", "section", "crime", "offense", "punishment", "law", "repercussion", "legal"]
    return any(k in question.lower() for k in keywords)

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    data = request.json
    user_message = data.get('message', '').strip()

    if is_ipc_related(user_message):
        try:
            result = qa_chain.invoke({"question": user_message})
            return jsonify({'success': True, 'message': result['answer']})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    else:
        return jsonify({
            'success': False,
            'message': "I am designed to answer questions specifically related to the Indian Penal Code (IPC). Please ask an IPC-related question."
        })

@app.route('/reset', methods=['POST'])
def reset_conversation():
    global memory
    memory.clear()
    return jsonify({'success': True, 'message': 'Conversation reset successfully'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
