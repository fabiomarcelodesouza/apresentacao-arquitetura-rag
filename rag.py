import json
import openai
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.docstore.document import Document

OPENAI_API_KEY = ""

def populate_vector_db(DB_PATH="./db/"):
    directory_path = '.\\BaseConhecimento'
    documents = [Document(page_content='', metadata={})]

    # Lista todos os arquivos no diretório
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
    
        # Verifica se o arquivo é um PDF
        if filename.lower().endswith('.pdf'):
            # Carregamento e preparação dos documentos (seu código existente)
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
        elif (filename.lower().endswith('.txt') or filename.lower().endswith('.json')):
            # Carregamento e preparação dos documentos (seu código existente)
            loader = TextLoader(file_path)
            documents.extend(loader.load())

    print(documents)
    text_splitter = CharacterTextSplitter(chunk_size=256, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(docs, embeddings)

    return db

def retrieve_documents(question, top_k=3, search_type="similarity"):
    # Use o índice FAISS para encontrar os trechos mais relevantes
    return db.search(question, top_k=top_k, search_type=search_type)

def format_prompt(retrieved_docs, question):
    # Formate os trechos recuperados e a pergunta para o prompt do ChatGPT
    context = "\n".join([doc.page_content for doc in retrieved_docs])

    template = """Utilize os seguintes fragmentos de contexto para responder à pergunta no final. 
                Se você não souber a resposta, apenas diga que não sabe, não tente inventar uma resposta.
                Use poucas frases e mantenha a resposta o mais concisa possível.
    {context}
    Questão: {question}
    Resposta útil:"""
    
    print(f"Template..........: {template}")

    prompt_completo = template.format(context=context, question=question)

    print(f"Prompt Completo...: {template}")

    return prompt_completo

def get_chatgpt_response(prompt, empresa):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)    

    response = client.chat.completions.create(
        model="gpt-4-0125-preview",  # ou outro modelo ChatGPT que você preferir        
        messages=[
            {"role": "system", "content": f"Vocé é um assistente que fornece informações sobre a empresa {empresa}."},
            {"role": "user", "content": prompt},
        ]
    )

    print(f"Prompt..............: {prompt}")
    print(f"Response............: {response.choices[0].message.content}")
    return response.choices[0].message.content

def ask_rag(question, empresa):
    fonte = {}

    # Recupere documentos relevantes
    retrieved_docs = retrieve_documents(question)

    # Formate o prompt com os documentos recuperados e a pergunta
    prompt = format_prompt(retrieved_docs, question)
    # prompt = question

    # Obtenha a resposta do ChatGPT
    answer = get_chatgpt_response(prompt, empresa)
    
    source = []
    
    for doc in retrieved_docs:
        source.append({"source": doc.metadata['source'], "page": doc.metadata.get('page', 0)})

    return answer, source

db = populate_vector_db()