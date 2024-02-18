from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time

import nltk
from nltk.corpus import stopwords


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier

        self.visited = set()        #check for URL pattern and answer Q1
        self.threshold = dict()     #detect repeated URL/trap
        self.commonWords = dict()   #answer Q3
        self.subdomains = dict()    #answer Q4
        self.longest = dict()      #answer Q2
        self.count = 0

        nltk.download('stopwords')
        self.stop_words = set(stopwords.words('english'))

        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                scraper.FinalPrint(self.count, self.visited, self.commonWords, self.subdomains, self.longest)   #
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp)
            scraper.update(tbd_url, resp, self.commonWords, self.subdomains, self.longest, self.stop_words)    #
            for scraped_url in scraped_urls:
                if scraper.second_check(scraped_url, self.visited, self.threshold): #
                    self.frontier.add_url(scraped_url)
                    self.visited.add(scraped_url)   #
            self.count += 1
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
