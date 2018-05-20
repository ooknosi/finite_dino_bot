#!/usr/bin/env python3
"""Reddit Bot Common Routines

Contains common Reddit bot functions such as keyword comment retrieval,
processed comment caching, and comment posting.

Allows bot authors to concentrate on writing their custom bot functions.

"""

from collections import deque
from os import mkdir
import re
import signal
import sys
from time import sleep
import praw
from config import (
    CACHE_FILE,
    CACHE_SIZE,
    KEYWORD,
    RETRIEVAL_LIMIT,
    SITE_NAME,
    SUBREDDITS,
    )

class RedditBot:
    """Superclass for Reddit bots which adds common bot routines.

    Parameters
    ----------
    site_name : str, optional
        Initializes praw under site_name within praw.ini.
        Defaults to config.SITE_NAME.
        See: https://praw.readthedocs.io/en/latest/getting_started
             /configuration/prawini.html#choosing-a-site
    keyword : str, optional
        Comment trigger word.
        Defaults to config.KEYWORD.
    retrieval_limit : int, optional
        Maximum number of comments to retrieve at a time.
        Defaults to config.RETRIEVAL_LIMIT.
        See: https://praw.readthedocs.io/en/latest/code_overview/models
             /subreddit.html#praw.models.Subreddit.comments
    subreddits : str, optional
        Subreddits to retrieve comments from.
        Defaults to config.SUBREDDITS.
        See: https://praw.readthedocs.io/en/latest/code_overview/models
             /subreddit.html#subreddit

    """

    def __init__(self,
                 site_name=SITE_NAME,
                 keyword=KEYWORD,
                 retrieval_limit=RETRIEVAL_LIMIT,
                 subreddits=SUBREDDITS,
                ):
        print("Initializing bot...")
        self.keyword = re.compile(keyword+r' ([ \w]+)', re.I)
        self.reddit = None
        self.retrieval_limit = retrieval_limit
        self.site_name = site_name
        self.subreddits = subreddits
        self.username = site_name
        self.processed_comments = self.read_cache(CACHE_FILE)
        signal.signal(signal.SIGINT, self.bot_exit)

    def authenticate(self, max_attempts=-1, seconds_between_attempts=60):
        """Authenticates SITE_NAME with Reddit.
        Sets self.reddit and self.username on success.

        Parameters
        ----------
        max_attempts : int, optional
            Maximum number of authentication attempts before failure.
            Defaults to -1 (infinite attempts).
        seconds_between_attempts : int, optional
            Seconds to wait between authentication attempts.
            Defaults to 60.

        """
        attempt = 0
        while attempt != max_attempts:
            try:
                print("Authenticating as {}...".format(self.site_name))
                self.reddit = praw.Reddit(self.site_name)
                self.username = self.reddit.user.me()
                print("Successfully authenticated as {}".format(self.username))
                return
            except praw.exceptions.APIException as error:
                print("Unable to authenticate:", error)
                print("Retrying in {} "
                      "seconds".format(seconds_between_attempts))
                sleep(seconds_between_attempts)
                attempt += 1
        raise RuntimeError('Failed to authenticate after {} '
                           'attempts'.format(max_attempts))


    def retrieve_comments(self):
        """Retrieves comments from subreddits, filters for keyword trigger, and
        excludes processed comments.

        Returns
        -------
        generator
            Dict of reddit.Comment and query.

        """
        try:
            print("Retrieving {} comments...".format(self.retrieval_limit))
            comments = self.reddit.subreddit(self.subreddits).comments(
                limit=self.retrieval_limit
                )
            for comment in comments:
                if (comment.author != self.username
                        and comment not in self.processed_comments
                        #and not self.has_already_replied(comment)
                        #and not self.is_summon_chain(comment)
                   ):
                    query = self.keyword.search(comment.body.lower())
                    if query:
                        self.processed_comments.append(comment.id)
                        yield {'comment': comment, 'query' : query.group(1)}
        except praw.exceptions.APIException as error:
            print("API Error:", error)
            raise
        except AttributeError as error:
            print(error)
            print("Unable to retrieve comments.")
            raise


    def submit_comment(self, target, comment):
        """Submit comment to target submission or comment.

        Parameters
        ----------
        target : reddit.submission object or reddit.comment object
            Target Reddit submission or comment.
        comment : str
            Comment to post.

        Returns
        -------
        object
            reddit.comment of newly created comment.

        """
        try:
            if target.author != self.username:
                print("Posting reply...")
                return target.reply(comment)
        except praw.exceptions.APIException as error:
            print("API Error:", error)
            raise

    @staticmethod
    def read_cache(file):
        """Opens and reads file, converting contents to \n separated list.
        Creates cache file if does not exist.

        Parameters
        ----------
        file : str
            Location of cache file.

        Returns
        -------
        collections.deque
            Contents of cache file, limited to config.CACHE_SIZE

        """
        try:
            print("Loading cache file into memory...")
            with open(file, 'r') as data:
                cache = data.read()
            mem_cache = deque(cache.split('\n'), CACHE_SIZE)
            print("Cache loaded.")
        except FileNotFoundError:
            print("Cache file not found.")
            print("Creating cache directory...")
            try:
                path = ''
                for subdirectory in file.split('/')[:-1]:
                    path += subdirectory + '/'
                    mkdir(path)
                print("Cache directory created.")
            except IOError as error:
                print(error)
                print("Unable to create cache file")
            mem_cache = deque([], CACHE_SIZE)
        return mem_cache

    @staticmethod
    def write_cache(file, mem_cache):
        """Writes list into file, converting list to \n separated contents.
        Overwrites original cache file.
        Creates cache file if does not exist.

        Parameters
        ----------
        file : str
            Location of cache file.
        mem_cache : list or deque
            Items in memory cache

        """
        try:
            print("Saving memory into cache file...")
            with open(file, 'w') as cache_file:
                try:
                    cache_file.write(mem_cache.popleft())
                    for entry in mem_cache:
                        cache_file.write('\n'+entry)
                    # avoid adding \n to end of file so that we don't get empty
                    # entries in deque when next loaded
                    print("Cache saved")
                except IndexError:
                    print("No items in cache")
        except IOError as error:
            print(error)
            print("Unable to create cache file")

    def bot_exit(self, *args, **kwargs):
        """Saves self.processed_comments into cache file before exiting."""
        # pylint: disable=unused-argument
        print("\nStopping bot...")
        self.write_cache(CACHE_FILE, self.processed_comments)
        print("Bot stopped")
        sys.exit()

    def is_summon_chain(self, target):
        """Checks if parent comment of target is from self.
        Used to prevent infinite reply loop caused by another bot.

        Parameters
        ----------
        target : reddit.comment object
            Target Reddit comment.

        Returns
        -------
        bool
            True if parent comment of target is from bot. False otherwise.

        """
        return True if (
            not target.is_root and target.parent().author == self.username
            ) else False

    def has_already_replied(self, target):
        """Checks if target comment has already been replied by bot.
        Used to prevent multiple replies to the same request.

        Parameters
        ----------
        target : reddit.comment object
            Target Reddit comment.

        Returns
        -------
        bool
            True if parent comment of target is from bot. False otherwise.

        """
        try:
            # implement replace_more()?
            target.refresh()
            for reply in target.replies.list():
                if reply.author == self.username:
                    print("Comment already processed.")
                    return True
            print("Processing comment...")
            return False
        except praw.exceptions.APIException as error:
            print("API Error:", error)
            # Failsafe
            return True
