[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)

# youtube-pl

A terminal based client for youtube

## Dependencies
* youtube-dl
* unlimited-youtube-search
* python-vlc
* pypresence
`pip install youtube-dl unlimited-youtube-search python-vlc pypresence`

## Running
```sh
pip install -r requirements.txt
python main.py
```

## TODOs
- [ ] Add jumping in playlists
- [ ] Add config file
- [x] Show video optionally
- [x] Add discord rich presence
- [ ] Upgrade to discord game activity
- [ ] Add play queue
- [ ] Abstract playback into a player class
- [ ] Ensure scenes are purely UI glues
- [ ] Universal command line
- [x] Add repeating

## User Guide

##### Search screen

enter query to search
enter `q` to quit

##### Media selection screen

enter `pa <number of video>` to play both audio only
enter `pv <number of video>` to play both audio and video

##### Media playback screen

Hotkeys:
* `q`: quit to search screen
* `n`: next song
* `N`: previous song
* `r`: next repeat mode (in order: NONE, ALL, ONE)
* `R`: previous repeat mode
* `[`: scroll to previous page of playlist
* `]`: scroll to next page of playlist
* `-`: decrease volume by 5%
* `+`: increase volume by 5%
