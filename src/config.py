#!/usr/bin/env python3
"""RedditBot Configuration"""

#####################
### MAIN SETTINGS ###
#####################

### site_name from praw.ini; passed into praw.Reddit.
# See: https://praw.readthedocs.io/en/latest/getting_started
# /configuration/prawini.html#choosing-a-site
SITE_NAME = 'FiniteDinoBot'

### Comment keyword to trigger bot.
KEYWORD = '!define'

### Footer to attach to each bot post
FOOTER = r"""

---

^(Request a definition using `!define <word>`.)   
^^I ^^am ^^a ^^bot ^^made ^^by ^^[\/u/ooknosi](https://reddit.com/user/ooknosi). ^^Beep ^^boop. ^^See ^^my ^^[code](https://github.com/ooknosi/finite_dino_bot).
"""

#########################
### OPTIONAL SETTINGS ###
#########################

### Maximum number of comments to retrieve.
RETRIEVAL_LIMIT = 500

### Maximum number of entries in cache for detected keyword comments
CACHE_SIZE = 500

### Comment cache file location
CACHE_FILE = 'cache/processed_comments'

### subreddits to parse; passed into reddit instance.
# See: https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html
SUBREDDITS = 'all-suicidewatch-depression-anxiety'
