import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
from pubmed_research.fetch_papers import fetch_papers, fetch_paper_details, save_to_csv

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch PubMed papers based on a query")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("-f", "--file", type=str, help="Output CSV filename", default="pubmed_results.csv")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    if args.debug:
        print(f"DEBUG: Query: {args.query}")
        print(f"DEBUG: Output File: {args.file}")

    pubmed_ids = fetch_papers(args.query)
    if args.debug:
        print(f"DEBUG: Found {len(pubmed_ids)} papers")

    details = fetch_paper_details(pubmed_ids)
    if args.debug:
        print(f"DEBUG: Processed {len(details)} papers")

    save_to_csv(details, args.file)
