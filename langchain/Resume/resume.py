from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from langchain import OpenAI, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain, ConversationChain
from langchain.memory import ConversationBufferWindowMemory


from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


import os
import glob

os.environ["OPENAI_API_KEY"] = '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'
PINECONE_API_KEY = '1a40031c-9c10-46ad-b429-2cd09d2102c3'
PINECONE_API_ENV = 'us-west1-gcp-free'

def saram_link_to_pdf(links:str,driver):
    link = links

    driver.get(link)
    driver.implicitly_wait(10)
    driver.find_elements(By.CLASS_NAME,'spr_jview.btn_jview.btn_print')[0].click() # 인쇄 버튼 넣기.
    time.sleep(14)
    
    # close_two_window(driver)
    driver.switch_to.window(driver.window_handles[-1])
    driver.close()
    
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])
    
    
    driver.find_elements(By.CLASS_NAME,'company')[0].click()
    driver.implicitly_wait(10)
    time.sleep(3)
    
    
    driver.switch_to.window(driver.window_handles[-1])
    driver.implicitly_wait(10)
    time.sleep(1)
    
    tmp = driver.find_elements(By.XPATH,f'//*[@id="content"]/div/div[2]/div[1]/dl[2]/dd')
    
    x = '<회사소개> \n'

    for div in tmp:
        x += div.text
    ## 창두개 끄기
    
    # time.sleep(2)
    close_two_window(driver)
    
    return x

def jobkorea_link_to_pdf(link:str,driver):
    
    driver.get(link)
    driver.find_element(By.CLASS_NAME,'girBtn.girBtnPrint.devPrint').click()
    time.sleep(14)

    close_two_window(driver)
    
    return

def peoplenjob_link_to_pdf(link:str,driver):
    driver.get(link)
    driver.find_element(By.XPATH,'//*[@id="content-main"]/div/div[1]/div[2]/button[2]').click()
    time.sleep(14)
    
    close_two_window(driver)
    return

def close_two_window(driver):
    
    driver.switch_to.window(driver.window_handles[-1]) # 창 처음창 옮기기
    time.sleep(1)
    driver.close()


    time.sleep(1)
    # WebDriverWait(driver, 10)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(1)
    driver.close()
    
    return

## 함수선언후 다시 드라이버로

# Driver 옵션 및 설정 경로, 드라이버 선언.
def get_company_info_saram(driver):
    return

def get_pdf(link,save_path):
    
    settings = {
        "recentDestinations": [{
            "id": "Save as PDF",
            "origin": "local",
            "account": "",
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2,
        #"isHeaderFooterEnabled": False,
        #"isLandscapeEnabled": True
    }

    prefs = {'printing.print_preview_sticky_settings.appState': json.dumps(settings),
             "download.prompt_for_download": False,
             "profile.default_content_setting_values.automatic_downloads": 1,
             "download.default_directory": save_path,
             "savefile.default_directory": save_path,
             "download.directory_upgrade": True,
             "safebrowsing.enabled": True}

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument('--kiosk-printing')


    # options.add_experimental_option("detach", True)
    # options.setHeadless(true);
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    x = ''
    if 'jobkorea' in link:
        jobkorea_link_to_pdf(link,driver)
    elif 'saram' in link:
        x = saram_link_to_pdf(link,driver)
    elif 'peoplenjob' in link:
        peoplenjob_link_to_pdf(link,driver)
    else:
        driver.close()
        return('해당 링크는 유효하지 않습니다.')
    
    return x

form = '''
<company name>
이곳에 회사이름을 적습니다.

<job name>
이곳에 직무를 적습니다.

<지원자격>
이 부분에 모든 지원자격을 나열합니다.
(1.)
(2.)
(3.)
(4.)
(5.)
(6.)
….

<우대사항>
이부분에 모든 우대사항을 나열합니다
(1.)
(2.)
(3.)
(4.)
(5.)
(6.)
….
'''

def company_info(link:str,open_api_key,pinecone_key,pinecone_env,form):

    os.environ['OPENAI_API_KEY'] = open_api_key
    PINECONE_API_KEY = pinecone_key
    PINECONE_API_ENV = pinecone_env

    save_path = os.getcwd()
    info = get_pdf(link,save_path)
    
    list_of_files = glob.glob('*')
    latest_file = max(list_of_files, key=os.path.getctime)
    
    ### pine cone 설정 임베딩
    loader = PyPDFLoader(latest_file)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(data)
    
    
    embeddings = OpenAIEmbeddings(openai_api_key=open_api_key)

    # initialize pinecone
    pinecone.init(
        api_key=PINECONE_API_KEY,  # find at app.pinecone.io
        environment=PINECONE_API_ENV  # next to api key in console
    )
    index_name = "cow" # put in the name of your pinecone index here
    
    index = pinecone.Index(index_name)
    
    index.delete(delete_all=True)
    
    ### query 문 변경
    docsearch = Pinecone.from_texts([t.page_content for t in texts], embeddings, index_name=index_name)
    
    query = "지원자격이랑 모집요건이 어떻게돼?"
    docs = docsearch.similarity_search(query, include_metadata=True,k=1)
    
    ### LLMchain 구성
    ##################
    summary_template = """
         given the all information {information}.
         I want you to Separate the preferred qualifications and eligibity criteria.
         {form} This is the example format.
         Write in Korean.
     """

    summary_prompt_template = PromptTemplate(
        input_variables=["information"],
        template=summary_template,
        partial_variables={
            "form": form
        },
    )
    
    ### chat model 설정
    chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0,
                        top_p=1,
                        frequency_penalty=0.9,
                        presence_penalty=0.4,)
    
    ###
    
    chain = LLMChain(llm=chat, prompt=summary_prompt_template)
    
    blocks = chain.run(docs)
    ### 지원자격과 우대사항 순으로 나열된다.
    
    split = blocks.split('\n\n')
    return info,split[0],split[1],split[2],split[3]

def return_docs(company_job:str,pdf_name:str):

    loader = PyPDFLoader(pdf_name)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(data)
    
    
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))
    index = pinecone.Index('cow') 

    index.delete(delete_all=True)
    # initialize pinecone
    pinecone.init(
        api_key=PINECONE_API_KEY,  # find at app.pinecone.io
        environment=PINECONE_API_ENV  # next to api key in console
    )
    index_name = "cow" # put in the name of your pinecone index here
    
    ### query 문 변경
    docsearch = Pinecone.from_texts([t.page_content for t in texts], embeddings, index_name=index_name)
    
    query = f"{company_job}자소서와 유사한 문서"
    docs = docsearch.similarity_search(query, include_metadata=True,k=2)
    return docs

''