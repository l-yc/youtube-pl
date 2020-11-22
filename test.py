import uyts
import pafy
import vlc
import time

query = input("Search query: ")
search = uyts.Search(query)

for idx, result in enumerate(search.results):
    print(idx, result)

idx = int(input("Select video: "))
video_url = "https://www.youtube.com/watch?v=" + search.results[idx].id
video = pafy.new(video_url)

for idx, stream in enumerate(video.streams):
    print(idx, stream)

idx = int(input("Select video: "))
stream = video.streams[idx]
print(stream.url)

instance = vlc.Instance()
player = instance.media_player_new()
media = instance.media_new(stream.url)
player.set_media(media)
player.play()

while True:
    print(player.get_time(), player.get_length())
    time.sleep(1)
