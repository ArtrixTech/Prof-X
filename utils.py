from publicsuffixlist import PublicSuffixList
import matplotlib.pyplot as plt
import requests
import json
import os

def get_top_domain(domain: str) -> str:
    psl = PublicSuffixList()
    # 获取公共后缀
    suffix = psl.publicsuffix(domain)
    
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
import time

class InputTimeoutError(Exception):
    pass

def input_with_timeout(prompt, timeout=10, default_input=""):
    """Prompt user for input, with a given timeout.
    
    Args:
    - prompt (str): The input prompt to display to the user.
    - timeout (int): The number of seconds to wait for user input.
    - default_input (str): The default input value to return if the user does not provide input.

    Returns:
    - str: The user's input, or the default input if the user does not provide input within the timeout.
    """
    sys.stdout.write(f"\r{prompt} (default <{timeout}s> = \"{default_input}\") ")
    sys.stdout.flush()

    result = {"value": None,"finished":False}

    def get_input(result):
        result["value"] = sys.stdin.readline().rstrip()
        result["finished"] = True

    def show_countdown(timeout,result):
        for i in range(timeout, 0, -1):
            if result['finished']:
                break
            sys.stdout.write(f"\r{prompt} (default <{i}s> = \"{default_input}\") ")
            sys.stdout.flush()
            time.sleep(1)

    input_thread = threading.Thread(target=get_input, args=(result,))
    input_thread.daemon = True
    input_thread.start()

    countdown_thread = threading.Thread(target=show_countdown, args=(timeout,result,))
    countdown_thread.daemon = True
    countdown_thread.start()

    input_thread.join(timeout)

    # Stop the countdown when input is received or timeout occurs
    if countdown_thread.is_alive():
        countdown_thread.join(timeout=0.1)  # Just to ensure the thread is terminated

    return result["value"] if result["value"] is not None else default_input


def display_progress_bar(done,total):
    """
    Display progress bar in console.

    Args:
    - percentage (float): Progress percentage from 0 to 100.
    """

    # 定义进度条的宽度
    bar_width = 50
    blocks = int(done / total * bar_width)
    bar = '<' + '=' * blocks + ' ' * (bar_width - blocks) + '>'
    sys.stdout.write("\r" + bar + f" {done}/{total} | {(100*done/total):.2f}%")
    sys.stdout.flush()

if __name__ == "__main__":

    # print(get_top_domain("www.baidu.com"))
    # print(get_top_domain("a.b.c.co.uk"))

    # print(input_with_timeout("Please input something:", 5, "x"))
    # print("done")

    for i in range(101):
        time.sleep(0.05)
        display_progress_bar(i,100)
