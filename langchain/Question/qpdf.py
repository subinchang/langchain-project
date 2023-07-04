from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
from langchain.document_loaders import PyPDFLoader
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain, ConversationChain
import os
from langchain.chains.question_answering import load_qa_chain


def technically_question(pdf_name):
    loader = PyPDFLoader(pdf_name)
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(data)

    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))
    pinecone.init(
        api_key=os.getenv("PINECONE_API_KEY"),  # find at app.pinecone.io
        environment=os.getenv("PINECONE_API_ENV")  # next to api key in console
    )
    index_name = "cow" # put in the name of your pinecone index here


    index = pinecone.Index('cow') 

    index.delete(delete_all=True)

    docsearch = Pinecone.from_texts([t.page_content for t in texts], embeddings, index_name='cow')

    chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0,top_p=1,frequency_penalty=0.7,
                     presence_penalty = 0.7)

    # llm = OpenAI( openai_api_key=OPENAI_API_KEY)
    chain = load_qa_chain(llm=chat, chain_type="stuff")

    query = "Please make 10 technically difficult questions and detail answer that data analysts are aiming. questions and answer should show in korean" 
    docs = docsearch.similarity_search(query, include_metadata=False,k=5)
    
    
    query = """Please make 10 technically difficult questions and detail answer based on (inputdocumentation)  
    that data analysts are aiming. questions and answer should show in korean. 그리고 문제 앞에 숫자로 번호달아줘"""

    
    x = chain.run(input_documents=docs, question=query)
    return(x)