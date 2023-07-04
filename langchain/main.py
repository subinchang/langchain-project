
import pandas as pd
import datetime
import os
import requests
import json
import csv

#Streamlit
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
from streamlit_chat import message
import pybase64 as base64 

#LangChain
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain, ConversationChain
from langchain import PromptTemplate
from serpapi import GoogleSearch

# #for vector q&a
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.vectorstores import Pinecone
# from langchain.embeddings.openai import OpenAIEmbeddings
# import pinecone
# from langchain.document_loaders import PyPDFLoader
# from langchain.chains.question_answering import load_qa_chain

#Custom package
from Crawl.crawl import jobko_scraper, saram_scraper, ppl_scraper
from Linkedin.profile import summary_linkedin
from Front.stream import load_lottiefile, load_lottieurl
from Resume.resume import saram_link_to_pdf, jobkorea_link_to_pdf, peoplenjob_link_to_pdf, close_two_window, get_company_info_saram, get_pdf, company_info, return_docs


#api key to os
with st.sidebar:
    openai_key = st.text_input("OpenAI Key", type="password")
    serpapi_key = st.text_input("SerpAPI Key", type="password")
    proxycurl_key = st.text_input("Proxycurl Key", type="password")

def sidebar_bg(side_bg):

   side_bg_ext = 'gpt.png'

   st.markdown(
      f"""
      <style>
      [data-testid="stSidebar"] > div:first-child {{
          background: url(data:image/{side_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()});
      }}
      </style>
      """,
      unsafe_allow_html=True,
      )


#Put Key in OS
os.environ["OPENAI_API_KEY"] = openai_key
os.environ["SERPAPI_API_KEY"] = serpapi_key
os.environ["PROXYCURL_API_KEY"] = proxycurl_key
# os.environ["PINECONE_API_KEY"] = '1a40031c-9c10-46ad-b429-2cd09d2102c3'
# os.environ["PINECONE_API_ENV"] = 'us-west1-gcp-free'

PINECONE_API_KEY = '1a40031c-9c10-46ad-b429-2cd09d2102c3'
PINECONE_API_ENV = 'us-west1-gcp-free'

#상단 메뉴 생성
selected = option_menu(
    menu_title=None,
    options=["HOME", "Resume", "LinkedIn", "Interview"],
    icons=["house-door-fill", "file-earmark-person-fill", "linkedin", "chat-square-dots-fill"], #https://icons.getbootstrap.com/
    # menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "purple", "font-size": "25px"}, 
        "nav-link": {"font-size": "22px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "purple"},
    }
)

# Home page
if selected == "HOME":
    st.title("👋🏻 Welcome to LLMops Prototype")
    H_col1, H_col2 = st.columns([3, 1])
    with H_col1:
        st.markdown('원하는 직무를 입력하고 여러 채용사이트의 직무 관련 공고를 한 번에 받아보세요.')
    with H_col2:
        lottie_ai = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_96bovdur.json")
        st_lottie(
            lottie_ai,
            speed=1,
            reverse=False,
            loop=True,
            quality="low", # medium ; high
            # renderer="svg", # canvas
            height=None,
            width=None,
            key=None,
        )
    
    # Auto complete select box
    job_df = pd.read_csv("Data/job_detail.csv")
    jobs = list(job_df["keyword"])
    jobs.insert(0, "")
    option = st.selectbox(
    '어떤 직무의 공고를 보고 싶으신가요?',
    jobs)
   
    
    # 엑셀저장
    @st.cache
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

    #공고 불러와서 Data프레임 보기
    button_list = st.button('공고 불러오기')
    if st.session_state.get('button') != True:
        st.session_state['button'] = button_list
    if st.session_state['button'] == True:
        jobko_df = jobko_scraper(option)
        saram_df =  saram_scraper(option)
        ppl_df = ppl_scraper(option)
        df = pd.concat([jobko_df, saram_df, ppl_df])
        st.dataframe(df)
        if st.button('엑셀로 저장하기'):
            df.to_csv(option+'.csv', index=False, header=['마감일', '제목', '회사', '지역', '조건', '링크'], encoding='utf-8-sig')

# 자기소개서 작성
if selected == "Resume":
    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown("## 자기소개서 초안 작성하기")
    with col2:
        lottie_resume = load_lottieurl("https://assets7.lottiefiles.com/private_files/lf30_cldvedro.json")
        st_lottie(
        lottie_resume,
        speed=0.8,
        reverse=False,
        loop=True,
        quality="low", # medium ; high
        # renderer="svg", # canvas
        height=None,
        width=None,
        key=None,
        )
    link = st.text_input('지원할 공고의 링크를 입력해주세요.')
    if link:
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
        
        a,b,c,d,e = company_info(link,openai_key,PINECONE_API_KEY,PINECONE_API_ENV,form)
        company_job = b.split('\n')[1]+':'+c.split('\n')[1]
        pdf_name = 'Resume/링커리어_합격자소서.pdf'
        docs = return_docs(company_job,pdf_name)
        
        prompt_template = '''
        You are a chatbot designed to write a cover letter.
        You are applying for this role: {role} in this compahy: {company}.
        The qualifications you satisfy are given as follows: {qualifications}.
        Based on these information, write a cover letter at least 800 words long.
        Refer to {page} for tone and style only.
        Do not use the information itself given in page.
        That information in page is a part of another user's cover letter.
        Use Korean only.
        '''
        prompt = PromptTemplate(
            input_variables=["page", "role", "company", "qualifications"], 
            template=prompt_template
        )
        chatgpt_chain = LLMChain(
            llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.2,
                                top_p=0.5),
            prompt=prompt, 
            verbose=True,  
        )
        
        res = chatgpt_chain.run(page=docs, role=c, company=b,
                        qualifications=d+e)
        st.info(res)
    

#링크드인 추천
if selected == "LinkedIn":
    lottie_linkedin = load_lottieurl("https://assets8.lottiefiles.com/packages/lf20_ywt06tjx.json")
    load_profile=False
    #입력란
    col_, L_col1, L_col2, col_= st.columns([1, 2, 2, 1])
    col_, L_col3, col_= st.columns([1, 4, 1])
    col_, L_col4, col_= st.columns([1, 4, 1])
    col_, L_col5, col_= st.columns([1, 4, 1])
    load_profile=False

    with L_col1:
        st.markdown("## 현직자 링크드인 추천을 받아보세요")
        st.markdown('원하는 회사와 직무의 현직자 링크드인 프로필을 확인해보세요.')
    with L_col2:
        st_lottie(
        lottie_linkedin,
        speed=1,
        reverse=False,
        loop=True,
        quality="low", # medium ; high
        # renderer="svg", # canvas
        height=None,
        width=None,
        key=None,
        )
    with L_col3:
        company = st.text_input("지원하는 회사")
    with L_col4:
        job = st.text_input("지원하는 직무")
    with L_col5:
        if st.button('링크드인 추천받기'):
            load_profile=True

    if load_profile==True:
        url,b,c,d,e = summary_linkedin(company, job)
        blocks = c.split("\n\n")

        st.subheader("추천인은 다음과 같습니다.")
        col_, L_col6, L_col7, col_= st.columns([1, 3, 1, 1])
            
        L_col6.markdown(f"[![Foo]({b})](http://google.com.au/)")
        L_col7.markdown(f"[![Foo]({e})]()")

        st.markdown("Linkedin URL")
        st.markdown(url)
        for i in range(len(blocks)):
            if i==len(blocks)-1:
                st.markdown(blocks[i])
            else:
                st.text(blocks[i])

#인터뷰
if selected == "Interview":
    # Setting page title and header
    lottie_linkedin = load_lottieurl("https://assets6.lottiefiles.com/packages/lf20_6wkp2o3cgq.json")
    st_lottie(
        lottie_linkedin,
        speed=1,
        reverse=False,
        loop=True,
        quality="low", # medium ; high
        # renderer="svg", # canvas
        height=None,
        width=None,
        key=None,
        )
    st.markdown("<h1 style='text-align: center;'>AI 면접 서비스</h1>", unsafe_allow_html=True)

    test_text = [
    '지원동기를 알려주신 것처럼, 핀테크 전문가 과정에 지원하게 된 이유가 무엇인가요?',
    '컴퓨터 공학과 철학을 함께 전공하셨다고 하셨는데, 이 두 분야를 결합하여 어떤 분야에서 활용하고 싶으신가요?',
    """이전에 참여하셨던 '블록체인을 활용한 스터디 관리 플랫폼' 프로젝트에서 어떤 역할을 맡으셨나요?""",
    '프로젝트 실패의 원인으로 개발에 대한 열정 부족을 꼽으셨는데, 이번 핀테크 전문가 과정에서는 어떻게 열정을 쏟아낼 계획인가요?',
    '빅데이터 프로젝트 경험이 부족하다고 하셨는데, 이를 보완하기 위해 어떤 노력을 하고 있나요?',
    '핀테크 분야에서 가장 관심 있는 기술이나 분야가 무엇인가요?',
    '이번 핀테크 전문가 과정에서 어떤 목표를 가지고 참여하고 있나요?',
    '금융에 대한 이해가 부족하다고 하셨는데, 이를 보완하기 위해 어떤 자기계발 방법을 사용하고 있나요?',
    '이번 핀테크 전문가 과정을 마치고 나서, 어떤 분야에서 활동하고 싶으신가요?',
    '핀테크 분야에서 성공적인 전문가가 되기 위해 필요한 역량이 무엇이라고 생각하시나요?',
    '어떤 데이터 분석 도구를 사용하시나요?',
    '데이터 분석을 통해 어떤 문제를 해결했나요?',
    '데이터 분석에서 가장 어려운 부분은 무엇인가요?',
    '데이터 분석을 위해 필요한 기술은 무엇인가요?',
    '데이터 분석에서 가장 중요한 요소는 무엇인가요?',
    '데이터 분석을 통해 얻은 결과를 어떻게 활용하시나요?',
    '데이터 분석에서 발생한 문제를 해결하기 위해 어떤 방법을 사용하시나요?',
    '데이터 분석에서 가장 성공적인 프로젝트는 무엇이었나요?',
    '데이터 분석에서 발생한 문제를 해결하기 위해 어떤 도구를 사용하시나요?',
    ]

    # Initialise session state variables
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []
    if 'past' not in st.session_state:
        st.session_state['past'] = []
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    if "num" not in st.session_state:
        st.session_state['num'] = 0

    # Sidebar - let user choose model, show total cost of current conversation, and let user clear the current conversation
    st.sidebar.title("Sidebar")
    clear_button = st.sidebar.button("Clear Conversation", key="clear")

    # reset everything
    if clear_button:
        st.session_state['generated'] = []
        st.session_state['past'] = []
        st.session_state['messages'] = [] 
        st.session_state['num'] = 0
        st.session_state['total_cost'] = 0.0



    # generate a response
    def generate_response(prompt):
        st.session_state['messages'].append({"role": "user", "content": prompt})
        response = test_text[st.session_state['num']]
        st.session_state['messages'].append({"role": "assistant", "content": response})
        st.session_state['num'] += 1

        print(st.session_state['messages'])
        return response


    # container for chat history
    response_container = st.container()
    # container for text box
    container = st.container()

    with container:
        with st.form(key='my_form', clear_on_submit=True):
            user_input = st.text_area("You:", key='input', height=100)
            submit_button = st.form_submit_button(label='Send')

        if submit_button and user_input:
            output = generate_response(user_input)
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)


    if st.session_state['generated']:
        with response_container:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
                message(st.session_state["generated"][i], key=str(i))
