#!/bin/env python3

import discord
from discord.ext import commands

class Moderator:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['k'])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """ Kick a member from the server """
        await ctx.guild.kick(member, reason=reason)
        await ctx.send(f'Member `{member}` kicked.\n'
                       f'Reason: `{reason}`.')

    @commands.command(aliases=['kb'])
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """ Ban a member from the server """
        await ctx.guild.ban(member, reason=reason, delete_message_days=0)
        await ctx.send(f'Member `{member}` banned.\n'
                       f'Reason: `{reason}`.')

    @commands.command(aliases=['ub'])
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: discord.Member, *, reason=None):
        """ Unban a member from the server
        Since you can't highlight them anymore use their name#discrim """
        await ctx.guild.unban(member, reason=reason)
        await ctx.send(f'Member `{member}` unbanned.\n'
                       f'Reason: `{reason}`.')

    @commands.command(aliases=['purge'])
    @commands.has_permissions(manage_messages=True)
    async def clean(self, ctx, num_msg: int):
        """ Remove bot messages from the last X messages """

        if num_msg > 100:
            return await ctx.send('Sorry, number of messages to be deleted must not exceed 100.')

        # Check so that only bot msgs are removed
        def check(message):
            return message.author.id == self.bot.member.id

        try:
            await ctx.channel.purge(check=check, limit=num_msg)
        except Exception as e:
            await ctx.send(f'Failed to delete messages.\n ```py\n{e}```')


def setup(bot):
    bot.add_cog(Moderator(bot))
