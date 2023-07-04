import requests
from bs4 import BeautifulSoup

import pandas as pd
import csv

#잡코리아 크롤링
def jobko_scraper(job):
    jobko_list = []
    for n in range(1,6):
        soup = requests.get('https://www.jobkorea.co.kr/Search/?stext={}&tabType=recruit&Page_No={}'.format(job, str(n)),
                headers={'User-Agent':'Mozilla/5.0'})
        try:
            html = BeautifulSoup(soup.text, 'html.parser').select_one('div.list-default')
            jobs = html.select('li.list-post')

            for job in jobs:
                deadline = job.select_one('span.date').text.strip()
                title = job.select_one('a.title').text.strip()
                company = job.select_one('a.name').text.strip()
                location = job.select_one('span.loc').text.strip()
                jobtype = job.select_one('span.exp').text.strip()
                url = 'https://www.jobkorea.co.kr'+job.find('a')['href']
                jobko_list.append([deadline, title, company, location, jobtype, url])
        except AttributeError:
            pass
    jobko_df = pd.DataFrame(jobko_list, columns=['마감일', '제목', '회사', '지역', '조건', '링크'])
    
    return jobko_df

#사람인 크롤링
def saram_scraper(job):
    saram_list = []
    if job:
        soup = requests.get('https://www.saramin.co.kr/zf_user/search/recruit?search_area=main&search_done=y&search_optional_item=n&searchType=search&searchword={}&recruitPage=1&recruitSort=relation&recruitPageCount=100&inner_com_type=&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&show_applied=&quick_apply=&except_read=&ai_head_hunting='.format(job),
                headers={'User-Agent':'Mozilla/5.0'})
        html = BeautifulSoup(soup.text, 'html.parser')
        jobs = html.select('div.item_recruit')
            
        for job in jobs:
            try:
                deadline = job.select_one('span.date').text.strip()
                title = job.select_one('a')['title'].strip().replace(',', '')
                company = job.select_one('div.area_corp > strong > a').text.strip()
                location = job.select('div.job_condition > span')[0].text.strip()
                jobtype = job.select('div.job_condition > span')[1].text.strip()
                url = 'https://www.saramin.co.kr'+job.select_one('h2.job_tit > a')['href']
                saram_list.append([deadline, title, company, location, jobtype, url])
            except Exception:
                pass
    saram_df = pd.DataFrame(saram_list, columns = ['마감일', '제목', '회사', '지역', '조건', '링크'])

    return saram_df

#피플앤잡 크롤링
def ppl_scraper(job):
    ppl_list = []
    if job:
        soup = requests.get('https://www.peoplenjob.com/jobs?field=all&q={}'.format(job),
                headers={'User-Agent':'Mozilla/5.0'})
        try:
            html = BeautifulSoup(soup.text, 'html.parser')
            jobs = html.select('div.min-h-screen > table > tbody > tr')

            for job in jobs:
                deadline = job.select_one('span.job-fin-date').text.strip().replace('.', '/')
                title = job.select_one('td.job-title').text.strip().replace('\n', '')
                company = job.select_one('td.name').text.strip().replace('\n','')
                location = job.select('td > a')[-1].text.strip().replace('\n', '')
                url = job.select_one('td.job-title > a')['href']
                ppl_list.append([deadline, title, company, location, url])
        except Exception:
            pass
    ppl_df = pd.DataFrame(ppl_list, columns = ['마감일', '제목', '회사', '지역', '링크'])

    return ppl_df

#마지막 피플앤잡 크롤링에는 조건이 빠져있다!()