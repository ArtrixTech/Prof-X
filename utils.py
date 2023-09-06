from publicsuffixlist import PublicSuffixList

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

if __name__ == "__main__":

    print(get_top_domain("www.baidu.com"))
    print(get_top_domain("a.b.c.co.uk"))
