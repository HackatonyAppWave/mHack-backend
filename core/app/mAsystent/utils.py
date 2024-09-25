import pandas as pd
import json
import re


def get_majors(text):
    majors_pattern = re.compile(r'majors:\s*(.+)')

    majors_strs = re.findall(majors_pattern, text)
    majors = {}
    try:
        if majors_strs:
            majors = json.loads(majors_strs[0].replace("'", '"'))
    except:
        pass

    
    return majors


def decode_polish_characters(input_string):
    decoded_string = re.sub(r'\\u([\da-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), input_string)
    return decoded_string


def get_deed_and_article_pairs(text):
    deed_pattern = re.compile(r'akt prawny:\s*(.*)\s*artykuł')
    art_pattern = re.compile(r'artykuł: (Art\.\s*\S+\.)?')
    
    deeds = re.findall(deed_pattern, text)
    arts = re.findall(art_pattern, text)

    if len(deeds) != len(arts):
        return None
    
    pairs = [(deeds[i], arts[i]) for i in range(len(deeds))]
    
    return pairs


def get_urls_from_text(text):
    urls_pattern = re.compile(r'urls:\s*(https?://[A-Za-z0-9\.-]+/\S*)')
    urls = re.findall(urls_pattern, text)
    return urls


def faq_to_csv():
    with open("faq.json", "r") as f:
        faq = json.load(f)
    data = {"questions": [], "answers": [], "urls": []}
    for obj in faq["faq"]:
        data["questions"].append(obj["question"])
        data["answers"].append(obj["answer"])
        data["urls"].append(obj["url"])
    pd.DataFrame(data).to_csv("faq.csv", index=False)
