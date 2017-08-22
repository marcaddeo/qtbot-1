#!/bin/env python

import aiohttp
import discord
from discord.ext import commands
from bs4 import BeautifulSoup
from utils import aiohttp_wrap as aw


class AskAsk:
    def __init__(self, bot):
        self.bot = bot
        self.aio_session = bot.aio_session
        self.scrape_uri = 'http://www.ask.com/web?q={}&o=0&qo=homepageSearchBox'

    def _get_ask_links(html):
        """ Gets all result links from [REDACTED] """
        soup = BeautifulSoup(html, 'lxml')

        link_list = []

        for link in soup.find_all('a', {'class': 'result-link'}, href=True):
            link_list.append(link['href'])

        if not link_list:
            return None

        # Filter some ask specific links
        # i.e. //www.ask.com/youtube?q=scroopy+noopers&v=CIAXKuxtTsc
        for link in link_list:
            print(link)
            if link.startswith('//'):
                print(f'Popped: {link}')
                link_list.pop(link_list.index(link))

        return link_list

    @commands.command(name='ask', aliases=['g'])
    async def ask_search(self, ctx, *, query):
        """ Get search results from [REDACTED], now that Google hates me. """

        # Handle no input
        if not query:
            return await ctx.send('Feel free to search something.')

        # Format query for search url
        search_query = query.replace(' ', '+')

        # Get response and store links
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
        resp_html = await aw.aio_get_text(self.aio_session, self.scrape_uri.format(search_query), headers=headers)

        link_list = AskAsk._get_ask_links(resp_html)

        if link_list is None:
            return await ctx.send("Sorry, I couldn't find anything for `{}.".format(query))

        await ctx.send('**Top result:**\n{}\n**See Also:**\n1. <{}>\n2. <{}>'.format(link_list[0], link_list[1], link_list[2]))


def setup(bot):
    bot.add_cog(AskAsk(bot))
