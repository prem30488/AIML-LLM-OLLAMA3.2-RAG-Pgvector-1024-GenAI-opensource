import os
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# Modern v0.3 Import Style
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage, AIMessage
from flask import Flask, request, send_file, jsonify, Response
# 1. Initialize LLM and Embeddings (Using Ollama)
llm = OllamaLLM(model="llama3.2", base_url="http://host.docker.internal:11434") # or your preferred model
embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://host.docker.internal:11434")

# 2. Setup Vector Store (Example with dummy data)
# In production, you'd load your PDFs/Docs here
texts = ["LangChain is a framework for building LLM applications.", 
         "FAISS is a library for efficient similarity search."]
vectorstore = FAISS.from_texts(texts, embeddings)
retriever = vectorstore.as_retriever()

# 3. Create contextualize question chain
# This rephrases the user's question to be standalone based on chat history
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

# 4. Create Answer chain
system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum.\n\n"
    "{context}"
)
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

# 5. Create final RAG chain
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# --- EXAMPLE USAGE ---
chat_history = []

def ask_question(query):
    global chat_history
    response = rag_chain.invoke({"input": query, "chat_history": chat_history})
    
    # Update history
    chat_history.extend([
        HumanMessage(content=query),
        AIMessage(content=response["answer"]),
    ])
    
    return response["answer"]
    
app = Flask(__name__)
@app.post("/RAGchat")
def chat():
    question = request.json["question"]
    answer = ask_question(question)
    return jsonify({
        "answer": answer
    })
# ================================
# Server
# ================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8007)
#print(ask_question("What is LangChain?"))
#print(ask_question("And what is the other library you mentioned?")) # Tests context/history