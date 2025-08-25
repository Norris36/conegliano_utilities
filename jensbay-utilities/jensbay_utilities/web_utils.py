import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm


def find_all_links(start_url: str, max_links: int = 1000) -> set:
    """
    Finds all links on a given URL and recursively explores linked pages.

    Args:
        start_url (str): The starting URL to begin the search.
        max_links (int): The maximum number of links to find.

    Returns:
        set: A set of all unique links found.
    """
    visited_links = set()
    links_to_visit = [start_url]
    total_links = 0
    last_found_link = ""

    with tqdm(total=max_links, unit='links', desc='Crawling Links') as pbar:
        while links_to_visit and total_links < max_links:
            current_url = links_to_visit.pop(0)
            
            if current_url not in visited_links:
                visited_links.add(current_url)
                total_links += 1
                pbar.update(1)

                try:
                    response = requests.get(current_url, timeout=10)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.content, 'html.parser')
                    new_links = [
                        urljoin(current_url, link.get('href')) 
                        for link in soup.find_all('a', href=True)
                    ]

                    for link in new_links:
                        # Extract the main domain from the URL
                        try:
                            main_stem = link.split('/')[2]  # Get domain
                        except (IndexError, AttributeError):
                            main_stem = 'unknown'
                            
                        # Add new links to visit if they haven't been processed
                        if (link not in visited_links and 
                            link not in links_to_visit and 
                            'webdam' not in link.lower()):
                            links_to_visit.append(link)
                            last_found_link = main_stem

                except requests.exceptions.RequestException as e:
                    print(f"Error accessing {current_url}: {e}")
                except Exception as e:
                    print(f"Unexpected error with {current_url}: {e}")
                        
            pbar.set_description(f"Last Link Found: {last_found_link}")

    return visited_links