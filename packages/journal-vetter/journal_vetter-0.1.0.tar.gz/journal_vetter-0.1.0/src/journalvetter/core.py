from langchain.schema import Document
from typing import List, Dict
import fitz
import json
from pathlib import Path
from langchain.text_splitter import TokenTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from dotenv import load_dotenv, find_dotenv
from langchain.prompts import PromptTemplate
from .config import load_config

load_dotenv()

#function that recieved a journal's PDF and extracts the raw text into a varible & returns it
def readpdf(path:str)->str:
    pdftext = []
    doc = fitz.open(path)
    for page in doc:
        temp = page.get_text()
        pdftext.append(temp);
    #return the variable "rawtext"
    doc.close()
    return "\n".join(pdftext)

#function that takes a journal's extracted data and formats it into a document with it's important properties (metadata)
#(as defined by the user in the Dictionary-template)
def gettemplate()->Dict[str, str]:
    getting = True
    template : Dict[str,str] = {}
    print("To finish creating the template, type D or d")
    while(getting):
        curr_key = input("Enter desired key:\n")
        curr_val = input("Enter desired value:\n")
        answer = input("Does this look correct?(y/n): key: " + curr_key + " value: " + curr_val + "\n")
        if(answer.lower()=='y'):
            template[curr_key] = curr_val
        elif(answer.lower()=='d'):
            getting = False
        else:
            continue    
    return template

#function from which the other above two are called; a list of journals is iterated through, parsed & formatted
#into documents then returned
def aggregatedata(journalspath:Path)->List[str]:
    filedatas : List[str] = []
    for file in journalspath.glob("*.pdf"):
        currfile_data = readpdf(file)
        filedatas.append(currfile_data)
    return filedatas

#split the passed-in raw document-metadata pair into a ~1000 token Document & return
def createembeddings(journaldatas:List[str])->List[List[str]]:
    textsplitter = TokenTextSplitter(encoding_name="cl100k_base", chunk_size=50, chunk_overlap=0)
    tokenized_journals : List[List[str]] = []
    for journaldata in journaldatas:
        currtokens = textsplitter.split_text(journaldata)
        tokenized_journals.append(currtokens)
    return tokenized_journals

def buildquery(mode)->PromptTemplate:
    if(mode=='cli'):
        prompt = PromptTemplate(
            input_variables=["template", "journalcontexts"],
            template="""
                You are a research librarian assistant.  You will be given:

                1. Desired attributes (as JSON):  
                    {template}

                2. A series of journal summaries, each prefixed by its filename:  
                    {journalcontexts}

                TASK:
                - For each journal, give a one-sentence “Fit Score” (0–10) based on how well it matches the attributes.  
                - Then list pros and cons in bullets.  
                - Finally, in a line that starts exactly **“Recommended Journal: ”**, name the single journal with the highest Fit Score and give a 2-sentence rationale.

                Your final answer _must_ end with exactly:

                Recommended Journal: <Journal's Main Author Name & Article Title>
                Rationale: <Your concise reasoning.>
            """
        )
    if(mode == "library"):
        prompt = PromptTemplate(
            input_variables=["template", "journalcontexts"],
            template="""
                You are a research librarian assistant. You will be given:

                1. Desired attributes (as JSON):  
                {template}

                2. A series of journal summaries, each prefixed by its filename:  
                {journalcontexts}

                TASK:
                - Identify the single journal article that best matches the desired attributes.
                - Return **only** that article’s title as a plain string, with no additional text, bullets, or commentary.

            """
        )
    return prompt


#query the llm using our yaml-defined template-string & the prompt, as well as the condensed journal-data
#collected from compressjournals
def queryLLM(prompt:PromptTemplate, templatestr:str, journalcontexts:List[List[str]], llm)->str:
    journal_context_str = "\n\n".join(chunk for journal in journalcontexts for chunk in journal)
    chain = LLMChain(llm=llm, prompt=prompt)
    answer = chain.run(
        template = templatestr,
        journalcontexts = journal_context_str
    )
    return answer

#iterate through the downloaded text from the provoded journal-pdfs & get thoughtfully-condensed summaries
#that will be used later on for the llm's final reasoning/analysis
def compressjournals(filedatas:List[str], llm)->List[str]:
    summarized_journals: List[str] = []

    prompt = PromptTemplate(
        input_variables=["journalcontext"],
        template="""
            You are an expert at condensing scientific papers.  

            TASK:  
            Given the full extracted text below, produce a **single concise summary** that contains **only** the following elements:

            - **Title** (if available)  
            - **Authors** (if available)  
            - **Publication Year** (if available)  
            - **Research Field**  
            - **Methods** (briefly describe experimental or computational approaches)  
            - **Data** (type, size, source)  

            Also search and find the associated journal's impact factor & include the Journal's title in the same manner as above

            DO NOT include anything else—no background, no discussion points, no bullet lists of pros/cons, no extra commentary.  
            Return exactly those items, labeled, in plain text.

            ——————————————  
            Text to summarize:  {journalcontext}
        """
    )
    for file in filedatas:
        journalcontext = file
        chain = LLMChain(llm=llm, prompt=prompt)
        answer = chain.run(
            journalcontext = journalcontext
        )
        summarized_journals.append(answer)
    return summarized_journals

#"main" file for the program; replace yaml fields as needed, instantiale llm object & call appropriate functions
#in-order
def do_vet_journals(cfg, config_file_path, resources_path, output_file, field, impact_factor, cell_line, model_type, mode):
    if field:
        cfg["criteria"]["field"] = field
    if impact_factor:
        cfg["criteria"]["impact_factor"] = impact_factor
    if cell_line:
        cfg["criteria"]["cell_line"] = cell_line
    if model_type:
        cfg["criteria"]["model_type"] = model_type

    llm = ChatOpenAI(
        model_name=cfg['model']['name'],     
        temperature=0.0,        
        max_tokens=512,         
    )

    filedatas = aggregatedata(resources_path)
    summarized_files = compressjournals(filedatas, llm)
    tokenizedjournals = createembeddings(summarized_files)
    templatestr = json.dumps(cfg["criteria"], indent=2)
    prompt = buildquery(mode)
    answer = queryLLM(prompt, templatestr, tokenizedjournals, llm)

    if(mode=="cli"):
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(answer, encoding="utf-8")
        print(f"Results saved to {output_file}")
        print(answer)
    
    return answer