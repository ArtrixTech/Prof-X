from publicsuffixlist import PublicSuffixList
import matplotlib.pyplot as plt
import requests
import json
import os

def get_top_domain(domain: str) -> str:
    psl = PublicSuffixList()
    # 获取公共后缀
    suffix = psl.publicsuffix(domain)

    print(domain)
    
    # 域名和公共后缀分割，然后取最后一个部分作为一级域名
    domain_parts = domain.split(".")
    suffix_parts = suffix.split(".")
    
    if len(domain_parts) <= len(suffix_parts):
        return domain+'.'+suffix
    return domain_parts[-len(suffix_parts)-1]+'.'+suffix



def save_plot_to_imgur(fig):
    # 保存图表到临时文件
    temp_file = "temp_plot.png"
    fig.savefig(temp_file)

    # 将图表上传到Imgur
    url = "https://api.imgur.com/3/upload"
    headers = {"Authorization": "Client-ID YOUR_CLIENT_ID"}
    data = {"image": open(temp_file, "rb").read()}

    response = requests.post(url, headers=headers, data=data)
    response_data = json.loads(response.text)

    # 获取上传后的图片链接
    imgur_link = response_data["data"]["link"]

    # 删除临时文件
    os.remove(temp_file)

    return imgur_link

import sys
import threading

class InputTimeoutError(Exception):
    pass

def input_with_timeout(prompt, timeout=10, default_input=""):
    """Prompt user for input, with a given timeout.
    
    If the user does not provide input within the timeout, return a default input value.
    
    Args:
    - prompt (str): The input prompt to display to the user.
    - timeout (int): The number of seconds to wait for user input.
    - default_input (str): The default input value to return if the user does not provide input.

    Returns:
    - str: The user's input, or the default input if the user does not provide input within the timeout.
    """
    sys.stdout.write(prompt)
    sys.stdout.flush()

    result = {"value": None}

    def get_input(result):
        result["value"] = sys.stdin.readline().rstrip()

    thread = threading.Thread(target=get_input, args=(result,))
    thread.daemon = True
    thread.start()
    thread.join(timeout)

    return result["value"] if result["value"] is not None else default_input



if __name__ == "__main__":

    print(get_top_domain("www.baidu.com"))
    print(get_top_domain("a.b.c.co.uk"))

    print(input_with_timeout("Please input something:", 5, "default value"))
