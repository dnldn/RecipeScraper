import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


# Declare internal and external urls - internal will be the ones that are useful to us.
internal_urls = set()
external_urls = set()

# Verify that input url is valid so that process does not stall.
def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

# Parse input url to determine whether it is from the target website or an external link.
def get_all_website_links(url):
    urls = set()
    domain_name = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url).content, "html.parser")

    # Scanning all href tags in document.
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")

        # If href tag is empty, continue.
        if href == "" or href is None:
            continue

        # Join the url if it isn't an absolute link.
        href = urljoin(url, href)
        parsed_href = urlparse(href)

        # Clean URLs.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

        # Continue if URL is invalid.
        if not is_valid(href):
            continue

        # Continue if URL already exists in internal list. 
        # Note that operation will slow down as it goes along, because every crawl will result in a higher chance of redundancy.
        if href in internal_urls:
            continue

        # If domain name does not belong to target website, add to external url list.
        if domain_name not in href:
            if href not in external_urls:
                print(f"External link: {href}")
                external_urls.add(href)
            continue

        # Mark as new internal URL if all conditionals are passed.
        print(f"Internal link: {href}")
        urls.add(href)
        internal_urls.add(href)
    return urls

# Declare global counter for urls visited.
total_urls_visited = 0

# Declare maximum crawl depth. Higher numbers increase the odds of being blocked/timing out.
crawl_depth = 10

# Crawl targeted website. max_urls limits how long the crawl persists for - longer crawls may cause a timeout or blocking.
def crawl(url, max_urls=crawl_depth):

    # Iterating global counter of urls visited.
    global total_urls_visited
    total_urls_visited += 1

    # Print the URL that's currently being crawled.
    print(f"Crawling: {url}")

    # Get links, and run operation recursively until maximum url number is reached.
    links = get_all_website_links(url)
    for link in links:
        if total_urls_visited > max_urls:
            break
        crawl(link, max_urls=max_urls)

"""
Main operation. This operation needs to be run several times to get a large list of valid recipe URLs - it will time out after some time, and it is more time-efficient for this
operation to let it time out and run again than it is to implement a sleep timer and delay the crawl function. This is because the crawl function should start at the home
page of the recipe website to grab as many initial links to random recipes as possible- as opposed to starting on a recipe that will continously link back to 
recipes which have already been searched.

Because of this, the easiest way to grab the URLS after the operation is run is to just grab all lines from standard output that contain "Internal link: (url), and run a diff
against the existing list. Once a list of URLs is captured, it can be added to the "sites = []" array in the filter function.
"""

if __name__ == "__main__":

    # Perform crawl. This has been optimized for seriouseats.com, but it should work on any site that contains recipes and links to other recipes on those pages.
    crawl("https://www.seriouseats.com")

    # Print crawl statistics. Internal links are from the website, external urls link out.
    print("Total internal links:", len(internal_urls))
    print("Total external links:", len(external_urls))
    print("Total URLS:", len(internal_urls) + len(external_urls))
    print("Total crawled URLS:", max_urls)
