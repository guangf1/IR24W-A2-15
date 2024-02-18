import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from itertools import islice


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
        no_frag = f"{parsed.scheme}://{parsed.hostname}{parsed.path};{parsed.params}?{parsed.query}"
        final.append(no_frag)

    return final

def is_valid(url):
    try:
        domains = ["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]
        parsed = urlparse(url)
        response = requests.head(url)
        content = response.headers.get("Content-Length")
        if parsed.scheme not in set(["http", "https"]):
            return False
        elif not any(domain in parsed.hostname for domain in domains):
            return False
        elif re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|txt|ppsx)$", parsed.path.lower()) :
            return False
        elif re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|txt|ppsx)$", parsed.query.lower()) :
            return False
        elif content == None or content > 1048576 or content < 500:
            return False
        elif response.status_code != 200:
            return False
        else:
            return True

    except TypeError:
        print ("TypeError for ", parsed)
        raise
    except:
        return False

def second_check(URL, visited, threshold):

    try:
        if URL in visited:
            return False
        if len(visited) > 10000:
            return False

        parsed = urlparse(URL)

        if "calendar" in parsed.path:
            return False

        paths = parsed.path.split("/")

        if len(paths) < 3:
            return True

        part = paths[1] + paths[2]

        if paths[1] in threshold:
            threshold[paths[1]] += 1
        else:
            threshold[paths[1]] = 1
        
        if threshold[paths[1]] > 500:
            return False

        if part in threshold:
            threshold[part] += 1
        else:
            threshold[part] = 1

        if threshold[part] > 100:
            return False

        return True

    except:
        return False



def update(url, resp, common, subdomain, longest, stopwords):

    if(resp.status == 200):
        try:

            soup = BeautifulSoup(resp.raw_response.content, "html.parser")

            content = soup.get_text(separator = ' ', strip=True).lower()
            line_tokens = re.findall(r'[a-zA-Z0-9]+', content, re.ASCII)
            longest[url] = len(line_tokens)     #Question 2

            for word in line_tokens:    #Question3
                if word not in stopwords:
                    if word not in common:
                        common[word] = 1
                    else:
                        common[word] += 1

            parsed = urlparse(url)
            if("ics.uci.edu" in parsed.hostname):   #Question4
                part = parsed.hostname.split(".")
                if part[0] != "ics":
                    if parsed.scheme+"://"+parsed.hostname not in subdomain:
                        subdomain[parsed.scheme+"://"+parsed.hostname] = 1
                    else:
                        subdomain[parsed.scheme+"://"+parsed.hostname] += 1



        except:
            pass
    else:
        pass


def FinalPrint(count, visited, common, subdomain, longest):
    try:
        print(count)
        print(len(visited))
        print("\n")

        sorted_longest = dict(sorted(longest.items(), key = lambda x: (-x[1], x[0])))
        print(sorted_longest[0])
        print("\n")

        sorted_common = dict(sorted(common.items(), key = lambda x: (-x[1], x[0])))
        for key, value in islice(sorted_common.items(), 50):
            print(f'{key}: {value}')
        print("\n")

        sorted_sub = dict(sorted(subdomain.items(), key = lambda x: (-x[1], x[0])))
        for key, value in sorted_sub.items():
            print(f'{key}: {value}')
    except:
        pass