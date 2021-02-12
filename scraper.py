import uyts
from youtube_dl import YoutubeDL



class Scraper:
    """ Wrapper around scraper backends """
    def __init__(self):
        self.ydl = YoutubeDL()
        self.ydl.add_default_info_extractors()


    def search(self, query):
        results = uyts.Search(query)
        return results


    def get_info(self, url):
        info = self.ydl.extract_info(url, download=False)
        return info


    def get_video(self, vid):
        url = "https://www.youtube.com/watch?v=" + vid
        info = self.get_info(url)
        return Video(info)


    def get_playlist(self, pid):
        url = "https://www.youtube.com/playlist?list=" + pid
        info = self.get_info(url)
        return Playlist(info)



# of course, these should be more elaborate, but these are the only features
# that I need now
class Stream:
    def __init__(self, raw):
        self.raw = raw
        self.url = raw['url']



class Video:
    def __init__(self, raw):
        self.raw = raw
        self.title = raw['title']
        self.formats = raw['formats']


    def get_best_audio(self):
        """ Return the highest bitrate audio."""
        func = lambda x: x['vcodec'] == 'none'
        audio_only = list(filter(func, self.formats))
        audio_only.sort(reverse=True, key=lambda x: x['tbr'])
        return Stream(audio_only[0])
    

    def get_best(self):
        """ Return the highest bitrate audio + video."""
        func = lambda x: x['acodec'] != 'none' and x['vcodec'] != 'none'
        both = list(filter(func, self.formats))
        both.sort(reverse=True, key=lambda x: x['tbr'])
        return Stream(both[0])



class Playlist:
    def __init__(self, raw):
        self.raw = raw
        self.items = [Video(x) for x in raw['entries']]



