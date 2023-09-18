import os
import openai
from config import OPENAI_KEY, REMOTE_API_BASE, LOCAL_API_BASE
from utils import clear_last_line
import json
import tiktoken

openai.api_key = OPENAI_KEY


def switch_local():
    openai.api_base = LOCAL_API_BASE


def switch_remote():
    openai.api_base = REMOTE_API_BASE

def count_tokens(input_text):
    return len(tiktoken.encoding_for_model("gpt-3.5-turbo").encode(input_text))

def publication_summarize(input_text, retry=3, remote=True):

    if remote:
        switch_remote()
    else:
        switch_local()

    collected_messages = ""
    snippet_length = 50

    complete_max=2048

    for chunk in openai.ChatCompletion.create(
            model="gpt-3.5-turbo" if count_tokens(input_text)+complete_max<4097 else "gpt-3.5-turbo-16k",
            messages=[
                {
                    "role": "system",
                    "content": "以下是某作者的著作列表，格式为<Title,PublishYear,CitationNum>\n\n首先根据所有论文总结其研究方向大类（如材料学，计算机科学）；根据研究大类总结对应的小分类（大分类中可以有多个小分类）；同时用中文概述对应小分类的研究成果，不要输出具体论文名，不同分类单独总结，不要前置修饰语，直接枚举，文字精简\n\n内容使用JSON格式输出\n\n如：\n[{'subject':'计算机科学','sub_areas':[{'area':'计算机图形学', 'summary':‘<总结内容>'}, {'area':'机器学习', 'summary':‘<总结内容>'}]},{'subject':'自动化工程','sub_areas':[{'area':'人形机器人', 'summary':'<总结内容>'}]}]\n\n输出内容使用中文，确保输出完整，不要省略"
                },
                {
                    "role": "user",
                    "content": input_text
                }
            ],
            temperature=0.2,
            max_tokens=complete_max,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=2,
            stream=True,
    ):
        content = chunk["choices"][0].get("delta", {}).get("content")
        if content is not None:
            collected_messages += content
            clear_last_line(len("[")+snippet_length+1)

            print("[", end='')
            print(collected_messages[-snippet_length:], end='')
            print("]", end='', flush=True)

    clear_last_line(len("[")+snippet_length+1)

    try:
        json.loads(collected_messages)
    except:
        if retry > 0:
            print("OpenAI Failed, Retrying...")
            return publication_summarize(input_text, retry-1)
        else:
            return None, -1

    return collected_messages, -1
