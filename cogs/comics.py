import json
import random
import re
from datetime import datetime
from typing import Union, Tuple

import discord
from discord.ext import commands
from nltk.corpus import stopwords


class Comics:
    """A cog which allows you to fetch random / search for XKCD comics.

    Attributes
    ----------
    STOPWORDS : set
        A set of common stopwords which will be stripped from user input.

    COMICS : dict[str, dict]
        A full list of XKCD comics. Can be updated via :meth:`_update()`

    BLOB : dict[str, str]
        The keys are (for now) str representations of sets of the combined alt-text and safe-titles
        of any given comic. I will add transcriptions to this once I test its impact on performance
        since I think that will give better matches.

        The key is str(num) of the comic.

    Note
    ----
    The "BLOB" file was generated by running the alt-text and safe-titles through an equivalent of the
    process_text command below, which strips common words. The below command(s) test user searches
    based on the # of whole-word matches present in the keys of the blob file.
    """
    STOPWORDS = set(stopwords.words('english'))
    with open('data/xkcd_comics.json', encoding='utf8') as f:
        COMICS = json.load(f)
    with open('data/xkcd_blob.json') as f:
        BLOB = json.load(f)
    CURRENT_URL = 'https://xkcd.com/info.0.json'

    def __init__(self, bot):
        self.bot = bot
        self.session = bot.aio_session

    def process_text(self, text: str) -> str:
        """A helper method to strip common words from text.

        Parameters
        ----------
        text : str
            Text to be processed.

        Returns
        -------
        str
            The stripped text.
        """
        stripped_set = set([re.sub('\W+', '', x) for x in text.lower().split()])
        return ' '.join(stripped_set - self.STOPWORDS)

    def get_best_match(self, query: str) -> Union[Tuple[int, str], None]:
        """A helper method to retrieve a comic most similar to given input.

        Parameters
        ----------
        query : str
            User query for a comic.

        Returns
        -------
        Union[Tuple[int, str], None]
           (number_of_matches, str id of comic)
           Returns None if there were no hits whatsoever.
        """
        match_list = []
        input_set = set(query.lower().split())
        for key in self.BLOB:
            # Union of the two sets to determine # of whole word matches.
            strength = len(set(key.split()) & input_set)
            match_list.append((strength, self.BLOB[key]))

        # Sort the match list based on # of matches and select the first result.
        match_list.sort(key=lambda x: x[0], reverse=True)
        best_match = match_list[0]
        if best_match[0] == 0:
            # If None, comic_to_embed will select a random comic
            return None

        return best_match

    def comic_to_embed(self, id_tup: Union[Tuple, None]) -> discord.Embed:
        """A helper method to convert an xkcd comic to an embed.

        Parameters
        ----------
        id_tup : tuple
            The tuple returned by the get_best_match method.
            Can also be none to return a random comic

        Returns
        -------
        discord.Embed
        """
        # Determines whether to grab a random comic.
        if id_tup is None:
            comic = self.COMICS[random.choice(list(self.COMICS))]
        else:
            comic = self.COMICS[id_tup[1]]

        # Creates the embed
        em = discord.Embed()
        em.title = f"XKCD {comic['num']}: {comic['safe_title']}"
        em.set_image(url=comic['img'])
        # Some responses don't contain links
        em.url = comic['link'] or f'https://xkcd.com/{comic["num"]}/'

        # Determines what kind of footer to display
        # If id_tup is None, then it's a random comic
        if id_tup is None:
            footer = f'(Random comic) {comic["alt"]}'
        # If id_tup[0] is None, then the user searched an exact comic number
        elif id_tup[0] is None:
            footer = comic['alt']
        # The user searched via text
        else:
            footer = f'Matched with {id_tup[0]} hit(s)'
        em.set_footer(text=footer)
        em.timestamp = datetime(int(comic['year']),
                                int(comic['month']),
                                int(comic['day']))

        return em

    @commands.group(aliases=['xk'], invoke_without_command=True)
    async def xkcd(self, ctx, number: str = None):
        """Search for an xkcd by its number, or get a random one"""
        if number is None:
            return await ctx.send(embed=self.comic_to_embed(None))

        if number in self.COMICS:
            return await ctx.send(embed=self.comic_to_embed((None, number)))
        else:
            em = discord.Embed(title=':no_entry_sign: Comic not found')
            await ctx.send(embed=em)

    @xkcd.command(aliases=['s'])
    async def search(self, ctx, *, query):
        """Search for an xkcd comic with text"""
        best_match = self.get_best_match(query)
        comic = self.comic_to_embed(best_match)
        await ctx.send(embed=comic)

    @xkcd.command(name='update', aliases=['up'])
    @commands.is_owner()
    async def _update(self, ctx):
        """Update the xkcd file"""
        # Get the most recent comic
        async with self.session.get(self.CURRENT_URL) as r:
            current_comic = await r.json()

        most_recent_in_file = max([int(x) for x in self.COMICS])
        # If comics are already updated
        if current_comic['num'] == most_recent_in_file:
            em = discord.Embed(title=':no_entry_sign: Comics already up-to-date boss!',
                               color=discord.Color.dark_red())
            return await ctx.send(embed=em)

        # Gather comics to update and download them
        comics_to_update = list(range(most_recent_in_file, current_comic['num'] + 1))
        url = 'http://xkcd.com/{}/info.0.json'
        for num_comic in comics_to_update:
            async with self.session.get(url.format(num_comic)) as r:
                self.COMICS[str(num_comic)] = await r.json()

            self.BLOB[self.process_text(f"{self.COMICS[str(num_comic)]['safe_title']} \
                                        {self.COMICS[str(num_comic)]['alt']}")] = str(num_comic)

        # Update comic file
        with open('data/xkcd_comics.json', 'w', encoding='utf8') as f:
            json.dump(self.COMICS, f)

        # Update blob file
        with open('data/xkcd_blob.json', 'w', encoding='utf8') as f:
            json.dump(self.BLOB, f)

        em = discord.Embed(title=f':white_check_mark: Updated {len(comics_to_update)} comics!')
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Comics(bot))
