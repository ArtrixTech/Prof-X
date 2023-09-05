import os
import openai
from config import OPENAI_KEY, LOCAL_API_BASE
import json
openai.api_key = OPENAI_KEY


def switch_local():
    openai.api_base = LOCAL_API_BASE


def switch_remote():
    openai.api_base = "https://api.openai.com/v1"


def publication_summarize(input_text, retry=2):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "以下是某作者的著作列表，格式为<Title,PublishYear,CitationNum>\n\n首先根据所有论文总结其研究方向大类（如材料学，计算机科学）；根据研究大类总结对应的小分类（大分类中可以有多个小分类）；同时用中文概述对应小分类的研究成果，不要输出具体论文名，不同分类单独总结，不要前置修饰语，直接枚举\n\n内容使用JSON格式输出\n\n如：\n[{'subject':'计算机科学','sub_areas':[{'area':'计算机图形学', 'summary':‘<总结内容>'}, {'area':'机器学习', 'summary':‘<总结内容>'}]},{'subject':'自动化工程','sub_areas':[{'area':'人形机器人', 'summary':'<总结内容>'}]}]\n\n输出内容使用中文，确保输出完整，不要省略"
            },
            {
                "role": "user",
                "content": input_text
            }
        ],
        temperature=0.25,
        max_tokens=768,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=2,
        stream=True,
    )

    collected_chunks = []
    collected_messages = []

    # iterate through the stream of events
    for chunk in response:
        try:
            collected_chunks.append(chunk)  # save the event response
            chunk_message = chunk['choices'][0]['delta']  # extract the message
            collected_messages.append(chunk_message)  # save the message
            print(json.loads(str(chunk_message))['content'],end="")  # print the delay and text
        except:
            pass

    # print the time delay and text received
    full_reply_content = ''.join([m.get('content', '') for m in collected_messages])

    try:
        json.loads(full_reply_content)
    except:
        if retry > 0:
            print("OpenAI Return Error, retrying...")
            return publication_summarize(input_text, retry-1)
        else:
            return None, response['usage']['total_tokens']

    return full_reply_content, response['usage']['total_tokens']

