from flask import Flask, render_template, request, jsonify
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from src.prompt import *
import os


app = Flask(__name__)


#default route
@app.route('/')
def index():
    return render_template('chat.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)