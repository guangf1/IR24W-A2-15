import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):

    urls = []
    final = []

    if resp.status == 200:
        try:

            soup = BeautifulSoup(resp.raw_response.content, "html.parser")

            for hyperlink in soup.find_all('a', href=True):

                link = hyperlink['href']

                absolute = urljoin(url, link)

                if absolute.endswith("/"):
                    absolute.rstrip("/")

                urls.append(absolute)

        except:
            pass
    else:
        pass

    for url in urls:
        parsed = urlparse(url)
        no_frag = f"{parsed.scheme}://{parsed.netloc}{parsed.path};{parsed.params}?{parsed.query}"
        final.append(no_frag)

    return final

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        domains = [".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu"]
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        elif not any(domain in parsed.hostname for domain in domains):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|txt|ppsx)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def second_check(URL, visited, threshold):

    if URL in visited:
        return False
    if len(visited) > 12000:
        return False

    parsed = urlparse(URL)

    if "calendar" in parsed.path:
        return False

    paths = parsed.path.split("/")

    if len(paths) < 3:
        return True

    part = paths[1] + paths[2]

    if part in threshold:
        threshold[part] += 1
    else:
        threshold[part] = 1

    if(threshold[part]) > 500:
        return False

    return True