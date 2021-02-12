import uyts
from youtube_dl import YoutubeDL



class Scraper:
    """ Wrapper around scraper backends """
    def __init__(self):
        self.ydl = YoutubeDL()
        self.ydl.add_default_info_extractors()
        pass

    def search(self, query):
        results = uyts.Search(query)
        return results

    def get_info(self, url):
        info = self.ydl.extract_info(url, download=False)
        return info
