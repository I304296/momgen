from flask import Flask
import os
from flask import request
from flask import Response
import json

from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from gen_ai_hub.proxy.langchain.openai import OpenAIEmbeddings
from langchain_community.vectorstores.hanavector import HanaDB
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import S3FileLoader
from langchain_community.document_loaders import S3DirectoryLoader
from hdbcli import dbapi

app = Flask(__name__)
# Port number is required to fetch from env variable
# http://docs.cloudfoundry.org/devguide/deploy-apps/environment-variable.html#PORT

cf_port = os.getenv("PORT")

basedir = os.path.abspath(os.path.dirname(__file__))
cred_file = os.path.join(basedir, 'static/credentials.env')

CRED = []
with open(cred_file, "r") as file:
    for line in file.readlines():
        print(line.rstrip())
        key, value = line.replace('export ', '', 1).strip().split('=', 1)
        print(key+"\n"+value)
        os.environ[key] = value
    print(os.getenv("AICORE_LLM_CLIENT_ID"))


# Method to load data to HANA VE
@app.route('/load')
def load():
    folderName = request.args.get('f')
    #setEnv()
    loadData(folderName)
    returnObj = {"message":"OK"}
    return Response(json.dumps(returnObj), mimetype='application/json')

# Method to query via RAG
@app.route('/query')
def query():
    question = request.args.get('q')
    print(question)
    #setEnv()
    returnObj = {
        "question": question,
        "answer":callRAG(question)
        }
    return Response(json.dumps(returnObj), mimetype='application/json')

# Method to query via RAG
@app.route('/prompt', methods = ['POST'])
def prompt():
    question = request.json['question']
    print(question)
    #setEnv()
    returnObj = {
        "question": question,
        "answer":callRAG(question)
        }
    return Response(json.dumps(returnObj), mimetype='application/json')
        
def callRAG(question):
    print("Setting AI Proxy Client...")	
    proxy_client = get_proxy_client("gen-ai-hub")
    #proxy_client = get_proxy_client("aicore")
    print("Setting LLM Proxy...")	
    llm = ChatOpenAI(proxy_model_name="gpt-35-turbo", proxy_client=proxy_client)
    print("Getting Embeding...")	
    embeddings = OpenAIEmbeddings(proxy_model_name="text-embedding-ada-002", proxy_client=proxy_client)
    memory = ConversationBufferMemory(memory_key="chat_history", output_key="answer", return_messages=True)
    conn = dbapi.connect(
        address=os.environ.get("HANA_DB_ADDRESS"),
        port=os.environ.get("HANA_DB_PORT"),
        user=os.environ.get("HANA_DB_USER"),
        password=os.environ.get("HANA_DB_PASSWORD"),
        encrypt=True,
        sslValidateCertificate=False,
    )
    print("Connecting HANA VE...")
    db = HanaDB(embedding=embeddings, connection=conn, table_name="RAG_DOCS")
    print("Obtaining Retriever...")
    retriever = db.as_retriever(search_kwargs={"k": 2})
    prompt_template = """ 
    You are a helpful assistant. You are provided multiple context items that are related to the prompt you have to answer.
    Use the following pieces of context to answer the question at the end. If the answer is not in the context, reply exactly with "I don't know".

    ```
    {context}
    ```

    Question: {question}
    """
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain_type_kwargs = {"prompt": PROMPT}
    qa_chain = ConversationalRetrievalChain.from_llm(llm,retriever,return_source_documents=True,memory=memory,verbose=False,combine_docs_chain_kwargs=chain_type_kwargs,)
    print("Conversational retrieval chain created")
    answer = qa_chain.invoke({"question": question})
    print(answer)
    return answer["answer"]	

#Not in use - credential file is used to maintain this info
def setEnv():
    print("Setting Environment...")
    os.environ["AWS_ACCESS_KEY_ID"] = "AKIATDGJ6OMFJCBLCNUS"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "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"
    os.environ["AICORE_LLM_AUTH_URL"] = "https://btpllm-i304296.authentication.sap.hana.ondemand.com"
    os.environ["AICORE_LLM_CLIENT_ID"] = "sb-195169df-4b34-4fcc-b24b-3a6b01bc20c3!b119297|xsuaa_std!b77089"
    os.environ["AICORE_LLM_CLIENT_SECRET"] = "f786b365-3685-4faa-94b4-9a5d08685c01$tFZGs-THeyz23lf6rIYrElJCroh5ERy__UHDMlcu_6o="
    os.environ["AICORE_LLM_API_BASE"] = "https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com"
    os.environ["AICORE_LLM_RESOURCE_GROUP"] = "default"
    os.environ["HANA_DB_ADDRESS"] = "916aa478-2d88-4d34-85d2-8578be678367.hna0.canary-eu10.hanacloud.ondemand.com"
    os.environ["HANA_DB_PORT"] = "443"
    os.environ["HANA_DB_USER"] = "DBADMIN"
    os.environ["HANA_DB_PASSWORD"] = "HCP@sap1"
    print("Environment Set!")
    
def loadData(folderName):
    #loader = S3FileLoader("hcp-b4d8c785-4fc5-4ee7-bb59-a01917f0488f", fileName)
    loader = S3DirectoryLoader("hcp-b4d8c785-4fc5-4ee7-bb59-a01917f0488f",prefix=folderName)
    document = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30)
    texts = text_splitter.split_documents(document)
    
    proxy_client = get_proxy_client("gen-ai-hub")
    embeddings = OpenAIEmbeddings(proxy_model_name="text-embedding-ada-002", proxy_client=proxy_client)
    
    memory = ConversationBufferMemory(memory_key="chat_history", output_key="answer", return_messages=True)
    conn = dbapi.connect(
        address=os.environ.get("HANA_DB_ADDRESS"),
        port=os.environ.get("HANA_DB_PORT"),
        user=os.environ.get("HANA_DB_USER"),
        password=os.environ.get("HANA_DB_PASSWORD"),
        encrypt=True,
        sslValidateCertificate=False,
    )
    db = HanaDB(embedding=embeddings, connection=conn, table_name="RAG_DOCS")
    db.delete(filter={})
    db.add_documents(texts)

if __name__ == '__main__':
    if cf_port is None:
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        app.run(host='0.0.0.0', port=int(cf_port), debug=True)
