#!/usr/bin/env python3
"""FiniteDinoBot v0.1.0

Reddit bot that responds to '!define <word>' requests and replies with the
Wiktionary definition of the word.

"""

from functools import lru_cache
import re
from time import sleep
import urllib
from bs4 import BeautifulSoup
from praw.exceptions import APIException
from reddit_bot import RedditBot
from config import FOOTER

class FiniteDinoBot(RedditBot):
    """FiniteDinoBot"""

    DEFINE_URL = 'https://en.wiktionary.org/wiki/'
    BOLD = re.compile(r'<\/?(b|strong)[^>]*>', re.I|re.M)
    ITALICS = re.compile(r'<\/?(i|em)[^>]*>', re.I|re.M)
    CITATIONS = re.compile(r'(&#91;|\[)[\s\S]*?(&#93;|\])', re.M)
    EXAMPLES = re.compile(r'<ul>[\s\S]*?</ul>', re.I|re.M)
    HTML_TAGS = re.compile(r'<\/?[^>]+>', re.I|re.M)

    def __init__(self):
        super().__init__()

    @staticmethod
    @lru_cache(maxsize=32)
    def retrieve_definition(query):
        """Retrieve and extract first set of word definitions.

        Returns
        -------
        dict
            defintion, query_url, word_class, word
        """
        print('Looking up "{}"...'.format(query))

        query_url = FiniteDinoBot.DEFINE_URL + query.replace(' ', '_')

        url_request = urllib.request.Request(
            query_url,
            headers={'User-Agent': (
                'Mozilla/5.0 (Linux x86_64)'
                )}
            )

        try:
            with urllib.request.urlopen(url_request) as response:
                html = response.read()
        except urllib.error.HTTPError as error:
            print(error)
            print("Query not found.")
            return None

        soup = BeautifulSoup(html, 'html.parser')

        try:
            raw_definition = soup.find(
                'span',
                attrs={'id': [
                    'Noun', 'Pronoun', 'Verb', 'Adjective', 'Adverb',
                    'Conjunction', 'Preposition', 'Interjection'
                    ]},
                )
            print("Definition found.")
            return {
                'definition': str(raw_definition.find_next('ol')),
                'query_url': query_url,
                'word_class': raw_definition.get_text(),
                'word': str(raw_definition.find_next('p')),
                }
        except AttributeError as error:
            print('Error: No valid definition detected.')
            return None

    @staticmethod
    def format_definition_reply(data):
        """Formats definiton into Reddit markup.

        Parameters
        ----------
        data : dict
            defintion, query_url, word_class, word

        Returns
        -------
        reply : str
            Word definition formatted into Reddit markup.

        """
        print('Formatting reply to query...')

        for key in ('word', 'word_class', 'definition'):
            data[key] = FiniteDinoBot.BOLD.sub('**', data[key])
            data[key] = FiniteDinoBot.ITALICS.sub('_', data[key])
        data['definition'] = FiniteDinoBot.EXAMPLES.sub('', data['definition'])
        data['definition'] = (
            data['definition'].replace('<li>', '1. ').replace('</li>', '\n')
            )
        data['definition'] = (
            data['definition'].replace('<dd>', '  ').replace('</dd>', '\n')
            )
        data['definition'] = FiniteDinoBot.CITATIONS.sub('', data['definition'])
        for key in ('word', 'word_class', 'definition'):
            data[key] = FiniteDinoBot.HTML_TAGS.sub('', data[key])

        reply = '#### {}\n'.format(data['word'])
        reply += '*{}*\n\n'.format(data['word_class'])
        reply += data['definition']
        reply += '\n[^*Wiktionary*]({})'.format(data['query_url'])
        reply += FOOTER
        return reply

def main():
    """Main bot routine"""
    bot = FiniteDinoBot()
    bot.authenticate()

    while True:
        try:
            comments = bot.retrieve_comments()
            for comment in comments:
                data = bot.retrieve_definition(comment['query'])
                if data:
                    reply = bot.format_definition_reply(data)
                    bot.submit_comment(comment['comment'], reply)
        except APIException:
            print("Rate limit exceeded. Pausing for 2 minutes.")
            sleep(120)
        sleep(1)

if __name__ == '__main__':
    main()
