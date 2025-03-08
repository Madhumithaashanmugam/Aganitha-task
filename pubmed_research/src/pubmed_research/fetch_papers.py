import argparse
import requests
from typing import List, Dict
import pandas as pd
import xml.etree.ElementTree as ET


def fetch_papers(query: str, max_results: int = 10) -> List[str]:
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results,
    }

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        raise Exception("Error fetching data from PubMed API")

    data = response.json()
    return data["esearchresult"]["idlist"]


def fetch_paper_details(pubmed_ids: List[str], debug: bool = False) -> List[Dict]:
    if not pubmed_ids:
        return []

    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pubmed_ids),
        "retmode": "xml",
    }

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        raise Exception("Error fetching paper details from PubMed API")

    root = ET.fromstring(response.text)

    results = []
    for article in root.findall(".//PubmedArticle"):
        pmid_element = article.find(".//PMID")
        pmid = pmid_element.text if pmid_element is not None else "N/A"

        title_element = article.find(".//ArticleTitle")
        title = title_element.text if title_element is not None else "N/A"

        pub_date_element = article.find(".//PubDate")
        pub_date = pub_date_element.text if pub_date_element is not None else "N/A"

        non_academic_authors = []
        company_affiliations = []
        corresponding_author_email = "N/A"

        for author in article.findall(".//Author"):
            last_name = author.find(".//LastName")
            fore_name = author.find(".//ForeName")
            name = f"{fore_name.text if fore_name is not None else ''} {last_name.text if last_name is not None else ''}".strip()

            affiliation_element = author.find(".//Affiliation")
            affiliation = affiliation_element.text if affiliation_element is not None else ""

            if any(word in affiliation.lower() for word in ["inc.", "ltd.", "pharma", "biotech", "corporation"]):
                non_academic_authors.append(name)
                company_affiliations.append(affiliation)

            email_element = author.find(".//ElectronicAddress")
            if email_element is not None:
                corresponding_author_email = email_element.text

        result = {
            "PubmedID": pmid,
            "Title": title,
            "Publication Date": pub_date,
            "Non-academic Authors": ", ".join(non_academic_authors) if non_academic_authors else "N/A",
            "Company Affiliations": ", ".join(company_affiliations) if company_affiliations else "N/A",
            "Corresponding Author Email": corresponding_author_email,
        }

        if debug:
            print(f"DEBUG: Processed paper: {result}")

        results.append(result)

    return results


def save_to_csv(data: List[Dict], filename: str):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Results saved to {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and filter PubMed research papers.")
    parser.add_argument("query", type=str, help="Search query for PubMed")
    parser.add_argument("-d", "--debug", action="store_true", help="Print debug information")
    parser.add_argument("-f", "--file", type=str, help="Specify the filename to save results (default: print to console)")

    args = parser.parse_args()

    pubmed_ids = fetch_papers(args.query)
    details = fetch_paper_details(pubmed_ids, debug=args.debug)

    if args.file:
        save_to_csv(details, args.file)
    else:
        print(details)
