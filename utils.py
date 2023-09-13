import sys
import matplotlib as mpl
import matplotlib
import numpy as np
import time
import threading
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
    sys.stdout.write(
        f"\r{prompt} (default <{timeout}s> = \"{default_input}\") ")
    sys.stdout.flush()

    result = {"value": None, "finished": False}

    def get_input(result):
        result["value"] = sys.stdin.readline().rstrip()
        result["finished"] = True

    def show_countdown(timeout, result):
        for i in range(timeout, 0, -1):
            if result['finished']:
                break
            sys.stdout.write(
                f"\r{prompt} (default <{i}s> = \"{default_input}\") ")
            sys.stdout.flush()
            time.sleep(1)

    input_thread = threading.Thread(target=get_input, args=(result,))
    input_thread.daemon = True
    input_thread.start()

    countdown_thread = threading.Thread(
        target=show_countdown, args=(timeout, result,))
    countdown_thread.daemon = True
    countdown_thread.start()

    input_thread.join(timeout)

    # Stop the countdown when input is received or timeout occurs
    if countdown_thread.is_alive():
        # Just to ensure the thread is terminated
        countdown_thread.join(timeout=0.1)

        if result["value"] is None:
            print("")

    return result["value"] if result["value"] is not None else default_input


def display_progress_bar(done, total):
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


def generate_heatmap(author,heatmap_data, start_year, curr_year, tracing_year_span, max_year_span):

    fig, ax = plt.subplots()


    im = ax.imshow(heatmap_data[:tracing_year_span, :])
    print(np.arange(start_year, curr_year))
    ax.set_xticks(np.arange(curr_year-start_year+1,step=2), labels=np.arange(start_year, curr_year+1,step=2))
    ax.set_yticks(np.arange(tracing_year_span))
    # Show all ticks and label them with the respective list entries
   

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in np.arange(start_year, curr_year):
        for j in np.arange(tracing_year_span):
            text = ax.text(i, j, heatmap_data[j, i-start_year],
                           ha="center", va="center", color="w")

    ax.set_title(f"Research Heatmap of {author['name']}")
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":

    # print(get_top_domain("www.baidu.com"))
    # print(get_top_domain("a.b.c.co.uk"))

    # print(input_with_timeout("Please input something:", 5, "x"))
    # print("done")

    # for i in range(101):
    #     time.sleep(0.05)
    #     display_progress_bar(i,100)

    # vegetables = ["cucumber", "tomato", "lettuce", "asparagus",
    #           "potato", "wheat", "barley"]
    # farmers = ["Farmer Joe", "Upland Bros.", "Smith Gardening",
    #         "Agrifun", "Organiculture", "BioGoods Ltd.", "Cornylee Corp."]

    # harvest = np.array([[0.8, 2.4, 2.5, 3.9, 0.0, 4.0, 0.0],
    #                     [2.4, 0.0, 4.0, 1.0, 2.7, 0.0, 0.0],
    #                     [1.1, 2.4, 0.8, 4.3, 1.9, 4.4, 0.0],
    #                     [0.6, 0.0, 0.3, 0.0, 3.1, 0.0, 0.0],
    #                     [0.7, 1.7, 0.6, 2.6, 2.2, 6.2, 0.0],
    #                     [1.3, 1.2, 0.0, 0.0, 0.0, 3.2, 5.1],
    #                     [0.1, 2.0, 0.0, 1.4, 0.0, 1.9, 6.3]])


    # fig, ax = plt.subplots()
    # im = ax.imshow(harvest)

    # # Show all ticks and label them with the respective list entries
    # ax.set_xticks(np.arange(len(farmers)), labels=farmers)
    # ax.set_yticks(np.arange(len(vegetables)), labels=vegetables)

    # # Rotate the tick labels and set their alignment.
    # plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
    #         rotation_mode="anchor")

    # # Loop over data dimensions and create text annotations.
    # for i in range(len(vegetables)):
    #     for j in range(len(farmers)):
    #         text = ax.text(j, i, harvest[i, j],
    #                     ha="center", va="center", color="w")

    # ax.set_title("Harvest of local farmers (in tons/year)")
    # fig.tight_layout()
    # plt.show()

    heatmap =np.array( [[0,  1,  8, 11, 15, 13, 13,  9,  8, 10, 11, 10, 12,  7, 20,  7,  7, 13, 12, 15 ],
               [0,  0,  1,  8, 11, 15, 13, 13,  9,  8, 10, 11, 10, 12,  7, 20,  7,  7, 13, 12 ],
               [0,  0,  0,  1,  8, 11, 15, 13, 13,  9,  8, 10, 11, 10, 12,  7, 20,  7, 7, 13 ],
               [0,  0,  0,  0,  1,  8, 11, 15, 13, 13,  9,  8, 10, 11, 10, 12,  7, 20, 7,  7 ],
               [0,  0,  0,  0,  0,  1,  8, 11, 15, 13, 13,  9,  8, 10, 11, 10, 12,  7, 20,  7 ],
               [0,  0,  0,  0,  0,  0,  1,  9, 20, 35, 48, 61, 69, 69, 68, 64, 61, 60, 58, 70 ]])
    generate_heatmap(np.array(heatmap), 2004, 2023, 5, 10)
