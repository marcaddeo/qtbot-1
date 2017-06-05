import discord, json
from discord.ext import commands
from cogs.utils import *
import xkcd as xklib

class Comics():
    def __init__(self, bot):
        self.bot = bot

    @commands.bot.command()
    async def xkcd(self, *args):
        """ Search for a vaguely relevant xkcd comic (if you're lucky). Otherwise returns a random comic """
        # pre-generated blob file
        with open("data/xkcd_blob.json", "r") as f:
            self.jsonData = json.load(f)

        # Split query into list and remove nonalpha phrases
        self.wList = " ".join(args).lower().split()
        for x in self.wList[:]:
            if not x.isalpha():
                self.wList.remove(x)

        # Short circuit upon no alpha input --> rand comic
        if not self.wList:
            self.randComic = xklib.getRandomComic()
            return await self.bot.say("**{}**\n{}".format(self.randComic.getTitle(), self.randComic.getImageLink()))

        self.matchDict = {}
        for key, value in self.jsonData.items():
            self.count = 0
            for uw in self.wList:
                if uw in self.jsonData[key]["tfidf_words"]:
                    self.count += 1
            self.matchDict[self.jsonData[key]["num"]] = self.count

        self.n = keywithmaxval(self.matchDict)

        # no matches found --> random comic
        if self.matchDict[self.n] == 0:
            self.randComic = xklib.getRandomComic()
            return await self.bot.say("**{}**\n{}".format(self.randComic.getTitle(), self.randComic.getImageLink()))

        self.comic = xklib.getComic(self.n)

        return await self.bot.say("I found this comic with {} hits\n**{}**\n{}".format(self.matchDict[self.n], self.comic.getTitle(), self.comic.getImageLink()))

def setup(bot):
    bot.add_cog(Comics(bot))