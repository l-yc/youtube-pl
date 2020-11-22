#!/usr/bin/python3

import uyts
import pafy
import vlc
import time

import curses

class UI:
    def __init__(self, stdscr):
        if stdscr is not None:
            self.stdscr = stdscr
        self.quit = False

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

    def input(self, r, c, prompt_string):
        curses.echo()
        self.stdscr.addstr(r, c, prompt_string)
        self.stdscr.refresh()
        val = self.stdscr.getstr(r + 1, c, 20)
        curses.noecho()
        return val

    def format_result(self, idx, result):
        return "{:2}: {} [{}]".format(idx,
                                      result.title,
                                      result.duration if result.resultType == "video" else result.resultType)

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

    def play(self, video, index=None, playlist=None):
        ## -- stream --
        #self.stdscr.clear()
        #self.stdscr.border(0)
        #self.stdscr.addstr(5, 5, "Video: " + video.title, curses.A_BOLD)
        #for idx, stream in enumerate(video.streams):
        #    self.stdscr.addstr(7+idx, 5, self.format_stream(idx, stream), curses.A_NORMAL)

        #idx = int(self.input(curses.LINES-5, 5, "Select stream:"))
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

        curses.halfdelay(10)    # blocks for 1s
        while player.get_state() != vlc.State.Ended:
            self.stdscr.clear()
            self.stdscr.addstr(5, 5, "Playing:", curses.A_BOLD)
            self.stdscr.addstr(6, 5, video.title, curses.A_NORMAL)
            self.stdscr.addstr(7, 5, self.progress(player), curses.A_NORMAL)
            if playlist is not None:
                for idx, p in enumerate(playlist['items']):
                    if idx == 8:
                        break
                    self.stdscr.addstr(9+idx, 5, p['pafy'].title, (curses.A_BOLD if index == idx else curses.A_NORMAL))
            self.stdscr.refresh()

            try:
                ch = self.stdscr.getch()
                if ch == ord('q'):
                    break
                elif ch == ord(' '):
                    if player.get_state() != vlc.State.Paused:
                        player.pause()
                    else:
                        player.play()
            except:
                pass

        player.stop()

    def main(self):
        self.stdscr.clear()

        # -- search --
        self.stdscr.border(0)
        self.stdscr.addstr(5, 5, "Welcome to youtube-pl!", curses.A_BOLD)
        query = self.input(curses.LINES-5, 5, "Search:")
        if query == b"q":
            self.quit = True
            return
        search = uyts.Search(query)

        # -- video --
        self.stdscr.clear()
        self.stdscr.border(0)
        self.stdscr.addstr(5, 5, b"Search: " + query, curses.A_BOLD)
        for idx, result in enumerate(search.results):
            self.stdscr.addstr(7+idx, 5, self.format_result(idx, result), curses.A_NORMAL)

        idx = int(self.input(curses.LINES-5, 5, "Select video:"))
        if search.results[idx].resultType == 'video':
            url = "https://www.youtube.com/watch?v=" + search.results[idx].id
            video = pafy.new(url)
            self.play(video)
        elif search.results[idx].resultType == 'playlist':
            url = "https://www.youtube.com/playlist?list=" + search.results[idx].id
            playlist = pafy.get_playlist(url)
            for idx, p in enumerate(playlist['items']):
                self.play(p['pafy'], index=idx, playlist=playlist)

    def run(self):
        self.setup()
        while not self.quit:
            self.main()
        self.cleanup()

if __name__ == "__main__":
    ui = curses.wrapper(UI)
    ui.run()
