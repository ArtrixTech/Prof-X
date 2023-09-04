from scholarly import scholarly
import re

def get_authors_from_input(input_str):
    return [author.strip() for author in input_str.split(',')]

def choose_author(author_name):
    search_query = scholarly.search_author(author_name)
    authors = list(search_query)
    
    if len(authors) == 0:
        print(f"No results found for {author_name}.")
        return None
    if len(authors) == 1:
        return authors[0]
    
    print(f"Found multiple authors for {author_name}:")
    for idx, author in enumerate(authors):
        print(f"{idx + 1}. {author.name}, {author.affiliation}")
    
    choice = int(input("Please select the correct author by entering the number: ")) - 1
    return authors[choice]

def generate_markdown(author):

    author= scholarly.fill(author)

    print(author)

    # 基础信息部分
    markdown_data = f"# {author['name']}\n"
    markdown_data += "## 基础信息\n"
    markdown_data += f"- Name: {author['name']}\n"

    if 'url_picture' in author:
        markdown_data += f"![image]({author['url_picture']})\n"

    if 'affiliation' in author:
        markdown_data += f"- Affiliation: {author['affiliation']}\n"
    if 'interests' in author:
        markdown_data += f"- Research Interests: {', '.join(author['interests'])}\n"
    if 'email_domain' in author:
        markdown_data += f"- Email Domain: {author['email_domain']}\n"
    if 'scholar_id' in author:
        markdown_data += f"- Google Scholar Profile: [Link](https://scholar.google.com/citations?user={author['scholar_id']})\n"
    if 'homepage' in author:
        markdown_data += f"- Homepage: [Link]({author['homepage']})\n"
    if 'citedby' in author:
        markdown_data += f"- Cited by: {author['citedby']}\n"
    if 'hindex' in author:
        markdown_data += f"- h-index: {author['hindex']}\n"
    if 'i10index' in author:
        markdown_data += f"- i10-index: {author['i10index']}\n"

     # 著作信息部分
    if 'publications' in author:
        markdown_data += "\n## Publications\n"
        for publication in author['publications']:
            title = publication['bib'].get('title', 'Unknown Title')
            pub_year = publication['bib'].get('pub_year', 'Unknown Year')
            citation = publication['bib'].get('citation', 'Unknown Citation')
            num_citations = publication.get('num_citations', 0)
            citedby_url = publication.get('citedby_url', '#')

            markdown_data += f"- **{title}** ({pub_year})\n"
            markdown_data += f"  - Citation: {citation}\n"
            markdown_data += f"  - Number of Citations: [{num_citations}]({citedby_url})\n\n"


    return markdown_data


def save_to_md_file(author_name, content):
    filename = f"{author_name}.md"
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Saved to {filename}")

def main():
    input_str = input("Please enter the list of authors separated by commas: ")
    author_names = get_authors_from_input(input_str)
    
    for author_name in author_names:
        author = choose_author(author_name)
        if author:
            md_output = generate_markdown(author)
            save_to_md_file(author_name, md_output)

if __name__ == '__main__':
    main()