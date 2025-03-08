import argparse
from pubmed_research.fetch_papers import fetch_papers, fetch_paper_details, save_to_csv

if __name__ == "__main__":
   
    query = input("Enter your search query: ").strip()
    debug_mode = input("Enable debug mode? (yes/no): ").strip().lower() == "yes"
    file_name = input("Enter filename to save results (press Enter to display on screen): ").strip()

    if debug_mode:
        print(f"DEBUG: Query: {query}")
        if file_name:
            print(f"DEBUG: Output File: {file_name}")
        else:
            print(f"DEBUG: No file specified, displaying results on screen")

    try:
        pubmed_ids = fetch_papers(query)
        if debug_mode:
            print(f"DEBUG: Found {len(pubmed_ids)} papers: {pubmed_ids}")

        details = fetch_paper_details(pubmed_ids, debug=debug_mode)
        if debug_mode:
            print("DEBUG: Processed Papers:")
            for paper in details:
                print(paper) 

        if file_name:
            save_to_csv(details, file_name)
            print(f"Results saved to {file_name}")
        else:
            print("\nFetched Paper Details:")
            for paper in details:
                print(paper)  

    except Exception as e:
        print(f"Error occurred: {e}")
