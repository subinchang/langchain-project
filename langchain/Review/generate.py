import os
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import PyPDF2

def extract_text_from_pdf(file_path):
    """
    pdf path를 input으로 받아 string 으로반환
    """
    with open(file_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
    return text

def coverletter_interview(llm) -> LLMChain:
    """
    자기소개서를 기반으로 면접 10개를 뽑아주는 Chain
    coverletter_interview(llm).run(coverletter=text)
    """    
    role_template = """
        given the academic cover letter about a person {coverletter}. I want you to create:
        professional interview questions that are derived from their information on given cover letter.
        \
        write with korean.
        Write 10 possible interview questions as a numbered list.
        
        Questions:

     """

    interview_prompt_template = PromptTemplate(
        input_variables=["coverletter"],
        template=role_template,
    )
    
    return LLMChain(llm=llm, prompt=interview_prompt_template)

def tech_interview(llm) -> LLMChain:
    """
    지원하고자 하는 직무를 기반으로 테크 면접 질문 10개 생성.
    tech_interview(llm).run(job=직무)
    """ 
    
    role_template = """
        based on the job a person wants to work for I want you to
        Create: professional or technical interview questions for the {job}.
        \
        write with korean.
        Write 10 possible interview questions as a numbered list.
        
        Questions:
     """

    interview_prompt_template = PromptTemplate(
        input_variables=["job"],
        template=role_template,
    )
    return LLMChain(llm=llm, prompt=interview_prompt_template)

def ai_answer(llm) -> LLMChain:
    """
    질문과 답변을 토대로 질문을수정.
    ai_answer(llm).run(job=직무, question=질문,answer=답변)
    """
    
    role_template = """You're an interview expert. Based on the question about interviews and the interviewee response.
            interviews question: {question} interviewee response: {answer}.
            Please professionally edit the interviewee response, and feel free to use the user's information below if needed. 
            The user's information is the job position they want to work in.
            job position: {job}.
            \
            Write with korean.
            
            Edit response:
            """
    
        

    edit_template = PromptTemplate(
        input_variables=["job", "question", "answer"],
        template=role_template,
    )
    return LLMChain(llm=llm, prompt=edit_template)

def ai_feedback(llm) -> LLMChain:
    """
    면접 질문과 답변을 통해 피드백 생성.
    ai_feedback(llm).run(question=질문,answer=대답)
    """
    
    
    role_template = """Please review the interview records between the interviewer question and interviewee response
                    and provide feedback on the corresponding response. 
                    interviews question: {question} interviewee response: {answer}. 
                    provide the strengths and weaknesses of the corresponding interviewee from the interviewer's perspective. 
                    If there are no strengths or weaknesses to mention, please say 'no feedback'.

                    \
                    Write with korean.

                    Strengths:
                    Weakness:
                    """

    feedback_template = PromptTemplate(
        input_variables=["question", "answer"],
        template=role_template,
    )
    return LLMChain(llm=llm, prompt=feedback_template)

def modify_response(llm) -> LLMChain:
    """
    피드백을 바탕으로 최종 모법 답안 완성
    modify_response(llm).run(question=질문, answer=대답, feedback=피드백)
    """
    
    role_template = """Please modify the interviewee response: {answer} to the interviewer's question {question} based on the feedback: {feedback},
                    while preserving the strengths and addressing the weaknesses.

                    \
                    Write with korean.

                    Modify interviewee response:
                    """

    modify_template = PromptTemplate(
        input_variables=["question", "answer", "feedback"],
        template=role_template,
    )
    return LLMChain(llm=llm, prompt=modify_template)