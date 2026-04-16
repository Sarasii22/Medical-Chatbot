from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os

from src.helper import download_hugging_face_embeddings
from src.prompt import system_prompt

from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore

from langchain_ollama import ChatOllama
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# -----------------------
# INIT APP
# -----------------------
app = Flask(__name__)
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# -----------------------
# EMBEDDINGS
# -----------------------
embeddings = download_hugging_face_embeddings()

# -----------------------
# PINECONE SETUP
# -----------------------
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "medical-chatbot"

index = pc.Index(index_name)

vectorstore = PineconeVectorStore(
    index=index,
    embedding=embeddings
)

retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 3,
        "fetch_k": 8,
        "lambda_mult": 0.7
    }
)

# -----------------------
# LLM
# -----------------------
llm = ChatOllama(
    model="llama3",
    temperature=0.3
)

# -----------------------
# PROMPT
# -----------------------
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])

# -----------------------
# RAG CHAIN
# -----------------------
document_chain = create_stuff_documents_chain(llm, prompt)

rag_chain = create_retrieval_chain(
    retriever,
    document_chain
)

# -----------------------
# ROUTES
# -----------------------
@app.route("/")
def home():
    return render_template("chat.html")


@app.route("/get", methods=["POST"])
def chat():
    try:
        # safer input handling
        msg = request.form.get("msg", "").strip()

        if not msg:
            return jsonify({"answer": "Please enter a question."})

        print("User:", msg)

        response = rag_chain.invoke({"input": msg})

        # safer extraction (VERY IMPORTANT)
        answer = response.get("answer")

        if not answer:
            answer = "I don't have enough information in the provided documents."

        print("Bot:", answer)

        return jsonify({"answer": answer})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "answer": "Something went wrong. Please try again later."
        })


# -----------------------
# RUN
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)