from publicsuffixlist import PublicSuffixList
import matplotlib.pyplot as plt
import requests
import json

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

if __name__ == "__main__":

    print(get_top_domain("www.baidu.com"))
    print(get_top_domain("a.b.c.co.uk"))
