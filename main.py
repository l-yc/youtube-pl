#!/usr/bin/python3

import uyts
import pafy
import vlc
import pypresence

import time
import curses
import enum

class Scraper:
    """ Wrapper around scraper backends """
    def __init__(self):
        pass

    def search(self, query):
        results = uyts.Search(query)
        return results



class Scene:
    def __init__(self, UI):
        self.ui = UI

    # TODO parse a user input
    def parse(self, s):
        pass

    """
    Executes scene logic
    EXPECTS= args: tuple
    RETURNS= status: string
    """
    def play(self, args):
        pass



class WelcomeScene(Scene):
    def play(self, args):
        self.ui.update_status(state="Searching for a song...")
        self.ui.stdscr.clear()
        # -- search --
        self.ui.stdscr.border(0)
        self.ui.stdscr.addstr(5, 5, "Welcome to youtube-pl!", curses.A_BOLD)
        query = self.ui.input(curses.LINES-5, 5, "Search:", 100)
        if query == b"q":
            return State.EXIT, ()
        search = self.ui.scraper.search(query)
        return State.SELECT_MEDIA, (query, search,)



class SelectMediaScene(Scene):
    def format_result(self, idx, result):
        return "{:2}: {} [{}]".format(idx,
                                      result.title,
                                      result.duration if result.resultType == "video" else result.resultType)
    def play(self, args):
        query = args[0]
        search = args[1]

        self.ui.update_status(state="Searching for a song...")
        self.ui.stdscr.clear()
        # -- video --
        self.ui.stdscr.border(0)
        self.ui.stdscr.addstr(5, 5, b"Search: " + query, curses.A_BOLD)
        for idx, result in enumerate(search.results):
            self.ui.stdscr.addstr(7+idx, 5, self.format_result(idx, result), curses.A_NORMAL)

        idx = int(self.ui.input(curses.LINES-5, 5, "Select video:", 5))
        media = search.results[idx] 
        return State.PLAY_MEDIA, (media,)



class PlayMediaScene(Scene):
    def __init__(self, ui):
        super().__init__(ui)
        self.playlist_show_count = 8

    def format_stream(self, idx, stream):
        return "{:2}: {} [{}]".format(idx, stream.mediatype, stream.quality)

    def format_time(self, t):
        t //= 1000
        mm = t//60
        ss = t%60
        return "{:02}:{:02}".format(mm,ss)

    def progress(self, player):
        return "{} / {} [{}]".format(self.format_time(player.get_time()), 
                                     self.format_time(player.get_length()),
                                     player.get_state())

    def draw_playlist(self, index, playlist):
        if playlist is None:
            return

        show = slice(self.playlist_idx, self.playlist_idx+self.playlist_show_count)

        display_str =  "Playlist [{}-{}] / {}:".format(
            self.playlist_idx+1,
            min(len(playlist['items']), self.playlist_idx+self.playlist_show_count),
            len(playlist['items'])
        )
        self.ui.stdscr.addstr(9, 5, display_str, curses.A_NORMAL)

        for idx, p in enumerate(playlist['items'][show]):
            font = (curses.A_BOLD if index == self.playlist_idx+idx else curses.A_NORMAL)
            self.ui.stdscr.addstr(10+idx, 5,
                                  p['pafy'].title,
                                  font)

    def playlist_turn_page(self, playlist, n):
        if playlist is None:
            return

        self.playlist_idx += n * self.playlist_show_count
        if self.playlist_idx < 0:
            self.playlist_idx = 0
        elif self.playlist_idx >= len(playlist['items']):
            self.playlist_idx = \
                (len(playlist['items'])-1) // self.playlist_show_count \
                * self.playlist_show_count

    def playVideo(self, video, index=None, playlist=None):
        ## -- stream --
        #self.ui.stdscr.clear()
        #self.ui.stdscr.border(0)
        #self.ui.stdscr.addstr(5, 5, "Video: " + video.title, curses.A_BOLD)
        #for idx, stream in enumerate(video.streams):
        #    self.ui.stdscr.addstr(7+idx, 5, self.format_stream(idx, stream), curses.A_NORMAL)

        #idx = int(self.ui.input(curses.LINES-5, 5, "Select stream:"))
        #stream = video.streams[idx]
        stream = video.getbest()

        #import os
        #os.environ['VLC_VERBOSE'] = '-2'
        instance = vlc.Instance("--vout=dummy")
        #with open("vlc.log", "w") as f:
        #    instance.log_set_file(f)
        instance.log_unset()
        player = instance.media_player_new()
        media = instance.media_new(stream.url)
        player.set_media(media)
        player.play()

        return_state = State.PLAY_MEDIA_NEXT    # default state if video finishes playing
        curses.halfdelay(10)    # blocks for 1s
        while player.get_state() != vlc.State.Ended:
            self.ui.update_status(state=video.title)
            self.ui.stdscr.clear()
            self.ui.stdscr.addstr(5, 5, "Playing:", curses.A_BOLD)
            self.ui.stdscr.addstr(6, 5, video.title, curses.A_NORMAL)
            self.ui.stdscr.addstr(7, 5, self.progress(player), curses.A_NORMAL)

            self.draw_playlist(index, playlist)

            self.ui.stdscr.refresh()

            try:
                ch = self.ui.stdscr.getch()
                if ch == ord('q'):
                    return_state = State.WELCOME
                    break
                elif ch == ord('N'):
                    return_state = State.PLAY_MEDIA_PREV
                    break
                elif ch == ord('n'):
                    return_state = State.PLAY_MEDIA_NEXT
                    break
                elif ch == ord('['):
                    self.playlist_turn_page(playlist, -1)
                elif ch == ord(']'):
                    self.playlist_turn_page(playlist, +1)
                elif ch == ord(' '):
                    if player.get_state() != vlc.State.Paused:
                        player.pause()
                    else:
                        player.play()
            except:
                pass

        player.stop()
        return return_state

    def play(self, args):
        self.playlist_idx = 0

        media = args[0]
        if media.resultType == 'video':
            url = "https://www.youtube.com/watch?v=" + media.id
            video = pafy.new(url)
            return_state = self.playVideo(video)
        elif media.resultType == 'playlist':
            url = "https://www.youtube.com/playlist?list=" + media.id
            playlist = pafy.get_playlist(url)
            items = playlist['items']

            idx = 0
            p = None
            while idx < len(items):
                p = items[idx]
                return_state = self.playVideo(p['pafy'], index=idx, playlist=playlist)
                if return_state == State.PLAY_MEDIA_PREV:
                    idx -= 1
                elif return_state == State.PLAY_MEDIA_NEXT:
                    idx += 1
                elif return_state == State.WELCOME:
                    break
                else:
                    raise "Unknown state in player!"

        if return_state is State.PLAY_MEDIA_NEXT:
            return_state = State.WELCOME

        return return_state, ()



@enum.unique
class State(enum.Enum):
    EXIT = enum.auto()
    WELCOME = enum.auto()
    SELECT_MEDIA = enum.auto()
    PLAY_MEDIA = enum.auto()
    PLAY_MEDIA_PREV = enum.auto()
    PLAY_MEDIA_NEXT = enum.auto()

class UI:
    def __init__(self, stdscr):
        if stdscr is not None:
            self.stdscr = stdscr
        self.quit = False

        self.scraper = Scraper()

        self.client_id = "780606362727874570"  # Put your Client ID in here
        self.RPC = None
        self.display_status = False

    def setup(self):
        if self.stdscr is None:
            self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

    def cleanup(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def input(self, r, c, prompt_string, n):
        curses.echo()
        self.stdscr.addstr(r, c, prompt_string)
        self.stdscr.refresh()
        val = self.stdscr.getstr(r + 1, c, n)
        curses.noecho()
        return val

    def update_status(self, state):
        if not self.display_status:
            return
        if self.RPC is None:
            try:
                self.RPC = pypresence.Presence(self.client_id)  # Initialize the Presence client
                self.RPC.connect() # Start the handshake loop
                self.RPC.update(state=state)
                self.update_time = time.time()
            except:
                self.RPC = None
        elif self.update_time + 15 < time.time():
            self.RPC.update(state=state)
            self.update_time = time.time()

    def main(self, scene_graph):
        self.stdscr.clear()

        state = State.WELCOME
        args = None
        while state != State.EXIT:
            scene = scene_graph[state]
            state, args = scene.play(args)

    def run(self, scene_graph):
        self.setup()
        self.main(scene_graph)
        self.cleanup()



if __name__ == "__main__":
    ui = curses.wrapper(UI)
    ui.run({
        State.EXIT: None,
        State.WELCOME: WelcomeScene(ui),
        State.SELECT_MEDIA: SelectMediaScene(ui),
        State.PLAY_MEDIA: PlayMediaScene(ui)
    })
