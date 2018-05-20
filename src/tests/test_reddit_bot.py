#!/usr/bin/env python3
"""Unittests for finite_dino_bot.py"""

import unittest
import praw
import config
import reddit_bot

TEST_SUBREDDIT = 'FiniteDinoBot'

class TestRedditBot(unittest.TestCase):
    """Unittests for reddit_bot.RedditBot"""

    def setUp(self):
        self.reddit = praw.Reddit(config.SITE_NAME)

    def test_authenticate(self):
        """RedditBot.authenticate should instantiate self.reddit to
        praw.Reddit instance of FiniteDinoBot.

        """
        bot = reddit_bot.RedditBot(config.SITE_NAME)
        bot.authenticate()
        self.assertIsInstance(bot.reddit, type(self.reddit))
        self.assertEqual(bot.reddit.user.me(), config.SITE_NAME)

    def test_retrieve_comments(self):
        """RedditBot.retrieve_keyword_comments should yield comments
        containing the keyword trigger."""
        bot = reddit_bot.RedditBot(config.SITE_NAME)
        bot.reddit = self.reddit    # to avoid calling API multiple times
        bot.subreddits = TEST_SUBREDDIT
        bot.retrieval_limit = 10
        comments = bot.retrieve_comments()
        print("### RedditBot.retrieve_comments() ###")
        for index, comment in enumerate(comments):
            print("Result {}: {}".format(index+1, comment.body))
            self.assertIn(config.KEYWORD.lower(), comment['comment'].body.lower())

    @unittest.skip("TODO")
    def test_post_definition(self):
        """finite_dino_bot.post_definition should submit a post to Reddit in
        reply to parent comment."""
        pass

if __name__ == '__main__':
    unittest.main()
