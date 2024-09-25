from langchain.prompts import PromptTemplate
from langchain_community.llms import OpenAI
from langchain.chains import LLMChain
from langchain_community.embeddings import OpenAIEmbeddings
import pandas as pd
from langchain_community.vectorstores import FAISS
import json
import urllib.parse
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import pathlib
from .utils import decode_polish_characters

PATH = pathlib.Path(__file__).parent.resolve()


class UniAdvisor:
    def __init__(self) -> None:
        self.llm = OpenAI(temperature=0)
        self.load_database()
        self.data = pd.read_csv(os.path.join(PATH, "uni_db.csv"))

    def load_database(self):
        embeddings = OpenAIEmbeddings()
        self.db = FAISS.load_local(os.path.join(PATH, "uni_db"), embeddings)

    def get_chain(self, prompt_template, input_variables):
        return LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=prompt_template, input_variables=input_variables
            ),
        )

    def get_docs(self, query: str, k: int = 5):
        docs = self.db.similarity_search(query, k=k)
        doc_objs = [doc.dict() for doc in docs]
        return doc_objs

    def get_universities(self, doc_objs):
        universities = []
        for doc_obj in doc_objs:
            url = self.data.iloc[doc_obj["metadata"]["row"]]["uczelnia"]
            universities.append(url)
        return universities

    def get_references(self, doc_objs):
        urls = []
        for doc_obj in doc_objs:
            url = self.data.iloc[doc_obj["metadata"]["row"]]["link"]
            urls.append(url)
        return urls

    def get_majors(self, doc_objs):
        urls = []
        for doc_obj in doc_objs:
            url = self.data.iloc[doc_obj["metadata"]["row"]]["kierunek"]
            urls.append(url)
        return urls

    def get_contents(self, doc_objs):
        contents = []
        for doc_obj in doc_objs:
            contents.append(doc_obj["page_content"])
        return contents

    def __call__(self, interests):
        prompt_template = "Jesteś asystentem AI, który ma doradzić absolwentom liceum kierunki studiów na podstawie zainteresowań użytkownika oraz poniższego tekstu zaproponuj kierunki studiów najlepiej pasujące dla niego. Nie podawaj linku. Powinieneś uzasadnić swój wybór. \Zainteresowania:\n{interests}\nTekst:{text}"

        chain = self.get_chain(prompt_template, ["interests", "text"])

        docs = self.get_docs(interests)
        contents = self.get_contents(docs)
        majors = self.get_majors(docs)
        references = self.get_references(docs)

        response = chain.run(interests=interests, text="\n".join(contents))
        linked_majors = {major: link for major, link in zip(majors, references)}

        return response, linked_majors


if __name__ == "__main__":
    load_dotenv()
    gpt = UniAdvisor()
    interests = (
        "Lubie nauki scisle. Nie lubie ludzi. Wole siedziec przed komputerem. Lubie gry"
    )
    response, linked_majors = gpt(interests)
    print(response)
    print(linked_majors)
