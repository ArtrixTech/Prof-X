from scholarly import scholarly
import re
import os
from utils import get_top_domain, save_plot_to_imgur, input_with_timeout
from translator import Translator
from config import TX_SECRET_ID, TX_SECRET_KEY
import openai_assisted
import json

failed_authors = []


def get_authors_from_input(input_str):
    return [author.strip() for author in input_str.split(',')]


def choose_author(author_name):
    search_query = scholarly.search_author(author_name)
    authors = list(search_query)
    global failed_authors

    if len(authors) == 0:
        print(f"No results found for {author_name}.")
        failed_authors.append((author_name, "Author Not Found"))
        return None
    if len(authors) == 1:
        return authors[0]

    print(f"Found multiple authors for {author_name}:")

    for idx, author in enumerate(authors):
        print(f"{idx + 1}. {author['name']}, {author['affiliation']}")

    print("(Input x to skip this author)")

    choice = input_with_timeout(
        "Please select the correct author by entering the number: ", 25, 'x')

    if choice == 'x' or choice == 'X':
        failed_authors.append((author_name, "User Skipped/Choose Timeout"))
        return None
    return authors[int(choice) - 1]


def generate_markdown(author):

    author = scholarly.fill(author)

    print("Author info fetched.")

    markdown_data = ""
    h_index = None

    if 'url_picture' in author:
        markdown_data += f"![image]({author['url_picture']})\n"
    if 'citedby' in author:
        markdown_data += f"- Cited by: {author['citedby']}\n"
    if 'hindex' in author:
        markdown_data += f"- h-index: {author['hindex']}\n"
        h_index = int(author['hindex'])
    if 'i10index' in author:
        markdown_data += f"- i10-index: {author['i10index']}\n"
    if 'affiliation' in author:
        markdown_data += f"- Affiliation: {author['affiliation']}\n"
    if 'interests' in author:
        markdown_data += f"- Research Interests: {', '.join(author['interests'])}\n"
    if 'email_domain' in author:
        markdown_data += f"- Email Domain: {author['email_domain']}\n"
    if 'scholar_id' in author:
        markdown_data += f"- Google Scholar Profile: https://scholar.google.com/citations?user={author['scholar_id']}\n"
    if 'homepage' in author:
        markdown_data += f"- Homepage: [Link]({author['homepage']})\n"

    # 著作信息部分
    if 'publications' in author:

        publicaions = author['publications']

        summary_section = ""

        publication_section = ""
        publication_ai_data_prep = ""
        publication_titles = []

        if h_index:
            publicaions = publicaions[:h_index]

        for publication in publicaions:
            title = publication['bib'].get('title', 'Unknown Title')
            pub_year = publication['bib'].get('pub_year', 'Unknown Year')
            citation = publication['bib'].get('citation', 'Unknown Citation')
            num_citations = publication.get('num_citations', 0)
            citedby_url = publication.get('citedby_url', '#')

            publication_ai_data_prep += f"{title},{pub_year},{num_citations}\n"

            publication_titles.append(title)

        def summary_ai():
            ai_summary, total_tokens = openai_assisted.publication_summarize(publication_ai_data_prep)
        
            if ai_summary:
                print(f"AI Summarized.")
                return ai_summary, total_tokens
            else:
                result=input_with_timeout("AI summarization failed for 3 times, still retry?(y/n): ", 10, 'n')
                if result=='y' or result=='Y':
                    return summary_ai()
                else:
                    return None, -1
                
        ai_summary, total_tokens = summary_ai()
        if ai_summary is None:
            failed_authors.append((author['name'], "AI Summarization Failed"))
            return None

        ai_summary = json.loads(ai_summary)

        for subject in ai_summary:
            summary_section += f"#### {subject['subject']}\n"
            for sub_area in subject['sub_areas']:
                summary_section += f"- **{sub_area['area']}**:\n"
                summary_section += f"  {sub_area['summary']}\n\n"

        tr = Translator(TX_SECRET_ID, TX_SECRET_KEY)
        translations = tr.batch_translate(publication_titles, "zh")
        print("Publication title translated.")

        for idx, publication in enumerate(publicaions):
            title = publication['bib'].get('title', 'Unknown Title')
            pub_year = publication['bib'].get('pub_year', 'Unknown Year')
            citation = publication['bib'].get('citation', 'Unknown Citation')
            num_citations = publication.get('num_citations', 0)
            citedby_url = publication.get('citedby_url', '#')

            publication_section += f"- **{title}** ({pub_year})\n"
            publication_section += f"  - {translations[idx]}\n"
            publication_section += f"  - Citation: {citation}\n"
            publication_section += f"  - Number of Citations: [{num_citations}]({citedby_url})\n\n"

    markdown_data += "\n## Research Summary\n"
    markdown_data += summary_section

    markdown_data += "\n## Publications\n"
    markdown_data += publication_section

    markdown_data += "\n## Raw Data\n"
    markdown_data += f"```json\n{json.dumps(author, indent=2)}\n```\n"

    return markdown_data


def save_to_md_file(author_info, domain, content):
    directory = f"saved/{domain}"
    os.makedirs(directory, exist_ok=True)

    h_index = author_info.get("hindex", "-1")

    filename = f"{directory}/[{h_index}]{author_info['name']}.md"

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Saved to {filename}")


def main():
    input_str = input("Please enter the list of authors separated by commas: ")
    author_names = get_authors_from_input(input_str)

    for author_name in author_names:
        print(f"Processing {author_name}:")
        author = choose_author(author_name)

        if author:
            print(f"Authour found, fetching more info...")
            md_output = generate_markdown(author)
            mail_raw = author.get('email_domain', '@no_data.com')
            if '@' in mail_raw:
                save_to_md_file(author, get_top_domain(
                    mail_raw).removeprefix('@'), md_output)
            else:
                save_to_md_file(author, 'unclassified', md_output)


if __name__ == '__main__':
    main()
