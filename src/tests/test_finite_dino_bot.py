#!/usr/bin/env python3
"""Unittests for finite_dino_bot.py"""

import unittest
from finite_dino_bot import FiniteDinoBot

class TestFiniteDinoBot(unittest.TestCase):
    """Unittests for finite_dino_bot."""

    def setUp(self):
        self.bot = FiniteDinoBot()

    @unittest.skip("TODO")
    def test_retrieve_definition(self):
        """finite_dino_bot.retrieve_definition should retrive the definition of
        the word passed into it."""
        pass

    @unittest.skip("TODO")
    def test_retrieve_definition_fail(self):
        """finite_dino_bot.retrieve_definition should return False if the
        requested word does not have a Wiktionary entry.
        """
        pass

    @unittest.skip("TODO")
    def test_format_definition_reply(self):
        """finite_dino_bot.post_definition should submit a post to Reddit in
        reply to parent comment."""
        pass

if __name__ == '__main__':
    unittest.main()
