import sys
import matplotlib as mpl
import matplotlib
import numpy as np
import time
import threading
from publicsuffixlist import PublicSuffixList
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.font_manager as fm
import requests
import json
import os
import pyimgur


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


def save_plot_to_imgur(fig, client_id):

    temp_file = "temp_plot.png"
    fig.savefig(temp_file)

    im = pyimgur.Imgur(client_id)
    uploaded_image = im.upload_image(temp_file)
    os.remove(temp_file)

    return uploaded_image.link


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

    return len("\r" + bar + f" {done}/{total} | {(100*done/total):.2f}%")


def generate_heatmap(author, heatmap_data, start_year, curr_year, tracing_year_span, show=False):

    font_path = 'resources/fonts/Overpass-Medium.ttf'
    fm.fontManager.addfont(font_path)

    # import sys
    # import numpy
    # numpy.set_printoptions(threshold=sys.maxsize)
    # print(heatmap_data)

    def mask_lower_tri(heatmap_data):
        heatmap_data = np.fliplr(heatmap_data)
        rows, cols = np.tril_indices(heatmap_data.shape[0], k=-1)
        heatmap_data[rows, cols] = -1
        return np.fliplr(heatmap_data)

    # heatmap_data = mask_lower_tri(np.log1p(heatmap_data+1))
    heatmap_data = mask_lower_tri(heatmap_data)

    cmap = plt.colormaps['plasma']
    cmap.set_under(color='white')

    fig, ax = plt.subplots(figsize=(7, tracing_year_span*0.2), dpi=100)
    ax.imshow(heatmap_data[:tracing_year_span, :],
              cmap=cmap, aspect='auto', vmin=0)

    max_val, min_val = np.max(heatmap_data[:tracing_year_span, :]), np.min(
        heatmap_data[:tracing_year_span, :])

    ax.set_xticks(np.arange(curr_year-start_year+1, step=2),
                  labels=np.arange(start_year, curr_year+1, step=2), fontsize=8)
    ax.set_yticks(np.arange(tracing_year_span),
                  labels=np.arange(tracing_year_span), fontsize=8)
    ax.tick_params(axis=u'both', which=u'both', length=3, color='w')
    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)

    for i in np.arange(start_year, curr_year+1):
        for j in np.arange(tracing_year_span):

            data = int(heatmap_data[j, i-start_year])
            if data > 0:
                text = ax.text(i-start_year, j, data, ha="center", va="center",
                               color="k" if (data-min_val)/max_val > 0.8 else "w", fontsize=10-len(str(data)), )

    title_text = ax.set_title(
        f"Research Heatmap of {author['name']}   ", loc='right', y=0, pad=10)
    title_text.set_fontname('Overpass')
    fig.tight_layout()

    if show:
        plt.show()

    return fig

def clear_last_line(last_length):
    print('\r' + ' ' * last_length + '\r', end='')
    print(' ' * last_length*2, end='')
    print('\r' + ' ' * last_length*2 + '\r', end='')

import string
def remove_symbols(text):
    # 创建一个包含所有标点符号的字符串
    symbols = string.punctuation

    # 使用str.translate()方法将标点符号和空格替换为空字符
    translation_table = str.maketrans('', '', symbols)
    cleaned_text = text.translate(translation_table)

    return cleaned_text

if __name__ == "__main__":

    # print(get_top_domain("www.baidu.com"))
    # print(get_top_domain("a.b.c.co.uk"))

    # print(input_with_timeout("Please input something:", 5, "x"))
    # print("done")

    # for i in range(101):
    #     time.sleep(0.05)
    #     display_progress_bar(i,100)\

    from config import IMGUR_CLIENT_ID

    heatmap = np.array([[6.0000e+00,  1.6000e+01,  0.0000e+00,  3.0000e+00,  2.2000e+01,  0.0000e+00,
                         0.0000e+00,  1.2000e+01,  0.0000e+00,  3.0000e+00,  2.3000e+01,  2.5000e+01,
                         2.1000e+02,  8.4000e+01,  0.0000e+00,  4.8000e+01,  5.2000e+01,  8.1000e+01,
                         6.2000e+01,  1.2200e+02,  4.2000e+01,  4.4900e+02,  2.5200e+02,  1.1400e+02,
                         1.4300e+02,  0.0000e+00,  8.0000e+00,  5.6000e+01,  0.0000e+00,  0.0000e+00, ],
                        [2.0000e+01,  3.7000e+01,  0.0000e+00,  6.0000e+00,  2.5000e+01,  0.0000e+00,
                         0.0000e+00,  2.7000e+01,  0.0000e+00,  0.0000e+00,  3.7000e+01,  3.2000e+01,
                         2.6400e+02,  1.3500e+02,  0.0000e+00,  1.2500e+02,  1.2500e+02,  1.6800e+02,
                         1.1400e+02,  3.6900e+02,  2.0500e+02,  2.3200e+03,  8.8500e+02,  4.1700e+02,
                         3.8300e+02,  0.0000e+00,  2.3400e+02,  4.7800e+02,  0.0000e+00,  0.0000e+00, ],
                        [1.3000e+01,  5.3000e+01,  0.0000e+00,  5.0000e+00,  3.8000e+01,  0.0000e+00,
                         0.0000e+00,  2.1000e+01,  0.0000e+00,  7.0000e+00,  3.9000e+01,  3.4000e+01,
                         2.4800e+02,  2.0100e+02,  0.0000e+00,  1.8100e+02,  1.2300e+02,  2.5100e+02,
                         1.5200e+02,  7.4700e+02,  3.7000e+02,  5.2850e+03,  1.7220e+03,  7.3400e+02,
                         6.6600e+02,  0.0000e+00,  8.5000e+02,  6.1300e+02,  0.0000e+00,  0.0000e+00, ],
                        [7.0000e+00,  4.9000e+01,  0.0000e+00,  9.0000e+00,  3.5000e+01,  0.0000e+00,
                         0.0000e+00,  2.9000e+01,  0.0000e+00,  1.9000e+01,  4.6000e+01,  4.5000e+01,
                         2.9800e+02,  2.9000e+02,  0.0000e+00,  2.3400e+02,  2.0200e+02,  3.6000e+02,
                         1.9200e+02,  1.1240e+03,  5.2300e+02,  8.7490e+03,  2.2640e+03,  9.3800e+02,
                         9.2900e+02,  0.0000e+00,  7.0600e+02,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [1.1000e+01,  4.1000e+01,  0.0000e+00,  7.0000e+00,  5.3000e+01,  0.0000e+00,
                         0.0000e+00,  3.8000e+01,  0.0000e+00,  1.5000e+01,  5.8000e+01,  6.5000e+01,
                         3.7800e+02,  2.8300e+02,  0.0000e+00,  2.7400e+02,  2.7400e+02,  4.9100e+02,
                         2.7300e+02,  1.3570e+03,  7.9000e+02,  1.2028e+04,  2.4160e+03,  1.0620e+03,
                         1.0320e+03,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [2.2000e+01,  3.1000e+01,  0.0000e+00,  9.0000e+00,  4.9000e+01,  0.0000e+00,
                         0.0000e+00,  4.0000e+01,  0.0000e+00,  2.0000e+01,  7.4000e+01,  6.5000e+01,
                         4.1000e+02,  3.2100e+02,  0.0000e+00,  3.4900e+02,  3.6300e+02,  7.6500e+02,
                         2.7700e+02,  1.6610e+03,  9.7200e+02,  1.4054e+04,  2.2420e+03,  1.1270e+03,
                         7.1700e+02,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [1.1000e+01,  4.7000e+01,  0.0000e+00,  1.2000e+01,  5.1000e+01,  0.0000e+00,
                         0.0000e+00,  4.9000e+01,  0.0000e+00,  2.1000e+01,  6.3000e+01,  7.9000e+01,
                         4.1500e+02,  4.3500e+02,  0.0000e+00,  3.6200e+02,  4.5600e+02,  1.0240e+03,
                         2.7500e+02,  1.7670e+03,  1.0020e+03,  1.5565e+04,  2.1960e+03,  7.1500e+02,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [1.6000e+01,  3.7000e+01,  0.0000e+00,  9.0000e+00,  6.5000e+01,  0.0000e+00,
                         0.0000e+00,  5.6000e+01,  0.0000e+00,  2.4000e+01,  8.2000e+01,  6.7000e+01,
                         6.1900e+02,  5.6200e+02,  0.0000e+00,  4.4200e+02,  4.6900e+02,  1.3090e+03,
                         2.5500e+02,  1.9770e+03,  1.0510e+03,  1.5499e+04,  1.3420e+03,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [1.8000e+01,  5.3000e+01,  0.0000e+00,  1.5000e+01,  7.7000e+01,  0.0000e+00,
                         0.0000e+00,  4.3000e+01,  0.0000e+00,  3.0000e+01,  9.8000e+01,  9.6000e+01,
                         9.0900e+02,  7.6100e+02,  0.0000e+00,  5.2900e+02,  5.3000e+02,  1.5290e+03,
                         2.2300e+02,  2.0810e+03,  9.0500e+02,  1.0535e+04,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [2.4000e+01,  4.8000e+01,  0.0000e+00,  3.0000e+01,  5.7000e+01,  0.0000e+00,
                         0.0000e+00,  3.7000e+01,  0.0000e+00,  2.2000e+01,  1.2200e+02,  1.1100e+02,
                         1.7860e+03,  9.7800e+02,  0.0000e+00,  6.3800e+02,  4.6700e+02,  1.7320e+03,
                         2.0900e+02,  1.7670e+03,  5.2300e+02,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [2.0000e+01,  5.9000e+01,  0.0000e+00,  2.2000e+01,  4.5000e+01,  0.0000e+00,
                         0.0000e+00,  3.5000e+01,  0.0000e+00,  2.6000e+01,  1.5400e+02,  1.2000e+02,
                         2.9690e+03,  1.1620e+03,  0.0000e+00,  7.6800e+02,  4.5700e+02,  1.7750e+03,
                         1.5700e+02,  1.0140e+03,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [1.3000e+01,  7.5000e+01,  0.0000e+00,  8.0000e+00,  5.8000e+01,  0.0000e+00,
                         0.0000e+00,  5.5000e+01,  0.0000e+00,  4.4000e+01,  2.1100e+02,  1.6000e+02,
                         4.5060e+03,  1.5070e+03,  0.0000e+00,  9.6900e+02,  3.8300e+02,  1.7240e+03,
                         8.7000e+01,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [2.1000e+01,  7.6000e+01,  0.0000e+00,  1.5000e+01,  3.4000e+01,  0.0000e+00,
                         0.0000e+00,  6.4000e+01,  0.0000e+00,  5.1000e+01,  3.2000e+02,  1.5600e+02,
                         6.6930e+03,  1.6580e+03,  0.0000e+00,  1.2230e+03,  2.9000e+02,  1.0460e+03,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [3.3000e+01,  8.9000e+01,  0.0000e+00,  6.0000e+00,  3.9000e+01,  0.0000e+00,
                         0.0000e+00,  4.5000e+01,  0.0000e+00,  4.0000e+01,  4.8400e+02,  2.0100e+02,
                         8.4130e+03,  1.8410e+03,  0.0000e+00,  1.3210e+03,  1.4700e+02,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [2.8000e+01,  7.9000e+01,  0.0000e+00,  6.0000e+00,  5.5000e+01,  0.0000e+00,
                         0.0000e+00,  3.7000e+01,  0.0000e+00,  4.7000e+01,  8.0800e+02,  1.9300e+02,
                         9.4470e+03,  2.0230e+03,  0.0000e+00,  8.8400e+02,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [2.7000e+01,  7.5000e+01,  0.0000e+00,  1.4000e+01,  5.4000e+01,  0.0000e+00,
                         0.0000e+00,  4.1000e+01,  0.0000e+00,  4.4000e+01,  9.3600e+02,  1.9400e+02,
                         1.0116e+04,  1.9390e+03,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [2.8000e+01,  7.6000e+01,  0.0000e+00,  6.0000e+00,  7.1000e+01,  0.0000e+00,
                         0.0000e+00,  3.6000e+01,  0.0000e+00,  3.3000e+01,  1.0520e+03,  1.9000e+02,
                         1.0036e+04,  1.1680e+03,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [2.5000e+01,  7.5000e+01,  0.0000e+00,  1.0000e+01,  7.5000e+01,  0.0000e+00,
                         0.0000e+00,  4.0000e+01,  0.0000e+00,  2.5000e+01,  1.1380e+03,  1.8200e+02,
                         6.5190e+03,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [3.2000e+01,  7.7000e+01,  0.0000e+00,  2.0000e+01,  1.2100e+02,  0.0000e+00,
                         0.0000e+00,  5.2000e+01,  0.0000e+00,  2.8000e+01,  1.1390e+03,  9.1000e+01,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [2.5000e+01,  9.2000e+01,  0.0000e+00,  4.4000e+01,  1.2600e+02,  0.0000e+00,
                         0.0000e+00,  6.3000e+01,  0.0000e+00,  7.0000e+00,  7.4600e+02,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [3.7000e+01,  1.1000e+02,  0.0000e+00,  6.8000e+01,  1.5300e+02,  0.0000e+00,
                         0.0000e+00,  5.0000e+01,  0.0000e+00,  7.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [3.4000e+01,  1.1100e+02,  0.0000e+00,  7.2000e+01,  1.6800e+02,  0.0000e+00,
                         0.0000e+00,  6.3000e+01,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [4.7000e+01,  1.2100e+02,  0.0000e+00,  8.3000e+01,  1.3600e+02,  0.0000e+00,
                         0.0000e+00,  4.8000e+01,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [2.5000e+01,  1.2000e+02,  0.0000e+00,  6.5000e+01,  1.4000e+02,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [3.7000e+01,  1.2500e+02,  0.0000e+00,  7.1000e+01,  1.4300e+02,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [4.1000e+01,  1.0600e+02,  0.0000e+00,  7.8000e+01,  8.0000e+01,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [4.3000e+01,  1.2300e+02,  0.0000e+00,  5.5000e+01,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [4.8000e+01,  1.1400e+02,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [4.6000e+01,  5.9000e+01,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ],
                        [3.0000e+01,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,
                         0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00, ]])
    fig = generate_heatmap({"name": "Yann Lecun"},
                           np.array(heatmap), 1994, 2023, 30)
    save_plot_to_imgur(fig, IMGUR_CLIENT_ID)
