import os
from serpapi import GoogleSearch
import requests
import streamlit as st

from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain import PromptTemplate

##test
from langchain import OpenAI
from langchain.chains.summarize import load_summarize_chain

os.environ["OPENAI_API_KEY"] = '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'


## 키워드 두개 회사이름 직장을 입력값으로 받아서 -> 링크, 프로필사진, 요약 텍스트를 반환해주는 함수를 만들어 보자.
def get_linkedin_profile_url(company_name, job_title):
    params = {
        "engine": "google",
        "q": f"{company_name} {job_title} site:linkedin.com/in/",
        "api_key": os.getenv("SERPAPI_API_KEY")
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    # Extract the first LinkedIn profile URL from the search results
    linkedin_url = results["organic_results"][0]["link"]

    return linkedin_url

###### 링크드인 정보 추출함수
#변환전 -> 소개글이 길 경우 토큰이 넘어가기 때문에 아래 코드로 수정함
# def scrape_linkedin_profile(linkedin_profile_url: str):
#     """링크드인에서 프록시컬 api이용해
#     정보를 추출합니다."""
#     api_endpoint = "https://nubela.co/proxycurl/api/v2/linkedin"
#     header_dic = {"Authorization": f'Bearer {os.getenv("PROXYCURL_API_KEY")}'}

#     response = requests.get(
#         api_endpoint, params={"url": linkedin_profile_url}, headers=header_dic
#     )
    
#     # 데이터 정제과정
#     data = response.json()
#     data = {
#         k: v
#         for k, v in data.items()
#         if v not in ([], "", "", None)
#         and k not in ["people_also_viewed", "certifications"]
#     }
#     if data.get("groups"):
#         for group_dict in data.get("groups"):
#             group_dict.pop("profile_pic_url")

#     return data

def scrape_linkedin_profile(linkedin_profile_url: str):
    """링크드인에서 프록시컬 api이용해
    정보를 추출합니다."""
    api_endpoint = "https://nubela.co/proxycurl/api/v2/linkedin"
    header_dic = {"Authorization": f'Bearer {os.getenv("PROXYCURL_API_KEY")}'}

    response = requests.get(
        api_endpoint, params={"url": linkedin_profile_url}, headers=header_dic
    )
    
    # 데이터 정제과정
    data = response.json()
    data = {
        k: v
        for k, v in data.items()
        if v not in ([], "", "", None)
        and k not in ["people_also_viewed", "certifications",'background_cover_image_url','similarly_named_profiles',
                  'public_identifier', 'activities']
    }   
    if data.get("groups"):
        for group_dict in data.get("groups"):
            group_dict.pop("profile_pic_url")
    
    return data


### 정제된 데이터를 가지고 요약본을 만들어주는 함수를 만들어보자.

form = '''Name: Jihyeon Han
JOB: Kakao Corp 데이터 분석가

* 경력:
- 현재 Kakao Corp에서 공동체데이터센터 응용분석팀에서 데이터 분석가로 일하고 있습니다. (2021년 10월 1일 ~ 현재)
- 이전에는 학사 학위를 취득한 고려대학교에서 공부하며 다양한 경험을 쌓았습니다. (2014년 1월 1일 ~ 2019년 12월 31일)

* 학위:
- 고려대학교에서 학사 학위를 취득하였습니다.

* Skills:
- 데이터 분석
- 영어

Jihyeon Han은 현재 Kakao Corp에서 데이터 분석가로 일하고 있으며, 이전에는 고려대학교에서 학사 학위를 취득하며 다양한 경험을 쌓았습니다.
데이터 분석과 영어에 능숙하며, 이전 경력들도 다양한 분야에서 경험을 쌓았습니다.'''

### 모델 선언

llm_creative = ChatOpenAI(temperature=0.1, model_name="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"))

def get_summary_chain() -> LLMChain:
    summary_template = """
        given the information about a person from linkedin {information}. I want you to create:
        creative experience summary,startdate,enddate with them that are derived from their activity on given Linkedin data.
        and use topic {topic}
        \
        write with korean
        example form : {form}
     """

    summary_prompt_template = PromptTemplate(
        input_variables=["information"],
        template=summary_template,
        partial_variables={
            "topic": '1.이름 2.직업 3.경력, 학위 등등 4.skills 각 토픽별로 두줄씩 띄워주시고 경력같은 경우 이전경력들도 다 설명해주세요 토픽별 세부 리스트는 * 로 시작해주세요'
            ,'form' : form
        },
    )
    return LLMChain(llm=llm_creative, prompt=summary_prompt_template)

### output link,pic,summary_txt,data, 와 현재 재직중인 회사 로고 추가할거 회사로고.
def summary_linkedin(company_name:str,job_title:str):
    # link 불러오기
    link = get_linkedin_profile_url(company_name,job_title)
    
    # 불러온 link 에서 json 파일 받아오기.
    
    data = scrape_linkedin_profile(link)
    ### data는 정제된 데이터 이다.
    data['experiences'][0]['logo_url']
    ### summarychain 받아오기
    summary_chain = get_summary_chain()
    summary_txt = summary_chain.run(
        information=data
    )
    return link,data['profile_pic_url'],summary_txt,data,data['experiences'][0]['logo_url']