import os
import openai
from config import OPENAI_KEY, LOCAL_API_BASE
import json
openai.api_key = OPENAI_KEY


def switch_local():
    openai.api_base = LOCAL_API_BASE


def switch_remote():
    openai.api_base = "https://api.openai.com/v1"


def publication_summarize(input_text, retry=3):

    collected_messages = ""

    for chunk in openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "以下是某作者的著作列表，格式为<Title,PublishYear,CitationNum>\n\n首先根据所有论文总结其研究方向大类（如材料学，计算机科学）；根据研究大类总结对应的小分类（大分类中可以有多个小分类）；同时用中文概述对应小分类的研究成果，不要输出具体论文名，不同分类单独总结，不要前置修饰语，直接枚举\n\n内容使用JSON格式输出\n\n如：\n[{'subject':'计算机科学','sub_areas':[{'area':'计算机图形学', 'summary':‘<总结内容>'}, {'area':'机器学习', 'summary':‘<总结内容>'}]},{'subject':'自动化工程','sub_areas':[{'area':'人形机器人', 'summary':'<总结内容>'}]}]\n\n输出内容使用中文，确保输出完整，不要省略,严格遵守JSON格式"
                },
                {
                    "role": "user",
                    "content": input_text
                }
            ],
            temperature=0.25,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=2,
            stream=True,
    ):
        content = chunk["choices"][0].get("delta", {}).get("content")
        if content is not None:
            collected_messages += content
            print(content, end='',flush=True)
    print('')

    try:
        json.loads(collected_messages)
    except:
        if retry > 0:
            print("OpenAI Failed, Retrying...")
            return publication_summarize(input_text, retry-1)
        else:
            return None, -1


    return collected_messages, -1
